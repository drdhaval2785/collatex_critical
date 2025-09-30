import os
import subprocess
import re
import json
from importlib.resources import files
from .utils import ensure_collatex_jar, ensure_pandoc
from .batch import run_batch  # your existing batch function
import json
import os
import urllib.request

FONTS_DIR = "fonts"
DEFAULT_TRANSLITS = ["devanagari", "slp1", "iast"]


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


def run_generate(project_id, translits=None):
    if translits is None:
        translits = DEFAULT_TRANSLITS

    input_dir = os.path.join("input", project_id)
    output_dir = os.path.join("output", project_id)
    os.makedirs(output_dir, exist_ok=True)

    # -------- Ensure dependencies --------
    jar_path = ensure_collatex_jar()
    ensure_pandoc()
    # Ensure the availability of font
    ensure_fonts_for_scripts(translits)

    # -------- Prepare transliteration directories --------
    for t in translits:
        os.makedirs(os.path.join(input_dir, t), exist_ok=True)
        os.makedirs(os.path.join(output_dir, t), exist_ok=True)

    # -------- Transliterate source files --------
    src = translits[0]
    src_dir = os.path.join(input_dir, src)
    if not os.path.isdir(src_dir) or not os.listdir(src_dir):
        raise FileNotFoundError(f"No files found in {src_dir}.")

    for fname in os.listdir(src_dir):
        fpath = os.path.join(src_dir, fname)
        if not os.path.isfile(fpath):
            continue
        for t in translits[1:]:
            outpath = os.path.join(input_dir, t, fname)
            cmd = [
                "sanscript", "--from", src, "--to", t,
                "--input-file", fpath, "--output-file", outpath
            ]
            print("Running:", " ".join(cmd))
            subprocess.run(cmd, check=True)

    # -------- Collate SLP1 files --------
    slp1_dir = os.path.join(input_dir, "slp1")
    json_out = os.path.join(output_dir, "slp1", f"{project_id}.json")
    txt_files = [f for f in os.listdir(slp1_dir) if f.endswith(".txt")]
    txt_files.sort(key=natural_sort_key)
    txt_files = [os.path.join(slp1_dir, f) for f in txt_files]
    if txt_files:
        cmd = ["java", "-jar", jar_path, "-f", "json", "-o", json_out, *txt_files]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

    # -------- Run batch merger --------
    print("GENERATING MARKDOWN FILES FOR ALL TRANSLITERATIONS.")
    run_batch(project_id, translits)

    # -------- Pandoc conversions --------
    header_tex = str(files("collatex_critical.resources") / "header.tex")
    header_html = str(files("collatex_critical.resources") / "header_script.html")

    print("GENERATING HTML, TEX AND PDF FILES FOR ALL TRANSLITERATIONS.")
    for t in translits:
        md_file = os.path.join(output_dir, t, f"{project_id}.md")
        if not os.path.isfile(md_file):
            print(f"⚠️ {md_file} not found. Skipping {t}")
            continue

        # HTML
        html_out = os.path.join(output_dir, t, f"{project_id}.html")
        subprocess.run([
            "pandoc", "--standalone",
            f"--include-in-header={header_html}",
            md_file, "--metadata", f"title={project_id}_{t}",
            "-o", html_out
        ], check=True)
        print(f"Writeen {html_out}.")

        # TeX
        tex_out = os.path.join(output_dir, t, f"{project_id}.tex")
        fx = fontinfo(t)
        fontfile = fx['file']
        
        subprocess.run([
            "pandoc", md_file,
            "-o", tex_out,
            "--pdf-engine=xelatex",
            "-V", f'mainfont="{fontfile}"',
            "-V", f'mainfontoptions:Path=./fonts/',
            "--include-in-header", header_tex
        ], check=True)
        print(f"Writeen {tex_out}.")

        # PDF
        pdf_out = os.path.join(output_dir, t, f"{project_id}.pdf")
        subprocess.run([
            "pandoc", md_file,
            "-o", pdf_out,
            "--pdf-engine=xelatex",
            "-V", f'mainfont={fontfile}',
            "-V", f'mainfontoptions:Path=./fonts/',
            "--include-in-header", header_tex
        ], check=True)
        print(f"Writeen {pdf_out}")

    print(f"All done. Results are in {output_dir}")
