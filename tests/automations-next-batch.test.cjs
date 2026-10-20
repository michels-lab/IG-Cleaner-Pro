"use strict";
/* Offline real embedded logic: third Pending batch, newly imported rows, and
   frozen Focus preview stale on import. No Instagram access. */
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function script(id){const re=new RegExp('<script id="'+id+'">([\\s\\S]*?)<\\/script>');const m=html.match(re);assert(m,"Missing "+id);return m[1]}
assert(html.includes('onclick="igcAutoOpenPendingReviewBatch()"'),"Explicit Pending opener must be in Automations");
assert(html.includes('onclick="recoverSectionActiveBatch(\'pending\')"'),"Recover batch must be visible in Pending Lab");
const source=script("igc-automations-plan");new vm.Script(source);
const nodes=new Map();
function el(id){if(!nodes.has(id))nodes.set(id,{
  id,value:id==="igcAutoBatch"?"30":id==="igcAutoRest"?"0":"10",
  textContent:"",children:[],style:{},disabled:false,
  appendChild(c){this.children.push(c);return c},
  replaceChildren(){this.children=[]},
  addEventListener(){},setAttribute(){},
 } );return nodes.get(id)}
const store=new Map(),post=[],batchReplans=[];
let pendingSaved=null;
const profile=(name)=>({username:name,href:"https://www.instagram.com/"+name+"/"});
const pending=[...Array(155)].map((_,i)=>profile("pending."+String(i).padStart(3,"0")));
const already=pending.slice(0,60).map(x=>x.username);
let state={owner:"owner1",account:"profile1",task:"cancel",
  status:"complete",running:false,rows:[],attempted_usernames:already,
  issues:[],total:30,remaining:0,successful:30,errors:0,protected:0,skipped:0,wait_seconds:0};
const ctx={
  console, Map,Set,Number,String,Object,JSON,Date,Math,Error,RegExp,
  document:{getElementById:el,createElement:tag=>({
    tagName:tag,children:[],textContent:"",disabled:false,style:{},
    appendChild(c){this.children.push(c);return c},addEventListener(){},
    replaceChildren(){this.children=[]}
  }),hidden:false},
  location:{hash:"#igc-robot=32123.abcdefghijklmnopqrstuvwxy"},
  localStorage:{getItem:k=>store.has(k)?store.get(k):null,setItem:(k,v)=>store.set(k,String(v))},
  pendingRequestsRaw:pending,followingRaw:[],followersRaw:[],
  followingMap:new Map(),followersMap:new Map(),
  protectedSet:new Set(),doneSet:new Set(),
  showPage:id=>{ctx.lastPage=id},
  pendingFocusN:n=>{ctx.lastOpened=n},
  setInterval:()=>{},
  fetch:async(url,opts)=>{
    const op=url.split("/").at(-1);
    assert.equal(opts.headers["X-IGC-Bridge-Token"],"abcdefghijklmnopqrstuvwxy");
    if(op==="review-batch"){
      return {ok:true,json:async()=>({
        owner:"owner1",account:"profile1",task:"cancel",batch:pendingSaved
      })};
    }
    if(op==="replan-batch"){
      const payload=JSON.parse(opts.body);batchReplans.push(payload);
      assert(pendingSaved,"Only a pending cohort can be replanned");
      const old=pendingSaved;
      const remain=old.targets.filter((u,i)=>i!==0);
      pendingSaved={...old,original_targets:[...old.targets],
        targets:remain.slice(0,payload.desired_batch_size),
        carryover_targets:remain.slice(payload.desired_batch_size),
        selected_batch_size:payload.desired_batch_size};
      return {ok:true,json:async()=>({
        owner:payload.owner,account:payload.account,task:payload.task,
        batch_id:old.id,previous_size:old.targets.length,
        requested_new_size:payload.desired_batch_size,
        active_size:pendingSaved.targets.length,
        reusable_after_active:pendingSaved.carryover_targets.length,
        marked_reviewed:false,status:"replanned_active_cohort_not_archived"
      })};
    }
    if(op==="history"){
      const data=JSON.parse(opts.body);
      return {ok:true,json:async()=>({
        owner:data.owner,account:data.account,task:data.task,
        attempted_usernames:state.attempted_usernames
      })};
    }
    if(op==="start"){const payload=JSON.parse(opts.body);post.push(payload);
      state={...state,status:"starting",total:payload.targets.length,rows:payload.targets.map(username=>({username})),remaining:payload.targets.length};}
    return {ok:true,json:async()=>state};
  },
  confirm:()=>true
};ctx.window=ctx;
ctx.IGC_INSTAGRAM_PROFILES={owner:"owner1",active:"profile1",
  accounts:[{account_key:"profile1",username:"owner.name"}]};
vm.createContext(ctx);vm.runInContext(source,ctx,{timeout:1200});
(async()=>{
  ctx.igcAutoChoose("cancel");
  await ctx.igcAutoPoll();
  const triedKey=[...store.keys()].find(k=>k.includes("igc_actions_attempted_v1__"));
  assert(triedKey,"Prior batch journal must be saved per owner/Instagram/task");
  assert.equal(JSON.parse(store.get(triedKey)).length,60);
  await ctx.igcAutoStart();
  assert.equal(post.length,1);
  assert.deepEqual([...post[0].targets],pending.slice(60,90).map(x=>x.username),
    "Third batch must NOT restart from first 30 / second 30");
  ctx.igcAutoPageMove(1);
  assert.match(el("igcAutoPageStatus").textContent,/Page 2 \/ 2/);
  assert(el("igcAutoRows").children.length>0,"Import beyond first page must remain accessible");
  ctx.igcAutoOpenPendingReviewBatch();
  assert.equal(ctx.lastPage,"pendingRequests");
  assert.equal(ctx.lastOpened,30,"Pending review must be a separate read-only Focus click");

  // After importing a new archive, original results are protected and new
  // usernames should be picked up after all previous 155 attempts.
  pending.push(profile("fresh.from.new.export"));
  state={...state,status:"complete",rows:[],attempted_usernames:pending.slice(0,155).map(x=>x.username)};
  await ctx.igcAutoPoll();
  await ctx.igcAutoStart();
  assert.deepEqual([...post.at(-1).targets],["fresh.from.new.export"]);
  // The EXACT owner regression: a saved 40-target cohort must NOT hijack
  // Run after choosing 10. The old cohort remains untouched until the owner
  // explicitly archives it (never Reviewed), then a NEW 10-target selection.
  const oldNames=[...Array(40)].map((_,i)=>"saved."+String(i).padStart(3,"0"));
  pendingSaved={
    id:"saved-40-batch",targets:oldNames,
    action_results:Object.fromEntries(oldNames.map((u,i)=>[u,{status:i===0?"review":"pending",safe_no_click:false}])),
    recheck_results:{},protected_in_cohort:[]
  };
  el("igcAutoBatch").value="10";
  await ctx.igcAutoPoll();
  assert.match(el("igcAutoBatchApprovalDetails").textContent,/SAVED BATCH: 40 profiles/);
  assert.match(el("igcAutoBatchApprovalDetails").textContent,/NEW SELECTED SIZE: 10/);
  assert.equal(el("igcAutoReplanSize").style.display,"inline-flex");
  const before=post.length;
  await ctx.igcAutoStart();
  assert.equal(post.length,before,"Run must NOT start original saved 40 after selecting size 10");
  assert.equal(batchReplans.length,0,"Run must NOT silently archive old cohort");
  assert.match(el("igcAutoStatus").textContent,/SAVED COHORT: 40 profiles/);
  await ctx.igcAutoReplanSavedBatch();
  assert.equal(batchReplans.length,1);
  assert.equal(batchReplans[0].batch_id,"saved-40-batch");
  assert.equal(batchReplans[0].desired_batch_size,10);
  assert.equal(batchReplans[0].confirmation,"replan-size:saved-40-batch:10");
  assert.equal(pendingSaved.id,"saved-40-batch","Same cohort remains active");
  assert.equal(pendingSaved.original_targets.length,40,"Original users never archived or deleted");
  assert.equal(pendingSaved.targets.length,10);
  assert.equal(pendingSaved.carryover_targets.length,29);
  assert.equal(pendingSaved.selected_batch_size,10);
  state={...state,attempted_usernames:["saved.000"]};
  await ctx.igcAutoStart();
  assert.equal(post.length,before+1);
  assert.equal(post.at(-1).targets.length,10,
    "After explicit archival, Run MUST honor the newly selected size 10");
  assert.deepEqual([...post.at(-1).targets],pendingSaved.targets,
    "Run reuses the exact ten previously untouched users without skipping everyone else");
  console.log("PASS: third batch advances; reimport; saved 40 cannot override selected 10; 40 remain saved, 10 active, 29 reusable");
})().catch(e=>{console.error(e);process.exitCode=1});
