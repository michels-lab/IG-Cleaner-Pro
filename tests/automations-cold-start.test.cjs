"use strict";
/* Cold launch without an active robot must recover the disk journal before
 * selecting any action-changing batch. Local fixtures only, no Instagram. */
const assert=require("node:assert/strict");
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-automations-plan">([\s\S]*?)<\/script>/);
assert(script,"Automations module missing");
const elements=new Map();
function el(id){
 if(!elements.has(id))elements.set(id,{
  value:id==="igcAutoBatch"?"30":id==="igcAutoRest"?"0":id==="igcAutoGap"?"10":"",
  children:[],textContent:"",style:{},disabled:false,
  appendChild(child){this.children.push(child)},
  replaceChildren(){this.children=[]},
  addEventListener(){},setAttribute(){}
 });
 return elements.get(id);
}
const storage=new Map(),posts=[],historyCalls=[];
const first60=[...Array(60)].map((_,i)=>"requested."+String(i).padStart(3,"0"));
const profiles=[...Array(95)].map((_,i)=>({username:"requested."+String(i).padStart(3,"0")}));
const owner={owner:"login1",active:"ig1",accounts:[{account_key:"ig1",username:"my.handle"}]};
let failHistory=false,wrongOwner=false,visitedNoClick=false;
let state={owner:"",account:"",task:"",status:"idle",running:false,rows:[],
 attempted_usernames:[],total:0,remaining:0,successful:0,errors:0,protected:0,skipped:0,issues:[]};
const ctx={
 console,Map,Set,JSON,Object,Array,Number,String,Date,Math,Error,RegExp,
 document:{hidden:false,getElementById:el,createElement:el},
 localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,val)=>storage.set(key,String(val))},
 location:{hash:"#igc-robot=33333.0123456789abcdefghijabcdefgh"},
 IGC_INSTAGRAM_PROFILES:owner,
 pendingRequestsRaw:profiles,followingRaw:[],followersRaw:[],followingMap:new Map(),followersMap:new Map(),
 protectedSet:new Set(),doneSet:new Set(),setInterval(){},showPage(){},confirm:()=>true,
 fetch:async(url,opts)=>{
   const op=url.split("/").pop();
   assert.equal(opts.headers["X-IGC-Bridge-Token"],"0123456789abcdefghijabcdefgh");
   if(op==="history"){
     const request=JSON.parse(opts.body);historyCalls.push(request);
     if(failHistory)throw Error("Windows robot history unavailable");
     return {ok:true,json:async()=>({
       ...request,owner:wrongOwner?"different-owner":request.owner,
       attempted_usernames:first60,
       visited_usernames:visitedNoClick?[...first60,"requested.090"]:first60
     })};
   }
   if(op==="start"){
     const request=JSON.parse(opts.body);posts.push(request);
     state={...state,owner:request.owner,account:request.account,task:request.task,
       status:"starting",running:false,total:request.targets.length,
       remaining:request.targets.length,attempted_usernames:first60,
       rows:request.targets.map(username=>({username}))};
   }
   return {ok:true,json:async()=>state};
 }
};
ctx.window=ctx;
vm.createContext(ctx);vm.runInContext(script[1],ctx,{timeout:1500});
(async()=>{
 ctx.igcAutoChoose("cancel");
 assert.equal(storage.size,0,"Fresh Windows launch must not have action history in browser storage");
 await ctx.igcAutoStart();
 assert.equal(historyCalls.length,1,"Action launch needs explicit disk history even when robot was idle");
 assert.equal(posts.length,1);
 assert.deepEqual([...posts[0].targets],profiles.slice(60,90).map(x=>x.username),
   "First batch after app restart must start after previous 60 attempts");
 assert.equal(JSON.parse([...storage.values()].find(x=>x.includes("requested.000"))).length,60);

 // A no-click profile was already OPENED: it is not a completed
 // relationship mutation, but it MUST NOT enter another NEW batch. The
 // authoritative Windows visited ledger supersedes any stale client cache.
 const attemptedKey=[...storage.keys()].find(k=>k.startsWith("igc_actions_attempted_v1__"));
 assert(attemptedKey,"Expected persisted attempts cache");
 storage.set(attemptedKey,JSON.stringify([...first60]));
 state.attempted_usernames=[...first60];
 visitedNoClick=true;
 el("igcAutoBatch").value="35";
 await ctx.igcAutoStart();
 assert.equal(posts.length,2);
 assert.equal(posts[1].targets.length,34,
   "Only 34 fresh targets remain after excluding one previously opened no-click");
 assert(!posts[1].targets.includes("requested.090"),
   "An opened no-click target cannot be repeated in another automatic NEW batch");
 assert(posts[1].targets.includes("requested.091"));

 // Never fall back to a stale client cache when robot disk cannot be read.
 failHistory=true;
 await ctx.igcAutoStart();
 assert.equal(posts.length,2,"No action start when journal read fails");
 assert.match(el("igcAutoStatus").textContent,/history unavailable/);

 failHistory=false;wrongOwner=true;
 await ctx.igcAutoStart();
 assert.equal(posts.length,2,"No action start on unexpected history scope");
 assert.match(el("igcAutoStatus").textContent,/did not match/);
 console.log("PASS: cold launch, no-click visited exclusion, fail-closed foreign histories");
})().catch(error=>{console.error(error);process.exitCode=1});
