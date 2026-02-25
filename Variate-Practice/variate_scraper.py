#!/usr/bin/env python3
"""
variate_scraper.py — Extract questions, math, images, and answer choices
from Variate SingleFile HTML exports (.html saved by the SingleFile browser extension).

USAGE:
  python3 variate_scraper.py <input.html> [--output <output.html>]

WHAT IT DOES:
  1. Parses the SingleFile HTML saved from a Variate practice page
  2. Extracts every question (text, MathML, LaTeX, images, multiple-choice options)
  3. Emits a clean, self-contained HTML study sheet with all questions
  4. Also emits a JSON file with all structured data for AI training

NOTE ON ANSWERS:
  Variate does NOT embed correct answers in the page source.
  Answers are validated server-side only — they are never sent to the browser
  until after all attempts are used.  This scraper captures the QUESTIONS
  and any answer choices fully.  To capture correct answers you must either:
    a) Complete the assessment and save the review page, OR
    b) Use the browser console trick in the README to intercept the grading
       response after each submission.
"""

import sys
import json
import re
import base64
import argparse
from pathlib import Path
from html.parser import HTMLParser


# ─────────────────────────────────────────────────────────────────────────────
#  HTML Parser — collect all ql-editor divs (question text blocks) and images
# ─────────────────────────────────────────────────────────────────────────────

class VariateExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.questions = []         # list of question dicts
        self.choices = []           # list of choice dicts (multiple-choice answers)
        self.images = {}            # filename -> base64 data URI
        self.title = ""

        # State machine
        self._in_ql_editor = False
        self._in_choice = False
        self._in_title = False
        self._depth = 0             # nesting depth inside ql-editor
        self._choice_depth = 0
        self._current_html = []
        self._current_choice_html = []
        self._tag_stack = []
        self._img_counter = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        if tag == "title":
            self._in_title = True

        # Capture embedded images
        if tag == "img":
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            if src.startswith("data:image"):
                self._img_counter += 1
                fname = f"img_{self._img_counter:03d}_{alt[:30].replace(' ','_') or 'unnamed'}"
                self.images[fname] = src
                # Pass through into current block if active
                if self._in_ql_editor:
                    self._current_html.append(f'<img src="{src}" alt="{alt}" style="max-width:100%;">')

        # Multiple-choice option blocks
        if "ProblemInstanceFormChoice" in cls or "answer-multiple-choice" in cls:
            self._in_choice = True
            self._choice_depth = 1
            self._current_choice_html = []
            self._tag_stack.append(tag)
            return

        if self._in_choice:
            self._choice_depth += 1
            self._current_choice_html.append(f"<{tag}>")
            self._tag_stack.append(tag)
            return

        # ql-editor = question text container in Variate
        if tag == "div" and "ql-editor" in cls:
            self._in_ql_editor = True
            self._depth = 1
            self._current_html = []
            self._tag_stack.append(tag)
            return

        if self._in_ql_editor:
            self._depth += 1
            # Pass through math-related tags
            if tag in ("math", "mrow", "mi", "mn", "mo", "msup", "msub",
                       "mfrac", "mover", "munder", "msqrt", "mtext", "annotation",
                       "semantics", "mspace", "mtable", "mtr", "mtd", "mstyle",
                       "strong", "em", "u", "span", "sub", "sup", "p", "br",
                       "ul", "ol", "li"):
                attr_str = ""
                for k, v in attrs:
                    attr_str += f' {k}="{v}"'
                self._current_html.append(f"<{tag}{attr_str}>")
            self._tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            return

        if self._in_choice:
            self._choice_depth -= 1
            if self._choice_depth <= 0:
                self._in_choice = False
                text = self._strip_tags("".join(self._current_choice_html)).strip()
                if text:
                    self.choices.append({"text": text, "html": "".join(self._current_choice_html)})
            else:
                self._current_choice_html.append(f"</{tag}>")
            if self._tag_stack and self._tag_stack[-1] == tag:
                self._tag_stack.pop()
            return

        if self._in_ql_editor:
            self._depth -= 1
            if self._depth <= 0:
                self._in_ql_editor = False
                html_content = "".join(self._current_html)
                text_content = self._strip_tags(html_content).strip()
                # Normalize whitespace
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                if text_content:
                    self.questions.append({
                        "text": text_content,
                        "html": html_content,
                    })
                self._current_html = []
            else:
                if tag in ("math", "mrow", "mi", "mn", "mo", "msup", "msub",
                           "mfrac", "mover", "munder", "msqrt", "mtext", "annotation",
                           "semantics", "mspace", "mtable", "mtr", "mtd", "mstyle",
                           "strong", "em", "u", "span", "sub", "sup", "p", "br",
                           "ul", "ol", "li"):
                    self._current_html.append(f"</{tag}>")
            if self._tag_stack and self._tag_stack[-1] == tag:
                self._tag_stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ql_editor:
            self._current_html.append(data)
        if self._in_choice:
            self._current_choice_html.append(data)

    def _strip_tags(self, html):
        return re.sub(r'<[^>]+>', ' ', html)


# ─────────────────────────────────────────────────────────────────────────────
#  Post-process: group questions into problems and assign question numbers
# ─────────────────────────────────────────────────────────────────────────────

def structure_questions(raw_questions, choices):
    """
    Variate structure: question blocks are ordered. Multiple-choice options
    immediately follow the question they belong to.
    We try to identify:
      - Sub-problem number labels (e.g. 1.1, 1.2 ... from nav)
      - Which items are choices vs questions
    """
    structured = []
    # Filter out very short fragments that are just symbols/labels
    questions = [q for q in raw_questions if len(q["text"]) > 8]

    choice_set = set(c["text"].strip() for c in choices)

    for i, q in enumerate(questions):
        item = {
            "index": i + 1,
            "text": q["text"],
            "html": q["html"],
            "is_choice": q["text"].strip() in choice_set,
            "choices": [],
        }
        structured.append(item)

    return structured


# ─────────────────────────────────────────────────────────────────────────────
#  HTML output generator
# ─────────────────────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Extracted</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {{
  renderMathInElement(document.body, {{
    delimiters: [
      {{left: "$$", right: "$$", display: true}},
      {{left: "$", right: "$", display: false}}
    ]
  }});
}});
</script>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #fafafa; color: #222; max-width: 900px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #000; font-size: 1.4rem; border-bottom: 3px solid #CFB991; padding-bottom: 8px; }}
.source {{ color: #888; font-size: 0.8rem; margin-bottom: 20px; }}
.q-block {{ border: 1px solid #ddd; border-radius: 6px; margin-bottom: 16px; overflow: hidden; }}
.q-num {{ background: #000; color: #CFB991; padding: 6px 14px; font-weight: 700; font-size: 0.9rem; }}
.q-body {{ padding: 12px 16px; }}
.q-body img {{ max-width: 100%; border-radius: 4px; margin: 8px 0; }}
.choice-item {{ background: #f0f4ff; border-left: 3px solid #3949ab; padding: 6px 12px; margin: 4px 0; border-radius: 0 4px 4px 0; font-size: 0.9rem; }}
.answer-placeholder {{ background: #fff8e1; border: 1px dashed #ffa000; padding: 8px 12px; margin-top: 8px; color: #e65100; font-size: 0.85rem; border-radius: 4px; }}
.stats {{ background: #e8f5e9; border: 1px solid #a5d6a7; padding: 10px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 0.88rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="source">Extracted from SingleFile export &nbsp;|&nbsp; {num_q} question blocks found &nbsp;|&nbsp; {num_imgs} embedded images</div>
<div class="stats">
  <strong>⚠ About answers:</strong> Variate validates answers server-side only.
  Correct answers are NOT stored in the page HTML. They are sent back only after
  all 3 attempts are used. Use the <strong>answer_intercept.js</strong> bookmarklet
  in this folder to capture correct answers during live sessions.
</div>
{blocks}
</body>
</html>"""


def render_html_output(title, structured_items, num_imgs):
    blocks = []
    q_count = 0
    for item in structured_items:
        if item["is_choice"]:
            continue
        q_count += 1
        block = f"""<div class="q-block">
  <div class="q-num">Question {q_count}</div>
  <div class="q-body">
    <p>{item['html'] or item['text']}</p>
    <div class="answer-placeholder">[ Your answer here — see answer_intercept.js for live capture ]</div>
  </div>
</div>"""
        blocks.append(block)

    return HTML_TEMPLATE.format(
        title=title,
        num_q=q_count,
        num_imgs=num_imgs,
        blocks="\n".join(blocks),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract Variate questions from SingleFile HTML exports")
    parser.add_argument("input", help="Path to SingleFile .html export")
    parser.add_argument("--output", "-o", help="Output HTML path (default: <input>_extracted.html)")
    parser.add_argument("--json", "-j", help="Output JSON path (default: <input>_data.json)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_html = Path(args.output) if args.output else input_path.with_suffix("").with_name(input_path.stem + "_extracted.html")
    output_json = Path(args.json) if args.json else input_path.with_suffix("").with_name(input_path.stem + "_data.json")

    print(f"Reading: {input_path}")
    content = input_path.read_text(encoding="utf-8", errors="ignore")

    print("Parsing HTML...")
    extractor = VariateExtractor()
    extractor.feed(content)

    print(f"  Found {len(extractor.questions)} question text blocks")
    print(f"  Found {len(extractor.choices)} choice blocks")
    print(f"  Found {len(extractor.images)} embedded images")
    print(f"  Title: {extractor.title.strip()}")

    structured = structure_questions(extractor.questions, extractor.choices)
    q_only = [s for s in structured if not s["is_choice"]]
    print(f"  Identified {len(q_only)} questions (non-choice blocks)")

    # Write HTML
    html_out = render_html_output(
        extractor.title.strip() or input_path.stem,
        structured,
        len(extractor.images),
    )
    output_html.write_text(html_out, encoding="utf-8")
    print(f"Wrote HTML: {output_html}")

    # Write JSON (for AI training)
    json_data = {
        "source_file": str(input_path.name),
        "title": extractor.title.strip(),
        "total_question_blocks": len(extractor.questions),
        "total_choice_blocks": len(extractor.choices),
        "total_images": len(extractor.images),
        "questions": [
            {
                "index": s["index"],
                "text": s["text"],
                "is_choice": s["is_choice"],
                "correct_answer": None,  # filled in manually or via intercept
            }
            for s in structured
        ],
        "embedded_image_names": list(extractor.images.keys()),
    }
    output_json.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote JSON: {output_json}")


if __name__ == "__main__":
    main()
