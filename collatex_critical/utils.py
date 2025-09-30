import os
import sys
import json
import shutil
import re
import urllib.request
from importlib.resources import files

COLLATEX_JAR_URL = (
    "https://oss.sonatype.org/service/local/repositories/releases/content/"
    "eu/interedition/collatex-tools/1.7.1/collatex-tools-1.7.1.jar"
)
COLLATEX_JAR_PATH = os.path.join(
    os.path.expanduser("~"), ".collatex-critical", "collatex-tools-1.7.1.jar"
)

def ensure_collatex_jar():
    """Ensure collatex-tools JAR is available, download if missing."""
    os.makedirs(os.path.dirname(COLLATEX_JAR_PATH), exist_ok=True)
    if not os.path.exists(COLLATEX_JAR_PATH):
        print(f"Downloading CollateX JAR to {COLLATEX_JAR_PATH} ...")
        urllib.request.urlretrieve(COLLATEX_JAR_URL, COLLATEX_JAR_PATH)
        print("✅ Download complete")
    return COLLATEX_JAR_PATH


def ensure_pandoc():
    """Check that pandoc is installed on PATH."""
    if shutil.which("pandoc") is None:
        print("❌ Pandoc not found.")
        print("   Please install pandoc manually: https://pandoc.org/installing.html")
        sys.exit(1)


FONTS_DIR = "fonts"
DEFAULT_TRANSLITS = ["slp1", "iast", "devanagari"]


def ensure_font(font_name, url):
    os.makedirs(FONTS_DIR, exist_ok=True)
    path = os.path.join(FONTS_DIR, font_name)
    if not os.path.exists(path):
        print(f"Downloading font {font_name}...")
        urllib.request.urlretrieve(url, path)
    return path

def ensure_fonts_for_scripts(scripts):
    fjson = str(files("collatex_critical.resources") / "fontlist.json")
    with open(fjson, encoding="utf-8") as f:
        fonts_config = json.load(f)
    font_paths = {}
    for script in scripts:
        if script not in fonts_config:
            print(f"⚠️ No font configured for script '{script}'")
            continue
        font_info = fonts_config[script]
        font_paths[script] = ensure_font(font_info["file"], font_info["url"])
    return font_paths


def fontinfo(script):
    fjson = str(files("collatex_critical.resources") / "fontlist.json")
    with open(fjson, encoding="utf-8") as f:
        fonts_config = json.load(f)
    return fonts_config[script]


def natural_sort_key(filename):
    """
    Sorts filenames like 1.txt, 2.txt, 10.txt numerically.
    Supports leading zeros like 01.txt, 02.txt, 10.txt.
    """
    # Extract numeric part
    m = re.match(r"(\d+)", filename)
    if m:
        return int(m.group(1))
    return filename  # fallback
