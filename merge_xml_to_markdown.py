#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from indic_transliteration import sanscript

def main():
    if len(sys.argv) != 3:
        print("Usage: python xml_to_markdown.py collation_slp1.xml collated.md")
        sys.exit(1)

    xml_file = sys.argv[1]
    md_file = sys.argv[2]

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
        # gather readings (already in SLP1)
        readings_map = defaultdict(list)  # reading -> list of witnesses
        for rdg in app.findall("rdg"):
            text_slp = rdg.text.strip() if rdg.text else ""
            readings_map[text_slp].append(rdg.get("wit"))

        # identify majority reading
        sorted_readings = sorted(
            readings_map.items(),
            key=lambda x: (-len(x[1]), min(witness_order.index(w) for w in x[1]))
        )
        main_reading_slp, main_wits = sorted_readings[0]

        # convert SLP1 -> Devanagari for display
        main_display = sanscript.transliterate(main_reading_slp if main_reading_slp else "Φ", 'slp1', 'devanagari')

        # process minority readings
        minority_readings = sorted_readings[1:]
        if minority_readings:
            footnote_entries = []
            for text_slp, wits in minority_readings:
                display_text = sanscript.transliterate(text_slp if text_slp else "Φ", 'slp1', 'devanagari')
                wits_str = ",".join(sorted(wits, key=lambda w: witness_order.index(w)))
                footnote_entries.append(f"[{wits_str}] {display_text}")
            footnote_text = "; ".join(footnote_entries)
            footnotes.append(f"[^{footnote_counter}]: {footnote_text}")
            main_display += f"[^{footnote_counter}]"
            footnote_counter += 1

        main_text_parts.append(main_display)

    # join main text with spaces
    main_text = " ".join(main_text_parts)

    # write to markdown
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(main_text + "\n\n")
        for fn in footnotes:
            f.write(fn + "\n")

if __name__ == "__main__":
    main()
