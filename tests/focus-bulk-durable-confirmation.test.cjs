"use strict";
// GRANADA P0 #360/#371: exercise production bulk-review codec and BOTH HTML
// entrypoints with simulated quota, second-key failure, dual owner profiles,
// 30 confirmed users, 789 prior Reviewed and legacy modal callbacks.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

for(const entry of [
  "desktop/ig_cleaner_pro_v120_27_synced_companion.html",
  "index.html"
]){
  const html=fs.readFileSync(path.join(__dirname,"..",entry),"utf8");
  function extract(from,to){
    const a=html.indexOf(from),b=html.indexOf(to,a+from.length);
    assert(a>=0&&b>a,entry+": missing "+from);
    return html.slice(a,b);
  }
  // Under test: real production transactional helper, not a test copy.
  const helpers=extract("function igcCommitFocusDecision(","function confirmSafeFocusReviewed(){");
  const markedExtra=extract("function markExtraFocusNotReviewed(){","function confirmExtraFocusReviewed(");
  const confirmed=extract("function confirmSafeFocusReviewed(){","function snoozeSafeFocusBatch(");
  let active="A",failKey="",throwOnGet=false;
  const raw=new Map(),warnings=[],sync=[];
  const fullKey=k=>active+"::"+k;
  const localStorage={
    getItem(k){if(throwOnGet)throw Error("denied");return raw.get(fullKey(k))??null},
    setItem(k,v){
      if(k===failKey){const e=Error("quota");e.name="QuotaExceededError";throw e}
      raw.set(fullKey(k),String(v));
    },
    removeItem(k){raw.delete(fullKey(k))}
  };
  let cleared=0,hidden=0;
  const state={
    Date,Math,Array,Set,JSON,Map,console,
    localStorage,window:{igcQueueStateSync:k=>sync.push(k)},
    LS_REVIEW_META:"review-meta",LS_DONE:"done",LS_PROT:"protected",
    LS_PENDING_REVIEW_META:"pending-meta",LS_PENDING_OPENED:"pending-opened",
    reviewedMeta:{older:{reviewedAt:777}},doneSet:new Set(["older"]),
    protectedSet:new Set(["protected.old"]),pendingReviewedMeta:{},
    pendingOpenedSet:new Set(),activeFocusBatch:null,activeExtraReviewBatch:null,
    currentMode:"following",
    makeReviewMeta:(row,decision,source)=>({mode:"following",reviewedAt:Date.now(),
      relation:"no",followsBack:false,isFollower:false,reviewReason:decision,reviewSource:source}),
    msg:(s,t)=>warnings.push({s,t}),recordRowsHistory:()=>{},
    confirm:()=>true,pendingDecisionLabel:x=>x,
    document:{getElementById:()=>({value:"reviewed"})},
    clearActiveFocusBatch:()=>{cleared++;state.activeFocusBatch=null;state.activeExtraReviewBatch=null},
    forceClearStuckFocusBatch:()=>{},closeExtraFocusModal:()=>{hidden++},
    closeSafeFocusPopup:()=>{hidden++},closeFocusDialogAfterDecision:()=>{hidden++},
    renderPendingRequests:()=>{},buildRows:()=>{},applyFilters:()=>{},
    renderFollowersAllWorkspace:()=>{},renderFollowersMutualTab:()=>{},
    renderModuleDashboard:()=>{},cleanupResolvedActiveBatch:()=>{},
    renderActiveBatchDock:()=>{},forceLiveRefresh:()=>{},
    logAction:()=>{},maybeContinueGuidedSession:()=>{}
  };
  vm.createContext(state);
  vm.runInContext(helpers,state);
  vm.runInContext(confirmed,state);
  function seed(){
    raw.set(fullKey("review-meta"),JSON.stringify(state.reviewedMeta));
    raw.set(fullKey("done"),JSON.stringify([...state.doneSet]));
    raw.set(fullKey("protected"),JSON.stringify([...state.protectedSet]));
    raw.set(fullKey("pending-meta"),JSON.stringify(state.pendingReviewedMeta));
    raw.set(fullKey("pending-opened"),JSON.stringify([...state.pendingOpenedSet]));
  }
  seed();
  const rows=Array.from({length:30},(_,n)=>({username:"target."+n,riskScore:n,riskLevel:"alto"}));
  const batch={kind:"main",label:"Focus 30",rows};
  state.activeFocusBatch=batch;state.activeExtraReviewBatch=batch;
  const before=Object.fromEntries([...raw].filter(([k])=>k.startsWith("A::")));
  failKey="done";
  assert.equal(state.confirmSafeFocusReviewed(),false,entry+": failure must not announce confirmation");
  assert.equal(cleared,0,entry+": never clear cohort on failed second write");
  assert.equal(hidden,0,entry+": never close modal on failed persistence");
  assert.deepEqual(Object.fromEntries([...raw].filter(([k])=>k.startsWith("A::"))),before,
    entry+": second-write rejection restores every durable byte");
  assert.equal(state.doneSet.size,1);
  assert.equal(Object.keys(state.reviewedMeta).length,1);
  assert.equal(sync.length,0);
  failKey="";
  assert.equal(state.confirmSafeFocusReviewed(),true,entry+": retry successfully commits exact 30");
  assert.equal(state.doneSet.size,31);
  assert.equal(JSON.parse(raw.get("A::done")).length,31);
  assert.equal(Object.keys(JSON.parse(raw.get("A::review-meta"))).length,31);
  assert.equal(cleared,1);
  assert.equal(sync.length,1);
  assert.equal(state.reviewedMeta["target.0"].mode,"following");
  assert.equal(state.reviewedMeta["target.0"].iFollow,true);
  // Genuine new B user may add to B without causing a rebound in A.
  active="B";state.doneSet=new Set();state.reviewedMeta={};
  state.protectedSet=new Set();seed();
  assert.equal(state.igcCommitFocusDecision({kind:"main",rows:[{username:"b.user"}],label:"B"},"reviewed"),true);
  assert.deepEqual(JSON.parse(raw.get("B::done")),["b.user"]);
  assert.equal(JSON.parse(raw.get("A::done")).length,31,"Switch A-B-A must preserve previous 30 reviews");
  active="A";
  state.doneSet=new Set(JSON.parse(raw.get("A::done")));
  state.reviewedMeta=JSON.parse(raw.get("A::review-meta"));
  state.protectedSet=new Set(JSON.parse(raw.get("A::protected")));
  // Keep on mutual must add protections ONLY if all three keys commit.
  const mutual={kind:"mutual",rows:[{username:"mutual.new"}],label:"Mutuals"};
  const prior=[...raw];
  failKey="protected";
  assert.equal(state.igcCommitFocusDecision(mutual,"keep"),false);
  assert.deepEqual([...raw],prior,"Third-key protection rejection must restore meta+done");
  assert(!state.doneSet.has("mutual.new"));
  assert(!state.protectedSet.has("mutual.new"));
  failKey="";
  assert.equal(state.igcCommitFocusDecision(mutual,"keep"),true);
  assert(state.protectedSet.has("mutual.new"));
  assert.deepEqual(JSON.parse(raw.get("A::protected")).sort(),["mutual.new","protected.old"]);
  // Pending double-check must archive earlier verdict and never partially
  // write reviewed metadata if its opened ledger is full.
  state.pendingReviewedMeta={"pending.old":{reviewedAt:11,decision:"keep",label:"old"}};
  state.pendingOpenedSet=new Set(["pending.old"]);seed();
  const pending={kind:"pending",reviewMode:"double",rows:[{username:"pending.old",riskScore:4},
    {username:"pending.new",riskScore:2}],label:"Pending Double Check"};
  const priorPendingMeta=raw.get("A::pending-meta"),priorOpened=raw.get("A::pending-opened");
  failKey="pending-opened";
  assert.equal(state.igcCommitFocusDecision(pending,"reviewed"),false);
  assert.equal(raw.get("A::pending-meta"),priorPendingMeta);
  assert.equal(raw.get("A::pending-opened"),priorOpened);
  assert.equal(state.pendingReviewedMeta["pending.old"].decision,"keep");
  failKey="";
  assert.equal(state.igcCommitFocusDecision(pending,"reviewed"),true);
  const saved=JSON.parse(raw.get("A::pending-meta"));
  assert.equal(saved["pending.old"].previousReviews[0].decision,"keep");
  assert.equal(saved["pending.new"].reviewSource,"pending_double_check");
  assert.deepEqual(JSON.parse(raw.get("A::pending-opened")).sort(),["pending.new","pending.old"]);
  // Legacy "Couldn't review yet" must not ERASE prior reviewed/follow decisions.
  state.pendingOpenedSet.add("fresh.unreviewed");
  state.pendingReviewedMeta["pending.old"]={reviewedAt:99,decision:"keep"};
  const decisionBefore=JSON.stringify(state.pendingReviewedMeta);
  state.igcCommitFocusUnconfirmed({kind:"pending",label:"Focus",rows:[
    {username:"pending.old"},{username:"fresh.unreviewed"}]});
  assert.equal(JSON.stringify(state.pendingReviewedMeta),decisionBefore);
  assert(state.pendingOpenedSet.has("pending.old"));
  assert(!state.pendingOpenedSet.has("fresh.unreviewed"));
  // The older extra Focus dialog delegates, never reimplements destructive deletions.
  vm.runInContext(markedExtra,state);
  let delegated=0;
  state.markSafeFocusNotReviewed=()=>{delegated++;return true};
  state.activeExtraReviewBatch=mutual;
  assert.equal(state.markExtraFocusNotReviewed(),true);
  assert.equal(delegated,1);
  // A denied read is as safe as a denied write: no false change to RAM.
  throwOnGet=true;
  const beforeDone=JSON.stringify([...state.doneSet]);
  assert.equal(state.igcCommitFocusDecision({kind:"main",rows:[{username:"fail.read"}]},"reviewed"),false);
  assert.equal(JSON.stringify([...state.doneSet]),beforeDone);
  throwOnGet=false;
  assert(warnings.some(x=>x.s.includes("NO confirmé")));
  console.log("PASS "+entry+": 30-person atomic Focus commit, A-B-A, Pending double, protected, denial and legacy no-undo");
}
