"use strict";
// Regression for an owner workspace containing 9,896 cloud review rows.
// The server can cap an explicit limit=20000 to 1000; never silently drop
// historical reviews or replay thousands of older local decisions.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Missing production cloud synchronization script");
function cut(from,to){
  const a=script.indexOf(from),b=script.indexOf(to,a+from.length);
  assert(a>=0&&b>a,"Missing production function "+from);
  return script.slice(a,b);
}
const fixtures=Array.from({length:9896},(_,i)=>{
  const module=i<7493?"main":i<8713?"followers":"pending";
  const relation=module==="main"?"No me sigue":"Yo lo sigo";
  const snapshot={relation,relationGood:false,followsBack:false,isFollower:false,iFollow:true,dateMain:100};
  return {
    username:"fictional"+String(i).padStart(5,"0"),
    module,reviewed_at:"2026-11-12T19:00:00.000Z",
    reviewed_device:"desktop",decision:"reviewed",protected:false,
    context:{row:{...snapshot},meta:{mode:module==="main"?"following":"followers",...snapshot}}
  };
});
function harness(cutPage=-1,serverCap=1000){
  const doneSet=new Set(),reviewedMeta={},protectedSet=new Set();
  const pendingReviewedMeta={},pendingOpenedSet=new Set(),storage=new Map();
  let calls=0,writes=0;
  const ctx={console,Date,Math,Set,Map,JSON,Object,String,Number,
    doneSet,reviewedMeta,protectedSet,pendingReviewedMeta,pendingOpenedSet,
    LS_DONE:"done",LS_PROT:"protected",LS_REVIEW_META:"meta",
    LS_PENDING_REVIEW_META:"pendingmeta",LS_PENDING_OPENED:"pendingOpened",
    localStorage:{setItem:(key,value)=>storage.set(key,value)},
    S:{stats:{}},ms:value=>Date.parse(value)||0,
    window:{IGC_INSTAGRAM_PROFILES:{
      active:"legacy",accounts:[{account_key:"legacy",review_count:fixtures.length}]
    }},
    localStateRows:()=>fixtures.map(r=>({username:r.username,module:r.module,reviewed_at:r.reviewed_at}))
  };
  ctx.rest=async(q,options)=>{
    if(options.method==="POST"){writes+=JSON.parse(options.body).length;return null}
    assert.equal(options.method,"GET");
    assert(q.startsWith("profile_state?select="),"Use scoped profile_state endpoint");
    assert(q.includes("order=username.asc,module.asc"),"Stable paginated order");
    const limit=Number(new URLSearchParams(q.split("?")[1]).get("limit"));
    const offset=Number(new URLSearchParams(q.split("?")[1]).get("offset"));
    assert.equal(limit,1000);
    calls++;
    return offset===cutPage?[]:fixtures.slice(offset,offset+Math.min(limit,serverCap));
  };
  vm.createContext(ctx);
  vm.runInContext(cut("let completeProfileStateCache=null;","async function pushWorkspaceState(){"),ctx);
  vm.runInContext(cut("function applyOneState(r){","// Double Check cycle"),ctx);
  return {ctx,doneSet,reviewedMeta,pendingReviewedMeta,storage,counts:()=>({calls,writes})};
}
(async()=>{
  const a=harness();
  const result=await a.ctx.pullProfileState();
  assert.equal(result.rows,9896,"Must hydrate all pages, not just the first 1000");
  assert.equal(a.ctx.S.stats.statesDown,9896);
  assert.equal(a.doneSet.size,8713,"Main + follower historical reviews stay available");
  assert.equal(Object.keys(a.pendingReviewedMeta).length,1183);
  assert.equal(a.reviewedMeta.fictional07492.relation,"No me sigue");
  assert(a.storage.has("meta"),"Hydrated review state must persist locally");
  assert.equal(a.counts().calls,10);
  assert.equal(await a.ctx.pushProfileState(),0,
    "Cloud reviews must not be republished as if 8896 rows were missing");
  assert.equal(a.counts().writes,0);

  // An untrusted partial result must fail without overwriting local decisions.
  const truncated=harness(1000);
  await assert.rejects(truncated.ctx.pullProfileState(),/Sync incompleto/);
  assert.equal(truncated.doneSet.size,0,"Incomplete download may not partially apply records");
  assert.equal(truncated.ctx.S.stats.statesDown,undefined);

  // If an installation lowers the API max_rows limit, the cloud count guard
  // refuses to treat a short page as a complete profile history.
  const capped=harness(-1,500);
  await assert.rejects(capped.ctx.pullProfileState(),/Sync incompleto/);
  assert.equal(capped.doneSet.size,0);

  // A slim preflight GET cannot masquerade as fully hydrated review payloads.
  const slim=harness();
  await slim.ctx.readCompleteProfileState("username,module,reviewed_at");
  const full=await slim.ctx.pullProfileState();
  assert.equal(full.rows,9896);
  assert(slim.counts().calls>10,"A full hydration must replace any cached slim response");
  assert.equal(slim.reviewedMeta.fictional07492.relation,"No me sigue");
  console.log("PASS: complete 9896-row reviews; safe truncated-page refusal; full hydration after slim cache");
})().catch(e=>{console.error(e);process.exitCode=1});
