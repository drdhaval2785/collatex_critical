#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from indic_transliteration import sanscript
import os

def generate_markdown(xml_file, md_file, target_script):
    """
    Generate markdown from XML using given target_script.
    target_script: 'slp1', 'iast', or 'devanagari'
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # infer witness order from first <rdg> elements
    witness_order = []
    for rdg in root.findall(".//rdg"):
        wit = rdg.get("wit")
        if wit not in witness_order:
            witness_order.append(wit)

    footnote_counter = 1
    footnotes = []
    main_text_parts = []

    for app in root.findall("app"):
        # gather readings
        readings_map = defaultdict(list)  # reading -> list of witnesses
        for rdg in app.findall("rdg"):
            text_slp = rdg.text.strip() if rdg.text and rdg.text.strip() else ""
            readings_map[text_slp].append(rdg.get("wit"))

        if not readings_map:
            continue  # skip empty <app>

        # identify majority reading
        sorted_readings = sorted(
            readings_map.items(),
            key=lambda x: (-len(x[1]), min(witness_order.index(w) for w in x[1]))
        )
        main_reading_slp, main_wits = sorted_readings[0]

        # determine if main reading is empty and majority
        main_is_empty = not main_reading_slp
        if main_is_empty and len(main_wits) >= len(witness_order) / 2:
            main_display = ""
        else:
            if not main_reading_slp:
                main_reading_slp = "Φ"
            main_display = sanscript.transliterate(main_reading_slp, 'slp1', target_script)

        # process minority readings
        minority_readings = sorted_readings[1:]
        if minority_readings:
            footnote_entries = []
            for text_slp, wits in minority_readings:
                if not text_slp:
                    text_slp = "Φ"
                display_text = sanscript.transliterate(text_slp, 'slp1', target_script)
                wits_str = ",".join(sorted(wits, key=lambda w: witness_order.index(w)))
                footnote_entries.append(f"[{wits_str}] {display_text}")
            if footnote_entries:
                footnote_text = "; ".join(footnote_entries)
                footnotes.append(f"[^{footnote_counter}]: {footnote_text}")
                if main_display:
                    main_display += f"[^{footnote_counter}]"
                else:
                    main_display = f"[^{footnote_counter}]"
                footnote_counter += 1

        main_text_parts.append(main_display)

    # join main text with spaces, ignoring empty strings
    main_text = " ".join(filter(None, main_text_parts))

    # write to markdown
    os.makedirs(os.path.dirname(md_file), exist_ok=True)
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(main_text + "\n\n")
        for fn in footnotes:
            f.write(fn + "\n")

    print(f"Markdown file written to {md_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python merge_xml_to_markdown.py project_id")
        sys.exit(1)

    project_id = sys.argv[1]
    xml_file = os.path.join("output", project_id, "slp1", f"{project_id}.xml")

    # SLP1 output (as-is)
    md_slp1 = os.path.join("output", project_id, "slp1", f"{project_id}.md")
    generate_markdown(xml_file, md_slp1, 'slp1')

    # IAST output
    md_iast = os.path.join("output", project_id, "iast", f"{project_id}.md")
    generate_markdown(xml_file, md_iast, 'iast')

    # Devanagari output
    md_deva = os.path.join("output", project_id, "devanagari", f"{project_id}.md")
    generate_markdown(xml_file, md_deva, 'devanagari')

if __name__ == "__main__":
    main()

