## Video Compressor

A graphical video compressor — compress videos to a target file size.

This project is a fork of [peanemis/video-compressor](https://github.com/peanemis/video-compressor).

## What's different in this fork

- **Output resolution selection** — choose 720p, 1080p, 1440p, or 2160p (default: 1080p)
- **Downscale without upscale** — e.g. compress a 1440p source to 1080p for a smaller file at the same target size; sources smaller than the selected resolution are left unchanged
- Works with both GPU and CPU encoding (software scale + hardware encode)

Everything else from the original is preserved: queue compression, target size in MB, GPU acceleration (NVIDIA, Intel QuickSync, AMD), two-pass encoding, FFmpeg auto-install, and settings persistence.

## Features

- Compresses multiple videos in a queue
- Target any specific output file size in MB
- Output resolution: 720p / 1080p / 1440p / 2160p
- GPU acceleration (NVIDIA, Intel QuickSync, AMD)
- Automatically downloads and installs FFmpeg (Windows, Linux, macOS)
- Progress tracking with detailed status updates
- Supports mp4, avi, mkv, mov, wmv, flv, webm, m4v
- Two-pass encoding for optimal quality
- Automatic bitrate calculation
- Desktop notifications on completion
- Preserves audio quality
- Simple user interface
- Settings persistence between sessions
- Auto-opens output folder when complete

## Build

### Windows

1. Clone the repository.
2. Run `setup.bat`

### Linux / macOS

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies and build:
   ```bash
   pip install -r requirements.txt
   python setup.py build
   ```

### Manual (all platforms)

1. Clone the repository:
   ```bash
   git clone https://github.com/Sceef/video-compressor.git
   ```
2. Enter the project directory:
   ```bash
   cd video-compressor
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Build the application:
   ```bash
   python setup.py build
   ```

## Releases

Pushing a version tag triggers a GitHub Actions workflow that builds and publishes artifacts for **Windows**, **Linux**, and **macOS**.

```bash
git tag v3.2.0
git push origin v3.2.0
```

You can also run the workflow manually from the **Actions** tab (`workflow_dispatch`) to test builds without creating a release.

Release artifacts:

- `VideoCompressor-Windows-x64.zip`
- `VideoCompressor-Linux-x64.tar.gz`
- `VideoCompressor-macOS-arm64.tar.gz`

### Preview

![Preview](preview.png)

---

Built with Python 3.12, PyQt6, and FFmpeg.
