#!/bin/bash
# generate_all.sh
# ─────────────────────────────────────────────────────────────────────────────
# Batch-generate answer HTML for ALL your Variate practice assignments.
#
# USAGE:
#   bash generate_all.sh
#
# REQUIREMENTS:
#   - Python 3.6+
#   - One network capture file per assignment (see capture_network_bookmarklet.js)
#   - Place capture files in: ~/Downloads/ECET 337/captures/
#     OR pass TOKEN and a list of GA IDs directly below.
#
# ─────────────────────────────────────────────────────────────────────────────
# OPTION A: Provide one capture file per assignment
# (each file must contain "authorization: Bearer ..." and a groupAssessments URL)
# ─────────────────────────────────────────────────────────────────────────────

CAPTURES_DIR="$HOME/Downloads/ECET 337"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/generated"
mkdir -p "$OUTPUT_DIR"

FOUND=0
for f in "$CAPTURES_DIR"/*.txt "$CAPTURES_DIR"/*.har; do
  [ -f "$f" ] || continue
  echo "Processing: $f"
  BASENAME=$(basename "$f" | sed 's/\.[^.]*$//')
  python3 "$SCRIPT_DIR/variate_full_extractor.py" \
    --from-har "$f" \
    --output "$OUTPUT_DIR/${BASENAME}_answers.html" 2>&1 | tail -3
  FOUND=$((FOUND + 1))
done

if [ $FOUND -eq 0 ]; then
  echo ""
  echo "No capture files found in: $CAPTURES_DIR"
  echo "How to get a capture file for an assignment:"
  echo "  1. Open the Variate practice page"
  echo "  2. DevTools → Network → reload page"
  echo "  3. Right-click any request → 'Copy all as fetch'"
  echo "  4. Paste into a .txt file in: $CAPTURES_DIR"
  echo "  5. Run this script again"
  echo ""
  echo "OR use the bookmarklet (see capture_network_bookmarklet.js)"
fi

echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"/*.html 2>/dev/null || echo "None yet"
