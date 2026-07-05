"""Backward-compatible wrapper. Use videodownloader.services.download_service instead."""

from videodownloader.config import (
    BASE_YDL_OPTS as BASE_OPTS,
    COMMON_HEADERS,
    DOWNLOAD_FOLDER,
    DOWNLOAD_PATH,
)
from videodownloader.services.download_service import DownloadService


def smart_download(job, format_id=None):
    return DownloadService().download(job, format_id=format_id)
