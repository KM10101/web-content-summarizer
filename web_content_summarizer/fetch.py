from __future__ import annotations

from urllib.parse import urlparse

import httpx

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class FetchError(RuntimeError):
    pass


def fetch_html(url: str, timeout_seconds: float) -> tuple[str, str]:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise FetchError("URL must start with http:// or https://")

    headers = {"User-Agent": USER_AGENT}
    try:
        with httpx.Client(
            follow_redirects=True,
            headers=headers,
            timeout=timeout_seconds,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text, str(response.url)
    except httpx.TimeoutException as exc:
        raise FetchError(f"Request timeout: {url}") from exc
    except httpx.HTTPStatusError as exc:
        raise FetchError(
            f"HTTP error {exc.response.status_code}: {exc.request.url}"
        ) from exc
    except httpx.HTTPError as exc:
        raise FetchError(f"Failed to fetch URL: {url}") from exc
