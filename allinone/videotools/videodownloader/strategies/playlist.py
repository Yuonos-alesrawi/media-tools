import re

import yt_dlp

from videodownloader.strategies.base import FormatExtractionStrategy
from videodownloader.strategies.single_video import SingleVideoStrategy


class PlaylistStrategy(FormatExtractionStrategy):
    def can_handle(self, url: str) -> bool:
        return "list=" in url

    def extract(self, url: str) -> dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if "entries" not in info:
                return SingleVideoStrategy().extract(url)

            entries = [e for e in info.get("entries", []) if e is not None]
            total_videos = len(entries)

            if total_videos == 0:
                return {"formats": [], "url": url}

            playlist_formats_stats = {}

            for entry in entries:
                formats = entry.get("formats", [])
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
                        res = str(f.get("format_note") or f.get("height"))
                        res_match = re.search(r"\d+", res)
                        clean_res = f"{res_match.group()}p" if res_match else res
                        key = clean_res
                        video_size = f.get("filesize") or f.get("filesize_approx") or 0

                        if key not in playlist_formats_stats:
                            playlist_formats_stats[key] = {
                                "resolution": clean_res,
                                "total_filesize": 0,
                                "ext": f.get("ext"),
                                "count": 0,
                            }

                        playlist_formats_stats[key]["total_filesize"] += (
                            video_size + audio_size
                        )
                        playlist_formats_stats[key]["count"] += 1

            final_formats = []
            for stats in playlist_formats_stats.values():
                if stats["count"] == total_videos:
                    final_formats.append(
                        {
                            "format_id": "playlist",
                            "resolution": stats["resolution"],
                            "ext": stats["ext"],
                            "filesize": round(
                                stats["total_filesize"] / (1024 * 1024), 2
                            ),
                        }
                    )

            final_formats.sort(
                key=lambda x: (
                    int(re.search(r"\d+", x["resolution"]).group())
                    if re.search(r"\d+", x["resolution"])
                    else 0
                ),
                reverse=False,
            )

        return {"formats": final_formats, "url": url}
