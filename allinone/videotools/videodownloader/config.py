from pathlib import Path

DOWNLOAD_PATH = Path.home() / "Downloads"
DOWNLOAD_FOLDER = DOWNLOAD_PATH / "Videos"
COOKIES_FILE = Path(__file__).parent / "cookies.txt"

COMMON_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "es-US,en;q=0.9",
    "Origin": "https://player.hotmart.com",
    "Referer": "https://player.hotmart.com/",
}

BASE_YDL_OPTS = {
    "http_headers": COMMON_HEADERS,
    "paths": {"home": str(DOWNLOAD_FOLDER)},
    "nocheckcertificate": True,
    "quiet": True,
    "outtmpl": "%(title)s.%(ext)s",
    "retries": 10,
    "fragment_retries": 10,
    "skip_unavailable_fragments": True,
    "format": "bestvideo+bestaudio/best",
    "merge_output_format": "mp4",
    "cookiefile": str(COOKIES_FILE),
    "js_runtimes": {"node": {}},
    "yes_playlist": True,
}
