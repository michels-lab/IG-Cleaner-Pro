"use strict";
/* GRANADA: Destrabar Pending must not erase owner-requested Chrome-open
 * evidence and recycle the same targets in a new Focus. No browser/network. */
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,
  "../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
// Verify the SAFE action is reachable in the real Pending UI, not merely
// a dead helper function. Keep the history-destroying reset distinct.
assert.equal((html.match(/onclick="unlockModule\\('pending'\\)"/g)||[]).length,1,
  "Pending Lab must expose the safe non-repeat Destrabar control");
assert.equal((html.match(/onclick="clearPendingOpened\\(\\)"/g)||[]).length,1,
  "Explicit history reset remains separately labeled");
assert.match(html,/Destrabar tanda · sin repetir/);
function section(a,b){
 const i=html.indexOf(a),j=html.indexOf(b,i+a.length);
 assert(i>=0&&j>i,"Missing production source: "+a);
 return html.slice(i,j);
}
const history=["opened.one","opened.two"];
const rows=["opened.one","opened.two","fresh.three","fresh.four"];
let confirmAnswer=false,confirmCalls=0,cleared=0,rewritten=0,rendered=0,dashboard=0;
const notices=[];
const ctx={
  console,Date,Math,Set,Number,String,Array,
  pendingOpenedSet:new Set(history),
  activeFocusBatch:{kind:"pending",rows:[{username:"opened.one"}]},
  confirm:message=>{
    confirmCalls++;
    assert.match(message,/conservará los perfiles ya abiertos/);
    assert.match(message,/NO repetirlos/);
    return confirmAnswer;
  },
  msg:(message,level)=>notices.push({message,level}),
  focusFunnelData:()=>({
    total:rows.length,available:2,activeBlocked:1,openedLegacy:2}),
  clearActiveFocusBatch:()=>{
    cleared++;ctx.activeFocusBatch=null;
  },
  savePendingOpened:()=>rewritten++,
  renderPendingRequests:()=>rendered++,
  renderModuleDashboard:()=>dashboard++,
  isInActiveFocus:r=>
    !!ctx.activeFocusBatch?.rows?.some(x=>x.username===r.username),
};
vm.createContext(ctx);
vm.runInContext(section("function unlockModule(kind){",
  "function openAlternativeFocus(kind,n=30"),ctx);
vm.runInContext(section("function isPendingOpenableForFocus(row){",
  "function isMutualOpenableForFocus(row){"),ctx);
const candidates=()=>rows.map(username=>({
  username,opened:ctx.pendingOpenedSet.has(username),
  reviewed:false,snoozed:false,
})).filter(r=>ctx.isPendingOpenableForFocus(r)).map(x=>x.username);

// On Cancel of the confirmation, do NOT mutate the active batch or WAL.
ctx.unlockModule("pending");
assert.equal(cleared,0);
assert.equal(rewritten,0);
assert.deepEqual([...ctx.pendingOpenedSet],history);
assert.equal(ctx.activeFocusBatch.kind,"pending");

// On explicit "Destrabar", clear only this active cohort, preserving every
// previous Chrome opening. This must NOT add old profiles to a fresh Focus.
confirmAnswer=true;
ctx.unlockModule("pending");
assert.equal(cleared,1);
assert.equal(ctx.activeFocusBatch,null);
assert.equal(rewritten,0,"The durable open-attempt ledger is never rewritten");
assert.deepEqual([...ctx.pendingOpenedSet],history);
assert.deepEqual(candidates(),["fresh.three","fresh.four"]);
assert.match(notices.at(-1).message,/no los repetirá/);

// Clicking "Destrabar" again without a cohort must be harmless: don't
// require user consent, don't silently reset history or fabricate candidates.
const previouslyAsked=confirmCalls;
ctx.unlockModule("pending");
assert.equal(confirmCalls,previouslyAsked);
assert.equal(cleared,1);
assert.equal(rewritten,0);
assert.deepEqual([...ctx.pendingOpenedSet],history);
assert.deepEqual(candidates(),["fresh.three","fresh.four"]);
assert.match(notices.at(-1).message,/No hay tanda activa/);

// A separately named "Reset opened, unreviewed" action still exists,
// and is the ONLY source path permitted to explicitly clear the ledger.
const unlock=section("function unlockModule(kind){",
  "function openAlternativeFocus(kind,n=30");
const explicitReset=section("function clearPendingOpened(){",
  "function exportPendingCSV(){");
assert(!unlock.includes("pendingOpenedSet.clear()"),
  "Unlock must never erase Chrome navigation evidence");
assert(explicitReset.includes("if(!confirm(text))return;"));
assert(explicitReset.includes("pendingOpenedSet.clear()"));
assert(rendered>=2 && dashboard>=1);
console.log("GRANADA Pending unlock: active cohort canceled, visited marks durable, new Focus unique, separate explicit reset PASS");
