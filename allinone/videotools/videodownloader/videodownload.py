import yt_dlp
from videodownloader.geturl import capture_video
from yt_dlp.utils import UnsupportedError, DownloadError
from pathlib import Path
import asyncio
import  re
from .redis import ProgressStore

DOWNLOAD_PATH = Path.home() / "Downloads"
DOWNLOAD_FOLDER = DOWNLOAD_PATH/'Videos'

COMMON_HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'es-US,en;q=0.9',
    'Origin':'https://player.hotmart.com',
    "Referer": "https://player.hotmart.com/",
}

def make_progress_hook(job_id):
    def progress_hook(d):
        if d['status'] == 'downloading':

            percent = d.get('_percent_str')
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            downloaded = d.get('_downloaded_bytes_str', '').strip()

            if not percent or percent.strip() == '' or percent.strip() == '0.0%':
                percent = None  

            ProgressStore.set(job_id, {
                "percent": percent,
                "speed": speed,
                "eta": eta,
                "downloaded": downloaded,
            })

        elif d['status'] == 'finished':
            ProgressStore.set(job_id, {
                "percent": "100%",
                "speed": "",
                "eta": "Done",
                "downloaded": ""
            })

    return progress_hook

BASE_OPTS = {
    'http_headers': COMMON_HEADERS,
    "paths": {"home": str(DOWNLOAD_FOLDER)},
    'nocheckcertificate': True,
    'quiet': True,
    'outtmpl': '%(title)s.%(ext)s',
    "retries": 10,
    "fragment_retries": 10,
    "skip_unavailable_fragments": True,
    "format": "bestvideo+bestaudio/best",
    "merge_output_format": "mp4",
    "cookiefile": str(Path(__file__).parent / "cookies.txt"),
    "js_runtimes": {
        "node": {},
    },
}

def safe_filename(name):
    return re.sub(r'[^\w\-.]', '_', name)

def smart_download(job, format_id=None):
    ydl_opts = BASE_OPTS.copy()
    ydl_opts.update({"progress_hooks": [make_progress_hook(job.id)]})
    if job.job_type == 'Mp3':
        DOWNLOAD_FOLDER = DOWNLOAD_PATH/'Audios'
        DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        ydl_opts.update({
            "format": "bestaudio/best",
            "paths": {"home": str(DOWNLOAD_FOLDER)},
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        })
    elif job.job_type == 'VID':
        ydl_opts.update({
            'format': f'{format_id}+ba[ext=m4a]/b[ext=mp4]/b' if format_id else "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        })
    try:
        # المحاولة الأولى: تحميل مباشر عبر yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(job.url, download=True)
            if not info:
                raise Exception("Download failed")
            filepath = ydl.prepare_filename(info)
            if not Path(filepath).exists():
                raise Exception("File not created")
            safe_name = safe_filename(Path(filepath).name)
            job.filepath = str(Path(filepath).parent / safe_name)
        return info

    except (UnsupportedError, DownloadError):
        # إذا لم يكن مدعوم → نستخدم Playwright لاستخراج الرابط
        #print("⚠ الموقع غير مدعوم مباشرة — استخدام Playwright")
        real_url, user_agent = asyncio.run(capture_video(job.url, job.website_name)) 
        if real_url:
            ydl_opts.update({
                "http-headers":
                             {'User-Agent': user_agent
                        },
                    })
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(real_url, download=True)
                if not info:
                    raise Exception("Download failed")
                filepath = ydl.prepare_filename(info)
                if not Path(filepath).exists():
                    raise Exception("File not created")
                safe_name = safe_filename(Path(filepath).name)
                job.filepath = str(Path(filepath).parent / safe_name)
            return info

        else:
            raise Exception("Unable to extract video URL")
