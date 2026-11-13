"use strict";
// Exercise the production cloud-sync functions (no network, no Instagram account).
const assert=require("node:assert/strict");
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Production Supabase sync script must exist");
function cut(a,b){
  const first=script.indexOf(a),end=script.indexOf(b,first+a.length);
  assert(first>=0&&end>first,"Function boundaries not found: "+a);
  return script.slice(first,end);
}
const ms=t=>Date.parse(t)||0;
const remoteAt="2026-11-12T18:00:00.000Z";
const newerAt="2026-11-12T19:00:00.000Z";
const olderAt="2026-11-12T17:00:00.000Z";
const doneSet=new Set(["previous"]);
const reviewedMeta={previous:{mode:"following",reviewedAt:ms(newerAt),relation:"No me sigue"}};
const protectedSet=new Set();
const pendingReviewedMeta={};
const pendingOpenedSet=new Set();
const ctx={console,Date,Math,Set,Map,JSON,Object,String,Number,ms,
   doneSet,reviewedMeta,protectedSet,pendingReviewedMeta,pendingOpenedSet,
   window:{IGC_INSTAGRAM_PROFILES:{active:'legacy',accounts:[{account_key:'legacy',review_count:3}]}}};
vm.createContext(ctx);
vm.runInContext(cut("function applyOneState(r){","async function pullProfileState(){"),ctx);
const fresh={username:"newuser",module:"main",reviewed_at:remoteAt,
 reviewed_device:"android",decision:"reviewed",protected:false,
 context:{
   row:{relation:"not_follow",relationGood:false,followsBack:false,isFollower:false,iFollow:true,dateMain:100},
   meta:{mode:"following",relation:"No me sigue",relationGood:false,followsBack:false,isFollower:false,iFollow:true,dateMain:100}
 }};
assert.equal(ctx.applyOneState(fresh),true);
assert.equal(reviewedMeta.newuser.relation,"No me sigue",
  "Imported real review metadata must override generic sync relation codes");
assert(doneSet.has("newuser"));
assert.equal(ctx.applyOneState({...fresh,reviewed_at:olderAt,decision:"stale"}),false,
  "Older cloud review must never overwrite newer local review");
assert.equal(reviewedMeta.newuser.reviewReason,"reviewed");

const android={username:"androidonly",module:"main",reviewed_at:newerAt,
 reviewed_device:"android",decision:"reviewed",
 context:{row:{relation:"not_follow",followsBack:false,isFollower:false,relationGood:false,dateMain:200}}};
assert.equal(ctx.applyOneState(android),true);
assert.equal(reviewedMeta.androidonly.relation,"No me sigue",
  "Android source relation code must use the same label as the main table");
const local=[
 {username:"previous",module:"main",reviewed_at:olderAt},
 {username:"newuser",module:"main",reviewed_at:newerAt},
 {username:"androidonly",module:"main",reviewed_at:newerAt}
];
const writes=[];
ctx.localStateRows=()=>local;
ctx.rest=async(path,options)=>{
 if(options.method==="GET"){
  assert(path.startsWith("profile_state?select=username,module,reviewed_at"));
  return [
    {username:"previous",module:"main",reviewed_at:remoteAt},
    {username:"newuser",module:"main",reviewed_at:olderAt},
    {username:"androidonly",module:"main",reviewed_at:newerAt}
  ];
 }
 assert.equal(options.method,"POST");
 writes.push(...JSON.parse(options.body));
 return null;
};
vm.runInContext(cut("let completeProfileStateCache=null;","async function pushWorkspaceState(){"),ctx);
(async()=>{
  assert.equal(await ctx.pushProfileState(),1);
  assert.deepEqual(writes.map(x=>x.username),["newuser"],
   "Push should exclude remote-newer and equal-timestamp rows");
  console.log("PASS: review metadata survives sync and stale cloud writes are filtered");
})().catch(e=>{console.error(e);process.exitCode=1});
