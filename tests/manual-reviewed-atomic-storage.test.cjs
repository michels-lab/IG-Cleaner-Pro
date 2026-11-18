"use strict";
// GRANADA #360: real manual Reviewed commit and confirmation popup must be
// durable before advancing UI, statistics, and per-profile review ledgers.
const assert=require("node:assert/strict"),fs=require("node:fs"),
 path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function source(from,to){
 const start=html.indexOf(from),end=html.indexOf(to,start+from.length);
 assert(start>=0&&end>start,"Missing production source "+from);
 return html.slice(start,end);
}
const saved=new Map([["done",'["historic"]'],["meta",JSON.stringify({historic:{reviewedAt:17}})]]);
const oldSaved=Object.fromEntries(saved);
const originalMeta={historic:{reviewedAt:17}};
const msgs=[],stats={reviewed:0,reviewedGood:0,reviewedBad:0};
let attempts=0,failAt=2,queued=0,closed=0,rendered=0,recorded=0;
const rows=Array.from({length:30},(_,i)=>({username:"person"+i,relation:"No me sigue",relationGood:false}));
const ctx={
 Date,Set,Map,Object,JSON,Error,String,console,
 doneSet:new Set(["historic"]),reviewedMeta:{...originalMeta},
 LS_DONE:"done",LS_REVIEW_META:"meta",
 localStorage:{
  getItem:k=>saved.has(k)?saved.get(k):null,
  setItem(k,v){
   attempts++;
   if(attempts===failAt){const e=Error("QuotaExceededError");e.name="QuotaExceededError";throw e;}
   saved.set(k,v);
  },
  removeItem:k=>saved.delete(k)
 },
 window:{igcQueueStateSync:()=>queued++},
 msg:(message,kind)=>msgs.push({message,kind}),
 lastOpenedBatch:rows.map(r=>r.username),
 lastOpenedBatchMeta:{source:"focus",label:"Focus",count:30},
 lastVerifiedBatchForUndo:[],
 document:{getElementById:()=>({value:"reviewed"})},
 rowByUsername:username=>rows.find(r=>r.username===username),
 isDoneValid:row=>ctx.doneSet.has(row.username),
 makeReviewMeta:(row,reason,origin)=>({reviewedAt:123,mode:"following",reason,origin}),
 contextLabel:ctx=>ctx.label,
 sessionStats:stats,
 selected:new Set(rows.map(r=>r.username)),
 relationLabels:()=>({badShort:"bad",goodShort:"good"}),
 logAction:()=>recorded++,
 closeVerifyPopup(clear){closed++;if(clear)ctx.lastOpenedBatch=[]},
 renderAll:()=>rendered++,
 forceLiveRefresh(){}
};
vm.createContext(ctx);
vm.runInContext(source("function saveReviewedState(mutate){","function clearHiddenSelection(){"),ctx);
vm.runInContext(source("function confirmOpenedVerified(){","// =====================================================================\n// MODO FOCO 20/30/40"),ctx);
const doneReference=ctx.doneSet,metaReference=ctx.reviewedMeta;
assert.equal(ctx.confirmOpenedVerified(),undefined);
assert.equal(queued,0,"Rejected writes must not initiate cloud push");
assert.equal(closed,0,"Rejected Reviewed write must preserve open confirmation popup");
assert.equal(rendered,0,"Never render a phantom completed batch");
assert.equal(recorded,0,"No successful action log before commit");
assert.equal(stats.reviewed,0,"No false +30 reviews in session counters");
assert.equal(ctx.lastOpenedBatch.length,30,"The original cohort stays available for retry");
assert.deepEqual([...ctx.doneSet],["historic"]);
assert.deepEqual(Object.keys(ctx.reviewedMeta),["historic"]);
assert.deepEqual(Object.fromEntries(saved),oldSaved,"Second-key failure rolls back first write");
assert.equal(ctx.doneSet,doneReference,"Keep the canonical review Set reference");
assert.equal(ctx.reviewedMeta,metaReference,"Keep the canonical metadata reference");
assert(msgs.some(m=>m.kind==="w"&&m.message.includes("historial anterior")),
 "User must see a truthful storage warning instead of a success message");
attempts=0;failAt=0;
ctx.confirmOpenedVerified();
assert.equal(ctx.doneSet.size,31,"Exactly 30 confirmed profiles plus prior history");
assert.equal(Object.keys(ctx.reviewedMeta).length,31);
assert.equal(JSON.parse(saved.get("done")).length,31,"All 30 confirmed reviews persisted");
assert.equal(Object.keys(JSON.parse(saved.get("meta"))).length,31);
assert.equal(queued,1,"Cloud sync runs only after the two keys are durable");
assert.equal(closed,1,"The confirmation popup closes only after durable success");
assert.equal(rendered,1);
assert.equal(recorded,1);
assert.equal(stats.reviewed,30);
assert.equal(ctx.lastOpenedBatch.length,0);
assert.equal(ctx.doneSet,doneReference);
assert.equal(ctx.reviewedMeta,metaReference);
// Storage-denied read: never start any mutation or queue a sync.
const preceding=JSON.stringify(Object.fromEntries(saved));
ctx.lastOpenedBatch=["another"];
const firstGet=ctx.localStorage.getItem;
ctx.localStorage.getItem=()=>{throw Error("SecurityError")};
ctx.confirmOpenedVerified();
ctx.localStorage.getItem=firstGet;
assert.equal(JSON.stringify(Object.fromEntries(saved)),preceding);
assert.equal(queued,1);assert.equal(closed,1);assert.equal(stats.reviewed,30);
console.log("PASS: 30 Reviewed confirmations survive quota/retry; never inflate counts or close popup on failures");
