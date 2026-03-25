from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from .config import Settings
from .pipeline import run_pipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="web-content-summarizer",
        description="Summarize web pages into structured JSON.",
    )
    parser.add_argument("url", help="Target page URL.")
    parser.add_argument(
        "--language",
        default="中文",
        help="Output language. Default: 中文",
    )
    parser.add_argument(
        "--save-dir",
        default=None,
        help="Directory to save run artifacts. Default uses OUTPUT_DIR or runs/",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Disable writing run artifacts to disk.",
    )
    return parser


def _format_pretty(payload: dict) -> str:
    key_points = payload.get("keyPoints", [])
    action_items = payload.get("actionItems", [])
    tags = payload.get("tags", [])
    lines = [
        f"Title: {payload.get('title', '')}",
        "",
        f"Summary: {payload.get('summary', '')}",
        "",
        "Key Points:",
    ]
    lines.extend([f"- {point}" for point in key_points] or ["- (none)"])
    lines.append("")
    lines.append("Action Items:")
    lines.extend([f"- {item}" for item in action_items] or ["- (none)"])
    lines.append("")
    lines.append(f"Tags: {', '.join(tags) if tags else '(none)'}")
    return "\n".join(lines)


def _save_artifacts(save_dir: Path, payload: dict, metadata: dict) -> Path:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = save_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    result_file = run_dir / "result.json"
    metadata_file = run_dir / "metadata.json"

    result_file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    metadata_file.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return run_dir


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        settings = Settings.from_env()
        if args.save_dir:
            settings = Settings(
                api_key=settings.api_key,
                model=settings.model,
                base_url=settings.base_url,
                request_timeout_seconds=settings.request_timeout_seconds,
                max_input_chars=settings.max_input_chars,
                output_dir=Path(args.save_dir),
            )

        result = run_pipeline(url=args.url, language=args.language, settings=settings)
        payload = result.summary.model_dump(mode="json")
        metadata = {
            "source_url": result.source_url,
            "final_url": result.final_url,
            "extracted_title": result.extracted_title,
            "raw_text_chars": result.raw_text_chars,
            "truncated_chars": result.truncated_chars,
            "language": result.language,
        }

        print(_format_pretty(payload))
        print("\nJSON:\n")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        if not args.no_save:
            run_dir = _save_artifacts(
                settings.output_dir, payload=payload, metadata=metadata
            )
            print(f"\nSaved artifacts: {run_dir}")
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
