"""Backward-compatible wrapper. Use videodownloader.services.format_service instead."""

from videodownloader.services.format_service import FormatService


def get_playlist_details(url):
    return FormatService().get_formats(url)
