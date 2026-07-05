import asyncio
import re
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError, UnsupportedError

from videodownloader.config import BASE_YDL_OPTS, DOWNLOAD_PATH
from videodownloader.events import ProgressEvent, get_dispatcher
from videodownloader.geturl import capture_video


def _safe_filename(name: str) -> str:
    return re.sub(r"[^\w\-.]", "_", name)


def _make_progress_hook(job_id: int):
    dispatcher = get_dispatcher()

    def progress_hook(d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str")
            if not percent or percent.strip() == "" or percent.strip() == "0.0%":
                percent = None
            dispatcher.dispatch(
                ProgressEvent(
                    job_id=job_id,
                    percent=percent,
                    speed=d.get("_speed_str", "").strip(),
                    eta=d.get("_eta_str", "").strip(),
                    downloaded=d.get("_downloaded_bytes_str", "").strip(),
                )
            )
        elif d["status"] == "finished":
            dispatcher.dispatch(
                ProgressEvent(
                    job_id=job_id,
                    percent="100%",
                    speed="",
                    eta="Done",
                    downloaded="",
                )
            )

    return progress_hook


def _finalize_download(job, ydl, info) -> None:
    if not info:
        raise Exception("Download failed")
    filepath = ydl.prepare_filename(info)
    if not Path(filepath).exists():
        raise Exception("File not created")
    safe_name = _safe_filename(Path(filepath).name)
    job.filepath = str(Path(filepath).parent / safe_name)


class DownloadService:
    def download(self, job, format_id=None):
        ydl_opts = BASE_YDL_OPTS.copy()
        ydl_opts.update({"progress_hooks": [_make_progress_hook(job.id)]})

        if job.job_type == "Mp3":
            audio_folder = DOWNLOAD_PATH / "Audios"
            audio_folder.mkdir(parents=True, exist_ok=True)
            ydl_opts.update(
                {
                    "format": "bestaudio/best",
                    "paths": {"home": str(audio_folder)},
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        elif job.job_type == "VID":
            ydl_opts.update(
                {
                    "format": (
                        f"{format_id}+ba[ext=m4a]/b[ext=mp4]/b"
                        if format_id
                        else "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b"
                    ),
                }
            )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(job.url, download=True)
                _finalize_download(job, ydl, info)
            return info

        except (UnsupportedError, DownloadError):
            real_url, user_agent = asyncio.run(
                capture_video(job.url, job.website_name)
            )
            if not real_url:
                raise Exception("Unable to extract video URL")

            ydl_opts.update({"http-headers": {"User-Agent": user_agent}})
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(real_url, download=True)
                _finalize_download(job, ydl, info)
            return info
