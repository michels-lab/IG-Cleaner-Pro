"use strict";
// GRANADA #360: a cached or delayed cloud page must never cross an owner or
// Instagram workspace, and a sync read must bypass stale short-lived cache.
const assert=require("node:assert/strict");
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Production sync script must exist");
const start=script.indexOf("let completeProfileStateCache=null;");
const end=script.indexOf("async function pushProfileState(){",start);
assert(start>=0&&end>start,"Production paginated review reader must exist");
const rows={
 "first|A":[{username:"one",module:"main",reviewed_at:"2026-11-18T19:00:00Z"}],
 "first|B":[{username:"two",module:"main",reviewed_at:"2026-11-18T19:01:00Z"}],
 "second|B":[{username:"three",module:"pending",reviewed_at:"2026-11-18T19:02:00Z"}]
};
let calls=0,held=null;
const owner=()=>ctx.S.session.user.id;
const registry={active:"A",generation:0,accounts:[]};
const ctx={
 Date,Math,Set,Map,JSON,String,Number,Array,Error,console,
 window:{IGC_INSTAGRAM_PROFILES:registry},
 S:{session:{user:{id:"first"}}},
 rest:async query=>{
   assert(query.startsWith("profile_state?select="),"Read real paginated scoped reviews");
   calls++;
   const offset=Number(new URLSearchParams(query.split("?")[1]).get("offset"));
   return offset===0?(rows[owner()+"|"+registry.active]||[]):[];
 }
};
vm.createContext(ctx);
vm.runInContext(script.slice(start,end),ctx);
(async()=>{
  assert.equal((await ctx.readCompleteProfileState("*"))[0].username,"one");
  const firstCalls=calls;
  assert.equal((await ctx.readCompleteProfileState("*"))[0].username,"one");
  assert.equal(calls,firstCalls,"Same scoped read may use short-lived cache");
  registry.active="B";
  assert.equal((await ctx.readCompleteProfileState("*"))[0].username,"two",
    "Account B must not inherit account A's cached Reviewed state");
  ctx.S.session={user:{id:"second"}};
  assert.equal((await ctx.readCompleteProfileState("*"))[0].username,"three",
    "A new app owner must not inherit prior owner's cached Pending state");
  const beforeFresh=calls;
  rows["second|B"]=[{username:"newer",module:"pending",reviewed_at:"2026-11-18T19:03:00Z"}];
  assert.equal((await ctx.readCompleteProfileState("*",{fresh:true}))[0].username,"newer");
  assert(calls>beforeFresh,"Fresh reconciliation must not use a 4-second-old cloud snapshot");

  ctx.S.session={user:{id:"first"}};registry.active="A";
  let release;
  ctx.rest=async()=>new Promise(resolve=>{release=resolve});
  const pending=ctx.readCompleteProfileState("*",{fresh:true});
  for(let attempt=0;attempt<8&&!release;attempt++)await Promise.resolve();
  assert.equal(typeof release,"function","Controlled delayed cloud request must start");
  registry.active="B";
  release(rows["first|A"]);
  await assert.rejects(pending,/cambió la cuenta o el perfil/,
    "Mid-flight A-to-B handoff must reject stale A review rows, not apply them under B");
  ctx.rest=async q=>{
    const offset=Number(new URLSearchParams(q.split("?")[1]).get("offset"));
    return offset?[]:rows["first|B"];
  };
  assert.equal((await ctx.readCompleteProfileState("*",{fresh:true}))[0].username,"two",
    "Stale rejected response must not poison B cache");

  assert(script.includes("readCompleteProfileState('username,module,reviewed_at',{fresh:true})"),
    "Push must compare fresh server state before deciding writes");
  assert(script.includes("readCompleteProfileState('*',{fresh:true})"),
    "Pull must fetch fresh remote reviews before merging and displaying counters");
  // A->B->A across TWO pages keeps the same owner/account text but must be
  // rejected because the identity generation advanced during a page boundary.
  ctx.S.session={user:{id:"first"}};registry.active="A";registry.generation=10;
  let releaseNextPage;
  ctx.rest=async q=>{
    const offset=Number(new URLSearchParams(q.split("?")[1]).get("offset"));
    if(offset===0)return rows["first|A"];
    return new Promise(resolve=>{releaseNextPage=resolve});
  };
  const pendingPages=ctx.readCompleteProfileState("*",{fresh:true});
  for(let i=0;i<10&&!releaseNextPage;i++)await Promise.resolve();
  assert.equal(typeof releaseNextPage,"function","Page 2 must be in flight before account switch");
  registry.active="B";registry.generation=11;
  registry.active="A";registry.generation=12;
  releaseNextPage([]);
  await assert.rejects(pendingPages,/cambió la cuenta o el perfil/,
    "A->B->A between pages must reject the whole scan despite unchanged final account key");
  let afterSwitchCalls=0;
  ctx.rest=async q=>{
    afterSwitchCalls++;
    const offset=Number(new URLSearchParams(q.split("?")[1]).get("offset"));
    return offset?[]:[{username:"after-aba",module:"main"}];
  };
  assert.equal((await ctx.readCompleteProfileState("*"))[0].username,"after-aba",
    "Rejected A->B->A scan cannot publish a poisoned review cache");
  assert(afterSwitchCalls>=2,"A fresh generation forces a new complete download");
  const cacheCalls=afterSwitchCalls;
  await ctx.readCompleteProfileState("*");
  assert.equal(afterSwitchCalls,cacheCalls,"Unchanged generation still permits same-workspace cache");
  registry.generation=13;
  await ctx.readCompleteProfileState("*");
  assert(afterSwitchCalls>cacheCalls,"A->B->A generation invalidates even a current 4-second cache");

  // Multi-POST push is a second race: once 500 rows have been submitted
  // to account A, switching A->B->A during that HTTP wait must prevent
  // writing the remaining A rows into a new account generation.
  const pushStart=script.indexOf("async function pushProfileState(){");
  const pushEnd=script.indexOf("async function pushWorkspaceState(){",pushStart);
  assert(pushStart>=0&&pushEnd>pushStart,"Real production profile-state push required");
  vm.runInContext(script.slice(pushStart,pushEnd),ctx);
  ctx.ms=value=>Date.parse(value)||0;
  ctx.localStateRows=()=>Array.from({length:501},(_,i)=>({
    username:"sent"+i,module:"main",reviewed_at:"2026-11-18T22:00:00Z"
  }));
  let releaseFirstPost,postCount=0;
  ctx.rest=async(q,opt)=>{
    if(opt.method==="GET")return [];
    assert.equal(opt.method,"POST");
    postCount++;
    assert.equal(registry.active,"A","First POST under the original workspace");
    assert.equal(JSON.parse(opt.body).length,500,"First A POST is bounded to 500");
    return new Promise(resolve=>{releaseFirstPost=resolve});
  };
  const pendingPush=ctx.pushProfileState();
  for(let i=0;i<15&&!releaseFirstPost;i++)await Promise.resolve();
  assert.equal(typeof releaseFirstPost,"function","First A POST should start");
  registry.active="B";registry.generation=14;
  registry.active="A";registry.generation=15;
  releaseFirstPost(null);
  await assert.rejects(pendingPush,/cambió la cuenta o el perfil/,
    "A->B->A during one POST cannot authorize a second cross-generation POST");
  assert.equal(postCount,1,"No second chunk may send stale source-account review rows");

  console.log("PASS: fresh review reconciliation, owner/account/generation-scoped cache, A-B-A paginated scan rejection and multi-POST push guards");
})().catch(e=>{console.error(e);process.exitCode=1});
