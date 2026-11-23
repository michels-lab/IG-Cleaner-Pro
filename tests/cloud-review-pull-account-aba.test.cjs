"use strict";
// #360: Execute the actual cloud pull: delayed response from account A must
// never mutate current account B or A after an A->B->A generation change.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Required production Supabase sync script");
const begin=script.indexOf("async function pullProfileState(){");
const end=script.indexOf("// Double Check cycle",begin);
assert(begin>=0&&end>begin,"Actual source pullProfileState missing");

const saved=new Map();
let renderCount=0,readCount=0,applyCount=0,writeCount=0;
let deferred;
const account={active:"A",generation:0};
const S={session:{user:{id:"user-1"}},stats:{}};
const doneSet=new Set(["oldA"]),protectedSet=new Set(["protectA"]);
const reviewedMeta={oldA:{reviewedAt:100}};
const pendingReviewedMeta={pendingA:{reviewedAt:200}};
const pendingOpenedSet=new Set(["pendingA"]);
const ctx={
 console,window:{IGC_INSTAGRAM_PROFILES:account},S,
 Date,Set,Map,Object,JSON,Number,String,Error,
 doneSet,protectedSet,reviewedMeta,pendingReviewedMeta,pendingOpenedSet,
 LS_DONE:"done",LS_PROT:"protected",LS_REVIEW_META:"reviewed",
 LS_PENDING_REVIEW_META:"pending",LS_PENDING_OPENED:"opened",
 localStorage:{
   getItem:k=>saved.get(account.active+"::"+k)??null,
   setItem(k,v){writeCount++;saved.set(account.active+"::"+k,String(v))},
   removeItem:k=>saved.delete(account.active+"::"+k)
 },
 readCompleteProfileState(){
   readCount++;
   return new Promise(resolve=>{deferred=resolve;});
 },
 applyOneState(r){
   applyCount++;
   if(r.module==="pending"){
     pendingReviewedMeta[r.username]={reviewedAt:300};
     pendingOpenedSet.add(r.username);
   }else{
     doneSet.add(r.username);
     reviewedMeta[r.username]={reviewedAt:300};
   }
   return true;
 },
 buildRows:()=>renderCount++,applyFilters(){},renderAll(){},
 renderPendingRequests(){},renderFollowersMutualTab(){},renderFollowersAllWorkspace(){}
};
vm.createContext(ctx);vm.runInContext(script.slice(begin,end),ctx);
const remote=[{username:"unreviewed-from-old-account",module:"main"},
 {username:"request-from-old-account",module:"pending"}];
const baseline=()=>JSON.stringify({done:[...doneSet],protected:[...protectedSet],
 reviewed:reviewedMeta,pending:pendingReviewedMeta,opened:[...pendingOpenedSet]});
const base=baseline();
(async()=>{
  // A begins cloud paging, B becomes active before A finishes.
  const first=ctx.pullProfileState();
  account.active="B";account.generation++;
  deferred(remote);
  await assert.rejects(first,/cambió la cuenta o el perfil/);
  assert.equal(baseline(),base);
  assert.equal(saved.size,0);assert.equal(writeCount,0);
  assert.equal(applyCount,0);assert.equal(renderCount,0);
  assert.equal(S.stats.statesDown,undefined);

  // ABA is dangerous even when account is again A by response time.
  account.active="A";account.generation++;
  const second=ctx.pullProfileState();
  account.active="B";account.generation++;
  account.active="A";account.generation++;
  deferred(remote);
  await assert.rejects(second,/cambió la cuenta o el perfil/);
  assert.equal(baseline(),base);assert.equal(saved.size,0);
  assert.equal(applyCount,0);

  // Owner sign-out/login change without Instagram slot change also invalidates.
  const third=ctx.pullProfileState();
  S.session.user.id="user-2";
  deferred(remote);
  await assert.rejects(third,/cambió la cuenta o el perfil/);
  assert.equal(applyCount,0);assert.equal(saved.size,0);
  assert.equal(baseline(),base);

  // Fresh B task applies only B and commits its entire local snapshot.
  account.active="B";account.generation++;S.session.user.id="user-2";
  const success=ctx.pullProfileState();
  deferred([{username:"freshB",module:"main"}]);
  assert.deepEqual(JSON.parse(JSON.stringify(await success)),{rows:1,changed:1});
  assert.equal(applyCount,1);assert.equal(renderCount,1);
  assert.equal(S.stats.statesDown,1);
  assert.equal(saved.has("B::done"),true);
  assert.equal(saved.has("A::done"),false);
  assert.equal(JSON.parse(saved.get("B::done")).includes("freshB"),true);
  assert.equal(readCount,4);
  console.log("PASS: production pull rejects A->B, A->B->A and owner switch before any review write; fresh B persists normally");
})().catch(e=>{console.error(e);process.exitCode=1});
