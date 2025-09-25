import xml.etree.ElementTree as ET

def collatex_to_markdown(xml_file, witness_order=None):
    """
    Convert CollateX XML output to Markdown with main readings and clean footnotes.
    Footnotes are in format: [B] suKi naH; [C] saMtu
    """
    if witness_order is None:
        witness_order = []

    tree = ET.parse(xml_file)
    root = tree.getroot()

    apps = root.findall(".//app")

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

        # Look ahead for singleton continuation (merge tokens for same witness)
        if i + 1 < len(apps):
            next_readings = get_readings(apps[i + 1])
            if len(next_readings) == 1:
                next_wits, next_text = next_readings[0]
                for idx, (wits, text) in enumerate(readings):
                    # if witness appears in current readings → merge
                    if next_wits[0] in wits:
                        readings[idx] = (wits, text + " " + next_text)
                        i += 1  # skip next app, merged
                        break

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

        # Footnotes for alternate readings
        if len(sorted_readings) > 1:
            alts = []
            for text, wits in sorted_readings[1:]:
                for w in sorted(wits, key=lambda x: witness_order.index(x) if x in witness_order else len(witness_order)):
                    alts.append(f"[{w}] {text}")
            markdown_body.append(f"{main_text}[^{footnote_counter}]")
            footnotes.append((footnote_counter, "; ".join(alts)))
            footnote_counter += 1
        else:
            # No alternates
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

    # Footnotes text
    notes_text = "\n".join([f"[^{num}]: {alt}" for num, alt in footnotes])
    return f"{body_text}\n\n{notes_text}"


# Example usage
if __name__ == "__main__":
    witness_order = ["A", "B", "C"]
    md_output = collatex_to_markdown("collation.xml", witness_order)
    print(md_output)
