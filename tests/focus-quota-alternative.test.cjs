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
const ctx={JSON,Array,Set,Number,Math,Date,console,localStorage,
 LS_ACTIVE_FOCUS_BATCH:"focus-cohort",activeFocusBatch:null};
vm.createContext(ctx);vm.runInContext(html.slice(begin,end),ctx);
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
assert.throws(()=>ctx.saveActiveFocusBatch(),/quota/i,
 "A truly full browser must fail closed rather than invent a Focus review");
assert.equal(storage.get("focus-cohort"),previous,"Failed save preserves older durable batch");
errorKind="security";cap=Infinity;
assert.throws(()=>ctx.saveActiveFocusBatch(),e=>e.name==="SecurityError",
 "SecurityError is never treated as quota or bypassed");
assert.equal(storage.get("focus-cohort"),previous);
errorKind="quota";cap=Infinity;
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
   durable.set("focus-cohort",JSON.stringify(this.activeFocusBatch));
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
assert.deepEqual(pruneCtx.activeFocusBatch.rows.map(r=>r.username),["untouched"]);
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
