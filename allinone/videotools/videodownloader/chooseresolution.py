"""Backward-compatible wrapper. Use videodownloader.services.format_service instead."""

from videodownloader.services.format_service import FormatService
from videodownloader.strategies.single_video import _get_resolution as get_resolution


def simplify_formats(url):
    return FormatService().get_formats(url)
