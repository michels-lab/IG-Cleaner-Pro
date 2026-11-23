"use strict";
// GRANADA #371: lossless near-quota fallback, not a UI-only clamp or deletion.
// The real production codec is evaluated in an isolated browser-like VM.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const begin=html.indexOf("function safeBatchRow("),end=html.indexOf("function activeBatchUserSet(",begin);
assert(begin>=0&&end>begin,"Focus codec source missing");
const storage=new Map([["reviewed","R".repeat(12500)],["pending","P".repeat(7000)]]);
let cap=Infinity, errorKind="quota";
const localStorage={
 getItem:key=>storage.get(key)||null,
 removeItem:key=>storage.delete(key),
 setItem(key,value){
   if(errorKind==="security"){const e=Error("Browser storage denied");e.name="SecurityError";throw e}
   const total=[...storage].filter(([k])=>k!==key).reduce((n,[k,v])=>n+k.length+v.length,0);
   if(total+key.length+value.length>cap){const e=Error("Storage quota exceeded");e.name="QuotaExceededError";throw e}
   storage.set(key,value);
 }
};
const ctx={JSON,Array,Set,Number,Math,Date,console,localStorage,window:{},
 LS_ACTIVE_FOCUS_BATCH:"focus-cohort",activeFocusBatch:null};
vm.createContext(ctx);vm.runInContext(html.slice(begin,end),ctx);
// The diagnostic helper is defined *after* activeBatchUserSet in production.
// Load that real function separately, rather than pretending it is in the codec slice.
const diagStart=html.indexOf("function igcFocusStorageDiagnostic(");
const diagEnd=html.indexOf("function setActiveFocusBatch(",diagStart);
assert(diagStart>=0&&diagEnd>diagStart,"Production Focus diagnostic source missing");
vm.runInContext(html.slice(diagStart,diagEnd),ctx);
const rows=Array.from({length:30},(_,i)=>({
 username:"member."+i,
 href:"https://www.instagram.com/member."+i+"/",
 name:"Member "+i,relation:"not_following_back",riskScore:i,riskLevel:"high",
 riskReasons:["suspicious","no_followback"],timestamp:123456+i,dateMain:100,dateOther:101,
 iFollow:true,isFollower:i%2===0,followsBack:i%3===0,relationGood:i%4===0
}));
const batch={kind:"main",label:"Focus 30",openedAt:1234,status:"opened_unconfirmed",rows:rows.map(r=>ctx.safeBatchRow(r))};
// URL edge cases matter: never synthesize a link for an absent or empty
// original href. A custom URL must not be replaced by a guess.
batch.rows[1].href=undefined;
batch.rows[2].href='';
batch.rows[3].href='https://www.instagram.com/member.3/?from=import';
batch.rows[4].href=null;
batch.rows[5].riskReasons='legacy-risk-note';
const original=JSON.parse(JSON.stringify(batch));
const regular=JSON.stringify(ctx.igcEncodeActiveFocusBatch(batch));
const small=JSON.stringify(ctx.igcEncodeFocusBatchQuota(batch));
assert(small.length<regular.length*0.80,"Fallback must materially reduce quota use");
const baseline=[...storage].reduce((n,[k,v])=>n+k.length+v.length,0);
cap=baseline+"focus-cohort".length+small.length+3;
ctx.activeFocusBatch=batch;ctx.saveActiveFocusBatch();
assert.equal(JSON.parse(storage.get("focus-cohort")).storageFormat,3,
 "Realistic near-quota save uses the second encoding, not a false save");
ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),original,
 "Version 3 must losslessly restore all 30 rows, owners, flags and histories");
assert.equal(storage.get("reviewed"),"R".repeat(12500));
assert.equal(storage.get("pending"),"P".repeat(7000));
const previous=storage.get("focus-cohort");
cap=1;ctx.activeFocusBatch={...batch,openedAt:4567};
let rejectedQuota;
assert.throws(()=>ctx.saveActiveFocusBatch(),e=>{rejectedQuota=e;return /quota/i.test(String(e.name))},
 "A truly full browser must fail closed rather than invent a Focus review");
assert.equal(storage.get("focus-cohort"),previous,"Failed save preserves older durable batch");
// New failure-path regression must reveal the actual failed v4 payload, not
// only the larger v2 estimation; reporting values/usernames is forbidden.
const quotaReport=ctx.igcFocusStorageDiagnostic(rejectedQuota,ctx.activeFocusBatch);
assert.match(quotaReport,/key focus-cohort/,"Report fixed failing storage key");
assert.match(quotaReport,/format v4/,"Final rejected compact encoding must be identified");
assert.match(quotaReport,/attempted [1-9][0-9]* bytes/,"Report exact attempted write size");
assert(!quotaReport.includes("member.")&&!quotaReport.includes("https:"),
 "Never export private usernames or stored URLs through the diagnostic");
assert.equal(ctx.window.igcFocusWriteAttempt.format,"v4");
errorKind="security";cap=Infinity;
let rejectedSecurity;
assert.throws(()=>ctx.saveActiveFocusBatch(),e=>{rejectedSecurity=e;return e.name==="SecurityError"},
 "SecurityError is never treated as quota or bypassed");
assert.equal(storage.get("focus-cohort"),previous);
const securityReport=ctx.igcFocusStorageDiagnostic(rejectedSecurity,ctx.activeFocusBatch);
assert.match(securityReport,/format v2/,"Denied storage must never pretend fallback was tried");
assert(!securityReport.includes("Browser storage denied"),"Raw provider messages may leak sensitive data");
errorKind="quota";cap=Infinity;
ctx.saveActiveFocusBatch();
assert.equal(ctx.window.igcFocusWriteAttempt,null,"Successful retry clears stale diagnostics");
assert.equal(ctx.window.igcLastFocusStorageError,"","Successful retry clears stale storage warning");
storage.set("focus-cohort",JSON.stringify({...ctx.igcEncodeFocusBatchQuota(batch),rows:[["bad",0]]}));
ctx.activeFocusBatch=null;
ctx.loadActiveFocusBatch();
assert.equal(ctx.activeFocusBatch,null,"Malformed v3 must not produce fake reviewed targets");
storage.set("focus-cohort",previous);ctx.loadActiveFocusBatch();
assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),original,
 "Recoverable previous v3 storage must still reload after malformed data was repaired");
console.log("PASS: 30 Focus profiles, lossless quota fallback, reviewed/Pending preservation, storage denial and invalid data fail-closed");


// Pruning a recovered cohort must be transactional too: the UI must NOT
// discard rows in memory when the saved cohort could not be updated.
const pruneStart=html.indexOf("function pruneResolvedActiveFocusBatch(");
const pruneEnd=html.indexOf("function forceClearStuckFocusBatch(",pruneStart);
assert(pruneStart>=0&&pruneEnd>pruneStart,"Production Focus prune function missing");
let failPruneWrite=true,failPruneRemove=false;
const durable=new Map([["focus-cohort","previous durable cohort"]]);
const initialPrune={kind:"main",rows:[{username:"done"},{username:"untouched"}]};
const pruneCtx={
 console,
 LS_ACTIVE_FOCUS_BATCH:"focus-cohort",
 activeFocusBatch:initialPrune,
 activeExtraReviewBatch:initialPrune,
 activeBatchRowResolved:row=>row.username==="done",
 localStorage:{
   removeItem(key){if(failPruneRemove)throw Error("Storage denied");durable.delete(key)}
 },
 saveActiveFocusBatch(){
   if(failPruneWrite)throw Error("QuotaExceededError");
   durable.set("focus-cohort",JSON.stringify(pruneCtx.activeFocusBatch));
 }
};
vm.createContext(pruneCtx);
vm.runInContext(html.slice(pruneStart,pruneEnd),pruneCtx);
assert.equal(pruneCtx.pruneResolvedActiveFocusBatch(),false,
 "Durable pruning must roll back after rejected storage write");
assert.equal(pruneCtx.activeFocusBatch,initialPrune,
 "Failed prune must keep the exact previous in-memory cohort");
assert.equal(pruneCtx.activeExtraReviewBatch,initialPrune,
 "Failed prune must not make recovery display a different cohort");
assert.equal(durable.get("focus-cohort"),"previous durable cohort",
 "Failed write cannot erase the older saved cohort");
failPruneWrite=false;
assert.equal(pruneCtx.pruneResolvedActiveFocusBatch(),true);
assert.deepEqual([...pruneCtx.activeFocusBatch.rows].map(r=>r.username),["untouched"]);
assert.deepEqual(JSON.parse(durable.get("focus-cohort")).rows.map(r=>r.username),["untouched"]);
pruneCtx.activeBatchRowResolved=()=>true;
const savedAfterPrune=pruneCtx.activeFocusBatch;
failPruneRemove=true;
assert.equal(pruneCtx.pruneResolvedActiveFocusBatch(),false,
 "Storage removal denial must not claim the cohort was cleared");
assert.equal(pruneCtx.activeFocusBatch,savedAfterPrune);
assert.equal(pruneCtx.activeExtraReviewBatch,savedAfterPrune);
assert(durable.has("focus-cohort"));
failPruneRemove=false;
assert.equal(pruneCtx.pruneResolvedActiveFocusBatch(),true);
assert.equal(pruneCtx.activeFocusBatch,null);
assert.equal(pruneCtx.activeExtraReviewBatch,null);
assert(!durable.has("focus-cohort"),"Resolved persisted cohort must be removed");
console.log("PASS: Focus recovered-cohort pruning is durable on both write and remove failures");


// A user/robot decision clearing a cohort has the same durability contract:
// one successful disk deletion, THEN the two in-memory references are cleared.
const clearStart=html.indexOf("function clearActiveFocusBatch(");
const clearEnd=html.indexOf("function activeBatchRowResolved(",clearStart);
assert(clearStart>=0&&clearEnd>clearStart,"Production Focus clear function missing");
let failClear=true,clearAttempts=0,renderCount=0;
const clearSaved=new Map([["focus-cohort","must survive failed delete"]]);
const originalClear={kind:"pending",rows:[{username:"still-unreviewed"}]};
const clearCtx={
 LS_ACTIVE_FOCUS_BATCH:"focus-cohort",
 activeFocusBatch:originalClear,
 activeExtraReviewBatch:originalClear,
 localStorage:{
   removeItem(key){
     clearAttempts++;
     if(failClear)throw Error("SecurityError");
     clearSaved.delete(key);
   }
 },
 renderActiveBatchDock(){renderCount++}
};
vm.createContext(clearCtx);
vm.runInContext(html.slice(clearStart,clearEnd),clearCtx);
assert.throws(()=>clearCtx.clearActiveFocusBatch(),/SecurityError/,
 "A rejected delete must be reported rather than hiding a still-persisted batch");
assert.equal(clearCtx.activeFocusBatch,originalClear);
assert.equal(clearCtx.activeExtraReviewBatch,originalClear);
assert(clearSaved.has("focus-cohort"));
assert.equal(renderCount,0,"Do not redraw an uncommitted batch deletion");
failClear=false;
clearCtx.clearActiveFocusBatch();
assert.equal(clearAttempts,2,"Each clear attempt performs exactly one storage delete");
assert.equal(clearCtx.activeFocusBatch,null);
assert.equal(clearCtx.activeExtraReviewBatch,null);
assert(!clearSaved.has("focus-cohort"));
assert.equal(renderCount,1);
console.log("PASS: Focus clearing waits for durable deletion and never silently drops the prior cohort");
