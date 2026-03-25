from __future__ import annotations

import re

import trafilatura
from bs4 import BeautifulSoup

from .models import ExtractedContent


def _extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    if not title_tag:
        return ""
    return title_tag.get_text(strip=True)


def _fallback_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def extract_main_content(html: str, url: str) -> ExtractedContent:
    title = _extract_title(html)

    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_recall=True,
        url=url,
    )

    text = extracted if extracted else _fallback_text(html)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return ExtractedContent(title=title, text=text)
