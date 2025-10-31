from __future__ import annotations

import argparse
import importlib
import json
import platform
import time
from pathlib import Path
from typing import Any


def check_dependencies() -> dict[str, bool]:
    deps = {"tiktoken": False, "faker": False}
    for name in list(deps.keys()):
        try:
            importlib.import_module(name)
            deps[name] = True
        except Exception:
            deps[name] = False
    return deps


def print_banner(text: str):
    print("\n" + "=" * len(text))
    print(text)
    print("=" * len(text))


def get_system_info() -> dict[str, Any]:
    import sys

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run TOON benchmarks")
    parser.add_argument(
        "--token-efficiency",
        action="store_true",
        help="Run token efficiency benchmark only",
    )
    parser.add_argument("--speed", action="store_true", help="Run speed benchmark only")
    parser.add_argument(
        "--memory", action="store_true", help="Run memory benchmark only"
    )
    parser.add_argument(
        "--stress", action="store_true", help="Run stress benchmark with large-scale data"
    )
    parser.add_argument(
        "--realworld",
        action="store_true",
        help="Run real-world API response validation and token efficiency benchmark"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all benchmarks (default)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: benchmarks/results)",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--json",
        dest="json_out",
        action="store_true",
        help="Write combined JSON output",
    )

    args = parser.parse_args(argv)

    deps = check_dependencies()
    if args.verbose:
        print("Dependencies:", deps)

    # Determine which to run
    run_any = args.token_efficiency or args.speed or args.memory or args.stress or args.realworld or args.all
    if not run_any:
        args.all = True

    out_dir = args.output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    combined: dict[str, Any] = {"metadata": get_system_info()}

    # Token efficiency
    if args.all or args.token_efficiency:
        if not deps["tiktoken"]:
            print("[skip] token-efficiency: requires tiktoken (pip install tiktoken)")
        elif not deps["faker"]:
            print(
                '[skip] token-efficiency: requires faker (pip install faker or pip install -e ".[benchmark]")'
            )
        else:
            print_banner("Running Token Efficiency Benchmark…")
            start = time.time()
            from .token_efficiency import run_token_efficiency_benchmark

            res = run_token_efficiency_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            print(
                f"Total savings: {res['totals']['savings_percent']:.1f}% | wrote: {res['output']} | {elapsed:.2f}s"
            )
            combined["token_efficiency"] = res

    # Speed
    if args.all or args.speed:
        if not deps["faker"]:
            print(
                '[skip] speed: requires faker (pip install faker or pip install -e ".[benchmark]")'
            )
        else:
            print_banner("Running Speed Benchmark…")
            start = time.time()
            from .speed_benchmark import run_speed_benchmark

            res = run_speed_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            enc = res["summary"]["encoding"]["avg_speedup"]
            dec = res["summary"]["decoding"]["avg_speedup"]
            print(
                f"Avg speedup (encode/dec): {enc:.2f}x / {dec:.2f}x | wrote: {out_dir / 'speed-benchmark.md'} | {elapsed:.2f}s"
            )
            combined["speed"] = res

    # Memory
    if args.all or args.memory:
        if not deps["faker"]:
            print(
                '[skip] memory: requires faker (pip install faker or pip install -e ".[benchmark]")'
            )
        else:
            print_banner("Running Memory Benchmark…")
            start = time.time()
            from .memory_benchmark import run_memory_benchmark

            res = run_memory_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            print(f"Wrote: {out_dir / 'memory-benchmark.md'} | {elapsed:.2f}s")
            combined["memory"] = res

    # Stress
    if args.all or args.stress:
        if not deps["faker"]:
            print(
                '[skip] stress: requires faker (pip install faker or pip install -e ".[benchmark]")'
            )
        else:
            print_banner("Running Stress Benchmark…")
            start = time.time()
            from .stress_benchmark import run_stress_benchmark

            res = run_stress_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            print(
                f"Completed {res['summary']['total_scenarios']} scenarios | wrote: {out_dir / 'stress-benchmark.md'} | {elapsed:.2f}s"
            )
            combined["stress"] = res

    # Real-world
    if args.all or args.realworld:
        if not deps["tiktoken"]:
            print('[skip] realworld: requires tiktoken (pip install tiktoken)')
        else:
            print_banner("Running Real-World API Benchmark…")
            start = time.time()
            from .realworld_benchmark import run_realworld_benchmark

            res = run_realworld_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            compatible = res['summary']['compatible']
            total = res['summary']['total_samples']
            savings = res['summary']['avg_savings_percent']

            if total == 0:
                print(f"[skip] realworld: no samples found in data/realworld | {elapsed:.2f}s")
            else:
                print(
                    f"Compatibility: {compatible}/{total} samples | Avg savings: {savings:.1f}% | wrote: {out_dir / 'realworld-benchmark.md'} | {elapsed:.2f}s"
                )
            combined["realworld"] = res

    # Combined JSON
    if args.json_out:
        (out_dir / "all-benchmarks.json").write_text(
            json.dumps(combined, indent=2), encoding="utf-8"
        )
        if args.verbose:
            print("Wrote:", out_dir / "all-benchmarks.json")

    # Summary README
    lines = ["# Benchmarks Summary", "", f"System: {json.dumps(get_system_info())}", ""]
    if "token_efficiency" in combined:
        te = combined["token_efficiency"]["totals"]
        lines.append(
            f"- Token Efficiency: {te['savings_percent']:.1f}% saved (TOON {te['toon_tokens']:,} vs JSON {te['json_tokens']:,}) — see token-efficiency.md"
        )
    if "speed" in combined:
        s = combined["speed"]["summary"]
        lines.append(
            f"- Speed: avg encode {s['encoding']['avg_speedup']:.2f}x, avg decode {s['decoding']['avg_speedup']:.2f}x — see speed-benchmark.md"
        )
    if "memory" in combined:
        lines.append("- Memory: see memory-benchmark.md")
    if "stress" in combined:
        s = combined["stress"]["summary"]
        lines.append(
            f"- Stress: {s['passed']}/{s['total_scenarios']} scenarios passed, max memory {s['max_memory_mb']:.1f}MB — see stress-benchmark.md"
        )
    if "realworld" in combined:
        s = combined["realworld"]["summary"]
        lines.append(
            f"- Real-World: {s['compatible']}/{s['total_samples']} samples compatible, {s['avg_savings_percent']:.1f}% avg token savings — see realworld-benchmark.md"
        )
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
