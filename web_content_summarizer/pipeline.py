from __future__ import annotations

from .config import Settings
from .extract import extract_main_content
from .fetch import fetch_html
from .models import PipelineResult
from .summarize import create_client, summarize_content


def run_pipeline(url: str, language: str, settings: Settings) -> PipelineResult:
    html, final_url = fetch_html(
        url=url, timeout_seconds=settings.request_timeout_seconds
    )
    extracted = extract_main_content(html=html, url=final_url)
    if not extracted.text:
        raise ValueError("No extractable text found on the page.")

    truncated_text = extracted.text[: settings.max_input_chars]

    client = create_client(api_key=settings.api_key, base_url=settings.base_url)
    summary = summarize_content(
        client=client,
        model=settings.model,
        title=extracted.title,
        content=truncated_text,
        language=language,
    )

    if not summary.title and extracted.title:
        summary.title = extracted.title

    return PipelineResult(
        summary=summary,
        source_url=url,
        final_url=final_url,
        extracted_title=extracted.title,
        raw_text_chars=len(extracted.text),
        truncated_chars=len(truncated_text),
        language=language,
    )
