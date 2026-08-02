import asyncio
from urllib.parse import urlparse

import requests
import yt_dlp

from videodownloader.config import COMMON_HEADERS, COOKIES_FILE
from videodownloader.geturl import capture_video
from videodownloader.strategies.base import FormatExtractionStrategy


def _website_name(url: str) -> str:
    return urlparse(url).netloc


def _get_resolution(url: str) -> list:
    results = []
    ydl_opts = {
        "http_headers": COMMON_HEADERS,
        "quiet": True,
        "skip_download": True,
        "cookiefile": str(COOKIES_FILE),
        "js_runtime": "node",
        "js_runtimes": {"node": {}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            audio_f = next(
                (
                    f
                    for f in reversed(formats)
                    if f.get("vcodec") == "none" and f.get("acodec") != "none"
                ),
                None,
            )
            audio_size = (
                (audio_f.get("filesize") or audio_f.get("filesize_approx") or 0)
                if audio_f
                else 0
            )
            for f in formats:
                if f.get("vcodec") != "none":
                    video_size = f.get("filesize") or f.get("filesize_approx") or 0
                    total_size = video_size + audio_size
                    results.append(
                        {
                            "format_id": f["format_id"],
                            "ext": f.get("ext"),
                            "resolution": f.get("format_note") or f.get("height"),
                            "filesize": round(total_size / (1024 * 1024), 2),
                            "fps": f.get("fps"),
                            "has_audio": f.get("acodec") != "none",
                        }
                    )
        except Exception:
            try:
                response = requests.head(
                    url, allow_redirects=True, timeout=5, headers=COMMON_HEADERS
                )
                size_bytes = int(response.headers.get("Content-Length", 0))
                if size_bytes > 0:
                    results.append(
                        {
                            "format_id": "direct",
                            "resolution": "Orginal/Direct",
                            "extension": url.split(".")[-1][:4] if "." in url else "mp4",
                            "size_mb": round(size_bytes / (1024 * 1024), 2),
                        }
                    )
            except Exception:
                pass
    return results


def _deduplicate_formats(formats: list) -> list:
    seen = set()
    clean = []
    for f in formats:
        key = (f.get("resolution"), f.get("fps") or 0)
        if key not in seen:
            seen.add(key)
            clean.append(f)
    return clean


class SingleVideoStrategy(FormatExtractionStrategy):
    def can_handle(self, url: str) -> bool:
        return "list=" not in url

    def extract(self, url: str) -> dict:
        formats = _get_resolution(url)
        real_url = ""

        if not formats:
            websitename = _website_name(url)
            real_url, _user_agent = asyncio.run(capture_video(url, websitename))
            formats = _get_resolution(real_url)

        return {"formats": _deduplicate_formats(formats), "url": real_url}
