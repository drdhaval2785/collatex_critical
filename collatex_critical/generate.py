import os
import subprocess
import re
import json
from importlib.resources import files
from .utils import ensure_collatex_jar, ensure_pandoc
from .batch import run_batch  # your existing batch function


DEFAULT_TRANSLITS = ["devanagari", "slp1", "iast"]

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


def prepare_font(translit_scheme: str) -> str:
    """
    Create a LaTeX header file for the given transliteration scheme
    based on fonts.json mapping.
    Returns the path to the header file.
    """
    # Load font mapping JSON
    resources_dir = files("collatex_critical.resources")
    fonts_json = resources_dir / "fontlist.json"

    with open(fonts_json, "r", encoding="utf-8") as f:
        font_map = json.load(f)

    # Default fallback font if scheme not found
    font = font_map[translit_scheme]
    return font


def run_generate(project_id, translits=None):
    if translits is None:
        translits = DEFAULT_TRANSLITS

    input_dir = os.path.join("input", project_id)
    output_dir = os.path.join("output", project_id)
    os.makedirs(output_dir, exist_ok=True)

    # -------- Ensure dependencies --------
    jar_path = ensure_collatex_jar()
    ensure_pandoc()

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
    if "slp1" in translits:
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
        font = prepare_font(t)
        subprocess.run([
            "pandoc", md_file,
            "-o", tex_out,
            "--pdf-engine=xelatex",
            "-V", f'mainfont="{font}"',
            "--include-in-header", header_tex
        ], check=True)
        print(f"Writeen {tex_out}.")

        # PDF
        pdf_out = os.path.join(output_dir, t, f"{project_id}.pdf")
        subprocess.run([
            "pandoc", md_file,
            "-o", pdf_out,
            "--pdf-engine=xelatex",
            "-V", f'mainfont="{font}"',
            "--include-in-header", header_tex
        ], check=True)
        print(f"Writeen {pdf_out}")

    print(f"All done. Results are in {output_dir}")
