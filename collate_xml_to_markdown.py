import xml.etree.ElementTree as ET

def collatex_to_markdown(xml_file, witness_order=None):
    """
    Convert CollateX XML output to Markdown with main readings and footnotes.
    Footnotes format: [B] suKi naH; [C] saMtu
    Superscript markers appear immediately after the main word.
    Alternate readings are grouped by identical reading and sorted according to witness_order.
    """
    if witness_order is None:
        witness_order = []

    tree = ET.parse(xml_file)
    root = tree.getroot()

    apps = list(root.findall(".//app"))
    markdown_body = []
    footnotes = []
    footnote_counter = 1
    i = 0

    def get_readings(app):
        readings = []
        for rdg in app.findall("rdg"):
            wit_ids = [w.strip("#") for w in rdg.attrib["wit"].split()]
            text = (rdg.text or "").strip()
            if text:
                readings.append((wit_ids, text))
        return readings

    while i < len(apps):
        readings = get_readings(apps[i])

        # Merge consecutive singleton tokens from the same witness
        if i + 1 < len(apps):
            next_readings = get_readings(apps[i + 1])
            merged = False
            if len(next_readings) == 1:
                next_wits, next_text = next_readings[0]
                for idx, (wits, text) in enumerate(readings):
                    if next_wits[0] in wits:
                        readings[idx] = (wits, text + " " + next_text)
                        merged = True
                        break
                if merged:
                    i += 1  # skip next app

        if not readings:
            i += 1
            continue

        # Build vote map
        count_map = {}
        for wit_ids, text in readings:
            count_map.setdefault(text, set()).update(wit_ids)

        # Determine main reading
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

        # Handle footnotes for alternate readings
        if len(sorted_readings) > 1:
            # Group same reading witnesses and sort witnesses according to witness_order
            alt_map = {}
            for text, wits in sorted_readings[1:]:
                sorted_wits = sorted(wits, key=lambda x: witness_order.index(x) if x in witness_order else len(witness_order))
                alt_map.setdefault(text, []).extend(sorted_wits)

            # Build footnote string
            alts = []
            for text, wits_list in alt_map.items():
                # remove duplicates if a witness appears multiple times
                wits_unique = []
                for w in wits_list:
                    if w not in wits_unique:
                        wits_unique.append(w)
                alts.append(f"[{','.join(wits_unique)}] {text}")
            markdown_body.append(f"{main_text}[^{footnote_counter}]")
            footnotes.append((footnote_counter, "; ".join(alts)))
            footnote_counter += 1
        else:
            markdown_body.append(main_text)

        i += 1

    # Join body text and clean spacing around punctuation
    body_text = " ".join(markdown_body)
    body_text = (
        body_text.replace("  ", " ")
        .replace(" .", ".")
        .replace(" ,", ",")
        .replace(" :", ":")
        .replace(" ;", ";")
        .replace(" !", "!")
        .replace(" ?", "?")
    )

    # Prepare footnotes
    notes_text = "\n".join([f"[^{num}]: {alt}" for num, alt in footnotes])
    return f"{body_text}\n\n{notes_text}"


# ----------------- Example usage -----------------
if __name__ == "__main__":
    witness_order = [f"{i:02d}" for i in range(1, 11)]  # ["01","02",...,"10"]
    md_output = collatex_to_markdown("collation.xml", witness_order)
    print(md_output)
