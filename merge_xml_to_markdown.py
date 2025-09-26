#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from indic_transliteration import sanscript

def process_collation(xml_file):
    """Process XML and return main_text and footnotes in SLP1"""
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
        readings_map = defaultdict(list)  # reading -> list of witnesses
        for rdg in app.findall("rdg"):
            text_slp = rdg.text.strip() if rdg.text and rdg.text.strip() else "Φ"
            readings_map[text_slp].append(rdg.get("wit"))

        # sort readings by number of witnesses, then by witness order
        sorted_readings = sorted(
            readings_map.items(),
            key=lambda x: (-len(x[1]), min(witness_order.index(w) for w in x[1]))
        )
        main_reading_slp, main_wits = sorted_readings[0]

        # convert main reading to SLP1 output (keep Φ as is)
        main_display = main_reading_slp if main_reading_slp else "Φ"

        # process minority readings
        minority_readings = sorted_readings[1:]
        if minority_readings:
            footnote_entries = []
            for text_slp, wits in minority_readings:
                display_text = text_slp if text_slp else "Φ"
                wits_str = ",".join(sorted(wits, key=lambda w: witness_order.index(w)))
                footnote_entries.append(f"[#{wits_str}] {display_text}")
            footnote_text = "; ".join(footnote_entries)
            footnotes.append(f"[^{footnote_counter}]: {footnote_text}")
            # append footnote to main display only if not Φ
            if main_display != "Φ":
                main_display += f"[^{footnote_counter}]"
            else:
                main_display += f"[^{footnote_counter}]"
            footnote_counter += 1

        main_text_parts.append(main_display)

    main_text = " ".join(main_text_parts)
    return main_text, footnotes

def transliterate_text(main_text, footnotes, target):
    """Transliterate SLP1 main_text and footnotes to target script (devanagari or iast)"""
    def translit(s):
        # Preserve Φ and footnote superscripts
        parts = []
        i = 0
        while i < len(s):
            if s[i] == 'Φ':
                parts.append('Φ')
                i += 1
            elif s[i] == '[':
                # footnote or witness reference
                j = s.find(']', i)
                if j == -1:
                    parts.append(s[i])
                    i += 1
                else:
                    parts.append(s[i:j+1])
                    i = j+1
            else:
                # collect normal text until next Φ or [
                j = i
                while j < len(s) and s[j] != 'Φ' and s[j] != '[':
                    j += 1
                parts.append(sanscript.transliterate(s[i:j], 'slp1', target))
                i = j
        return ''.join(parts)

    main_text_out = translit(main_text)
    footnotes_out = [translit(fn) for fn in footnotes]
    return main_text_out, footnotes_out

def main():
    if len(sys.argv) != 2:
        print("Usage: python merger.py project_id")
        sys.exit(1)

    project_id = sys.argv[1]
    xml_file = f"output/{project_id}/slp1/{project_id}.xml"

    # ensure output directories exist
    os.makedirs(f"output/{project_id}/slp1", exist_ok=True)
    os.makedirs(f"output/{project_id}/iast", exist_ok=True)
    os.makedirs(f"output/{project_id}/devanagari", exist_ok=True)

    main_text_slp1, footnotes_slp1 = process_collation(xml_file)
    with open(f"output/{project_id}/slp1/{project_id}.md", "w", encoding="utf-8") as f:
        f.write(main_text_slp1 + "\n\n")
        for fn in footnotes_slp1:
            f.write(fn + "\n")

    # IAST
    main_text_iast, footnotes_iast = transliterate_text(main_text_slp1, footnotes_slp1, 'iast')
    with open(f"output/{project_id}/iast/{project_id}.md", "w", encoding="utf-8") as f:
        f.write(main_text_iast + "\n\n")
        for fn in footnotes_iast:
            f.write(fn + "\n")

    # Devanagari
    main_text_deva, footnotes_deva = transliterate_text(main_text_slp1, footnotes_slp1, 'devanagari')
    with open(f"output/{project_id}/devanagari/{project_id}.md", "w", encoding="utf-8") as f:
        f.write(main_text_deva + "\n\n")
        for fn in footnotes_deva:
            f.write(fn + "\n")

if __name__ == "__main__":
    main()

