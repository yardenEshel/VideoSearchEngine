import logging
import os

import yt_dlp

logger = logging.getLogger(__name__)


class VideoAssetManager:
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.video_path = os.path.join(self.base_dir, "downloaded_video.mp4")

    def download_video(self, search_query="super mario movie trailer", force=False):
        """
        Searches YouTube for the query and downloads the first result.
        Returns the path to the downloaded video.
        """
        if os.path.exists(self.video_path) and not force:
            logger.info("Video already exists at %s; skipping download.", self.video_path)
            return self.video_path

        if force and os.path.exists(self.video_path):
            os.remove(self.video_path)

        logger.info("Searching and downloading: '%s'...", search_query)

        # Options for yt-dlp. We explicitly avoid AV1 sources because ffmpeg inside
        # the slim image cannot decode them reliably, which breaks PySceneDetect.
        ydl_opts = {
            "format": (
                "bestvideo[ext=mp4][vcodec!*=av01]+bestaudio[ext=m4a]/"
                "bestvideo[vcodec!*=av01]+bestaudio/"
                "best[ext=mp4][vcodec!*=av01]/best"
            ),
            "merge_output_format": "mp4",
            "postprocessors": [
                {
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",  # yt-dlp uses the legacy spelling
                }
            ],
            "outtmpl": self.video_path,
            "noplaylist": True,
            "retries": 3,
            "quiet": False,  # Set to True to reduce console noise
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ytsearch1: performs a search and downloads the first result
            ydl.download([f"ytsearch1:{search_query}"])

        logger.info("Download complete [%s].", self.video_path)
        return self.video_path