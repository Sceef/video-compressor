import sys
from src import globals as g
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": [
        "PyQt6",
        "requests",
        "os",
        "sys",
        "subprocess",
        "json",
        "platform",
        "pathlib",
        "threading",
        "tarfile",
    ],
    "excludes": ["tkinter"],
    "optimize": 2,
    "include_files": [("res", "res")],
}

if sys.platform == "darwin":
    build_exe_options["bin_excludes"] = [
        "libiodbc.2.dylib",
        "libpq.5.dylib",
    ]

base = None
if sys.platform == "win32":
    base = "Win32GUI"

target_name = f"VideoCompressor_v{g.VERSION}"
if sys.platform == "win32":
    target_name += ".exe"

executable_kwargs = {
    "script": "main.py",
    "base": base,
    "target_name": target_name,
}
if sys.platform == "win32":
    executable_kwargs["icon"] = "res/icon.ico"

executables = [Executable(**executable_kwargs)]

setup(
    name="VideoCompressor",
    version=g.VERSION,
    description="Compress videos to any file size.",
    options={"build_exe": build_exe_options},
    executables=executables,
)
