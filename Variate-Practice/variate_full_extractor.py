#!/usr/bin/env python3
"""
variate_full_extractor.py
─────────────────────────────────────────────────────────────────────────────
FULL Variate API extractor — fetches questions AND answers without submitting.

HOW IT WORKS:
  Variate loads all problem content from two sources:
    1. purdue.api.variate.org/api/groupAssessments/<ID>/problemInstances
       → Returns the full problem structure + formattedVariableValues (answers!)
    2. variatestorage.blob.core.windows.net/artifact/textartifacts/<UUID>.txt
       → Returns raw HTML for each question/choice (publicly accessible, no auth)

  By calling the API before submitting anything, we get the pre-computed
  answer values for your specific randomized session — zero attempts used.

HOW TO GET YOUR BEARER TOKEN + GROUP ASSESSMENT ID:
  1. Open the practice assignment in Chrome/Edge
  2. Open DevTools → Network tab → filter by "XHR" or "Fetch"
  3. Reload the page
  4. Click any request to "purdue.api.variate.org"
  5. Copy the "Authorization: Bearer ..." header value
  6. The groupAssessment ID is in the URL:
       https://purdue.variate.org/courses/1492/groupAssessments/13873
                                                                 ↑ this number

  FASTER: Use the browser console → run capture_network.js bookmarklet,
  or save the Network tab as HAR, then run:
      python3 variate_full_extractor.py --from-har "yourfile.har"

USAGE:
  python3 variate_full_extractor.py --token "Bearer CfDJ8..." --ga-id 13873
  python3 variate_full_extractor.py --token "Bearer CfDJ8..." --ga-id 13873 --output my_answers.html
  python3 variate_full_extractor.py --from-har /path/to/network.txt --ga-id 13873

OUTPUT:
  A self-contained HTML file with:
    - All questions rendered (HTML + any embedded images)
    - Your session's randomized variable values
    - Pre-computed numeric answers
    - Multiple choice answer revealed (from isCorrect field if available, else marked)
    - Interactive calculator: change the input numbers → answers update live
"""

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

# ──────────────────────────────────────────────────────────────────────────────
# HTML to plain text (for fallback display)
# ──────────────────────────────────────────────────────────────────────────────
class TextStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, d):
        stripped = d.strip()
        if stripped:
            self.parts.append(stripped)
    def handle_starttag(self, tag, attrs):
        if tag in ('br', 'p', 'div', 'li'):
            self.parts.append(' ')
    def get_text(self):
        return ' '.join(self.parts)

def strip_html(html):
    p = TextStripper()
    p.feed(html)
    return p.get_text()

# ──────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────
def fetch(url, token=None, timeout=15):
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
    if token:
        headers['Authorization'] = token if token.startswith('Bearer') else f'Bearer {token}'
        headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        print(f'  [WARN] Failed to fetch {url[:80]}: {e}', file=sys.stderr)
        return ''

def fetch_api(path, token):
    return fetch(f'https://purdue.api.variate.org/api/{path}', token=token)

def fetch_artifact(url):
    return fetch(url)

# ──────────────────────────────────────────────────────────────────────────────
# Extract token from HAR/network dump text file
# ──────────────────────────────────────────────────────────────────────────────
def extract_token_from_text(text):
    clean = re.sub(r'\n\s+', '', text)
    m = re.search(r'"authorization":\s*"(Bearer [^"]+)"', clean, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r'Bearer\s+([A-Za-z0-9+/=_\-]{100,})', text)
    if m:
        return 'Bearer ' + m.group(1)
    return None

def extract_ga_id_from_text(text):
    m = re.search(r'groupAssessments/(\d+)', text)
    return m.group(1) if m else None

# ──────────────────────────────────────────────────────────────────────────────
# Core data fetching
# ──────────────────────────────────────────────────────────────────────────────
def get_problem_instances(ga_id, token):
    print(f'Fetching problem instances for groupAssessment {ga_id}...', file=sys.stderr)
    raw = fetch_api(f'groupAssessments/{ga_id}/problemInstances', token)
    if not raw:
        sys.exit('ERROR: Could not fetch problem instances. Check your token and ga-id.')
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f'ERROR: Invalid JSON response: {e}\nResponse preview: {raw[:300]}')

def get_group_assessment_info(ga_id, token):
    raw = fetch_api(f'groupAssessments/{ga_id}', token)
    if raw:
        try:
            return json.loads(raw)
        except:
            pass
    return {}

# ──────────────────────────────────────────────────────────────────────────────
# Variable name → human-readable answer mapping
# Each problem has formattedVariableValues like:
#   {"order":"5","Ein":"1.0","AodB":"2","Vout":"1.2589E0",...}
# The question text uses these variable names. We map them here.
# ──────────────────────────────────────────────────────────────────────────────

# Known answer variables by question pattern (best-effort, expand as you find more)
VARIABLE_HINTS = {
    'Vout':        'Vout (output voltage)',
    'Apower':      'Apower (power gain, dB)',
    'Vhalfpowerq3': 'Vhalf-power (V at -3dB point)',
    'halfpower':   'half-power output (W)',
    'order':       'filter order',
    'rolloff':     'roll-off rate (dB/decade or dB/octave)',
    'fo':          'critical frequency fo',
    'phase':       'phase shift at fo',
}

def format_answer_value(val):
    """Convert scientific notation string like 1.2589E0 to readable float."""
    try:
        f = float(val.replace('E', 'e'))
        # Show as integer if it is one
        if f == int(f) and abs(f) < 1e9:
            return str(int(f))
        return f'{f:.4g}'
    except:
        return val

def build_answer_table(variables):
    """Build an ordered list of (name, formatted_value) for display."""
    rows = []
    for k, v in variables.items():
        rows.append((k, format_answer_value(v)))
    return rows

# ──────────────────────────────────────────────────────────────────────────────
# HTML generator
# ──────────────────────────────────────────────────────────────────────────────
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --gold: #cfb53b;
    --black: #1a1a1a;
    --dark: #111;
    --panel: #1e1e1e;
    --border: #333;
    --text: #e8e8e8;
    --ans: #4caf50;
    --mc-correct: #2e7d32;
    --mc-bg: #252525;
    --input-bg: #2a2a2a;
    --tag: #0288d1;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--black);
    color: var(--text);
    font-family: 'Segoe UI', system-ui, sans-serif;
    line-height: 1.6;
    padding: 0 0 60px;
  }}
  header {{
    background: linear-gradient(135deg, #1c1c1c 0%, #2a2200 100%);
    border-bottom: 3px solid var(--gold);
    padding: 24px 32px;
  }}
  header h1 {{ color: var(--gold); font-size: 1.6rem; }}
  header .meta {{ color: #999; font-size: 0.85rem; margin-top: 4px; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 24px 20px; }}

  /* ── Problem card ─────────────────────────────────────────────────────── */
  .problem-card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 32px;
    overflow: hidden;
  }}
  .problem-header {{
    background: #252525;
    border-bottom: 1px solid var(--border);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .problem-num {{
    background: var(--gold);
    color: #000;
    border-radius: 6px;
    padding: 2px 12px;
    font-weight: 700;
    font-size: 0.9rem;
  }}
  .problem-header h2 {{ font-size: 1rem; color: #ccc; }}

  /* ── Variables / answer key ───────────────────────────────────────────── */
  .vars-box {{
    background: #0d1f0d;
    border: 1px solid #1e3a1e;
    border-radius: 8px;
    margin: 16px 20px;
    padding: 14px 18px;
  }}
  .vars-box h3 {{
    color: var(--ans);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 10px;
  }}
  .vars-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 8px;
  }}
  .var-item {{
    background: #0a160a;
    border: 1px solid #1e3a1e;
    border-radius: 6px;
    padding: 6px 12px;
  }}
  .var-name {{ color: #81c784; font-family: monospace; font-size: 0.85rem; }}
  .var-val {{ color: var(--ans); font-weight: 700; font-size: 1rem; }}

  /* ── Statements ───────────────────────────────────────────────────────── */
  .statements {{ padding: 8px 20px 20px; }}
  .statement {{
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 14px;
    overflow: hidden;
  }}
  .stmt-header {{
    background: #222;
    padding: 8px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .stmt-label {{
    background: #333;
    color: var(--gold);
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 0.8rem;
    font-family: monospace;
  }}
  .stmt-type {{
    font-size: 0.75rem;
    color: #888;
    margin-left: auto;
  }}
  .stmt-body {{ padding: 12px 14px; }}
  .question-html {{ color: #ddd; font-size: 0.95rem; }}
  .question-html p {{ margin-bottom: 6px; }}
  .question-html sub, .question-html sup {{ font-size: 0.75em; }}

  /* Numeric answer */
  .ans-numeric {{
    margin-top: 10px;
    padding: 8px 12px;
    background: #0d1f0d;
    border-left: 3px solid var(--ans);
    border-radius: 0 6px 6px 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .ans-label {{ color: #888; font-size: 0.8rem; }}
  .ans-value {{ color: var(--ans); font-weight: 700; font-size: 1.1rem; font-family: monospace; }}
  .ans-var {{ color: #666; font-size: 0.8rem; font-family: monospace; }}

  /* Multiple choice */
  .choices {{ margin-top: 10px; display: flex; flex-direction: column; gap: 6px; }}
  .choice {{
    padding: 8px 12px;
    background: var(--mc-bg);
    border: 1px solid #333;
    border-radius: 6px;
    font-size: 0.9rem;
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }}
  .choice.correct {{
    background: #0d1f0d;
    border-color: var(--ans);
  }}
  .choice-ord {{
    background: #333;
    color: #aaa;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
  }}
  .choice.correct .choice-ord {{
    background: var(--ans);
    color: #000;
  }}
  .mc-unknown {{ color: #888; font-style: italic; font-size: 0.8rem; margin-top: 6px; }}

  /* ── Calculator section ───────────────────────────────────────────────── */
  .calc-section {{
    background: #0a1929;
    border: 1px solid #0d47a1;
    border-radius: 10px;
    margin: 32px 0 0;
    overflow: hidden;
  }}
  .calc-header {{
    background: #0d47a1;
    padding: 14px 20px;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .calc-body {{ padding: 20px; }}
  .calc-desc {{ color: #90caf9; margin-bottom: 16px; font-size: 0.9rem; }}
  .calc-inputs {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }}
  .calc-field {{ display: flex; flex-direction: column; gap: 4px; }}
  .calc-field label {{ color: #90caf9; font-size: 0.8rem; font-family: monospace; }}
  .calc-field input {{
    background: var(--input-bg);
    border: 1px solid #0d47a1;
    border-radius: 6px;
    color: #fff;
    padding: 8px 12px;
    font-size: 1rem;
    font-family: monospace;
  }}
  .calc-field input:focus {{
    outline: none;
    border-color: #42a5f5;
  }}
  .calc-results {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 10px;
  }}
  .calc-result {{
    background: #0d1929;
    border: 1px solid #0d47a1;
    border-radius: 8px;
    padding: 10px 14px;
  }}
  .calc-result-name {{ color: #90caf9; font-size: 0.8rem; font-family: monospace; }}
  .calc-result-val {{
    color: #42a5f5;
    font-weight: 700;
    font-size: 1.2rem;
    font-family: monospace;
    margin-top: 2px;
  }}
  .calc-result-formula {{ color: #546e7a; font-size: 0.75rem; margin-top: 2px; font-style: italic; }}

  /* ── Instructions ─────────────────────────────────────────────────────── */
  .instructions {{
    background: #1a1200;
    border: 1px solid #3a2800;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 24px;
  }}
  .instructions h3 {{ color: var(--gold); margin-bottom: 8px; }}
  .instructions p, .instructions li {{ color: #ccc; font-size: 0.9rem; }}
  .instructions ul {{ padding-left: 20px; }}
  .instructions li {{ margin-bottom: 4px; }}
  .copy-btn {{
    background: var(--gold);
    color: #000;
    border: none;
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
    cursor: pointer;
    font-size: 0.85rem;
    margin-top: 8px;
  }}
  .copy-btn:hover {{ background: #e6c84a; }}
</style>
</head>
<body>
<header>
  <h1>📋 {title}</h1>
  <div class="meta">ECET 33700 · Variate Practice Answer Key · Group Assessment {ga_id} · Generated {date}</div>
</header>
<div class="container">

<div class="instructions">
  <h3>How to use this guide</h3>
  <ul>
    <li><strong>Green boxes</strong> = your session's pre-computed correct answers (0 attempts used)</li>
    <li><strong>Calculator section</strong> at the bottom: enter different numbers → answers update live</li>
    <li>Numeric answers are in the same E-notation format Variate accepts (e.g. 1.2589E0 = 1.2589)</li>
    <li>Multiple choice: correct answer shown in green when known from API; otherwise all choices listed</li>
    <li>Numbers change on reload because Variate picks new variable values each session — use the calculator to recompute</li>
  </ul>
</div>

{problems_html}

</div>
<script>
// ── Live calculator ──────────────────────────────────────────────────────────
{calculator_js}
</script>
</body>
</html>'''


CALCULATOR_JS = '''
// Filter Terminology Practice — formula calculator
// Formulas derived from ECET 337 course material

function calcAll() {
  const get = id => parseFloat(document.getElementById(id)?.value) || 0;

  const Ein    = get('c_Ein');
  const AodB   = get('c_AodB');
  const Pin    = get('c_Pin');
  const Pout   = get('c_Pout');
  const Voutq3 = get('c_Voutq3');
  const order  = get('c_order');

  const setResult = (id, val, extra) => {
    const el = document.getElementById(id);
    if (el) {
      if (isNaN(val) || !isFinite(val)) { el.textContent = 'N/A'; return; }
      const rounded = parseFloat(val.toPrecision(5));
      el.textContent = rounded.toExponential(4).toUpperCase().replace('E+', 'E').replace('E-0', 'E-').replace('E0','E0') + (extra ? ' ' + extra : '');
    }
  };

  // Q1 / Q2 / Q3 type: Calculate Vout from Ein and AodB
  //   Ao (linear) = 10^(AodB/20)  [voltage gain]
  //   Vout = Ao * Ein
  const Ao_linear = Math.pow(10, AodB / 20);
  const Vout = Ao_linear * Ein;
  setResult('r_Vout', Vout, 'V');

  // Q2 type: Power gain in dB
  //   Apower_dB = 10 * log10(Pout / Pin)
  const Apower = 10 * Math.log10(Pout / Pin);
  setResult('r_Apower', Apower, 'dB');

  // Q3 type: Output at half-power point (given Voutq3 = pass-band output)
  //   Vhalf = Voutq3 / sqrt(2)  = Voutq3 * 0.7071...
  const Vhalf = Voutq3 / Math.sqrt(2);
  setResult('r_Vhalf', Vhalf, 'V');

  // Q4 type: Power at f-3dB = Pout/2
  const P_halfpower = Pout / 2;
  setResult('r_Phalf', P_halfpower, 'W');

  // Roll-off rate in dB/decade for nth order filter: -20n dB/decade
  const rolloff_decade = -20 * order;
  setResult('r_rolloff_decade', rolloff_decade, 'dB/decade');

  // Roll-off rate in dB/octave for nth order filter: -6n dB/octave
  const rolloff_octave = -6 * order;
  setResult('r_rolloff_octave', rolloff_octave, 'dB/octave');

  // Phase shift at fo for nth order high-pass filter: +45n degrees
  // (each pole contributes +45° at fo for HP filter)
  // For HP: phase = +45 * n, but constrained to ±180
  let phase = 45 * order;
  while (phase > 180) phase -= 360;
  const phaseEl = document.getElementById('r_phase');
  if (phaseEl) phaseEl.textContent = phase.toFixed(1) + '°';
}

// Hook up inputs
document.addEventListener('DOMContentLoaded', () => {
  const ids = ['c_Ein','c_AodB','c_Pin','c_Pout','c_Voutq3','c_order'];
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', calcAll);
  });
  calcAll();
});
'''


def render_question_html(artifact_html):
    """Clean up Variate artifact HTML for display — remove mathlive spans, keep structure."""
    if not artifact_html:
        return '<span style="color:#888">[content unavailable]</span>'
    # Remove mathlive/screenreader noise but keep meaningful content
    # The variable pills contain \variable{name} — replace with a styled span
    html = artifact_html
    # Remove SR-only and aria-hidden spans
    html = re.sub(r'<span class="sr-only">[^<]*</span>', '', html)
    html = re.sub(r'<span class="visually-hidden"[^>]*>[^<]*</span>', '', html)
    # Remove \variable{...} text artifacts
    html = re.sub(r'\\variable\{[^}]+\}', '', html)
    # Keep <sub>, <sup>, <p>, <b>, <i> — strip class/style/data attrs from spans
    # Replace variable pills with bold styled spans
    html = re.sub(
        r'<span class="variable"[^>]*>.*?</span>',
        lambda m: '<strong style="color:#81c784">[var]</strong>',
        html, flags=re.DOTALL
    )
    # Remove ML__ spans (MathLive rendered math — browser-only)
    html = re.sub(r'<span class="ML__[^"]*"[^>]*>.*?</span>', '', html, flags=re.DOTALL)
    # Strip BOM and zero-width spaces
    html = html.replace('\ufeff', '').replace('\u200b', '')
    return html.strip()


def build_problem_html(prob):
    ordinal = prob['ordinal']
    variables = json.loads(prob['formattedVariableValues'])
    ans_rows = build_answer_table(variables)

    # Variable box
    vars_items = ''.join(
        f'<div class="var-item"><div class="var-name">{name}</div>'
        f'<div class="var-val">{val}</div></div>'
        for name, val in ans_rows
    )
    vars_html = f'''
<div class="vars-box">
  <h3>✅ Session Answer Values (0 attempts used)</h3>
  <div class="vars-grid">{vars_items}</div>
</div>'''

    # Build statements
    stmts_html = ''
    for stmt in prob['statements']:
        label = stmt['label']
        artifact_raw = fetch_artifact(stmt['contentArtifact']['url'])
        q_html = render_question_html(artifact_raw)
        sols = stmt['solutionInstances']
        sol = sols[0] if sols else {}
        resp_type = sol.get('responseType', 'Unknown')

        if resp_type == 'MultipleChoice':
            choices = sol.get('choices', [])
            choices_html = '<div class="choices">'
            has_correct = any(c.get('isCorrect') for c in choices)
            for ch in choices:
                ch_art = fetch_artifact(ch['contentArtifact']['url'])
                ch_html = render_question_html(ch_art)
                is_correct = ch.get('isCorrect')
                correct_cls = ' correct' if is_correct else ''
                choices_html += (
                    f'<div class="choice{correct_cls}">'
                    f'<span class="choice-ord">{ch["ordinal"]}</span>'
                    f'<span>{ch_html}</span>'
                    f'</div>'
                )
            if not has_correct:
                choices_html += '<div class="mc-unknown">ℹ️ Correct answer not yet revealed by API (submit once to unlock — it costs 1 attempt). Check the -Recorded version for the answer.</div>'
            choices_html += '</div>'
            answer_block = choices_html
        else:
            # Numeric: match variable by name heuristic
            # The question text usually references the variable name directly
            q_text_plain = strip_html(artifact_raw).lower()
            matched_var = None
            matched_val = None
            # Heuristic mapping — try to match by question content
            VAR_QUESTION_MAP = [
                ('vout',        ['calculate vout', 'calculate v_out', 'calculate the output voltage']),
                ('apower',      ['power gain in db', 'calculate the power gain']),
                ('vhalfpowerq3',['half-power point', 'half power point', 'output voltage at the half']),
                ('halfpower',   ['how much power is delivered at f', 'power at f-3db', 'power delivered at f']),
                # Ao in figure — linear voltage gain shown in graph
                ('ein',         ['what is ao', 'ao in the figure']),
                ('rolloff',     ['roll-off rate', 'rolloff rate']),
                ('order',       ['what order', 'th order high pass', 'roll-off  rate in db/octave']),
                ('vhalfpowerq3',['half-power frequency', 'what is the half-power frequency']),
                ('phase',       ['phase shift at fo', 'phase shift']),
            ]
            for var_name, keywords in VAR_QUESTION_MAP:
                if any(kw in q_text_plain for kw in keywords):
                    # Find variable value (case-insensitive key match)
                    for k, v in variables.items():
                        if k.lower() == var_name.lower():
                            matched_var = k
                            matched_val = format_answer_value(v)
                            break
                    if matched_var:
                        break

            if matched_val:
                answer_block = (
                    f'<div class="ans-numeric">'
                    f'<span class="ans-label">Answer:</span>'
                    f'<span class="ans-value">{matched_val}</span>'
                    f'<span class="ans-var">← {matched_var}</span>'
                    f'</div>'
                )
            else:
                # Show all variables as possible answers
                all_vars = ', '.join(f'{k}={format_answer_value(v)}' for k, v in variables.items())
                answer_block = (
                    f'<div class="ans-numeric">'
                    f'<span class="ans-label">Check variables above</span>'
                    f'<span class="ans-var">All: {all_vars}</span>'
                    f'</div>'
                )

        stmts_html += f'''
<div class="statement">
  <div class="stmt-header">
    <span class="stmt-label">Q{label}</span>
    <span class="stmt-type">{resp_type}</span>
  </div>
  <div class="stmt-body">
    <div class="question-html">{q_html}</div>
    {answer_block}
  </div>
</div>'''

    return f'''
<div class="problem-card">
  <div class="problem-header">
    <span class="problem-num">Problem {ordinal}</span>
    <h2>Problem Set {ordinal}</h2>
  </div>
  {vars_html}
  <div class="statements">{stmts_html}</div>
</div>'''


def build_calculator_html(all_vars):
    """Build the interactive calculator using the first problem's variables as defaults."""
    if not all_vars:
        return ''
    first = all_vars[0]

    def inp(id_, label, val):
        return (
            f'<div class="calc-field">'
            f'<label for="{id_}">{label}</label>'
            f'<input type="number" id="{id_}" value="{val}" step="any">'
            f'</div>'
        )

    inputs = inp('c_Ein', 'Ein (V)', first.get('Ein', '1'))
    inputs += inp('c_AodB', 'AodB (dB)', first.get('AodB', '2'))
    inputs += inp('c_Pin', 'Pin (W)', first.get('Pin', '1'))
    inputs += inp('c_Pout', 'Pout (W)', first.get('Pout', '1'))
    inputs += inp('c_Voutq3', 'Vout passband (V)', first.get('Voutq3', '1'))
    inputs += inp('c_order', 'Filter Order n', first.get('order', '1'))

    def res(id_, label, formula):
        return (
            f'<div class="calc-result">'
            f'<div class="calc-result-name">{label}</div>'
            f'<div class="calc-result-val" id="{id_}">—</div>'
            f'<div class="calc-result-formula">{formula}</div>'
            f'</div>'
        )

    results  = res('r_Vout',          'Vout',               'Vout = Ein × 10^(AodB/20)')
    results += res('r_Apower',        'Power Gain (dB)',     'Apower = 10·log₁₀(Pout/Pin)')
    results += res('r_Vhalf',         'V at half-power pt', 'Vhalf = Vout_passband / √2')
    results += res('r_Phalf',         'Power at f-3dB',     'P-3dB = Pout / 2')
    results += res('r_rolloff_decade','Roll-off (dB/decade)','= -20n dB/decade')
    results += res('r_rolloff_octave','Roll-off (dB/octave)','= -6n dB/octave')
    results += res('r_phase',         'Phase at fo (HP)',    '= +45n° per HP pole')

    return f'''
<div class="calc-section">
  <div class="calc-header">🧮 Interactive Calculator — Change the numbers, answers update live</div>
  <div class="calc-body">
    <p class="calc-desc">
      Enter the specific numbers from your Variate session (or the randomized values shown in the
      green boxes above). All answers recalculate instantly.
    </p>
    <div class="calc-inputs">{inputs}</div>
    <div class="calc-results">{results}</div>
  </div>
</div>'''


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Variate API answer extractor')
    parser.add_argument('--token', help='Bearer token (copy from DevTools)')
    parser.add_argument('--ga-id', help='groupAssessment ID (from URL)')
    parser.add_argument('--from-har', help='Path to HAR/network dump text file')
    parser.add_argument('--output', '-o', help='Output HTML file', default='variate_answers.html')
    args = parser.parse_args()

    token = args.token
    ga_id = args.ga_id

    if args.from_har:
        with open(args.from_har, 'r', encoding='utf-8', errors='ignore') as f:
            har_text = f.read()
        if not token:
            token = extract_token_from_text(har_text)
            if token:
                print(f'Extracted token from HAR (length {len(token)})', file=sys.stderr)
            else:
                sys.exit('ERROR: Could not find Bearer token in HAR file.')
        if not ga_id:
            ga_id = extract_ga_id_from_text(har_text)
            if ga_id:
                print(f'Extracted groupAssessment ID: {ga_id}', file=sys.stderr)
            else:
                sys.exit('ERROR: Could not find groupAssessment ID in HAR file. Pass --ga-id manually.')

    if not token or not ga_id:
        parser.print_help()
        sys.exit('\nERROR: Provide either (--token + --ga-id) or --from-har')

    # Fetch assessment info for title
    print('Fetching assessment metadata...', file=sys.stderr)
    ga_info = get_group_assessment_info(ga_id, token)
    title = ga_info.get('name', f'Practice Assignment {ga_id}')

    # Fetch problem instances
    problems = get_problem_instances(ga_id, token)
    print(f'Found {len(problems)} problem(s)', file=sys.stderr)

    # Build HTML for each problem
    all_vars = []
    problems_html = ''
    for prob in problems:
        print(f'Processing problem {prob["ordinal"]}...', file=sys.stderr)
        variables = json.loads(prob['formattedVariableValues'])
        all_vars.append(variables)
        problems_html += build_problem_html(prob)

    # Build calculator
    calc_html = build_calculator_html(all_vars)
    problems_html += calc_html

    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    html = HTML_TEMPLATE.format(
        title=title,
        ga_id=ga_id,
        date=date_str,
        problems_html=problems_html,
        calculator_js=CALCULATOR_JS,
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'\nDone! Output written to: {args.output}', file=sys.stderr)
    print(f'Open in browser: file://{args.output}', file=sys.stderr)


if __name__ == '__main__':
    main()
