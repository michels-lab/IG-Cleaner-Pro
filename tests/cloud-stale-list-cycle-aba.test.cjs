"use strict";
// P0 #360: actual Desktop cloud LIST and DOUBLE CHECK pull functions must
// reject old-owner and A->B->A responses before any account-scoped writes.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Production cloud script is mandatory");
const extract=(a,b)=>{const x=script.indexOf(a),y=script.indexOf(b,x+a.length);
  assert(x>=0&&y>x,"Missing real cloud function "+a);return script.slice(x,y)};
const source=extract("async function pullListSnapshots(){","async function pushPreparedBatches(){")
 + "\n" + extract("async function pullDoubleCheckCycle(){","async function pushDoubleCheckCycle(){");
const account={active:"A",generation:0}, S={session:{user:{id:"owner-a"}},stats:{}};
const saved=new Map([["A::doubleSeen",'["prior-A"]'],["B::doubleSeen",'["prior-B"]']]);
let writeCount=0,applied=0,metaSaves=0,renders=0,cycleRenders=0,requestCount=0;
let deliver;
const ctx={
 Date,JSON,Object,Number,String,Set,Map,Math,Error,console,
 S,window:{IGC_INSTAGRAM_PROFILES:account},
 dataMeta:{},LS_DOUBLE_CHECK_SEEN:"doubleSeen",IGC_DOUBLE_CYCLE_KEY:"doubleEpoch",
 localStorage:{
   getItem:k=>saved.get(account.active+"::"+k)??null,
   setItem(k,v){writeCount++;saved.set(account.active+"::"+k,String(v))},
   removeItem:k=>saved.delete(account.active+"::"+k)
 },
 rest:async(_endpoint,options)=>{requestCount++;assert.equal(options.method,"GET");
   return new Promise(resolve=>{deliver=resolve})},
 listPayload:()=>[],hash:x=>"local-hash-"+String(x).length,
 ms:t=>Date.parse(t)||0,
 applySnapshot:(_name,payload)=>{applied++;saved.set(account.active+"::applied",JSON.stringify(payload));return true},
 saveDataMeta:()=>metaSaves++,renderSyncedLists:()=>renders++,
 renderDoubleCheckStats:()=>cycleRenders++,
 cleanUsername:x=>String(x).trim().toLowerCase()
};
vm.createContext(ctx);vm.runInContext(source,ctx,{timeout:2000});
const list=[{list_name:"following",payload:[{username:"old-account"}],item_count:1,
 content_hash:"remote-original",captured_at:"2026-11-22T20:00:00Z"}];
const cycle=[{payload:{epoch:5,seen:["old-account"]}}];
(async()=>{
  const first=ctx.pullListSnapshots();
  account.active="B";account.generation++;
  deliver(list);
  await assert.rejects(first,/cambió la cuenta o el perfil/);
  assert.equal(applied,0);assert.equal(metaSaves,0);assert.equal(renders,0);
  assert.equal(writeCount,0);assert.equal(saved.has("B::applied"),false);
  assert.equal(S.stats.listsDown,undefined);

  // Double Check has its own remote async request and persisted cycle keys.
  account.active="A";account.generation++;
  const second=ctx.pullDoubleCheckCycle();
  account.active="B";account.generation++;
  account.active="A";account.generation++;
  deliver(cycle);
  await assert.rejects(second,/cambió la cuenta o el perfil/);
  assert.equal(saved.has("A::doubleEpoch"),false);
  assert.equal(saved.get("A::doubleSeen"),'["prior-A"]');
  assert.equal(saved.get("B::doubleSeen"),'["prior-B"]');
  assert.equal(writeCount,0);assert.equal(cycleRenders,0);

  // Sign-in identity changes also invalidate an in-flight list response.
  const third=ctx.pullListSnapshots();
  S.session.user.id="owner-b";
  deliver(list);
  await assert.rejects(third,/cambió la cuenta o el perfil/);
  assert.equal(applied,0);assert.equal(writeCount,0);

  // A clean current B fetch is allowed to update B's snapshot, not A's.
  account.active="B";account.generation++;
  const goodList=ctx.pullListSnapshots();deliver(list);
  const listsResult=await goodList;
  assert.equal(listsResult.changed,1);assert.equal(applied,1);
  assert.equal(saved.has("B::applied"),true);
  assert.equal(saved.has("A::applied"),false);
  assert.equal(metaSaves,1);assert.equal(renders,1);

  const goodCycle=ctx.pullDoubleCheckCycle();
  deliver([{payload:{epoch:8,seen:["prior-B","new-b"]}}]);
  await goodCycle;
  assert.equal(saved.get("B::doubleEpoch"),"8");
  assert.deepEqual(JSON.parse(saved.get("B::doubleSeen")).sort(),["new-b","prior-b"]);
  assert.equal(saved.get("A::doubleSeen"),'["prior-A"]');
  assert.equal(cycleRenders,1);assert.equal(requestCount,5);
  console.log("PASS: actual list/cycle cloud pulls block stale A-B-A and owner changes; current B updates its own keys only");
})().catch(e=>{console.error(e);process.exitCode=1});
