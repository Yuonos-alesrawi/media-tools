import yt_dlp
import requests
from pathlib import Path
from videodownloader.geturl import capture_video
from videodownloader.videodownload import COMMON_HEADERS
from urllib.parse import urlparse
import asyncio

def website_name(url):
    return urlparse(url).netloc

def get_resolution(url):
    results = []
    ydl_opts = {
        "http_headers": COMMON_HEADERS,
        'quiet': True,
        'skip_download': True,
        "cookiefile": str(Path(__file__).parent / "cookies.txt"),
        "js_runtime": "node",
        "js_runtimes": {
            "node": {}
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url,download=False)
            formats = info.get('formats', [])
            audio_f =  next((f for f in reversed(formats) if f.get('vcodec') == 'none' and f.get('acodec') != 'none'), None)
            audio_size = (audio_f.get('filesize') or audio_f.get('filesize_approx') or 0) if audio_f else 0
            for f in formats:
                # نريد فقط الفيديو (مع أو بدون صوت)
                if f.get('vcodec') != 'none':

                    video_size = f.get('filesize') or f.get('filesize_approx') or 0
                    total_size = video_size + audio_size

                    results.append({
                        'format_id': f['format_id'],
                        'ext': f.get('ext'),
                        'resolution': f.get('format_note') or f.get('height'),
                        'filesize': round(total_size / (1024 * 1024), 2),
                        'fps': f.get('fps'),
                        'has_audio': f.get('acodec') != 'none'
                    })
        except Exception:

            try:
                response = requests.head(url, allow_redirects=True, timeout=5, headers=COMMON_HEADERS)
                size_bytes = int(response.headers.get('Content-Length',0))
                if size_bytes > 0:
                    results.append({
                        'format_id': 'direct',
                        'resolution': 'Orginal/Direct',
                        'extension': url.split('.')[-1][:4] if '.' in url else 'mp4',
                        'size_mb': round(size_bytes / (1024 * 1024), 2),
                    })
            
            except:
                pass

    return results

def simplify_formats(url):
    formats = get_resolution(url)
    
    if not formats:
        websitename = website_name(url)
        real_url, user_agent = asyncio.run(capture_video(url, websitename))
        formats = get_resolution(real_url)
    else:
        real_url = ''

    seen = set()
    clean = []

    for f in formats:
        key = (f.get('resolution'), f.get('fps') or 0)

        if key not in seen:
            seen.add(key)
            clean.append(f)
    return {"formats":clean, "url": real_url}
        

