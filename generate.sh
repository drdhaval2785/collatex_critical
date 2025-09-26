#!/bin/bash
set -e

# Usage: ./generate.sh project_id
PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 project_id"
  exit 1
fi

# Hard-coded transliterations (expand this list as needed)
TRANSLITS=("devanagari" "slp1" "iast")

# Base directories
INPUT_DIR="input/$PROJECT_ID"
OUTPUT_DIR="output/$PROJECT_ID"

# Create translit directories in input/output
for t in "${TRANSLITS[@]}"; do
  mkdir -p "$INPUT_DIR/$t"
  mkdir -p "$OUTPUT_DIR/$t"
done

# Source transliteration = first in the list
SRC="${TRANSLITS[0]}"
SRC_DIR="$INPUT_DIR/$SRC"

if [ ! -d "$SRC_DIR" ] || [ -z "$(ls -A "$SRC_DIR" 2>/dev/null)" ]; then
  echo "No files found in $SRC_DIR. Aborting."
  exit 1
fi

# Step 1 & 2: Convert SRC → all others
echo "Converting $SRC witnesses to other transliterations..."
for file in "$SRC_DIR"/*; do
  [ -f "$file" ] || continue
  filename=$(basename "$file")

  for t in "${TRANSLITS[@]:1}"; do
    sanscript --from="$SRC" --to="$t" --input-file "$file" --output-file "$INPUT_DIR/$t/$filename"
  done
done

# Step 3: Run collator on SLP1
if [[ " ${TRANSLITS[*]} " =~ " slp1 " ]]; then
  echo "Running collator on slp1 witnesses..."
  python3 collator.py "$PROJECT_ID"
else
  echo "Warning: 'slp1' not in transliteration list, skipping collator/merger."
  exit 0
fi

# Step 4: Run merger
echo "Running merger..."
python3 merger.py "$PROJECT_ID"

# Step 5 & 6: Pandoc → PDF and TeX for all transliterations
for t in "${TRANSLITS[@]}"; do
  MD_FILE="$OUTPUT_DIR/$t/$PROJECT_ID.md"
  if [ -f "$MD_FILE" ]; then
    echo "Converting $MD_FILE to PDF..."
    pandoc "$MD_FILE" \
      -o "$OUTPUT_DIR/$t/$PROJECT_ID.pdf" \
      --pdf-engine=xelatex \
      -V mainfont="Sanskrit2003"

    echo "Converting $MD_FILE to TeX..."
    pandoc "$MD_FILE" \
      -o "$OUTPUT_DIR/$t/$PROJECT_ID.tex" \
      --pdf-engine=xelatex \
      -V mainfont="Sanskrit2003"
  else
    echo "Warning: $MD_FILE not found. Skipping PDF/TeX conversion for $t."
  fi
done

echo "✅ All done. Results are in $OUTPUT_DIR"

