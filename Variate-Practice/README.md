# Variate Practice — Tools & Answer Keys

## Files in this folder

| File | Purpose |
|------|---------|
| `ECET337_Laplace_Transforms_Practice_Answers.html` | **Full answer key** for Laplace Transforms Practice with all work shown |
| `variate_scraper.py` | Python script to extract questions from SingleFile HTML exports |
| `answer_intercept.js` | Browser console script to capture correct answers during live sessions |
| `scrape_all_practices.sh` | Batch script to process all Variate exports at once |

---

## Answering your questions

### Q: Do the SingleFile extension files give enough info?

**Yes, for questions** — but **no, for correct answers**.

What SingleFile captures ✅:
- All question text (plain text + HTML)
- MathML blocks (the rendered math)
- LaTeX strings embedded in the page
- Circuit schematic images (base64-embedded JPEGs/PNGs/SVGs)
- Multiple-choice option text
- Point values and question numbering

What SingleFile does NOT capture ❌:
- **Correct answers** — these are validated server-side only and never sent to the browser before submission
- The Variate platform intentionally withholds correct answers until all 3 attempts are exhausted (or the assessment closes)

---

## How to get correct answers

### Strategy 1 — answer_intercept.js (best for practice problems)
1. Open the Variate practice page in Chrome/Firefox
2. Open DevTools → Console (F12)
3. Paste the entire contents of `answer_intercept.js` and press Enter
4. Submit each answer as normal
5. After each submission, the console logs the server's grading response
6. When done: `copy(JSON.stringify(window.__variate_answers__, null, 2))`
7. Paste the clipboard into a `.json` file

**What you get:** The grading result (correct/incorrect) and sometimes the correct value depending on the question type. Math-input questions on Variate typically only say correct/incorrect without revealing the answer on the first 2 attempts. Multiple-choice questions may reveal the correct option.

### Strategy 2 — Complete the assessment, then save the review page
After using all attempts or after the assessment closes, Variate shows the correct answers in the review. Save that page with SingleFile.

### Strategy 3 — The Recorded versions
Many practice assessments have a "-Recorded" counterpart (e.g., "ECET 337-Laplace Transforms-Recorded") which is a worked example with the same problem types. Save those with SingleFile and use them as answer keys.

---

## Using variate_scraper.py

```bash
# Single file
python3 variate_scraper.py "Variate - ECET 337 CLR Introduction-Practice - Submit.html"

# All files at once
bash scrape_all_practices.sh
```

The scraper outputs:
- `*_extracted.html` — Clean question list you can open in any browser
- `*_data.json` — Structured data for AI training/study tools

---

## Assessments available (from your Downloads folder)

Already have SingleFile exports for:
- ECET 337 CLR Introduction-Practice
- ECET 337 RC Laplace-Practice
- ECET 337 RC Differential Equations-Practice

Still need to export:
- ECET 337-Basic Analog Calculations-Practice
- ECET 337 Impedance Combination-Practice
- ECET 337 Standard Waveforms-Practice
- ECET 337-C&L in the Time Domain-Practice
- ECET 337 RC Laplace-Practice
- ECET 337 RL Circuits with Laplace Transforms-Practice
- ECET 337-Filter Terminology-Practice
- ECET 337 2nd Order Butterworth Low Pass Filter-Practice
- ECET 337 4th Order Bessel HP Filter-Practice
- 21-HW-Bandpass Filter-Practice
- 26-HW-Closed Loop-Practice
- 27-Proportional Control-Practice
- PI Control Software-Practice

**To export:** Open each in browser while logged into Variate, click the SingleFile extension icon, save.

---

## Table line numbers — quick reference (Nixon Table)

| Signal | Table Entry |
|--------|-------------|
| DC / Step | **2** |
| Sine | **6** |
| Cosine | **7** |
| Ramp | **4** |
| Decaying exponential (τs form) | **13a** |
| Decaying exponential (a form) | **13b** |
| Rising exponential (τs form) | **17a** |
| Rising exponential (a form) | **17b** |
