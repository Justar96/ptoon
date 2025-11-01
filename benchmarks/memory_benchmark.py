from __future__ import annotations

import gc
import json
import sys
import tracemalloc
from pathlib import Path
from typing import Any

import ptoon

from .datasets import get_all_datasets
from .utils import format_bytes


# Number of times to repeat memory measurements (use min to get conservative estimate)
MEMORY_REPEATS = 5


def measure_memory(func, *args, **kwargs) -> tuple[Any, int, int]:
    gc.collect()
    tracemalloc.start()
    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, current, peak


def measure_memory_repeated(func, *args, **kwargs) -> tuple[Any, int, int]:
    """Measure memory multiple times and return minimum peak (conservative estimate)."""
    peaks: list[int] = []
    result = None
    for _ in range(MEMORY_REPEATS):
        result, current, peak = measure_memory(func, *args, **kwargs)
        peaks.append(peak)
    return result, current, min(peaks)


def run_memory_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    datasets = get_all_datasets()
    results: dict[str, Any] = {"string_size": [], "encoding": [], "decoding": []}

    for name, _emoji, _description, data in datasets:
        json_str = json.dumps(data, ensure_ascii=False)
        toon_str = ptoon.encode(data)

        # output size comparison (bytes of Python str -> size in memory via getsizeof)
        json_size = sys.getsizeof(json_str)
        toon_size = sys.getsizeof(toon_str)
        size_diff = json_size - toon_size
        size_pct = (size_diff / json_size * 100.0) if json_size > 0 else 0.0
        results["string_size"].append(
            {
                "dataset": name,
                "json_size": json_size,
                "toon_size": toon_size,
                "diff": size_diff,
                "diff_percent": size_pct,
            }
        )

        # encoding memory (repeated measurements, use min peak)
        _, cur_json, peak_json = measure_memory_repeated(lambda data=data: json.dumps(data, ensure_ascii=False))
        _, cur_toon, peak_toon = measure_memory_repeated(lambda data=data: ptoon.encode(data))
        results["encoding"].append(
            {
                "dataset": name,
                "json_peak": peak_json,
                "toon_peak": peak_toon,
                "diff": peak_json - peak_toon,
            }
        )

        # decoding memory (repeated measurements, use min peak)
        _, cur_json_d, peak_json_d = measure_memory_repeated(lambda json_str=json_str: json.loads(json_str))
        _, cur_toon_d, peak_toon_d = measure_memory_repeated(lambda toon_str=toon_str: ptoon.decode(toon_str))
        results["decoding"].append(
            {
                "dataset": name,
                "json_peak": peak_json_d,
                "toon_peak": peak_toon_d,
                "diff": peak_json_d - peak_toon_d,
            }
        )

    # write reports
    out_dir = output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    md: list[str] = ["# Memory Benchmark", ""]
    md.append("## Output Size (sys.getsizeof on Python str)")
    md.append("")
    md.append("| Dataset | JSON | TOON | Diff | % |")
    md.append("|---|---:|---:|---:|---:|")
    for row in results["string_size"]:
        md.append(
            f"| {row['dataset']} | {format_bytes(row['json_size'])} | {format_bytes(row['toon_size'])} | {format_bytes(abs(row['diff']))} | {row['diff_percent']:.1f}% |"
        )
    md.append("")
    md.append("## Encoding Peak Memory (tracemalloc)")
    md.append("| Dataset | JSON | TOON | Diff |")
    md.append("|---|---:|---:|---:|")
    for row in results["encoding"]:
        md.append(
            f"| {row['dataset']} | {format_bytes(row['json_peak'])} | {format_bytes(row['toon_peak'])} | {format_bytes(abs(row['diff']))} |"
        )
    md.append("")
    md.append("## Decoding Peak Memory (tracemalloc)")
    md.append("| Dataset | JSON | TOON | Diff |")
    md.append("|---|---:|---:|---:|")
    for row in results["decoding"]:
        md.append(
            f"| {row['dataset']} | {format_bytes(row['json_peak'])} | {format_bytes(row['toon_peak'])} | {format_bytes(abs(row['diff']))} |"
        )
    md.append("")

    (out_dir / "memory-benchmark.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "memory-benchmark.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    res = run_memory_benchmark()
    print(json.dumps({k: len(v) for k, v in res.items() if isinstance(v, list)}, indent=2))
