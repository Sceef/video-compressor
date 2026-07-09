VERSION = "3.2.1"
TITLE = f"CVC v{VERSION}"
READY_TEXT = f"Select your videos to get started."
RESOLUTION_OPTIONS = {
    "720p": 720,
    "1080p": 1080,
    "1440p": 1440,
    "2160p": 2160,
}
DEFAULT_SETTINGS = {"target_size": 20.0, "use_gpu": False, "output_resolution": "1080p"}

ffmpeg_path = "ffmpeg"
ffprobe_path = "ffprobe"
queue = []
completed = []
root_dir = ""
bin_dir = ""
output_dir = ""
res_dir = ""
ffmpeg_installed = False
compressing = False
