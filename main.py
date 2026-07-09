import json
import sys
import os
import psutil
import src.globals as g
from notifypy import Notify
from src.download import DownloadThread
from src.platform_utils import ffmpeg_paths, icon_path, open_folder
from src.thread import CompressionThread
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QProgressBar,
)
from PyQt6.QtGui import QIcon
from src.styles import *


def load_settings():
    try:
        with open(os.path.join(g.res_dir, "settings.json"), "r") as f:
            return json.load(f)
    except:
        return g.DEFAULT_SETTINGS


def save_settings(settings):
    with open(os.path.join(g.res_dir, "settings.json"), "w") as f:
        json.dump(settings, f)


def kill_ffmpeg():
    for proc in psutil.process_iter():
        if "ffmpeg" in proc.name():
            proc.kill()


def delete_bin():
    print("@@@@@@@@@@@@@@@@@@@@@@ DELETING BIN @@@@@@@@@@@@@@@@@@@@@@@")
    for root, dirs, files in os.walk(g.bin_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.verify_directories()
        self.settings = load_settings()
        self.setFixedSize(WINDOW.w, WINDOW.h)
        self.setWindowTitle(g.TITLE)
        icon = icon_path(g.res_dir)
        if icon:
            self.setWindowIcon(QIcon(icon))

        # Select Button
        self.button_select = QPushButton("Select Videos", self)
        self.button_select.resize(SELECT_BUTTON.w, SELECT_BUTTON.h)
        self.button_select.move(SELECT_BUTTON.x, SELECT_BUTTON.y)
        self.button_select.clicked.connect(self.select_videos)
        self.button_select.setEnabled(False)

        # Compress Button
        self.button_compress = QPushButton("Compress", self)
        self.button_compress.resize(COMPRESS_BUTTON.w, COMPRESS_BUTTON.h)
        self.button_compress.move(COMPRESS_BUTTON.x, COMPRESS_BUTTON.y)
        self.button_compress.clicked.connect(self.compress_videos)
        self.button_compress.setEnabled(False)

        # Abort Button
        self.button_abort = QPushButton("Abort", self)
        self.button_abort.resize(ABORT_BUTTON.w, ABORT_BUTTON.h)
        self.button_abort.move(ABORT_BUTTON.x, ABORT_BUTTON.y)
        self.button_abort.clicked.connect(self.abort_compression)
        self.button_abort.setEnabled(False)

        # File Size Label
        self.label_size = QLabel("Size (MB)", self)
        self.label_size.resize(FILE_SIZE_LABEL.w, FILE_SIZE_LABEL.h)
        self.label_size.move(FILE_SIZE_LABEL.x, FILE_SIZE_LABEL.y)

        # File Size Entry
        self.edit_size = QLineEdit(str(self.settings["target_size"]), self)
        self.edit_size.resize(FILE_SIZE_ENTRY.w, FILE_SIZE_ENTRY.h)
        self.edit_size.move(FILE_SIZE_ENTRY.x, FILE_SIZE_ENTRY.y)
        self.edit_size.setEnabled(True)

        # GPU Label
        self.label_gpu = QLabel("Use GPU", self)
        self.label_gpu.resize(GPU_LABEL.w, GPU_LABEL.h)
        self.label_gpu.move(GPU_LABEL.x, GPU_LABEL.y)

        # GPU Checkbox
        self.checkbox_gpu = QCheckBox(self)
        self.checkbox_gpu.resize(GPU_CHECKBOX.w, GPU_CHECKBOX.h)
        self.checkbox_gpu.move(GPU_CHECKBOX.x, GPU_CHECKBOX.y)
        self.checkbox_gpu.setChecked(self.settings["use_gpu"])

        # Resolution Label
        self.label_resolution = QLabel("Resolution", self)
        self.label_resolution.resize(RESOLUTION_LABEL.w, RESOLUTION_LABEL.h)
        self.label_resolution.move(RESOLUTION_LABEL.x, RESOLUTION_LABEL.y)

        # Resolution Combo
        self.combo_resolution = QComboBox(self)
        self.combo_resolution.addItems(list(g.RESOLUTION_OPTIONS.keys()))
        self.combo_resolution.resize(RESOLUTION_COMBO.w, RESOLUTION_COMBO.h)
        self.combo_resolution.move(RESOLUTION_COMBO.x, RESOLUTION_COMBO.y)
        self.combo_resolution.setCurrentText(
            self.settings.get("output_resolution", "1080p")
        )

        # Log Label
        self.label_log = QLabel(g.READY_TEXT, self)
        self.label_log.setEnabled(True)
        self.label_log.resize(LOG_AREA.w, LOG_AREA.h)
        self.label_log.move(LOG_AREA.x, LOG_AREA.y)
        self.label_log.setWordWrap(True)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.resize(PROGRESS_BAR.w, PROGRESS_BAR.h)
        self.progress_bar.move(PROGRESS_BAR.x, PROGRESS_BAR.y)
        self.progress_bar.setRange(0, 100)

        self.download_thread = None
        self.compress_thread = None

        self.button_select.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.button_compress.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.button_abort.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.label_size.setStyleSheet(LABEL_STYLE)
        self.edit_size.setStyleSheet(LINEEDIT_STYLE)
        self.label_gpu.setStyleSheet(LABEL_STYLE)
        self.checkbox_gpu.setStyleSheet(CHECKBOX_STYLE)
        self.label_resolution.setStyleSheet(LABEL_STYLE)
        self.combo_resolution.setStyleSheet(COMBOBOX_STYLE)
        self.label_log.setStyleSheet(LABEL_LOG_STYLE)
        self.progress_bar.setStyleSheet(PROGRESS_BAR_STYLE)

        self.verify_ffmpeg()

    def closeEvent(self, event):
        # Save settings when closing
        self.settings["target_size"] = float(self.edit_size.text())
        self.settings["use_gpu"] = self.checkbox_gpu.isChecked()
        self.settings["output_resolution"] = self.combo_resolution.currentText()
        save_settings(self.settings)
        kill_ffmpeg()

        if os.path.exists(os.path.join(g.root_dir, "TEMP")):
            os.remove(os.path.join(g.root_dir, "TEMP"))

        event.accept()

    def reset(self):
        g.compressing = False
        g.queue = []
        self.button_select.setEnabled(True)
        self.button_select.setStyleSheet(BUTTON_SELECT_STYLE)
        self.button_select.setFocus()
        self.button_compress.setEnabled(False)
        self.button_compress.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.button_abort.setEnabled(False)
        self.button_abort.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.edit_size.setEnabled(True)
        self.combo_resolution.setEnabled(True)
        self.update_log(g.READY_TEXT)
        self.update_progress(0)

    def verify_directories(self):
        print("Verifying directories...")
        if getattr(sys, "frozen", False):
            # Running as compiled executable
            g.root_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            g.root_dir = os.path.dirname(os.path.abspath(__file__))

        print(f"Root: {g.root_dir}")
        g.bin_dir = os.path.join(g.root_dir, "bin")

        if not os.path.exists(g.bin_dir):
            os.mkdir(g.bin_dir)

        print(f"Bin: {g.bin_dir}")
        g.output_dir = os.path.join(g.root_dir, "output")

        if not os.path.exists(g.output_dir):
            os.mkdir(g.output_dir)

        print(f"Output: {g.output_dir}")
        g.res_dir = os.path.join(g.root_dir, "res")
        print(f"Res: {g.res_dir}")

    def verify_ffmpeg(self):
        print("Verifying FFmpeg...")
        ffmpeg_path, ffprobe_path = ffmpeg_paths(g.bin_dir)
        print(f"FFmpeg: {ffmpeg_path}")
        print(f"FFprobe: {ffprobe_path}")

        if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
            g.ffmpeg_installed = True
            g.ffmpeg_path = ffmpeg_path
            g.ffprobe_path = ffprobe_path
            self.reset()
        else:
            self.download_thread = DownloadThread()
            self.download_thread.installed.connect(self.installed)
            self.download_thread.update_log.connect(self.update_log)
            self.download_thread.update_progress.connect(self.update_progress)
            self.download_thread.start()

    def select_videos(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v);;All Files (*.*)",
        )

        if len(file_paths) > 0:
            for PATH in file_paths:
                if PATH in g.queue:
                    continue

                g.queue.append(PATH)

            self.button_compress.setEnabled(True)
            self.button_compress.setStyleSheet(BUTTON_COMPRESS_STYLE)
            print(f"Selected: {g.queue}")
            msg = f"Selected {len(g.queue)} video(s)."
            self.update_log(msg)

    def compress_videos(self):
        g.compressing = True
        self.button_select.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.button_compress.setStyleSheet(BUTTON_DISABLED_STYLE)
        self.button_abort.setEnabled(True)
        self.button_abort.setStyleSheet(BUTTON_ABORT_STYLE)
        self.button_select.setEnabled(False)
        self.button_compress.setEnabled(False)
        self.edit_size.setEnabled(False)
        self.combo_resolution.setEnabled(False)
        resolution_height = g.RESOLUTION_OPTIONS[self.combo_resolution.currentText()]
        self.compress_thread = CompressionThread(
            float(self.edit_size.text()),
            self.checkbox_gpu.isChecked(),
            resolution_height,
        )
        self.compress_thread.completed.connect(self.completed)
        self.compress_thread.update_log.connect(self.update_log)
        self.compress_thread.update_progress.connect(self.update_progress)
        self.compress_thread.start()

    def abort_compression(self):
        kill_ffmpeg()
        self.completed(True)

    def update_log(self, text):
        self.label_log.setText(text)

    def update_progress(self, progress_percentage):
        self.progress_bar.setValue(progress_percentage)

    def installed(self):
        g.ffmpeg_installed = True
        g.ffmpeg_path, g.ffprobe_path = ffmpeg_paths(g.bin_dir)
        self.reset()
        n = Notify()
        n.title = "FFmpeg installed!"
        n.message = "You can now compress your videos."
        icon = icon_path(g.res_dir)
        if icon:
            n.icon = icon
        n.send()

    def completed(self, aborted=False):
        g.compressing = False
        self.compress_thread.terminate()
        self.reset()
        n = Notify()
        n.title = "Done!" if not aborted else "Aborted!"
        n.message = (
            "Your videos are ready." if not aborted else "Your videos are cooked!"
        )
        icon = icon_path(g.res_dir)
        if icon:
            n.icon = icon
        n.send()

        if not aborted:
            open_folder(g.output_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
