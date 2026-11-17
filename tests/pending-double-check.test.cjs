"use strict";
/* Pending Double Check: a second pass must NEVER clear original decisions. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function extract(start,end){
 const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
 assert(a>=0&&b>a,"Production function missing: "+start);
 return html.slice(a,b);
}
for(const token of [
 'id="pendingDoubleCheckStats"','onclick="igcPendingDoubleCheckAll()"',
 'onclick="igcPendingDoubleCheckSelected()"','onclick="igcPendingDoubleResetCycle()"',
 'function igcPendingDoubleCheckOne(username)','function igcPendingDoubleToggleSelected(username,checked)',
 'igcPendingDoubleSelected.has(r.username)','igcPendingDoubleSeen().has(r.username)',
 "activeFocusBatch.reviewMode='double'","pendingReviewedMeta[r.username]",
 "if(b.reviewMode==='double')"
]) assert(html.includes(token),"Missing real UI/state contract: "+token);
const store=new Map(),messages=[],opened=[],events=[],data={
 A:Array.from({length:45},(_,i)=>"request"+String(i+1).padStart(2,"0")),
 B:["separate01","separate02"]
},metadata={
 A:Object.fromEntries(data.A.map(u=>[u,{reviewedAt:100,decision:"still_pending",label:"first-review"}])),
 B:Object.fromEntries(data.B.map(u=>[u,{reviewedAt:100,decision:"reviewed",label:"other"}]))
};
const oldA=JSON.stringify(metadata.A),oldB=JSON.stringify(metadata.B);
let account="A", allow=true,qualityChecks=0,saves=0;
const ctx={
 console,Map,Set,Array,Object,Date,Number,String,Math,JSON,encodeURIComponent,
 cleanUsername:u=>String(u||"").toLowerCase().trim(),
 localStorage:{
  getItem:key=>store.get(account+"::"+key)||null,
  setItem:(key,value)=>store.set(account+"::"+key,String(value)),
  removeItem:key=>store.delete(account+"::"+key)
 },
 IGC_INSTAGRAM_PROFILES:{active:"A"},
 pendingRows:()=>data[account].map(u=>({
  username:u,href:"https://www.instagram.com/"+u+"/",
  reviewed:!!metadata[account][u]?.reviewedAt,snoozed:false,riskScore:0,riskLevel:"bajo"
 })),
 pendingOldestFirstSort:(a,b)=>a.username.localeCompare(b.username),
 activeFocusBatch:null,activeExtraReviewBatch:null,pendingReviewedMeta:metadata.A,
 pendingSnoozeMap:{},pendingOpenedSet:new Set(data.A),
 document:{getElementById:id=>({value:"still_pending"})},
 msg:(message,level)=>messages.push({message,level}),
 confirm:()=>allow,
 igcConfirmBatchQuality:()=>{qualityChecks++;return allow},
 setActiveFocusBatch(kind,rows,label){
  ctx.activeFocusBatch={kind,rows:rows.map(r=>({...r})),label,openedAt:Date.now(),status:"opened_unconfirmed"};
  ctx.activeExtraReviewBatch=ctx.activeFocusBatch;
 },
 saveActiveFocusBatch:()=>{store.set(account+"::active",JSON.stringify(ctx.activeFocusBatch));saves++},
 showSafeFocusPopup:()=>assert.equal(ctx.activeBatchRowResolved(ctx.activeFocusBatch.rows[0],"pending"),false,
  "Original review cannot auto-close a second review"),
 logAction:(type,message,details)=>events.push({type,message,details}),
 renderPendingRequests:()=>{},renderModuleDashboard:()=>{},
 closeSafeFocusPopup:()=>{},closeExtraFocusModal:()=>{},closeFocusDialogAfterDecision:()=>{},
 savePendingReviewedMeta:()=>{},savePendingOpened:()=>{},saveProfileHistory:()=>{},
 recordProfileHistory:(u,event,details)=>events.push({u,event,details}),
 clearActiveFocusBatch:()=>{ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null},
 cleanupResolvedActiveBatch:()=>{},renderActiveBatchDock:()=>{},
 forceLiveRefresh:()=>{},maybeContinueGuidedSession:()=>{},
};
ctx.window=ctx;ctx.window.open=url=>{opened.push({account,url});return null};
vm.createContext(ctx);
vm.runInContext(extract("function activeBatchRowResolved(row,kind){","function pruneResolvedActiveFocusBatch(){"),ctx);
vm.runInContext(extract("const IGC_PENDING_DOUBLE_SEEN=","function pendingCandidateRows(){"),ctx);
assert.equal(ctx.igcPendingDoubleRows().length,45);
assert.equal(ctx.igcPendingDoubleCheckAll(),true);
assert.equal(ctx.activeFocusBatch.kind,"pending");
assert.equal(ctx.activeFocusBatch.reviewMode,"double");
assert.equal(ctx.activeFocusBatch.rows.length,30);
assert.equal(ctx.igcPendingDoubleRows().length,15);
assert.equal(opened.length,30);
assert.equal(JSON.stringify(metadata.A),oldA,"Opening second round must never modify first reviews");
assert.equal(ctx.activeBatchRowResolved({username:"request01"},"pending"),false);
assert.equal(JSON.parse(store.get("A::active")).reviewMode,"double","Batch recoverable after reload");
// Cannot launch a second batch over an unconfirmed batch.
assert.equal(ctx.igcPendingDoubleCheckAll(),false);
assert.equal(ctx.igcPendingDoubleRows().length,15);
const snapshot=JSON.stringify(metadata.A), openedLedger=[...ctx.pendingOpenedSet];
vm.runInContext(extract("function markSafeFocusNotReviewed(){","function confirmSafeFocusReviewed(){"),ctx);
ctx.markSafeFocusNotReviewed();
assert.equal(JSON.stringify(metadata.A),snapshot,"Unconfirmed second round cannot erase review");
assert.deepEqual([...ctx.pendingOpenedSet],openedLedger,"Unconfirmed second round cannot erase opened ledger");
assert.equal(ctx.igcPendingDoubleCheckAll(),true);
assert.equal(ctx.activeFocusBatch.rows.length,15);
assert.equal(opened.length,45,"Second 15 complete same 45-person cycle");
assert.equal(ctx.igcPendingDoubleRows().length,0);
assert.equal(ctx.igcPendingDoubleCheckAll(),false,"Never recycle previously seen in same cycle");
// Explicit reset only after no pending batch, and never modifies prior decisions.
ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null;
allow=false;assert.equal(ctx.igcPendingDoubleResetCycle(),false);
assert.equal(ctx.igcPendingDoubleRows().length,0);
allow=true;assert.equal(ctx.igcPendingDoubleResetCycle(),true);
assert.equal(ctx.igcPendingDoubleRows().length,45);
assert.equal(JSON.stringify(metadata.A),oldA);
// Single and selected do not require wiping reviewed marks.
assert.equal(ctx.igcPendingDoubleCheckOne("request45"),true);
assert.equal(ctx.activeFocusBatch.rows.length,1);
ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null;
assert.equal(ctx.igcPendingDoubleToggleSelected("request01",true),true);
assert.equal(ctx.igcPendingDoubleToggleSelected("request02",true),true);
assert.equal(ctx.igcPendingDoubleCheckSelected(),true);
assert.deepEqual(Array.from(ctx.activeFocusBatch.rows,r=>r.username),["request01","request02"]);
// Confirm a new decision: archive old review, update only selected, keep audit event.
vm.runInContext(extract("function confirmSafeFocusReviewed(){","function snoozeSafeFocusBatch(days){"),ctx);
ctx.confirmSafeFocusReviewed();
assert.equal(metadata.A.request01.decision,"still_pending");
assert.equal(metadata.A.request01.reviewSource,"pending_double_check");
assert.equal(metadata.A.request01.previousReviews.length,1);
assert.equal(metadata.A.request01.previousReviews[0].reviewedAt,100);
assert.equal(metadata.A.request03.reviewedAt,100,"No unrelated decision may be rewritten");
assert.equal(ctx.activeFocusBatch,null);
assert(events.some(e=>e.u==="request01"&&e.event==="review"&&e.details.mode==="double_check"));
// Account A and B have independent double-cycle storage and selection.
const afterA=store.get("A::igc_pending_double_check_seen_v1");
account="B";ctx.IGC_INSTAGRAM_PROFILES.active="B";ctx.pendingReviewedMeta=metadata.B;
assert.equal(ctx.igcPendingDoubleRows().length,2);
assert.equal(ctx.igcPendingDoubleCheckSelected(),false,"A selection must not appear in B");
assert.equal(ctx.igcPendingDoubleCheckAll(),true);
assert.equal(ctx.activeFocusBatch.rows.length,2);
assert.equal(JSON.stringify(metadata.B),oldB);
ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null;
account="A";ctx.IGC_INSTAGRAM_PROFILES.active="A";ctx.pendingReviewedMeta=metadata.A;
assert.equal(store.get("A::igc_pending_double_check_seen_v1"),afterA);
assert.equal(ctx.igcPendingDoubleRows().length,42);
assert(qualityChecks>=5&&saves>=4);
console.log("PASS: Pending Double Check 45=30+15, one/selected, no-auto-resolve, crash persistence, non-destructive cancel/confirm, scoped A-B-A and explicit cycle reset");
