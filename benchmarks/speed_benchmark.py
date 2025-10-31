from __future__ import annotations

import gc
import json
import statistics
import timeit
from pathlib import Path
from typing import Any

import ptoon

from .datasets import get_all_datasets


def format_time(seconds: float) -> str:
    ms = seconds * 1000.0
    if ms < 1.0:
        return f"{ms * 1000.0:.2f} µs"
    return f"{ms:.2f} ms"


def calculate_speedup(baseline: float, comparison: float) -> tuple[float, str]:
    if comparison == 0:
        return float("inf"), "∞x faster"
    ratio = baseline / comparison
    desc = f"{ratio:.2f}x faster" if ratio >= 1.0 else f"{(1/ratio):.2f}x slower"
    return ratio, desc


def adjust_iterations(data_size_bytes: int) -> int:
    if data_size_bytes < 10_000:
        return 2000
    if data_size_bytes < 200_000:
        return 500
    return 100


def _median_timer(fn, number: int, repeat: int = 5) -> float:
    times: list[float] = []
    for _ in range(repeat):
        gc.collect()
        gc.disable()
        try:
            t = timeit.timeit(fn, number=number)
        finally:
            gc.enable()
        times.append(t / number)
    return statistics.median(times)


def run_speed_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    datasets = get_all_datasets()
    results: dict[str, Any] = {"encoding": [], "decoding": [], "roundtrip": []}

    for name, _emoji, _description, data in datasets:
        json_str = json.dumps(data, ensure_ascii=False)
        toon_str = ptoon.encode(data)
        size_bytes = len(json_str.encode("utf-8")) + len(toon_str.encode("utf-8"))
        iters = adjust_iterations(size_bytes)

        # encoding
        enc_json = _median_timer(
            lambda data=data: json.dumps(data, ensure_ascii=False), number=iters
        )
        enc_toon = _median_timer(lambda data=data: ptoon.encode(data), number=iters)
        enc_ratio, enc_desc = calculate_speedup(enc_json, enc_toon)
        results["encoding"].append(
            {
                "dataset": name,
                "json_time": enc_json,
                "toon_time": enc_toon,
                "speedup": enc_ratio,
                "desc": enc_desc,
            }
        )

        # decoding
        dec_json = _median_timer(
            lambda json_str=json_str: json.loads(json_str), number=iters
        )
        dec_toon = _median_timer(
            lambda toon_str=toon_str: ptoon.decode(toon_str), number=iters
        )
        dec_ratio, dec_desc = calculate_speedup(dec_json, dec_toon)
        results["decoding"].append(
            {
                "dataset": name,
                "json_time": dec_json,
                "toon_time": dec_toon,
                "speedup": dec_ratio,
                "desc": dec_desc,
            }
        )

        # roundtrip
        rt_json = _median_timer(
            lambda data=data: json.loads(json.dumps(data, ensure_ascii=False)),
            number=iters,
        )
        rt_toon = _median_timer(
            lambda data=data: ptoon.decode(ptoon.encode(data)), number=iters
        )
        rt_ratio, rt_desc = calculate_speedup(rt_json, rt_toon)
        results["roundtrip"].append(
            {
                "dataset": name,
                "json_time": rt_json,
                "toon_time": rt_toon,
                "speedup": rt_ratio,
                "desc": rt_desc,
            }
        )

    # aggregates
    def _agg(kind: str) -> dict[str, float]:
        arr = results[kind]
        sp = [x["speedup"] for x in arr]
        return {
            "avg_speedup": float(statistics.mean(sp)) if sp else 0.0,
            "median_speedup": float(statistics.median(sp)) if sp else 0.0,
            "min_speedup": float(min(sp)) if sp else 0.0,
            "max_speedup": float(max(sp)) if sp else 0.0,
        }

    results["summary"] = {
        "encoding": _agg("encoding"),
        "decoding": _agg("decoding"),
        "roundtrip": _agg("roundtrip"),
    }

    # write report
    out_dir = output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)

    md = ["# Speed Benchmark", ""]
    for kind in ("encoding", "decoding", "roundtrip"):
        md.append(f"## {kind.title()}")
        md.append("")
        md.append("| Dataset | JSON | TOON | Speedup |")
        md.append("|---|---:|---:|---:|")
        for row in results[kind]:
            md.append(
                f"| {row['dataset']} | {format_time(row['json_time'])} | {format_time(row['toon_time'])} | {row['speedup']:.2f}x |"
            )
        s = results["summary"][kind]
        md.append("")
        md.append(
            f"Avg: {s['avg_speedup']:.2f}x, Median: {s['median_speedup']:.2f}x, Min: {s['min_speedup']:.2f}x, Max: {s['max_speedup']:.2f}x"
        )
        md.append("")

    (out_dir / "speed-benchmark.md").write_text("\n".join(md), encoding="utf-8")
    (out_dir / "speed-benchmark.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    res = run_speed_benchmark()
    print(json.dumps(res["summary"], indent=2))
