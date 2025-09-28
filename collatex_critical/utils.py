import os
import sys
import shutil
import urllib.request

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
