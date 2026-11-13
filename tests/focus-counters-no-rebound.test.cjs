"use strict";
// Regression: Focus KPI must reflect the actual openable cohort immediately,
// while Recheck deliberately retains already reviewed non-followback profiles.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function extract(from,to){
  const start=html.indexOf(from), end=html.indexOf(to,start+from.length);
  assert(start>=0&&end>start, "Missing Focus counter source: "+from);
  return html.slice(start,end);
}
const rows=[
  {username:"a",followsBack:false,relationGood:false},
  {username:"b",followsBack:false,relationGood:false},
  {username:"c",followsBack:false,relationGood:false},
  {username:"mutual",followsBack:true,relationGood:true}
];
const scoped={first:rows,second:[{username:"other",followsBack:false,relationGood:false}]};
let active="first";
const done={first:new Set(),second:new Set()};
const ctx={
  Date,Math,Set,console,
  V113:{cache:null,cacheAt:0,cacheMs:2000},
  safe:(fn,fallback)=>{try{return fn()}catch{return fallback}},
  withTempMode:(_mode,fn)=>fn(),
  buildRowsForMode:()=>scoped[active],
  pendingRows:()=>[],followersMutualRows:()=>[],
  protectedSet:new Set(),isSnoozed:()=>false,
  isDoneValidForMode:r=>done[active].has(r.username),
  isMainFocusOpenable:r=>!r.followsBack&&!r.relationGood&&!done[active].has(r.username),
  cleanUsername:u=>u
};
vm.createContext(ctx);
vm.runInContext(extract("function uniq(rows){","function tag(label,value"),ctx);
vm.runInContext(extract("function rowsFor(kind){","function stateFor(kind){"),ctx);
function counts(){
  return {
    main:ctx.rowsFor("main").length,
    recheck:ctx.rowsFor("recheck").length,
    double:ctx.rowsFor("double").length,
    reviewed:ctx.cache().noMeSigue.filter(r=>ctx.isDoneValidForMode(r,"following")).length
  };
}
assert.deepEqual(counts(),{main:3,recheck:3,double:3,reviewed:0});
done.first.add("a");
assert.deepEqual(counts(),{main:2,recheck:3,double:3,reviewed:1},
  "Reviewed confirmation must update the KPI without waiting for the 2-second cache to expire");
done.first.add("b");
assert.deepEqual(counts(),{main:1,recheck:3,double:3,reviewed:2});
active="second";
assert.deepEqual(counts(),{main:1,recheck:1,double:1,reviewed:0},
  "Switching Instagram accounts must not reuse a KPI snapshot from another account");
done.second.add("other");
assert.deepEqual(counts(),{main:0,recheck:1,double:1,reviewed:1});
active="first";
assert.deepEqual(counts(),{main:1,recheck:3,double:3,reviewed:2},
  "Returning to previous account must show its own current review state");
scoped.first.push({username:"fresh",followsBack:false,relationGood:false});
assert.deepEqual(counts(),{main:2,recheck:4,double:4,reviewed:2},
  "A genuine new import may legitimately increase availability");
// Realistic 30-person batch: confirmations must be idempotent, and rapid account
// switching/re-import must not reintroduce reviewed candidates into normal Focus.
const batch=Array.from({length:30},(_,i)=>({username:"batch."+i,followsBack:false,relationGood:false}));
scoped.first.push(...batch);
const beforeBatch=counts();
for(const r of batch)done.first.add(r.username);
assert.equal(counts().main,beforeBatch.main-30,
  "Thirty confirmed eligible reviews must remove exactly thirty normal Focus candidates");
assert.equal(counts().recheck,beforeBatch.recheck,
  "Recheck intentionally includes reviewed profiles");
assert.equal(counts().reviewed,beforeBatch.reviewed+30,
  "Thirty confirmed reviews must be counted once");
for(let i=0;i<8;i++){
  active="second";
  assert.deepEqual(counts(),{main:0,recheck:1,double:1,reviewed:1});
  active="first";
  assert.equal(counts().main,beforeBatch.main-30,
    "Fast account switching must not restore reviewed Focus candidates");
}
scoped.first=[...scoped.first.map(r=>({...r}))]; // ZIP re-import returns fresh row objects.
ctx.V113.cache=null;
assert.equal(counts().main,beforeBatch.main-30,
  "Fresh ZIP row objects and cache invalidation cannot override completed reviews");
assert.equal(counts().reviewed,beforeBatch.reviewed+30);
console.log("PASS: Focus counter is live, consistent with actual openable rows and isolated between accounts");
