# collatex_critical/batch.py
import os
from .collatex_critical import collatex_critical

DEFAULT_TRANSLITS = ["devanagari", "slp1", "iast"]

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
