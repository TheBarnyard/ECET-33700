/**
 * answer_intercept.js
 * ─────────────────────────────────────────────────────────────────────────────
 * VARIATE ANSWER CAPTURE BOOKMARKLET
 *
 * PURPOSE:
 *   Variate correct answers are NEVER in the page source before submission.
 *   After you submit an answer, the server returns a grading response that
 *   includes whether you were correct and (on some question types) the
 *   correct value.  This script intercepts those responses.
 *
 * HOW TO USE:
 *   METHOD A — Browser Console (easiest):
 *     1. Open a Variate practice assessment in Chrome/Firefox
 *     2. Open DevTools (F12) → Console tab
 *     3. Paste this ENTIRE script and press Enter
 *     4. Submit answers as normal — captured data appears in console
 *        and is stored in window.__variate_answers__
 *     5. At the end, type:  copy(JSON.stringify(window.__variate_answers__, null, 2))
 *        to copy all captured answers to clipboard
 *
 *   METHOD B — Bookmarklet:
 *     1. Create a new browser bookmark
 *     2. Set the URL to:  javascript:(function(){ /* paste minified version here *\/ })();
 *     3. Click the bookmark on any Variate page to activate
 *
 * WHAT IS CAPTURED:
 *   - Question text (from the DOM at time of submission)
 *   - Your submitted answer
 *   - Whether it was correct/incorrect
 *   - The server's response body (may contain correct answer on some question types)
 *
 * IMPORTANT NOTES:
 *   - This works by monkey-patching fetch() — completely client-side, no extensions needed
 *   - Variate uses POST to /api/... endpoints for grading
 *   - The correct answer is NOT always in the response; it depends on question type
 *     and whether the professor enabled immediate feedback
 *   - On MATH INPUT questions, Variate typically only says correct/incorrect
 *     without revealing the answer until all attempts are exhausted
 *   - On MULTIPLE CHOICE questions, the response often includes more detail
 *
 * ─────────────────────────────────────────────────────────────────────────────
 */

(function() {
  'use strict';

  if (window.__variate_interceptor_active__) {
    console.log('[Variate] Interceptor already active. Answers so far:', window.__variate_answers__);
    return;
  }
  window.__variate_interceptor_active__ = true;
  window.__variate_answers__ = window.__variate_answers__ || [];

  const origFetch = window.fetch;

  window.fetch = async function(...args) {
    const response = await origFetch.apply(this, args);

    // Clone so we can read body without consuming it
    const url = (typeof args[0] === 'string') ? args[0] : (args[0]?.url || '');
    const isVariateGrade = url.includes('variate') &&
      (url.includes('response') || url.includes('grade') || url.includes('attempt') || url.includes('submit'));

    if (isVariateGrade) {
      try {
        const clone = response.clone();
        const body = await clone.json().catch(() => null) || await clone.text().catch(() => null);

        // Extract question context from the DOM
        const activeQuestion = extractActiveQuestion();

        const record = {
          timestamp: new Date().toISOString(),
          url: url,
          method: (args[1] && args[1].method) || 'GET',
          request_body: parseRequestBody(args[1]),
          response_status: response.status,
          response_body: body,
          question_context: activeQuestion,
        };

        window.__variate_answers__.push(record);
        console.log('[Variate Intercept]', record);
        console.log(`[Variate] Total captured: ${window.__variate_answers__.length}`);
        console.log('[Variate] To export: copy(JSON.stringify(window.__variate_answers__, null, 2))');
      } catch (e) {
        console.warn('[Variate] Could not parse response:', e);
      }
    }

    return response;
  };

  // Also intercept XMLHttpRequest for older code paths
  const origXHROpen = XMLHttpRequest.prototype.open;
  const origXHRSend = XMLHttpRequest.prototype.send;

  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__variate_url__ = url;
    this.__variate_method__ = method;
    return origXHROpen.apply(this, [method, url, ...rest]);
  };

  XMLHttpRequest.prototype.send = function(body) {
    const xhr = this;
    const url = xhr.__variate_url__ || '';
    const isVariateGrade = url.includes('variate') &&
      (url.includes('response') || url.includes('grade') || url.includes('attempt') || url.includes('submit'));

    if (isVariateGrade) {
      xhr.addEventListener('load', function() {
        try {
          const respBody = JSON.parse(xhr.responseText);
          const record = {
            timestamp: new Date().toISOString(),
            url: url,
            method: xhr.__variate_method__,
            request_body: body ? JSON.parse(body) : null,
            response_status: xhr.status,
            response_body: respBody,
            question_context: extractActiveQuestion(),
          };
          window.__variate_answers__.push(record);
          console.log('[Variate XHR Intercept]', record);
        } catch(e) {
          console.warn('[Variate XHR] Parse error', e);
        }
      });
    }

    return origXHRSend.apply(this, [body]);
  };

  function parseRequestBody(opts) {
    if (!opts || !opts.body) return null;
    try {
      return JSON.parse(opts.body);
    } catch {
      return opts.body;
    }
  }

  function extractActiveQuestion() {
    // Try to find what question is currently being answered
    // by looking at focused/recently-interacted elements
    try {
      const editors = document.querySelectorAll('.ql-editor');
      const questions = [];
      editors.forEach((el, i) => {
        const text = el.innerText?.trim();
        if (text && text.length > 10) {
          questions.push({ index: i, text: text.substring(0, 300) });
        }
      });
      return questions;
    } catch {
      return null;
    }
  }

  console.log('[Variate] ✅ Answer intercept active!');
  console.log('[Variate] Submit answers normally. Data will be logged here.');
  console.log('[Variate] Export when done: copy(JSON.stringify(window.__variate_answers__, null, 2))');
  console.log('[Variate] Then paste into a .json file for your answer key.');

})();
