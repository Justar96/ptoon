from __future__ import annotations

import functools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .datasets import get_all_datasets


@functools.lru_cache(maxsize=1)
def _get_tokenizer():
    try:
        import tiktoken  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dep
        raise RuntimeError(
            "Token efficiency benchmark requires 'tiktoken'. Install with: pip install tiktoken"
        ) from exc
    return tiktoken.get_encoding("o200k_base")


def count_tokens(text: str) -> int:
    enc = _get_tokenizer()
    return len(enc.encode(text))


def format_number(n: int) -> str:
    return f"{n:,}"


def generate_bar_chart(percentage: float, max_width: int = 25) -> str:
    pct = max(0.0, min(100.0, percentage))
    filled = int(round((100 - pct) / 100 * max_width))
    empty = max_width - filled
    return f"{'█' * filled}{'░' * empty} {100 - pct:.1f}% TOON"


def truncate_dataset_for_display(name: str, data: dict[str, Any]) -> dict[str, Any]:
    # Heuristic truncation for readability
    if "repositories" in data:
        return {"repositories": data["repositories"][:3]}
    if "metrics" in data:
        return {"metrics": data["metrics"][:5]}
    if "orders" in data:
        return {"orders": data["orders"][:2]}
    if "employees" in data:
        return {"employees": data["employees"][:5]}
    return data


@dataclass
class DatasetResult:
    name: str
    emoji: str
    description: str
    json_tokens: int
    toon_tokens: int
    savings: int
    savings_percent: float


def _encode_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _encode_toon(data: Any) -> str:
    # Import toon lazily to avoid circular imports in some tooling
    import pytoon

    return pytoon.encode(data)


def generate_markdown_report(
    results: list[DatasetResult],
    totals: dict[str, Any],
    examples: dict[str, dict[str, Any]],
) -> str:
    lines: list[str] = []
    lines.append("# Token Efficiency Benchmark")
    lines.append("")
    for r in results:
        bar = generate_bar_chart(r.savings_percent)
        lines.append(
            f"- {r.emoji} {r.name}: {bar} — TOON {format_number(r.toon_tokens)} vs JSON {format_number(r.json_tokens)} | 💰 {r.savings_percent:.1f}% saved"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        f"Totals: TOON {format_number(totals['toon_tokens'])} vs JSON {format_number(totals['json_tokens'])} — 💰 {totals['savings_percent']:.1f}% saved"
    )
    lines.append("")

    # Collapsible details
    lines.append("## Details")
    for r in results:
        lines.append("")
        lines.append(
            f"<details><summary>{r.emoji} {r.name} — {r.savings_percent:.1f}% saved</summary>"
        )
        lines.append("")
        lines.append(r.description)
        lines.append("")
        lines.append("#### JSON (truncated)")
        # Use pre-truncated example data
        truncated = examples[r.name]
        lines.append("\n```json")
        lines.append(_encode_json(truncated)[:2000])
        lines.append("```\n")
        lines.append("#### TOON (truncated)")
        lines.append("\n```")
        lines.append(_encode_toon(truncated)[:2000])
        lines.append("```\n")
        lines.append("</details>")

    return "\n".join(lines)


def run_token_efficiency_benchmark(output_dir: Path | None = None) -> dict[str, Any]:
    datasets = get_all_datasets()
    results: list[DatasetResult] = []
    examples: dict[str, dict[str, Any]] = {}
    total_json = 0
    total_toon = 0

    for name, emoji, description, data in datasets:
        json_str = _encode_json(data)
        toon_str = _encode_toon(data)
        json_tok = count_tokens(json_str)
        toon_tok = count_tokens(toon_str)
        savings = max(0, json_tok - toon_tok)
        savings_pct = (savings / json_tok * 100.0) if json_tok > 0 else 0.0
        res = DatasetResult(
            name=name,
            emoji=emoji,
            description=description,
            json_tokens=json_tok,
            toon_tokens=toon_tok,
            savings=savings,
            savings_percent=savings_pct,
        )
        # Build truncated examples for report
        examples[name] = truncate_dataset_for_display(name, data)
        results.append(res)
        total_json += json_tok
        total_toon += toon_tok

    totals = {
        "json_tokens": total_json,
        "toon_tokens": total_toon,
        "savings": max(0, total_json - total_toon),
        "savings_percent": (
            ((total_json - total_toon) / total_json * 100.0) if total_json > 0 else 0.0
        ),
    }

    report = generate_markdown_report(results, totals, examples)

    out_dir = output_dir or (Path(__file__).resolve().parent / "results")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "token-efficiency.md").write_text(report, encoding="utf-8")

    return {
        "datasets": [
            {
                "name": r.name,
                "emoji": r.emoji,
                "description": r.description,
                "json_tokens": r.json_tokens,
                "toon_tokens": r.toon_tokens,
                "savings": r.savings,
                "savings_percent": r.savings_percent,
            }
            for r in results
        ],
        "totals": totals,
        "output": str(out_dir / "token-efficiency.md"),
    }


if __name__ == "__main__":  # manual run helper
    result = run_token_efficiency_benchmark()
    print(json.dumps({"totals": result["totals"]}, indent=2))
