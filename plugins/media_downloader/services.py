# plugins/media_downloader/services.py
import yt_dlp
import os

class VideoDownloadService:
    @staticmethod
    def download(video_url, output_dir):
        """Inapakua video kutoka kwenye URL na kuisave kwenye folder la output"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            return {
                "title": info.get('title'),
                "filename": os.path.basename(filename),
                "duration": info.get('duration'),
                "filepath": filename
            }
