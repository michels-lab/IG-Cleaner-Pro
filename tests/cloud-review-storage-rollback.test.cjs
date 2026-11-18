"use strict";
// GRANADA #360: cloud reviews only alter the visible in-memory state if
// their durable localStorage snapshot committed; mid-write quota must roll back.
const assert=require("node:assert/strict"),fs=require("node:fs"),
 path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Production cloud sync script is required");
const begin=script.indexOf("async function pullProfileState(){");
const end=script.indexOf("// Double Check cycle",begin);
assert(begin>=0&&end>begin,"Production pullProfileState body is required");
const keys={done:"done",protected:"protected",reviewed:"reviewed",pending:"pending",opened:"opened"};
const saved=new Map([
 [keys.done,'["old"]'],[keys.protected,'["protected.old"]'],
 [keys.reviewed,JSON.stringify({old:{reviewedAt:1}})],
 [keys.pending,JSON.stringify({pendingold:{reviewedAt:1}})],
 [keys.opened,'["pendingold"]']
]);
const initial=Object.fromEntries(saved);
let writes=0,failAt=3,rendered=0;
const ctx={
 Date,Set,Map,JSON,String,Number,Object,Error,console,
 LS_DONE:keys.done,LS_PROT:keys.protected,
 LS_REVIEW_META:keys.reviewed,LS_PENDING_REVIEW_META:keys.pending,
 LS_PENDING_OPENED:keys.opened,
 doneSet:new Set(["old"]),protectedSet:new Set(["protected.old"]),
 reviewedMeta:{old:{reviewedAt:1}},
 pendingReviewedMeta:{pendingold:{reviewedAt:1}},
 pendingOpenedSet:new Set(["pendingold"]),
 S:{stats:{}},
 localStorage:{
   getItem:k=>saved.has(k)?saved.get(k):null,
   setItem(k,v){
     writes++;
     if(failAt===writes){const e=Error("QuotaExceededError");e.name="QuotaExceededError";throw e;}
     saved.set(k,v)
   },
   removeItem:k=>saved.delete(k)
 },
 readCompleteProfileState:async(_fields,options)=>{
   assert.equal(options.fresh,true,"Hydration must not trust cached cloud reviews");
   return [{username:"newreview",module:"main"},{username:"newpending",module:"pending"}];
 },
 buildRows:()=>rendered++,applyFilters(){},renderAll(){},
 renderPendingRequests(){},renderFollowersMutualTab(){},renderFollowersAllWorkspace(){}
};
ctx.applyOneState=r=>{
 if(r.module==="main"){
   ctx.doneSet.add(r.username);ctx.protectedSet.add(r.username);
   ctx.reviewedMeta[r.username]={reviewedAt:1000};return true;
 }
 ctx.pendingReviewedMeta[r.username]={reviewedAt:1000};
 ctx.pendingOpenedSet.add(r.username);return true;
};
vm.createContext(ctx);
vm.runInContext(script.slice(begin,end),ctx);
(async()=>{
  const doneReference=ctx.doneSet,metaReference=ctx.reviewedMeta;
  await assert.rejects(ctx.pullProfileState(),/No se guardaron las revisiones sincronizadas/,
    "Quota halfway through 5 writes must not be silently ignored");
  assert.equal(ctx.doneSet,doneReference,"Canonical review set identity is preserved");
  assert.equal(ctx.reviewedMeta,metaReference,"Canonical review metadata identity is preserved");
  assert.deepEqual([...ctx.doneSet],["old"]);
  assert.deepEqual([...ctx.protectedSet],["protected.old"]);
  assert.deepEqual(Object.keys(ctx.reviewedMeta),["old"]);
  assert.deepEqual(Object.keys(ctx.pendingReviewedMeta),["pendingold"]);
  assert.deepEqual([...ctx.pendingOpenedSet],["pendingold"]);
  assert.deepEqual(Object.fromEntries(saved),initial,
    "Previously durable five keys must be restored if one write is rejected");
  assert.equal(ctx.S.stats.statesDown,undefined,
    "Failed cloud reconciliation must not advertise a completed download");
  assert.equal(rendered,0,"Don't display phantom Review/Pending changes");
  writes=0;failAt=0;
  const result=await ctx.pullProfileState();
  assert.deepEqual(JSON.parse(JSON.stringify(result)),{rows:2,changed:2});
  assert.equal(ctx.doneSet,doneReference);
  assert.equal(ctx.reviewedMeta,metaReference);
  assert(ctx.doneSet.has("newreview"));
  assert(ctx.pendingOpenedSet.has("newpending"));
  assert.deepEqual(JSON.parse(saved.get(keys.done)).sort(),["newreview","old"]);
  assert.equal(JSON.parse(saved.get(keys.pending)).newpending.reviewedAt,1000);
  assert.equal(ctx.S.stats.statesDown,2);
  assert.equal(rendered,1);
  console.log("PASS: cloud review storage failure rolls back RAM and disk; success persists both");
})().catch(e=>{console.error(e);process.exitCode=1});
