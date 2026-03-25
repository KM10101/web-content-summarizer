from __future__ import annotations

import json
import re

from openai import OpenAI

from .models import SummaryOutput


class SummarizeError(RuntimeError):
    pass


def _normalize_items(items: list[str], *, limit: int) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in items:
        value = item.strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
        if len(cleaned) >= limit:
            break
    return cleaned


def _normalize_output(result: SummaryOutput) -> SummaryOutput:
    result.title = result.title.strip()
    result.summary = result.summary.strip()
    result.keyPoints = _normalize_items(result.keyPoints, limit=5)
    result.actionItems = _normalize_items(result.actionItems, limit=5)
    result.tags = _normalize_items(result.tags, limit=5)
    return result


def create_client(api_key: str, base_url: str | None) -> OpenAI:
    kwargs: dict[str, str] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _build_messages(
    title: str,
    content: str,
    language: str,
) -> list[dict[str, str]]:
    system_prompt = (
        "You are a web content summarization assistant. "
        "Return valid JSON only with exactly these keys: "
        "title, summary, keyPoints, actionItems, tags. "
        "Do not include markdown fences or extra keys. "
        f"Output language: {language}."
    )
    user_prompt = (
        "Summarize the following web page content into the required JSON schema.\n\n"
        f"Original title:\n{title}\n\n"
        f"Main text:\n{content}\n"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise SummarizeError("Model output is not valid JSON.")
    payload = raw[start : end + 1]
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SummarizeError("Failed to parse model JSON output.") from exc


def summarize_content(
    client: OpenAI,
    model: str,
    title: str,
    content: str,
    language: str,
) -> SummaryOutput:
    messages = _build_messages(title=title, content=content, language=language)
    last_error: Exception | None = None

    for _ in range(2):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            raw_output = completion.choices[0].message.content or ""
            parsed = _extract_json(raw_output)
            validated = SummaryOutput.model_validate(parsed)
            return _normalize_output(validated)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "The previous answer was invalid. "
                        "Return valid JSON only with keys: "
                        "title, summary, keyPoints, actionItems, tags."
                    ),
                }
            )

    raise SummarizeError("Failed to produce valid structured summary.") from last_error
