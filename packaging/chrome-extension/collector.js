/* Pure, read-only helpers shared by the Chrome popup and injected isolated world.
 * No cookies, fetch, network, automation, DOM mutation or Instagram actions.
 */
(function (root) {
  "use strict";
  const BAD_NAMES = new Set([
    "accounts","about","api","challenge","checkpoint","direct","developer",
    "explore","graphql","help","legal","p","reel","reels","stories",
    "auth_platform","privacy","terms","web","login","signup","settings"
  ]);
  const USER_RE = /^[a-z0-9._]{1,30}$/i;
  function username(value) {
    let v = String(value || "").trim().replace(/^@/, "");
    if (/^https?:\/\//i.test(v)) {
      try {
        const u = new URL(v);
        if (!["instagram.com", "www.instagram.com"].includes(u.hostname.toLowerCase())) return "";
        v = u.pathname.split("/").filter(Boolean)[0] || "";
      } catch { return ""; }
    }
    const lower = v.toLowerCase();
    return USER_RE.test(v) && !BAD_NAMES.has(lower) ? lower : "";
  }
  function profileFromUrl(url) {
    try {
      const u = new URL(url);
      if (!["instagram.com", "www.instagram.com"].includes(u.hostname.toLowerCase())) return "";
      const segments = u.pathname.split("/").filter(Boolean);
      return segments.length === 1 ? username(segments[0]) : "";
    } catch { return ""; }
  }
  // Parses explicit visible "1,234", "12.4K", "1,2 mil", "2M" values.
  // Marks every compact count approximate; no false claim of precise counts.
  function parseCount(value) {
    const t = String(value || "").trim().replace(/[\u00a0\u202f\s]/g, "");
    const m = t.match(/^(\d[\d.,]*)(k|m|b|mil|mill[oó]n(?:es)?)?$/i);
    if (!m) return null;
    let n = m[1], unit = (m[2] || "").toLowerCase();
    if (unit) {
      const multiplier = unit === "k" || unit === "mil" ? 1000 :
        (unit === "m" || unit.startsWith("mill")) ? 1000000 : 1000000000;
      // One decimal separator at most for compact "1.2K", localized "1,2 mil".
      if (!/^\d+(?:[.,]\d{1,2})?$/.test(n)) return null;
      const number = Number(n.replace(",", "."));
      return Number.isFinite(number) ? { count: String(Math.round(number * multiplier)), approximate: true } : null;
    }
    if (/^\d+$/.test(n)) return { count: n, approximate: false };
    if (/^\d{1,3}(?:[.,]\d{3})+$/.test(n)) {
      return { count: n.replace(/[.,]/g, ""), approximate: false };
    }
    return null;
  }
  function csvRows(text) {
    const rows = [];
    let row = [], cell = "", quoted = false;
    const s = String(text || "").replace(/^\uFEFF/, "");
    for (let i = 0; i < s.length; i++) {
      const ch = s[i];
      if (ch === '"') {
        if (quoted && s[i + 1] === '"') { cell += '"'; i++; }
        else if (!quoted && cell === "") quoted = true;
        else if (quoted) quoted = false;
        else throw Error("Invalid CSV quoting");
      } else if (!quoted && ch === ",") { row.push(cell); cell = ""; }
      else if (!quoted && (ch === "\n" || ch === "\r")) {
        row.push(cell); if (row.some(v => v.trim())) rows.push(row);
        row = []; cell = "";
        if (ch === "\r" && s[i + 1] === "\n") i++;
      } else { cell += ch; }
    }
    if (quoted) throw Error("Unclosed quoted CSV field");
    row.push(cell);
    if (row.some(v => v.trim())) rows.push(row);
    return rows;
  }
  function importQueue(csv) {
    const rows = csvRows(csv);
    if (!rows.length) throw Error("The CSV is empty.");
    const headers = rows.shift().map(s => s.trim().toLowerCase());
    const col = headers.indexOf("username");
    if (col < 0) throw Error("Import a Following CSV containing a username column.");
    const result = [], seen = new Set();
    for (const row of rows) {
      const candidate = username(row[col] || "");
      if (candidate && !seen.has(candidate)) {
        seen.add(candidate); result.push(candidate);
      }
    }
    if (!result.length) throw Error("The CSV contains no valid Instagram profile usernames.");
    return result;
  }
  function csvCell(value) {
    const text = String(value ?? "");
    return /[",\n\r]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
  }
  const HEADERS = ["username","followers","following","checked_at","source","status","approximate"];
  function exportCsv(records, orderedNames) {
    const out = [HEADERS.map(csvCell).join(",")];
    const byName = records || {};
    for (const user of orderedNames || []) {
      const v = byName[user];
      if (!v || v.status !== "ok") continue;
      out.push(HEADERS.map(h => csvCell(v[h])).join(","));
    }
    return out.join("\r\n") + "\r\n";
  }
  function extractVisibleProfile(doc, url) {
    const user = profileFromUrl(url);
    if (!user) return { error: "Open an Instagram profile page first (not Login, Reels or a challenge)." };
    const data = { followers: null, following: null };
    // Restrict reads to the profile header and explicit profile-counter links.
    // Do not scan DMs, comments, cookies, arbitrary body text, or private APIs.
    const header = doc.querySelector("header");
    if (!header) return { error: "Instagram profile header is not visible. Wait for it to load." };
    const anchors = Array.from(header.querySelectorAll('a[href], a[role="link"]'));
    for (const link of anchors) {
      let dest = "";
      try { dest = new URL(link.getAttribute("href") || "", url).pathname; } catch { continue; }
      let category = "";
      if (dest === "/" + user + "/followers/" || dest === "/" + user + "/followers") category = "followers";
      if (dest === "/" + user + "/following/" || dest === "/" + user + "/following") category = "following";
      if (!category) continue;
      const title = Array.from(link.querySelectorAll("[title]")).map(e => e.getAttribute("title")).find(s => parseCount(s));
      const text = String(link.innerText || link.textContent || "").replace(/,/g, ",");
      const aria = link.getAttribute("aria-label") || "";
      // Only interpret numeric tokens next to the link's own known counter.
      const token = title || ((text + " " + aria).match(/\d[\d.,]*(?:\s*(?:k|m|b|mil|mill[oó]n(?:es)?))?/i) || [])[0];
      const value = parseCount(token);
      if (value) data[category] = value;
    }
    // Some public Instagram layouts render named counters without anchors.
    // Match only explicit header list items with a complete counter label.
    for (const item of Array.from(header.querySelectorAll("li"))) {
      const text = String(item.innerText || item.textContent || "").trim();
      const m = text.match(/^\s*(\d[\d.,]*(?:\s*(?:k|m|b|mil|mill[oó]n(?:es)?))?)\s*(followers|following|seguidores|seguidos)\s*$/i);
      if (!m) continue;
      const kind = /following|seguidos/i.test(m[2]) ? "following" : "followers";
      if (!data[kind]) data[kind] = parseCount(m[1]);
    }
    if (!data.followers || !data.following) {
      return { username: user, error: "Could not verify both counters from the visible profile header. Nothing was saved." };
    }
    return {
      username: user, followers: data.followers.count, following: data.following.count,
      checked_at: new Date().toISOString(), source: "instagram_visible_profile_extension",
      status: "ok", approximate: String(data.followers.approximate || data.following.approximate)
    };
  }
  // Keep a complete dated local measurement history. A new pass never deletes
  // the preceding count; imported older single-record stores migrate lazily.
  function validMeasurement(record) {
    return !!record && record.status === "ok" &&
      /^\d+$/.test(String(record.followers || "")) &&
      /^\d+$/.test(String(record.following || "")) &&
      Number.isFinite(Date.parse(record.checked_at || ""));
  }
  function firstPassQueue(queue, records) {
    // Never-measured first, incomplete/unavailable second. Already measured last.
    const names = [...new Set(queue || [])];
    const data = records || {};
    const never = names.filter(u => !data[u]);
    const incomplete = names.filter(u => data[u] && !validMeasurement(data[u]));
    return [...never, ...incomplete];
  }
  function oldestFirst(queue, records) {
    const data = records || {};
    return [...new Set(queue || [])].filter(u => validMeasurement(data[u]))
      .sort((a,b) => Date.parse(data[a].checked_at) - Date.parse(data[b].checked_at)
        || a.localeCompare(b));
  }
  function appendMeasurement(records, history, record) {
    const user = username(record?.username);
    if (!user || !validMeasurement(record)) throw Error("Only complete dated measurements may be saved.");
    const previous = records[user];
    const timeline = Array.isArray(history[user]) ? history[user] : [];
    // Preserve historical measurements, including rows from releases predating history.
    if (validMeasurement(previous) && !timeline.some(row =>
        row.checked_at === previous.checked_at && row.followers === previous.followers &&
        row.following === previous.following)) timeline.push({...previous});
    if (!timeline.some(row => row.checked_at === record.checked_at &&
        row.followers === record.followers && row.following === record.following))
      timeline.push({...record});
    history[user] = timeline;
    records[user] = {...record};
    return {previous:validMeasurement(previous) ? {...previous} : null,
      followers_delta:validMeasurement(previous) ?
        Number(record.followers) - Number(previous.followers) : null,
      following_delta:validMeasurement(previous) ?
        Number(record.following) - Number(previous.following) : null};
  }
  function historyCsv(history, queue) {
    const headers = ["username","followers","following","checked_at","source","status","approximate"];
    const lines = [headers.join(",")];
    for (const user of [...new Set(queue || [])]) {
      for (const row of history[user] || []) {
        if (!validMeasurement(row)) continue;
        lines.push(headers.map(k => csvCell(row[k])).join(","));
      }
    }
    return lines.join("\r\n") + "\r\n";
  }
  const api = { username, profileFromUrl, parseCount, csvRows, importQueue, exportCsv, extractVisibleProfile,
    validMeasurement, firstPassQueue, oldestFirst, appendMeasurement, historyCsv };
  root.IGC_CAPTURE = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
