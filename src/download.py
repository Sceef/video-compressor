import os
import shutil
import tarfile
import zipfile
import requests
import src.globals as g
from src.platform_utils import ffmpeg_download_info, make_executable
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    installed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def download_ffmpeg(self):
        info = ffmpeg_download_info()
        print("Downloading FFmpeg...")
        bin_path = g.bin_dir
        archive_ext = "zip" if info["archive"] == "zip" else "tar.xz"
        file_path = os.path.join(bin_path, f"ffmpeg.{archive_ext}")
        response = requests.get(info["url"], stream=True)

        if not response.ok:
            print(f"Download failed: {response.status_code}\n{response.text}")
            return

        print(f"Source: {info['url']}")
        total_size = response.headers.get("content-length")

        with open(file_path, "wb") as f:
            if total_size is None:
                f.write(response.content)
            else:
                downloaded = 0
                total_size = int(total_size)

                for chunk in response.iter_content(chunk_size=4096):
                    downloaded += len(chunk)
                    f.write(chunk)
                    percentage = (downloaded / total_size) * 100
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    message = f"Downloading FFmpeg...\n{downloaded_mb:.1f} MB / {total_mb:.1f} MB"
                    self.update_log.emit(message)
                    self.update_progress.emit(int(percentage))

        self.archive_path = file_path
        self.download_info = info

    def install_ffmpeg(self):
        print("Installing FFmpeg...")
        info = self.download_info
        archive_path = self.archive_path

        if info["archive"] == "zip":
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                zip_file.extractall(g.bin_dir)
        else:
            with tarfile.open(archive_path, "r:xz") as tar_file:
                tar_file.extractall(g.bin_dir)

        os.remove(archive_path)

        extracted_root = os.path.join(g.bin_dir, os.listdir(g.bin_dir)[0])
        extracted_bin = os.path.join(extracted_root, "bin")

        for file_name in os.listdir(extracted_bin):
            src = os.path.join(extracted_bin, file_name)
            dst = os.path.join(g.bin_dir, file_name)
            try:
                shutil.move(src, dst)
                make_executable(dst)
            except OSError:
                print(f"Skipped {file_name} - file already exists")

        shutil.rmtree(extracted_root)

        ffplay_path = os.path.join(g.bin_dir, info["remove_play"])
        if os.path.exists(ffplay_path):
            os.remove(ffplay_path)

    def run(self):
        self.download_ffmpeg()
        self.install_ffmpeg()
        self.installed.emit()
