/**
 * capture_network_bookmarklet.js
 * ─────────────────────────────────────────────────────────────────────────────
 * VARIATE NETWORK CAPTURE BOOKMARKLET
 *
 * PURPOSE:
 *   When you open a Variate practice page, paste this into the browser console.
 *   It intercepts all fetch() calls and logs them in a format that
 *   variate_full_extractor.py can read (--from-har flag).
 *
 * HOW TO USE:
 *   1. Open the Variate practice assignment in your browser
 *   2. Open DevTools (F12) → Console tab
 *   3. Paste this entire script and press Enter
 *   4. Reload the page (Ctrl+R) — all network requests will be captured
 *   5. Type in console:  downloadCapture()
 *   6. A .txt file will download — pass it to the extractor:
 *        python3 variate_full_extractor.py --from-har captured.txt
 *
 * ALTERNATIVELY (faster):
 *   DevTools → Network tab → after page loads → right-click any request
 *   → "Copy all as fetch" → paste into a .txt file
 *   Then run: python3 variate_full_extractor.py --from-har yourfile.txt
 *
 * NOTE: This captures requests only — not responses. The extractor
 * re-makes the API call itself, so the token is all we need.
 */

(function() {
  const captured = [];
  const origFetch = window.fetch;

  window.fetch = function(url, options) {
    captured.push({
      url: url,
      method: (options && options.method) || 'GET',
      headers: (options && options.headers) || {},
      body: (options && options.body) || null,
      timestamp: new Date().toISOString()
    });
    return origFetch.apply(this, arguments);
  };

  window.downloadCapture = function() {
    const lines = captured.map(c => {
      const hdrs = JSON.stringify(c.headers, null, 2);
      return `fetch("${c.url}", {\n  "headers": ${hdrs},\n  "body": ${JSON.stringify(c.body)},\n  "method": "${c.method}"\n}); ;`;
    }).join('\n');
    const blob = new Blob([lines], { type: 'text/plain' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `variate_capture_${Date.now()}.txt`;
    a.click();
    console.log(`Downloaded ${captured.length} captured requests`);
  };

  console.log('%c✅ Variate capture active. Reload page, then type: downloadCapture()',
    'color: #4caf50; font-weight: bold; font-size: 14px');
  console.log('Requests captured so far:', captured.length);
})();
