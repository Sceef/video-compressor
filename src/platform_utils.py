import os
import platform
import subprocess
import sys


def binary_name(name):
    if sys.platform == "win32":
        return f"{name}.exe"
    return name


def ffmpeg_paths(bin_dir):
    return (
        os.path.join(bin_dir, binary_name("ffmpeg")),
        os.path.join(bin_dir, binary_name("ffprobe")),
    )


def icon_path(res_dir):
    ico = os.path.join(res_dir, "icon.ico")
    if os.path.exists(ico):
        return ico
    return None


def open_folder(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)


def ffmpeg_download_info():
    base = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest"
    system = platform.system()

    if system == "Windows":
        return {
            "url": f"{base}/ffmpeg-master-latest-win64-gpl.zip",
            "archive": "zip",
            "remove_play": binary_name("ffplay"),
        }

    if system == "Linux":
        return {
            "url": f"{base}/ffmpeg-master-latest-linux64-gpl.tar.xz",
            "archive": "tar.xz",
            "remove_play": binary_name("ffplay"),
        }

    if system == "Darwin":
        machine = platform.machine().lower()
        suffix = "macosarm64" if machine in ("arm64", "aarch64") else "macos64"
        return {
            "url": f"{base}/ffmpeg-master-latest-{suffix}-gpl.tar.xz",
            "archive": "tar.xz",
            "remove_play": binary_name("ffplay"),
        }

    raise RuntimeError(f"Unsupported platform: {system}")


def make_executable(path):
    if sys.platform != "win32":
        os.chmod(path, os.stat(path).st_mode | 0o111)
