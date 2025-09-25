#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import re
import sys

def collatex_to_markdown(xml_file, witness_order=None):
    if witness_order is None:
        witness_order = []

    tree = ET.parse(xml_file)
    root = tree.getroot()

    apps = list(root.findall(".//app"))
    markdown_body = []
    footnotes = []
    footnote_counter = 1

    # Buffers for consecutive variants per witness
    variant_buffer = {w: "" for w in witness_order}

    def get_readings(app):
        readings = []
        for rdg in app.findall("rdg"):
            wit_ids = [w.strip("#") for w in rdg.attrib["wit"].split()]
            text = (rdg.text or "").strip()
            if text:
                readings.append((wit_ids, text))
        return readings

    for app in apps:
        readings = get_readings(app)
        if not readings:
            continue

        # Count witnesses for each reading
        count_map = {}
        for wits, text in readings:
            count_map.setdefault(text, set()).update(wits)

        # Sort readings: by number of witnesses (desc), then witness_order
        def sort_key(item):
            text, wits = item
            size = len(wits)
            precedence = min(
                witness_order.index(w) if w in witness_order else len(witness_order)
                for w in wits
            )
            return (-size, precedence)

        sorted_readings = sorted(count_map.items(), key=sort_key)

        main_text, main_wits = sorted_readings[0]
        max_count = len(main_wits)

        # Determine majority null: if more than half witnesses don't have this reading
        total_wits = len(witness_order)
        missing_count = total_wits - max_count
        if max_count <= 1 or missing_count >= (total_wits / 2):
            main_text = None

        # Update variant buffers
        for text, wits in sorted_readings:
            if text == main_text:
                continue
            for w in wits:
                variant_buffer[w] += text + " "

        # Build footnotes for this position if main_text exists or variants present
        alt_map = {}
        for w, buf in variant_buffer.items():
            buf = buf.strip()
            if buf:
                alt_map.setdefault(buf, []).append(w)
                variant_buffer[w] = ""  # reset

        # Append to markdown body
        if main_text:
            markdown_body.append(f"{main_text}[^{footnote_counter}]" if alt_map else main_text)
        elif alt_map:
            markdown_body.append(f"Φ[^{footnote_counter}]")

        if alt_map:
            alts = []
            for text, wits_list in alt_map.items():
                # sort witnesses according to witness_order
                wits_unique = []
                for w in sorted(wits_list, key=lambda x: witness_order.index(x) if x in witness_order else len(witness_order)):
                    if w not in wits_unique:
                        wits_unique.append(w)
                alts.append(f"[{','.join(wits_unique)}] {text}")
            footnotes.append((footnote_counter, "; ".join(alts)))
            footnote_counter += 1

    # Join body text with spaces
    body_text = " ".join(markdown_body)
    body_text = re.sub(r'\s+', ' ', body_text).strip()

    # Combine footnotes
    notes_text = "\n".join([f"[^{num}]: {alt}" for num, alt in footnotes])

    return f"{body_text}\n\n{notes_text}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python xml_to_markdown.py input.xml output.md")
        sys.exit(1)

    xml_file = sys.argv[1]
    md_file = sys.argv[2]

    witness_order = [f"{i:02d}" for i in range(1, 11)]  # default 01..10
    md_output = collatex_to_markdown(xml_file, witness_order)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_output)

    print(f"Markdown written to {md_file}")
