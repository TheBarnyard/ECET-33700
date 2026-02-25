/**
 * devtools_capture_all.js
 * ─────────────────────────────────────────────────────────────────────────────
 * PASTE THIS INTO THE DEVTOOLS CONSOLE ON ANY VARIATE PAGE.
 *
 * HOW TO USE:
 *   1. Go to https://purdue.variate.org/courses/1492  (your course page)
 *   2. Open DevTools → Console  (F12 → Console tab)
 *   3. Paste this entire script, press Enter
 *   4. Wait ~30 seconds while it fetches everything
 *   5. A .txt file auto-downloads — pass it to variate_full_extractor.py
 *        python3 variate_full_extractor.py --from-har downloaded_file.txt
 *   6. Open the resulting HTML in your browser — all answers shown
 *
 * WHAT IT DOES:
 *   - Grabs your Bearer token from memory (already in the page)
 *   - Fetches /api/assessments to get ALL your assignments
 *   - Fetches /api/groupAssessments/{id}/problemInstances for each one
 *   - Fetches every artifact URL (question text, LaTeX, choices)
 *   - Packages everything into one self-contained JSON/text file
 *   - Auto-downloads it
 *
 * NO SUBMISSIONS. NO ATTEMPTS USED. ZERO CLICKS AFTER PASTE.
 * ─────────────────────────────────────────────────────────────────────────────
 */
(async function VARIATE_CAPTURE_ALL() {

  // ── 1. Extract Bearer token from React app state / XHR headers ────────────
  function getToken() {
    // Try intercepting from a live request (most reliable)
    // Variate stores auth in React context — walk the fiber tree
    function findInFiber(el) {
      const key = Object.keys(el).find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance'));
      if (!key) return null;
      let fiber = el[key];
      let depth = 0;
      while (fiber && depth < 500) {
        const pending = fiber.memoizedState;
        if (pending && pending.queue && pending.queue.dispatch) {
          // not what we want
        }
        // Look for auth token in memoized props/state
        const props = fiber.memoizedProps || {};
        const state = fiber.memoizedState || {};
        for (const obj of [props, state]) {
          if (obj && typeof obj === 'object') {
            const s = JSON.stringify(obj).slice(0, 500);
            const m = s.match(/Bearer\s+([A-Za-z0-9+/=_\-]{200,})/);
            if (m) return 'Bearer ' + m[1];
          }
        }
        fiber = fiber.return;
        depth++;
      }
      return null;
    }

    // Try from React root first
    const root = document.getElementById('root') || document.querySelector('[data-reactroot]') || document.body;
    const fromFiber = findInFiber(root);
    if (fromFiber) return fromFiber;

    // Fallback: intercept next fetch call
    return null;
  }

  // ── 2. Intercept token from real requests ─────────────────────────────────
  let capturedToken = null;
  const origFetch = window._origFetch || window.fetch;
  window._origFetch = origFetch;

  window.fetch = function(url, opts) {
    if (!capturedToken && opts && opts.headers) {
      const h = opts.headers;
      const auth = (typeof h.get === 'function' ? h.get('authorization') : h['authorization']) || '';
      if (auth.startsWith('Bearer ')) capturedToken = auth;
    }
    return origFetch.apply(this, arguments);
  };

  // Try immediately from fiber
  capturedToken = getToken();

  // ── 3. If no token yet, trigger a fetch to capture it ────────────────────
  if (!capturedToken) {
    console.log('%c[Variate] Waiting for token from next API call...', 'color:#90caf9');
    // Trigger a benign API call that will fire with auth headers
    try { await origFetch('https://purdue.api.variate.org/api/time'); } catch(e) {}
    await new Promise(r => setTimeout(r, 500));
  }

  // Final fallback: ask user to paste token
  if (!capturedToken) {
    capturedToken = prompt(
      'Could not auto-capture token.\n\n' +
      'In DevTools → Network tab, click any request to purdue.api.variate.org\n' +
      '→ Headers → copy the Authorization header value (starts with "Bearer ").\n\n' +
      'Paste it here:'
    );
    if (!capturedToken) { console.error('[Variate] No token — aborting.'); return; }
  }

  console.log('%c[Variate] ✅ Token captured', 'color:#4caf50; font-weight:bold');

  // ── 4. Fetch helpers ───────────────────────────────────────────────────────
  const API = 'https://purdue.api.variate.org/api';
  const headers = {
    'accept': '*/*',
    'authorization': capturedToken,
    'content-type': 'application/json; charset=utf-8',
  };

  async function apiGet(path) {
    try {
      const r = await origFetch(`${API}/${path}`, { headers });
      if (!r.ok) { console.warn(`[Variate] ${path} → ${r.status}`); return null; }
      return r.json();
    } catch(e) {
      console.warn(`[Variate] ${path} error:`, e.message);
      return null;
    }
  }

  async function fetchArtifact(url) {
    try {
      const r = await origFetch(url);
      return r.ok ? r.text() : '';
    } catch(e) { return ''; }
  }

  // ── 5. Get course ID from URL ──────────────────────────────────────────────
  const courseMatch = location.pathname.match(/courses\/(\d+)/);
  const courseId = courseMatch ? courseMatch[1] : '1492';
  console.log(`%c[Variate] Course ID: ${courseId}`, 'color:#90caf9');

  // ── 6. Get all group assessments ──────────────────────────────────────────
  console.log('%c[Variate] Fetching all assessments...', 'color:#90caf9');
  const gaList = await apiGet(`groupAssessments?groupId=${courseId}&pageSize=200`);

  // Also try the assessments endpoint
  const assessmentList = await apiGet(`assessments?groupId=${courseId}&pageSize=200`);

  // Collect GA IDs from both sources
  const gaIds = new Set();

  if (gaList && Array.isArray(gaList.items || gaList)) {
    const items = gaList.items || gaList;
    items.forEach(ga => gaIds.add(ga.id));
    console.log(`[Variate] Found ${items.length} group assessments from groupAssessments endpoint`);
  }

  if (assessmentList && Array.isArray(assessmentList.items || assessmentList)) {
    const items = assessmentList.items || assessmentList;
    items.forEach(a => {
      if (a.groupAssessmentId) gaIds.add(a.groupAssessmentId);
      if (a.id) gaIds.add(a.id);
    });
  }

  // If we can't get GA list, grab from current page URL
  const gaMatch = location.pathname.match(/groupAssessments\/(\d+)/);
  if (gaMatch) gaIds.add(parseInt(gaMatch[1]));

  // Also grab any GA IDs visible in the current page HTML
  const pageText = document.body.innerText;
  // Try to extract from any visible links or data attributes
  document.querySelectorAll('[href*="groupAssessments"]').forEach(el => {
    const m = el.href.match(/groupAssessments\/(\d+)/);
    if (m) gaIds.add(parseInt(m[1]));
  });

  console.log(`%c[Variate] Total unique GA IDs found: ${gaIds.size}`, 'color:#4caf50');
  if (gaIds.size === 0) {
    console.warn('[Variate] No group assessment IDs found. Try navigating to a specific assessment page first.');
  }

  // ── 7. Fetch problem instances for each GA ─────────────────────────────────
  const allData = {
    courseId,
    capturedAt: new Date().toISOString(),
    token: capturedToken,  // saved for reuse
    groupAssessments: []
  };

  for (const gaId of gaIds) {
    console.log(`%c[Variate] Fetching GA ${gaId}...`, 'color:#90caf9');

    // Get GA metadata
    const gaInfo = await apiGet(`groupAssessments/${gaId}`) || { id: gaId, name: `Assessment ${gaId}` };

    // Get problem instances (the gold — contains formattedVariableValues = answers)
    const problems = await apiGet(`groupAssessments/${gaId}/problemInstances`);

    if (!problems || !Array.isArray(problems) || problems.length === 0) {
      console.log(`  [skip] No problems found for GA ${gaId}`);
      continue;
    }

    console.log(`  ✅ ${gaInfo.name || gaId}: ${problems.length} problem(s)`);

    // Collect all artifact URLs to fetch
    const artifactUrls = new Set();
    for (const prob of problems) {
      for (const stmt of (prob.statements || [])) {
        if (stmt.contentArtifact?.url) artifactUrls.add(stmt.contentArtifact.url);
        for (const sol of (stmt.solutionInstances || [])) {
          for (const ch of (sol.choices || [])) {
            if (ch.contentArtifact?.url) artifactUrls.add(ch.contentArtifact.url);
          }
        }
      }
      for (const va of (prob.variableArtifacts || [])) {
        if (va.url) artifactUrls.add(va.url);
      }
    }

    // Fetch all artifacts
    console.log(`  Fetching ${artifactUrls.size} artifacts...`);
    const artifactCache = {};
    const urlArr = [...artifactUrls];
    // Batch fetches to avoid rate limiting
    const BATCH = 10;
    for (let i = 0; i < urlArr.length; i += BATCH) {
      const batch = urlArr.slice(i, i + BATCH);
      const results = await Promise.all(batch.map(u => fetchArtifact(u)));
      batch.forEach((u, j) => { artifactCache[u] = results[j]; });
    }

    allData.groupAssessments.push({
      id: gaId,
      name: gaInfo.name || `Assessment ${gaId}`,
      typename: gaInfo.typename,
      startDate: gaInfo.startDate,
      endDate: gaInfo.endDate,
      problems,
      artifactCache
    });
  }

  // ── 8. Also save raw fetch format for variate_full_extractor.py ──────────
  // Build the "Copy all as fetch" format that the Python script expects
  const fetchLines = [`  FORMAT           `];

  // Add one fake entry with the token so the extractor can find it
  fetchLines.push(`fetch("https://purdue.api.variate.org/api/time", {
    "headers": {
      "accept": "*/*",
      "authorization": "${capturedToken}",
      "content-type": "application/json; charset=utf-8"
    },
    "body": null,
    "method": "GET"
  }); ;`);

  // Add GA IDs as fetch entries so the extractor can discover them
  for (const ga of allData.groupAssessments) {
    fetchLines.push(`fetch("https://purdue.api.variate.org/api/groupAssessments/${ga.id}/problemInstances", {
    "headers": {
      "accept": "*/*",
      "authorization": "${capturedToken}",
      "content-type": "application/json; charset=utf-8"
    },
    "body": null,
    "method": "GET"
  }); ;`);
  }

  // ── 9. Package and download ────────────────────────────────────────────────
  const output = {
    meta: {
      tool: 'variate_capture_all.js',
      version: '2.0',
      capturedAt: allData.capturedAt,
      courseId,
      totalAssignments: allData.groupAssessments.length,
      instructions: [
        'Pass this file to variate_full_extractor.py:',
        '  python3 variate_full_extractor.py --from-json variate_capture.json',
        'Or use the fetch-format .txt file with:',
        '  python3 variate_full_extractor.py --from-har variate_capture.txt --ga-id <ID>'
      ]
    },
    token: capturedToken,
    groupAssessments: allData.groupAssessments
  };

  // Download JSON (complete data)
  const jsonBlob = new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' });
  const jsonLink = document.createElement('a');
  jsonLink.href = URL.createObjectURL(jsonBlob);
  jsonLink.download = `variate_capture_${courseId}_${Date.now()}.json`;
  jsonLink.click();

  // Download fetch-format .txt (for variate_full_extractor.py --from-har)
  const txtBlob = new Blob([fetchLines.join('\n')], { type: 'text/plain' });
  const txtLink = document.createElement('a');
  txtLink.href = URL.createObjectURL(txtBlob);
  txtLink.download = `variate_capture_${courseId}_${Date.now()}.txt`;
  setTimeout(() => txtLink.click(), 300);

  // ── 10. Print summary to console ──────────────────────────────────────────
  console.log('%c\n[Variate] ════════════════════════════════════════════', 'color:#4caf50; font-weight:bold');
  console.log('%c✅ CAPTURE COMPLETE', 'color:#4caf50; font-weight:bold; font-size:16px');
  console.log(`%c${allData.groupAssessments.length} assignments captured`, 'color:#81c784');
  console.log('');
  for (const ga of allData.groupAssessments) {
    const totalAnswers = ga.problems.reduce((acc, p) => {
      const vars = JSON.parse(p.formattedVariableValues || '{}');
      return acc + Object.keys(vars).length;
    }, 0);
    console.log(`  📋 ${ga.name} (ID: ${ga.id})`);
    console.log(`     ${ga.problems.length} problem(s), ${totalAnswers} answer variables`);
    for (const prob of ga.problems) {
      const vars = JSON.parse(prob.formattedVariableValues || '{}');
      const varStr = Object.entries(vars).map(([k,v]) => `${k}=${v}`).join(', ');
      console.log(`     Problem ${prob.ordinal}: ${varStr}`);
    }
  }
  console.log('');
  console.log('%c📥 Two files downloaded:', 'color:#90caf9');
  console.log('   variate_capture_*.json  — complete data (recommended)');
  console.log('   variate_capture_*.txt   — fetch format for --from-har flag');
  console.log('');
  console.log('%cNext step:', 'color:#ffb74d; font-weight:bold');
  console.log('  python3 variate_full_extractor.py --from-json variate_capture_*.json');
  console.log('%c════════════════════════════════════════════════════', 'color:#4caf50; font-weight:bold');

  // Restore original fetch
  window.fetch = origFetch;

})();
