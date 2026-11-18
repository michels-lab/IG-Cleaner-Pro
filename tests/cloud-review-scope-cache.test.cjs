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
const registry={active:"A",accounts:[]};
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
  console.log("PASS: fresh review reconciliation, owner/account-scoped cache and in-flight switch rejection");
})().catch(e=>{console.error(e);process.exitCode=1});
