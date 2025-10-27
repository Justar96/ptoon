from __future__ import annotations

import argparse
import importlib
import json
import platform
import time
from pathlib import Path
from typing import Any, Dict


def check_dependencies() -> Dict[str, bool]:
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


def get_system_info() -> Dict[str, Any]:
    import sys

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run TOON benchmarks")
    parser.add_argument("--token-efficiency", action="store_true", help="Run token efficiency benchmark only")
    parser.add_argument("--speed", action="store_true", help="Run speed benchmark only")
    parser.add_argument("--memory", action="store_true", help="Run memory benchmark only")
    parser.add_argument("--all", action="store_true", help="Run all benchmarks (default)")
    parser.add_argument("--output-dir", type=Path, default=None, help="Output directory (default: benchmarks/results)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Write combined JSON output")

    args = parser.parse_args(argv)

    deps = check_dependencies()
    if args.verbose:
        print("Dependencies:", deps)

    # Determine which to run
    run_any = args.token_efficiency or args.speed or args.memory or args.all
    if not run_any:
        args.all = True

    out_dir = args.output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    combined: Dict[str, Any] = {"metadata": get_system_info()}

    # Token efficiency
    if args.all or args.token_efficiency:
        if not deps["tiktoken"]:
            print("[skip] token-efficiency: requires tiktoken (pip install tiktoken)")
        elif not deps["faker"]:
            print("[skip] token-efficiency: requires faker (pip install faker or pip install -e \".[benchmark]\")")
        else:
            print_banner("Running Token Efficiency Benchmark…")
            start = time.time()
            from .token_efficiency import run_token_efficiency_benchmark

            res = run_token_efficiency_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            print(f"Total savings: {res['totals']['savings_percent']:.1f}% | wrote: {res['output']} | {elapsed:.2f}s")
            combined["token_efficiency"] = res

    # Speed
    if args.all or args.speed:
        if not deps["faker"]:
            print("[skip] speed: requires faker (pip install faker or pip install -e \".[benchmark]\")")
        else:
            print_banner("Running Speed Benchmark…")
            start = time.time()
            from .speed_benchmark import run_speed_benchmark

            res = run_speed_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            enc = res["summary"]["encoding"]["avg_speedup"]
            dec = res["summary"]["decoding"]["avg_speedup"]
            print(f"Avg speedup (encode/dec): {enc:.2f}x / {dec:.2f}x | wrote: {out_dir / 'speed-benchmark.md'} | {elapsed:.2f}s")
            combined["speed"] = res

    # Memory
    if args.all or args.memory:
        if not deps["faker"]:
            print("[skip] memory: requires faker (pip install faker or pip install -e \".[benchmark]\")")
        else:
            print_banner("Running Memory Benchmark…")
            start = time.time()
            from .memory_benchmark import run_memory_benchmark

            res = run_memory_benchmark(output_dir=out_dir)
            elapsed = time.time() - start
            print(f"Wrote: {out_dir / 'memory-benchmark.md'} | {elapsed:.2f}s")
            combined["memory"] = res

    # Combined JSON
    if args.json_out:
        (out_dir / "all-benchmarks.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
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
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
