'use strict';

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.join(__dirname, '..');
const htmlPath = path.join(root, 'desktop', 'ig_cleaner_pro_v120_27_synced_companion.html');
const html = fs.readFileSync(htmlPath, 'utf8');

function requireToken(token, why) {
  assert(html.includes(token), why + ': ' + token);
}

for (const [token, why] of [
  ['<title>Instagram Cleaner Pro v120.39</title>', 'Desktop title must match active development version'],
  ['Engine v119 · UI v120.39', 'Desktop visible UI version must match active development version'],
  ['function readFile(file)', 'Desktop must read local files'],
  ["r.readAsText(file,'utf-8')", 'Desktop must parse the full selected file'],
  ['function extractFromJSON(data,source)', 'JSON importer must exist'],
  ['JSON.parse(text)', 'JSON validation must parse the full document'],
  ['function extractFromRaw(text,source)', 'HTML/raw export fallback must exist'],
  ['async function parseFiles(files,type)', 'Shared import pipeline must exist'],
  ["document.getElementById('followingInput')", 'Following import control must exist'],
  ["document.getElementById('followersInput')", 'Followers import control must exist'],
  ["document.getElementById('pendingInput')", 'Pending import control must exist']
]) requireToken(token, why);

for (const token of [
  "const LS_PROT='ig_v13_protected'",
  "const LS_DONE='ig_v13_done'",
  "const LS_REVIEW_META='ig_v15_review_meta'",
  "const LS_ACTIVE_FOCUS_BATCH='ig_v68_active_focus_batch'",
  "const LS_PROFILE_HISTORY='ig_v69_profile_history'",
  "const LS_PENDING_REQUESTS='ig_v47_pending_requests'",
  "const LS_PENDING_REVIEW_META='ig_v50_pending_review_meta'",
  "SNAP_DB='ig_cleaner_pro_history'",
  'indexedDB.open(SNAP_DB,1)',
  'function exportFullBackup()',
  'function importFullBackup(input)'
]) requireToken(token, 'Persistent-state compatibility token missing');

for (const token of [
  'Revisar de nuevo 30',
  'Double Check 30',
  'Ver NO ME SIGUE revisados',
  'Followers',
  'Mutuals',
  'Pending',
  'function setActiveFocusBatch(kind,rows,label)',
  'function saveActiveFocusBatch()',
  'function loadActiveFocusBatch()',
  'function renderRecentActivity()'
]) requireToken(token, 'Required product workflow missing');

for (const token of [
  'async function pullDoubleCheckCycle()',
  'async function pushDoubleCheckCycle()',
  'window.igcQueueDoubleCheckCycle=function()',
  "state_key:'focus_double_check_cycle'",
  'followersEvidence:{partial:!!(window.V119_HTML?.active && window.V119_HTML?.partial)',
  "window.igcQueueDoubleCheckCycle?.()",
  'ig_cleaner_double_check_epoch'
]) requireToken(token, 'Desktop + Android Double Check cycle sync missing');

// HTML parsing moves non-whitespace text between <style> blocks into visible
// body content, rendering raw "\\n\\n" above the sidebar on Chromium.
assert(!html.includes('\\n\\\\n<style'), 'Literal backslash-n before CSS renders as visible UI text');
assert(!html.includes('</style>\\\\n\\n<style'), 'Literal backslash-n after CSS renders as visible UI text');
for (const token of [
  "IGC_INSTAGRAM_OWNER=igcOwnerFingerprint()",
  "getInstagramOwnerEmail",
  "IGC_INSTAGRAM_REGISTRY_KEY",
  "igc_profile__'+IGC_INSTAGRAM_OWNER+'__'"
]) requireToken(token, "Per-login Instagram local-state isolation missing");

const staticHtml = html.replace(/<script[\s\S]*?<\/script>/gi, '');
const ids = [...staticHtml.matchAll(/\sid=["']([^"']+)["']/gi)].map(m => m[1]);
const seen = new Set(), duplicates = new Set();
for (const id of ids) {
  if (seen.has(id)) duplicates.add(id);
  seen.add(id);
}
assert.strictEqual(duplicates.size, 0, 'Duplicate static DOM IDs: ' + [...duplicates].join(', '));

const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).filter(Boolean);
assert(scripts.length >= 5, 'Expected multiple inline application modules.');
for (let i = 0; i < scripts.length; i++) {
  try { new Function(scripts[i]); }
  catch (err) { throw new Error('Inline script #' + i + ' syntax error: ' + err.message); }
}

console.log('Desktop contract passed:', {
  bytes: Buffer.byteLength(html),
  staticIds: ids.length,
  inlineScripts: scripts.length
});
