import json
import sys
from collections import defaultdict

def collatex_json_to_markdown(collatex_json):
    witnesses = collatex_json["witnesses"]
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

        # Select base reading: most frequent, break ties by witness order
        max_count = max(len(ws) for ws in freq.values())
        candidates = [r for r, ws in freq.items() if len(ws) == max_count]

        if len(candidates) == 1:
            base_reading = candidates[0]
        else:
            # tie-breaker by witness order
            base_reading = min(candidates, key=lambda r: witnesses.index(freq[r][0]))

        # If variants exist, prepare apparatus
        variants = {r: ws for r, ws in freq.items() if r != base_reading}
        if variants:
            footnote_marker = f"[^{note_counter}]"
            markdown_text.append(base_reading + footnote_marker)

            # Format apparatus entry
            parts = []
            for reading, ws in variants.items():
                label = f"[{','.join(ws)}]"
                parts.append(f"{label} {reading.strip()}")
            apparatus_notes.append(f"[^{note_counter}]: " + "; ".join(parts))
            note_counter += 1
        else:
            markdown_text.append(base_reading)

    return " ".join(markdown_text) + "\n\n" + "\n".join(apparatus_notes)


# Example usage:
if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, 'r', encoding='utf-8') as fin:
    	data = json.load(fin)
    print(collatex_json_to_markdown(data))


