import json
import sys
import os
from collections import defaultdict
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# --------------------------
# Collation and Markdown generation
# --------------------------
def collatex_json_to_markdown(collatex_json, witnesses):
    table = collatex_json["table"]
    markdown_text = []
    apparatus_notes = []
    note_counter = 1

    for col in table:
        readings = []
        for i, w in enumerate(witnesses):
            if i < len(col) and col[i]:
                readings.append(("".join(col[i]), w))

        if not readings:
            continue

        # Count frequency of each reading
        freq = defaultdict(list)
        for reading, w in readings:
            freq[reading].append(w)

        # Select base reading: most frequent, tie-break by witness order
        max_count = max(len(ws) for ws in freq.values())
        candidates = [r for r, ws in freq.items() if len(ws) == max_count]
        if len(candidates) == 1:
            base_reading = candidates[0]
        else:
            base_reading = min(candidates, key=lambda r: witnesses.index(freq[r][0]))

        # Only create apparatus if variants exist
        variants = {r: ws for r, ws in freq.items() if r != base_reading}
        if variants:
            footnote_marker = f"[^{note_counter}]"
            markdown_text.append(base_reading.rstrip() + footnote_marker)

            # Apparatus formatting: club witnesses with same reading
            parts = []
            for reading, ws in variants.items():
                label = f"[{','.join(ws)}]"
                parts.append(f"{label} {reading.strip()}")
            apparatus_notes.append((f"[^{note_counter}]", "; ".join(parts)))
            note_counter += 1
        else:
            markdown_text.append(base_reading.rstrip())

    return " ".join(markdown_text), apparatus_notes

# --------------------------
# Safe transliteration
# --------------------------
def safe_transliterate(text, target_script):
    """
    Transliterates SLP1 text to target_script, keeping footnote markers [^1] 
    and witness tags [w1,w2] unchanged.
    """
    pattern = r'\[\^\d+\]|\[[^\]]+\]'
    parts = []
    last = 0
    for m in re.finditer(pattern, text):
        if m.start() > last:
            parts.append(transliterate(text[last:m.start()], sanscript.SLP1, target_script))
        parts.append(m.group(0))
        last = m.end()
    if last < len(text):
        parts.append(transliterate(text[last:], sanscript.SLP1, target_script))
    return ''.join(parts)

def transliterate_markdown(text, apparatus, target_script):
    translit_text = safe_transliterate(text, target_script)
    translit_apparatus = []
    for footnote, rest in apparatus:
        translit_rest = safe_transliterate(rest, target_script)
        translit_apparatus.append(f"{footnote}: {translit_rest}")
    return translit_text, translit_apparatus

# --------------------------
# Main script
# --------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python collator.py <project_id>")
        sys.exit(1)

    project_id = sys.argv[1]
    input_path = f"output/{project_id}/slp1/{project_id}.json"
    output_base = f"output/{project_id}"

    # Load JSON
    with open(input_path, "r", encoding="utf-8") as f:
        collatex_json = json.load(f)

    witnesses = collatex_json["witnesses"]

    # Generate base markdown
    text, apparatus = collatex_json_to_markdown(collatex_json, witnesses)

    # Scripts to output
    scripts = {
        "slp1": sanscript.SLP1,
        "devanagari": sanscript.DEVANAGARI,
        "iast": sanscript.IAST,
    }

    for script_name, target_script in scripts.items():
        out_dir = os.path.join(output_base, script_name)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{project_id}.md")

        translit_text, translit_apparatus = transliterate_markdown(text, apparatus, target_script)

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(translit_text + "\n\n" + "\n".join(translit_apparatus))

        print(f"Written {out_file}")

if __name__ == "__main__":
    main()

