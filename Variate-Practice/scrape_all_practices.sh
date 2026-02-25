#!/bin/bash
# scrape_all_practices.sh
# ─────────────────────────────────────────────────────────────────────────────
# Batch-runs variate_scraper.py on all Variate SingleFile HTML exports
# in the Downloads/ECET 337 folder.
#
# USAGE: bash scrape_all_practices.sh
#
# OUTPUT: Creates <filename>_extracted.html and <filename>_data.json
#         for each Variate HTML export found.
# ─────────────────────────────────────────────────────────────────────────────

ECET_DIR="/mnt/c/Users/Offic/Downloads/ECET 337"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/extracted"

mkdir -p "$OUTPUT_DIR"

echo "Scanning: $ECET_DIR"
echo "Output:   $OUTPUT_DIR"
echo ""

count=0
while IFS= read -r -d '' file; do
  # Only process Variate pages (skip other SingleFile saves)
  if echo "$file" | grep -qi "variate\|ECET 337\|ecet"; then
    echo "Processing: $(basename "$file")"
    python3 "$SCRIPT_DIR/variate_scraper.py" \
      "$file" \
      --output "$OUTPUT_DIR/$(basename "${file%.*}")_extracted.html" \
      --json   "$OUTPUT_DIR/$(basename "${file%.*}")_data.json"
    ((count++))
    echo ""
  fi
done < <(find "$ECET_DIR" -name "Variate*.html" -print0 2>/dev/null)

echo "Done. Processed $count files."
echo "Extracted files are in: $OUTPUT_DIR"
