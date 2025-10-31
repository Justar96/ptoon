from __future__ import annotations

import gc
import json
import multiprocessing
import queue
import signal
import statistics
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Callable

import ptoon

from .utils import format_bytes, format_time


def _get_faker() -> Any:
    """Return a seeded Faker instance (seed=12345). Import only when needed."""
    try:
        from faker import Faker  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise RuntimeError(
            "Dataset generation requires 'faker'. Install with: pip install faker"
        ) from exc
    Faker.seed(12345)
    return Faker()


# ============================================================================
# Dataset Generators
# ============================================================================


def generate_deeply_nested_structure(depth: int, breadth: int = 3) -> dict[str, Any]:
    """Generate nested objects/arrays to specified depth.

    Args:
        depth: Nesting depth (10-15 recommended for stress testing)
        breadth: Number of children at each level

    Returns:
        Deeply nested structure alternating between objects and arrays
    """
    fk = _get_faker()

    def build_level(current_depth: int, use_array: bool) -> Any:
        if current_depth >= depth:
            # Leaf nodes: primitive values
            return fk.random_element([
                fk.random_int(0, 1000),
                fk.word(),
                fk.random.random() < 0.5,
            ])

        if use_array:
            # Array level
            return [
                build_level(current_depth + 1, False)
                for _ in range(breadth)
            ]
        else:
            # Object level
            return {
                f"field_{i}": build_level(current_depth + 1, True)
                for i in range(breadth)
            }

    return {"root": build_level(0, False)}


def generate_wide_array(size: int, element_type: str = "primitives") -> list[Any]:
    """Generate arrays with many items (100K-1M).

    Args:
        size: Number of array elements
        element_type: 'primitives', 'objects', or 'mixed'

    Returns:
        Large array optimized for specified element type
    """
    fk = _get_faker()

    if element_type == "primitives":
        # Mixed primitive types
        return [
            fk.random_element([
                fk.random_int(0, 10000),
                fk.word(),
                fk.random.random() < 0.5,
            ])
            for _ in range(size)
        ]
    elif element_type == "objects":
        # Uniform objects for tabular format
        return [
            {
                "id": i,
                "name": fk.name(),
                "value": fk.random_int(0, 1000),
                "active": i % 3 == 0,
            }
            for i in range(size)
        ]
    else:  # mixed
        # Heterogeneous elements (forces list format)
        result: list[Any] = []
        for i in range(size):
            if i % 3 == 0:
                result.append(fk.random_int(0, 1000))
            elif i % 3 == 1:
                result.append({"nested": fk.word()})
            else:
                result.append([fk.word(), fk.random_int(0, 100)])
        return result


def generate_large_tabular_dataset(rows: int, columns: int = 10) -> dict[str, Any]:
    """Generate uniform tabular data (10K-50K rows).

    Args:
        rows: Number of data rows
        columns: Number of columns (5-20 recommended)

    Returns:
        Dict with uniform records array (optimal for tabular TOON format)
    """
    fk = _get_faker()

    records: list[dict[str, Any]] = []
    for i in range(rows):
        record: dict[str, Any] = {"id": i}
        for col in range(columns - 1):  # -1 because id is already there
            # Mix of column types
            if col % 4 == 0:
                record[f"col_{col}"] = fk.random_int(0, 100000)
            elif col % 4 == 1:
                record[f"col_{col}"] = fk.word()
            elif col % 4 == 2:
                record[f"col_{col}"] = round(fk.random.uniform(0, 1000), 2)
            else:
                record[f"col_{col}"] = fk.random.random() < 0.5
        records.append(record)

    return {"records": records}


def generate_payload_by_size(target_mb: int, structure_type: str = "tabular") -> dict[str, Any]:
    """Generate payload targeting specific size in MB.

    Args:
        target_mb: Target size in megabytes
        structure_type: 'tabular', 'nested', 'wide_array', or 'mixed'

    Returns:
        Data structure of approximately target size (within ±5% tolerance)
    """
    target_bytes = target_mb * 1024 * 1024
    tolerance = 0.05  # ±5%
    max_iterations = 10

    # Initial parameter estimates
    if structure_type == "tabular":
        rows = max(100, target_bytes // 200)
        columns = 10
    elif structure_type == "nested":
        depth = min(15, max(8, 8 + target_mb // 10))
        breadth = min(10, max(3, 3 + target_mb // 20))
    elif structure_type == "wide_array":
        array_size = max(1000, target_bytes // 50)
    else:  # mixed
        tabular_rows = max(100, target_bytes // 500)
        array_size = max(100, min(10000, target_bytes // 100))
        nested_depth = 8
        nested_breadth = 3

    # Iteratively adjust to reach target size
    for iteration in range(max_iterations):
        # Generate data with current parameters
        if structure_type == "tabular":
            data = generate_large_tabular_dataset(max(1, rows), columns)
        elif structure_type == "nested":
            data = generate_deeply_nested_structure(max(1, depth), max(1, breadth))
        elif structure_type == "wide_array":
            data = {"array": generate_wide_array(max(1, array_size), "objects")}
        else:  # mixed
            data = {
                "nested": generate_deeply_nested_structure(max(1, nested_depth), max(1, nested_breadth)),
                "tabular": generate_large_tabular_dataset(max(1, tabular_rows), 8),
                "array": generate_wide_array(max(1, array_size), "mixed"),
            }

        # Measure actual size
        json_str = json.dumps(data, ensure_ascii=False)
        actual_bytes = len(json_str.encode("utf-8"))

        # Check if within tolerance
        lower_bound = target_bytes * (1 - tolerance)
        upper_bound = target_bytes * (1 + tolerance)

        if lower_bound <= actual_bytes <= upper_bound:
            # Within tolerance, done
            return data

        # Calculate scale factor for adjustment
        if actual_bytes > 0:
            scale_factor = target_bytes / actual_bytes
        else:
            scale_factor = 2.0

        # Adjust parameters based on scale factor
        if structure_type == "tabular":
            if actual_bytes < target_bytes:
                rows = max(1, int(rows * scale_factor * 1.05))
            else:
                rows = max(1, int(rows * scale_factor * 0.95))
        elif structure_type == "nested":
            # Adjust depth and breadth for nested structures
            if actual_bytes < target_bytes:
                # Increase breadth first (more impact), then depth
                if breadth < 10:
                    breadth = min(10, int(breadth * 1.3))
                elif depth < 15:
                    depth = min(15, int(depth * 1.1))
            else:
                # Decrease breadth first, then depth
                if breadth > 2:
                    breadth = max(2, int(breadth * 0.9))
                elif depth > 2:
                    depth = max(2, int(depth * 0.9))
        elif structure_type == "wide_array":
            if actual_bytes < target_bytes:
                array_size = max(1, int(array_size * scale_factor * 1.05))
            else:
                array_size = max(1, int(array_size * scale_factor * 0.95))
        else:  # mixed
            if actual_bytes < target_bytes:
                tabular_rows = max(1, int(tabular_rows * scale_factor * 1.05))
                array_size = max(1, int(array_size * scale_factor * 1.05))
                if nested_breadth < 10:
                    nested_breadth = min(10, nested_breadth + 1)
            else:
                tabular_rows = max(1, int(tabular_rows * scale_factor * 0.95))
                array_size = max(1, int(array_size * scale_factor * 0.95))
                if nested_breadth > 2:
                    nested_breadth = max(2, nested_breadth - 1)

    # Return best effort after max iterations
    return data


# ============================================================================
# Measurement Infrastructure
# ============================================================================


class TimeoutException(Exception):
    """Raised when operation times out."""
    pass


def _timeout_handler(signum: int, frame: Any) -> None:
    """Signal handler for timeout."""
    raise TimeoutException("Operation timed out")


def _worker_target(result_queue: multiprocessing.Queue, func: Callable[..., Any], args: tuple, kwargs: dict) -> None:
    """Worker function to run in separate process (Windows timeout).

    Puts the result or exception marker into the queue.
    """
    try:
        result = func(*args, **kwargs)
        result_queue.put(("success", result))
    except Exception as e:
        result_queue.put(("error", e))


def measure_with_timeout(
    func: Callable[..., Any],
    timeout_seconds: int,
    *args: Any,
    **kwargs: Any
) -> tuple[Any, float, bool]:
    """Execute function with timeout protection.

    Args:
        func: Function to execute
        timeout_seconds: Timeout in seconds
        *args, **kwargs: Arguments to pass to func

    Returns:
        Tuple of (result, duration, timed_out)

    Note:
        On Windows, uses multiprocessing with spawn context and forcibly terminates
        timed-out workers via proc.terminate() + proc.join(). This is necessary because
        ProcessPoolExecutor's with-block calls shutdown(wait=True) by default, which
        blocks waiting for tasks to complete, defeating the timeout.

        On Unix, uses signal-based timeout (more efficient for single-process cases).
    """
    result = None
    timed_out = False
    start = time.perf_counter()

    # Use signal-based timeout on Unix, multiprocessing on Windows
    if sys.platform == "win32":
        # Windows: use multiprocessing with spawn for true timeout and termination
        # Must use spawn context (default on Windows) for proper process isolation
        ctx = multiprocessing.get_context("spawn")
        result_queue: multiprocessing.Queue = ctx.Queue()

        # Create worker process
        proc = ctx.Process(
            target=_worker_target,
            args=(result_queue, func, args, kwargs)
        )

        try:
            proc.start()

            # Wait for result with timeout
            try:
                status, value = result_queue.get(timeout=timeout_seconds)
                duration = time.perf_counter() - start

                if status == "success":
                    result = value
                    timed_out = False
                    # Clean join on success
                    proc.join(timeout=1)
                else:  # error
                    # Clean join before re-raising
                    proc.join(timeout=1)
                    # Re-raise the exception from the worker
                    raise value

            except queue.Empty:
                # Timeout occurred
                duration = time.perf_counter() - start
                timed_out = True
                result = None

                # Forcibly terminate the worker process
                proc.terminate()
                proc.join(timeout=5)  # Wait up to 5s for clean termination

                if proc.is_alive():
                    # If still alive after terminate+join, force kill
                    proc.kill()
                    proc.join()

        finally:
            # Final cleanup: ensure process is terminated if still running
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=1)
                if proc.is_alive():
                    proc.kill()
                    proc.join()

    else:
        # Unix: use signal
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel alarm
            duration = time.perf_counter() - start
        except TimeoutException:
            duration = time.perf_counter() - start
            timed_out = True
            result = None
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    return result, duration, timed_out


def measure_latency_percentiles(
    func: Callable[..., Any],
    iterations: int,
    *args: Any,
    **kwargs: Any
) -> dict[str, float]:
    """Run function multiple times and calculate latency percentiles.

    Args:
        func: Function to benchmark
        iterations: Number of iterations
        *args, **kwargs: Arguments to pass to func

    Returns:
        Dict with keys: p50, p95, p99, min, max, mean
    """
    times: list[float] = []

    for _ in range(iterations):
        gc.collect()
        start = time.perf_counter()
        func(*args, **kwargs)
        duration = time.perf_counter() - start
        times.append(duration)

    times.sort()

    return {
        "p50": times[len(times) // 2] if times else 0.0,
        "p95": times[int(len(times) * 0.95)] if times else 0.0,
        "p99": times[int(len(times) * 0.99)] if times else 0.0,
        "min": min(times) if times else 0.0,
        "max": max(times) if times else 0.0,
        "mean": statistics.mean(times) if times else 0.0,
    }


def measure_stress_scenario(
    data: Any,
    scenario_name: str,
    timeout: int = 300
) -> dict[str, Any]:
    """Orchestrate measurements for a single stress scenario.

    Args:
        data: Data to test
        scenario_name: Human-readable scenario name
        timeout: Timeout in seconds (default 5 minutes)

    Returns:
        Dict with measurement results and metadata
    """
    result: dict[str, Any] = {
        "scenario": scenario_name,
        "data_size_mb": _estimate_data_size_mb(data),
        "encode_time": 0.0,
        "decode_time": 0.0,
        "encode_memory_mb": 0.0,
        "decode_memory_mb": 0.0,
        "latency_percentiles": {},
        "timed_out": False,
        "error": None,
    }

    try:
        # Encoding with timeout
        toon_str, encode_time, encode_timeout = measure_with_timeout(
            ptoon.encode, timeout, data
        )
        result["encode_time"] = encode_time
        result["timed_out"] = encode_timeout

        if encode_timeout:
            result["error"] = "Encoding timed out"
            return result

        # Encoding memory
        gc.collect()
        tracemalloc.start()
        try:
            _ = ptoon.encode(data)
            _, peak_enc = tracemalloc.get_traced_memory()
            result["encode_memory_mb"] = peak_enc / (1024 * 1024)
        finally:
            tracemalloc.stop()

        # Decoding with timeout
        decoded, decode_time, decode_timeout = measure_with_timeout(
            ptoon.decode, timeout, toon_str
        )
        result["decode_time"] = decode_time

        if decode_timeout:
            result["timed_out"] = True
            result["error"] = "Decoding timed out"
            return result

        # Decoding memory
        gc.collect()
        tracemalloc.start()
        try:
            _ = ptoon.decode(toon_str)
            _, peak_dec = tracemalloc.get_traced_memory()
            result["decode_memory_mb"] = peak_dec / (1024 * 1024)
        finally:
            tracemalloc.stop()

        # Latency percentiles (fewer iterations for large data)
        data_mb = result["data_size_mb"]
        iterations = 3 if data_mb > 10 else (5 if data_mb > 1 else 10)

        encode_percentiles = measure_latency_percentiles(
            ptoon.encode, iterations, data
        )
        decode_percentiles = measure_latency_percentiles(
            ptoon.decode, iterations, toon_str
        )

        result["latency_percentiles"] = {
            "encode": encode_percentiles,
            "decode": decode_percentiles,
        }

        # Roundtrip validation
        if decoded != data:
            result["error"] = "Roundtrip validation failed"

    except Exception as e:
        result["error"] = str(e)

    return result


# ============================================================================
# Stress Test Runner
# ============================================================================


def run_stress_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    """Run stress benchmark with large-scale data scenarios.

    Args:
        output_dir: Output directory for results (default: benchmarks/results)

    Returns:
        Dict with scenarios, summary, and output path
    """
    results: list[dict[str, Any]] = []

    # Define stress scenarios
    scenarios: list[tuple[str, Callable[[], Any], int]] = [
        # (name, generator, timeout_seconds)
        ("Deeply Nested (10 levels)", lambda: generate_deeply_nested_structure(10), 60),
        ("Deeply Nested (12 levels)", lambda: generate_deeply_nested_structure(12), 120),
        ("Deeply Nested (15 levels)", lambda: generate_deeply_nested_structure(15), 300),

        ("Wide Array - 100K primitives", lambda: {"array": generate_wide_array(100_000, "primitives")}, 60),
        ("Wide Array - 100K objects", lambda: {"array": generate_wide_array(100_000, "objects")}, 120),
        ("Wide Array - 500K objects", lambda: {"array": generate_wide_array(500_000, "objects")}, 300),

        ("Large Tabular - 10K rows", lambda: generate_large_tabular_dataset(10_000), 60),
        ("Large Tabular - 25K rows", lambda: generate_large_tabular_dataset(25_000), 120),
        ("Large Tabular - 50K rows", lambda: generate_large_tabular_dataset(50_000), 300),

        ("Payload - 1MB tabular", lambda: generate_payload_by_size(1, "tabular"), 60),
        ("Payload - 10MB tabular", lambda: generate_payload_by_size(10, "tabular"), 180),
        ("Payload - 50MB tabular", lambda: generate_payload_by_size(50, "tabular"), 600),
        ("Payload - 100MB tabular", lambda: generate_payload_by_size(100, "tabular"), 1200),
        ("Payload - 1MB nested", lambda: generate_payload_by_size(1, "nested"), 60),
        ("Payload - 10MB mixed", lambda: generate_payload_by_size(10, "mixed"), 300),
        ("Payload - 50MB mixed", lambda: generate_payload_by_size(50, "mixed"), 600),
    ]

    print(f"Running {len(scenarios)} stress scenarios...")

    for i, (name, generator, timeout) in enumerate(scenarios, 1):
        print(f"  [{i}/{len(scenarios)}] {name}...", end=" ", flush=True)

        try:
            data = generator()
            scenario_result = measure_stress_scenario(data, name, timeout)
            results.append(scenario_result)

            if scenario_result["timed_out"]:
                print("⏱ TIMEOUT")
            elif scenario_result["error"]:
                print(f"✗ ERROR: {scenario_result['error']}")
            else:
                print(f"✓ {format_time(scenario_result['encode_time'] + scenario_result['decode_time'])}")
        except Exception as e:
            print(f"✗ EXCEPTION: {e}")
            results.append({
                "scenario": name,
                "error": str(e),
                "timed_out": False,
            })

    # Calculate summary
    passed = sum(1 for r in results if not r.get("error") and not r.get("timed_out"))
    failed = len(results) - passed
    max_memory = max(
        (max(r.get("encode_memory_mb", 0), r.get("decode_memory_mb", 0)) for r in results),
        default=0.0
    )

    summary = {
        "total_scenarios": len(results),
        "passed": passed,
        "failed": failed,
        "max_memory_mb": max_memory,
    }

    # Generate report
    report_md = _generate_stress_report(results, summary)

    # Write output
    out_dir = output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    md_path = out_dir / "stress-benchmark.md"
    json_path = out_dir / "stress-benchmark.json"

    md_path.write_text(report_md, encoding="utf-8")
    json_path.write_text(
        json.dumps({"scenarios": results, "summary": summary}, indent=2),
        encoding="utf-8"
    )

    return {
        "scenarios": results,
        "summary": summary,
        "output": str(md_path),
    }


# ============================================================================
# Report Generation
# ============================================================================


def _generate_stress_report(results: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    """Generate markdown report for stress benchmark.

    Args:
        results: List of scenario results
        summary: Summary statistics

    Returns:
        Markdown report string
    """
    lines = ["# Stress Benchmark", ""]
    lines.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Scenarios: {summary['passed']}/{summary['total_scenarios']} passed")
    lines.append("")

    # Overview table
    lines.append("## Overview")
    lines.append("")
    lines.append("| Scenario | Data Size | Encode Time | Decode Time | Memory Peak | Status |")
    lines.append("|---|---:|---:|---:|---:|---|")

    for r in results:
        scenario = r.get("scenario", "Unknown")
        data_size = format_bytes(int(r.get("data_size_mb", 0) * 1024 * 1024))
        encode_time = format_time(r.get("encode_time", 0)) if r.get("encode_time") else "—"
        decode_time = format_time(r.get("decode_time", 0)) if r.get("decode_time") else "—"
        memory_mb = max(r.get("encode_memory_mb", 0), r.get("decode_memory_mb", 0))
        memory_str = format_bytes(int(memory_mb * 1024 * 1024)) if memory_mb > 0 else "—"

        if r.get("timed_out"):
            status = "⏱ Timeout"
        elif r.get("error"):
            status = "✗ Error"
        else:
            status = "✓ Pass"

        lines.append(f"| {scenario} | {data_size} | {encode_time} | {decode_time} | {memory_str} | {status} |")

    lines.append("")

    # Latency analysis
    lines.append("## Latency Analysis")
    lines.append("")
    lines.append("Percentile breakdown for successful scenarios:")
    lines.append("")

    for r in results:
        if r.get("error") or r.get("timed_out") or "latency_percentiles" not in r:
            continue

        scenario = r["scenario"]
        lines.append(f"### {scenario}")
        lines.append("")
        lines.append("| Operation | p50 | p95 | p99 | min | max |")
        lines.append("|---|---:|---:|---:|---:|---:|")

        for op in ["encode", "decode"]:
            if op in r["latency_percentiles"]:
                p = r["latency_percentiles"][op]
                lines.append(
                    f"| {op.capitalize()} | {format_time(p['p50'])} | {format_time(p['p95'])} | "
                    f"{format_time(p['p99'])} | {format_time(p['min'])} | {format_time(p['max'])} |"
                )

        lines.append("")

    # Failures/timeouts
    failures = [r for r in results if r.get("error") or r.get("timed_out")]
    if failures:
        lines.append("## Failures & Timeouts")
        lines.append("")
        for r in failures:
            scenario = r.get("scenario", "Unknown")
            error = r.get("error", "Timeout" if r.get("timed_out") else "Unknown error")
            lines.append(f"- **{scenario}**: {error}")
        lines.append("")

    # Summary statistics
    lines.append("## Summary Statistics")
    lines.append("")
    lines.append(f"- Total scenarios: {summary['total_scenarios']}")
    lines.append(f"- Passed: {summary['passed']}")
    lines.append(f"- Failed: {summary['failed']}")
    lines.append(f"- Max memory used: {format_bytes(int(summary['max_memory_mb'] * 1024 * 1024))}")

    # Find slowest operations
    encode_times = [(r["scenario"], r["encode_time"]) for r in results if "encode_time" in r and r["encode_time"] > 0]
    decode_times = [(r["scenario"], r["decode_time"]) for r in results if "decode_time" in r and r["decode_time"] > 0]

    if encode_times:
        slowest_encode = max(encode_times, key=lambda x: x[1])
        lines.append(f"- Slowest encode: {slowest_encode[0]} ({format_time(slowest_encode[1])})")

    if decode_times:
        slowest_decode = max(decode_times, key=lambda x: x[1])
        lines.append(f"- Slowest decode: {slowest_decode[0]} ({format_time(slowest_decode[1])})")

    lines.append("")

    return "\n".join(lines)


# ============================================================================
# Utility Functions
# ============================================================================


def _estimate_data_size_mb(data: Any) -> float:
    """Estimate in-memory size by encoding to JSON.

    Args:
        data: Data structure to estimate

    Returns:
        Size in megabytes
    """
    json_str = json.dumps(data, ensure_ascii=False)
    bytes_count = len(json_str.encode("utf-8"))
    return bytes_count / (1024 * 1024)


def _format_latency_percentiles(percentiles: dict[str, float]) -> str:
    """Format percentile dict as readable string.

    Args:
        percentiles: Dict with p50, p95, p99 keys

    Returns:
        Formatted string for markdown tables
    """
    return f"p50={format_time(percentiles['p50'])}, p95={format_time(percentiles['p95'])}, p99={format_time(percentiles['p99'])}"


if __name__ == "__main__":
    res = run_stress_benchmark()
    print(json.dumps(res["summary"], indent=2))
