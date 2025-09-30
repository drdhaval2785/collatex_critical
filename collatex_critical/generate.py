import os
import subprocess
import re
import os
import urllib.request
from importlib.resources import files
from .collatex_critical import collatex_critical
from .utils import ensure_collatex_jar, ensure_pandoc, ensure_font, ensure_fonts_for_scripts, fontinfo, natural_sort_key, DEFAULT_TRANSLITS



def run_batch(project_id, translits=None):
    """
    Batch processing: convert JSON → Markdown for all transliterations
    """
    if translits is None:
        translits = DEFAULT_TRANSLITS
    input_path = f"output/{project_id}/slp1/{project_id}.json"
    output_base = f"output/{project_id}"

    for script_name in translits:
        out_dir = os.path.join(output_base, script_name)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{project_id}.md")

        x = collatex_critical(input_path, out_file, "slp1", script_name)
        text = x["text"]
        apparatus = x["apparatus"]

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(text + "\n\n" + "\n".join(apparatus))

        print(f"Written {out_file}")

def run_generate(project_id, translits=None):
    if translits is None:
        translits = DEFAULT_TRANSLITS

    input_dir = os.path.join("input", project_id)
    output_dir = os.path.join("output", project_id)
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(input_dir, exist_ok=True)

    # -------- Ensure dependencies --------
    jar_path = ensure_collatex_jar()
    ensure_pandoc()
    # Ensure the availability of font
    ensure_fonts_for_scripts(translits)

    # -------- Prepare transliteration directories --------
    os.makedirs(os.path.join(input_dir, "slp1"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "slp1"), exist_ok=True)
    for t in translits:
        os.makedirs(os.path.join(input_dir, t), exist_ok=True)
        os.makedirs(os.path.join(output_dir, t), exist_ok=True)

    # -------- Transliterate source files --------
    src = "devanagari"
    src_dir = os.path.join(input_dir, src)

    for fname in os.listdir(src_dir):
        fpath = os.path.join(src_dir, fname)
        if not os.path.isfile(fpath):
            continue
        for t in translits:
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
