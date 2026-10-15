/* Chrome MV3 popup controller. Explicit human interaction only.
 * Never injects into the page until Capture is clicked, never touches cookies
 * and never performs follow/unfollow/cancel/like actions.
 */
"use strict";
(function () {
  const C = globalThis.IGC_CAPTURE;
  const $ = id => document.getElementById(id);
  let state = {queue: [], records: {}};
  let currentWorkspace = "";
  let busy = false;
  const storageKey = workspace => "igc_chrome_counts_v1__" + encodeURIComponent(workspace);
  const scope = () => {
    const w = C.username($("workspace").value);
    if (!w) throw Error("Enter a valid Instagram workspace username first.");
    return w;
  };
  const empty = () => ({queue: [], records: {}});
  const error = e => status(e?.message || String(e), "error");
  function status(message, kind="") {
    const el = $("status");
    el.textContent = message;
    el.className = kind;
  }
  async function selectWorkspace() {
    const w = scope();
    const response = await chrome.storage.local.get([storageKey(w)]);
    const stored = response[storageKey(w)];
    state = stored && Array.isArray(stored.queue) && stored.records &&
            typeof stored.records === "object" && !Array.isArray(stored.records)
      ? {queue: stored.queue.map(C.username).filter(Boolean), records: stored.records} : empty();
    currentWorkspace = w;
    await chrome.storage.local.set({igc_chrome_last_workspace_v1: w});
    render();
  }
  async function save() {
    if (!currentWorkspace || currentWorkspace !== scope())
      throw Error("Choose and load the correct Instagram workspace before saving.");
    await chrome.storage.local.set({[storageKey(currentWorkspace)]: state});
    render();
  }
  function ordered() {
    return [...new Set([...state.queue, ...Object.keys(state.records).filter(C.username)])];
  }
  function render() {
    const rows = ordered();
    const valid = rows.filter(u => state.records[u]?.status === "ok").length;
    $("queueSize").textContent = String(state.queue.length);
    $("savedSize").textContent = String(valid);
    $("remainingSize").textContent = String(Math.max(0,state.queue.filter(u => state.records[u]?.status !== "ok").length));
    $("next").disabled = busy || !state.queue.some(u => state.records[u]?.status !== "ok");
    $("capture").disabled = busy;
    $("export").disabled = busy || !valid;
    $("current").textContent = state.queue.length
      ? "Next: @" + (state.queue.find(u => state.records[u]?.status !== "ok") || "All imported profiles captured")
      : "Open a profile in Chrome to capture it, or import a Following CSV queue first.";
  }
  async function action(fn) {
    if (busy) return;
    busy = true; render();
    try { await fn(); } catch (e) { error(e); }
    finally { busy = false; render(); }
  }
  async function importFile() {
    const file = $("queueFile").files?.[0];
    if (!file) return;
    await selectWorkspace();
    const names = C.importQueue(await file.text());
    // Replace only the queue, NEVER delete previous captured records.
    state.queue = names;
    await save();
    status("Imported " + names.length + " unique Following profiles for @" + currentWorkspace +
      ". Previous results were preserved.", "success");
  }
  async function activeInstagramTab() {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    if (!tab || !Number.isInteger(tab.id)) throw Error("Open a regular Chrome tab first.");
    return tab;
  }
  async function nextProfile() {
    await selectWorkspace();
    const next = state.queue.find(u => state.records[u]?.status !== "ok");
    if (!next) throw Error("All queued profiles already have saved counters.");
    const tab = await activeInstagramTab();
    // Navigate only on the user's explicit click. Chrome's normal session is
    // never cloned, uploaded, automated in the background, or debug-attached.
    await chrome.tabs.update(tab.id, {url: "https://www.instagram.com/" + next + "/"});
    status("Opened @" + next + ". Wait for the page to load, then click Capture visible counts.", "success");
  }
  async function capture() {
    await selectWorkspace();
    const tab = await activeInstagramTab();
    if (!C.profileFromUrl(tab.url || ""))
      throw Error("Open a regular Instagram profile tab first, not Login, Reels or CAPTCHA.");
    // activeTab permission is acquired through the user's popup interaction.
    // The collector executes in an isolated extension world; no page script,
    // cookies, or credentials are read or exported.
    await chrome.scripting.executeScript({target:{tabId:tab.id},files:["collector.js"]});
    const answer = await chrome.scripting.executeScript({
      target:{tabId:tab.id},
      func:() => globalThis.IGC_CAPTURE.extractVisibleProfile(document, location.href)
    });
    const result = answer?.[0]?.result;
    if (!result || result.error || result.status !== "ok")
      throw Error(result?.error || "Instagram has not displayed both profile counters.");
    if (state.queue.length && !state.queue.includes(result.username))
      throw Error("@" + result.username + " is not in this workspace's imported Following queue. Nothing was saved.");
    if (!C.username(result.username) || !/^(?:\d+)$/.test(result.followers) ||
        !/^(?:\d+)$/.test(result.following))
      throw Error("Invalid profile counter result; nothing saved.");
    state.records[result.username] = {
      username:result.username, followers:result.followers,
      following:result.following, checked_at:result.checked_at,
      source:"instagram_visible_profile_extension", status:"ok",
      approximate:result.approximate === "true" ? "true" : "false"
    };
    await save();
    status("Saved @" + result.username + ": " + result.followers +
      " followers / " + result.following + " following" +
      (result.approximate === "true" ? " (approximate)" : "") + ".", "success");
  }
  async function exportResults() {
    await selectWorkspace();
    const csv = C.exportCsv(state.records, ordered());
    if (!Object.values(state.records).some(v => v?.status === "ok"))
      throw Error("Capture at least one visible profile before exporting.");
    const fileName = "IG-Cleaner-Profile-Counts-" + currentWorkspace + "-" +
      new Date().toISOString().slice(0,10) + ".csv";
    const url = URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
    try { await chrome.downloads.download({url,filename:fileName,saveAs:true}); }
    finally { setTimeout(() => URL.revokeObjectURL(url),30000); }
    status("Export started. Import this CSV in Insta Cleaner → Automations → Profile Counts.", "success");
  }
  async function clear() {
    await selectWorkspace();
    if (!window.confirm("Delete the local imported queue and captured counts for @" +
         currentWorkspace + "? Other workspaces are not affected.")) return;
    state = empty(); await save();
    status("Local workspace cleared: @" + currentWorkspace + ".", "success");
  }
  function wire() {
    $("workspace").addEventListener("change", () => action(selectWorkspace));
    $("queueFile").addEventListener("change", () => action(importFile));
    $("next").addEventListener("click", () => action(nextProfile));
    $("capture").addEventListener("click", () => action(capture));
    $("export").addEventListener("click", () => action(exportResults));
    $("clear").addEventListener("click", () => action(clear));
    chrome.storage.local.get(["igc_chrome_last_workspace_v1"])
      .then(v => {
        $("workspace").value = C.username(v.igc_chrome_last_workspace_v1) || "";
        if ($("workspace").value) return action(selectWorkspace);
        render();
      }).catch(error);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", wire);
  else wire();
})();
