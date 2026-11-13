"use strict";
// Regression for an offline/older Desktop sending obsolete relationship snapshots.
// Runs production functions under a mocked per-Instagram Supabase REST endpoint.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Missing production cloud sync");
function slice(start,end){
 const a=script.indexOf(start),b=script.indexOf(end,a+start.length);
 assert(a>=0&&b>a,"Missing sync implementation section: "+start);
 return script.slice(a,b);
}
const row=username=>({username,href:"https://www.instagram.com/"+username+"/",timestamp:1234});
const ago=ms=>new Date(Date.now()-ms).toISOString();
function harness(account,deviceType='desktop'){
 const store=new Map(),remote=new Map(),writes=[],renders=[];
 const ctx={console,Date,Number,String,Math,JSON,Set,Map,Array,
  window:{},followingRaw:[row("old")],followersRaw:[],pendingRequestsRaw:[],
  followingMap:new Map(),followersMap:new Map(),dataMeta:{},S:{stats:{}},
  currentDevice:()=>({type:deviceType,id:"test-device"}),
  saveDataMeta:()=>store.set("meta",JSON.stringify(ctx.dataMeta)),
  renderSyncedLists:changed=>renders.push([...changed]),ms:s=>Date.parse(s)||0
 };
 ctx.rest=async(q,opts={})=>{
   if(opts.method==="POST"){
     assert(q.startsWith("list_snapshots?on_conflict"));
     for(const incoming of JSON.parse(opts.body)){
       const existing=remote.get(incoming.list_name);
       // Mimic server trigger, which rejects old or equal imported timestamps.
       if(!existing||Date.parse(incoming.captured_at)>Date.parse(existing.captured_at))
         remote.set(incoming.list_name,JSON.parse(JSON.stringify(incoming)));
       writes.push(incoming);
     }
     return null;
   }
   assert(q.startsWith("list_snapshots?select="));
   return [...remote.values()].map(x=>JSON.parse(JSON.stringify(x)));
 };
 ctx.account=account;
 vm.createContext(ctx);
 vm.runInContext(slice("function hash(s){","function renderSyncedLists(changed){"),ctx);
 vm.runInContext(slice("window.igcMarkLocalSnapshotsDirty=function(kinds){","async function pushPreparedBatches(){"),ctx);
 return {ctx,remote,writes,renders,store};
}
const snapshot=(x,name,source,capturedAt)=>{
 const payload=source.map(u=>({...row(u),name:"",url:"",fbid:"",source:"",method:""}));
 return {list_name:name,payload,item_count:payload.length,content_hash:x.ctx.hash(JSON.stringify(payload)),
   captured_at:capturedAt,updated_at:capturedAt,source_device:"desktop"};
};
(async()=>{
 // Existing cloud snapshot beats a stale legacy local dataset on first sign-in.
 const old=harness("first");
 old.remote.set("following",snapshot(old,"following",["cloud.new"],ago(120000)));
 assert.equal((await old.ctx.pushListSnapshots()).lists,0);
 assert.equal(old.writes.length,0,"Do not re-upload outdated list with today's timestamp");
 await old.ctx.pullListSnapshots();
 assert.deepEqual(old.ctx.followingRaw.map(r=>r.username),["cloud.new"]);
 assert.equal(old.ctx.dataMeta.following.dirtyAt,undefined);

 // A new explicit manual import is legitimate and must update the cloud.
 old.ctx.followingRaw=[row("fresh.import")];
 old.ctx.window.igcMarkLocalSnapshotsDirty(["following"]);
 assert(old.ctx.dataMeta.following.dirtyAt>0);
 assert.equal((await old.ctx.pushListSnapshots()).lists,1);
 assert.deepEqual(old.writes.map(x=>x.list_name),["following"]);
 await old.ctx.pullListSnapshots();
 assert.deepEqual(old.ctx.followingRaw.map(r=>r.username),["fresh.import"]);
 assert.equal((await old.ctx.pushListSnapshots()).lists,0,"No duplicate upload after sync");

 // An import made earlier than a newer cloud revision must not win.
 const stale=harness("first");
 stale.remote.set("following",snapshot(stale,"following",["new.remote"],new Date(Date.now()+100000).toISOString()));
 stale.ctx.followingRaw=[row("stale.local")];
 stale.ctx.window.igcMarkLocalSnapshotsDirty(["following"]);
 assert.equal((await stale.ctx.pushListSnapshots()).lists,0);
 await stale.ctx.pullListSnapshots();
 assert.deepEqual(stale.ctx.followingRaw.map(r=>r.username),["new.remote"]);

 // A Pending-only ZIP import must not change following/followers timestamps.
 const pending=harness("second");
 pending.ctx.pendingRequestsRaw=[row("pending.new")];
 pending.ctx.window.igcMarkLocalSnapshotsDirty(["pending"]);
 assert(pending.ctx.dataMeta.pending.dirtyAt>0);
 assert.equal(pending.ctx.dataMeta.following,undefined);
 assert.equal((await pending.ctx.pushListSnapshots()).lists,2,
   "Initial empty cloud can accept existing Following plus explicit Pending; Followers remains empty");
 assert.deepEqual(pending.writes.map(x=>x.list_name),["following","pending"]);
 assert.equal(old.ctx.followingRaw[0].username,"fresh.import",
   "Two independent Instagram sessions must never mutate each other's local lists");

 // A verified empty Pending export is a real import, not an absent input:
 // syncing it must remove older Pending accounts instead of resurrecting them.
 const empty=harness("third");
 empty.remote.set("following",snapshot(empty,"following",["old"],ago(90000)));
 empty.remote.set("pending",snapshot(empty,"pending",["stale.pending"],ago(90000)));
 empty.ctx.pendingRequestsRaw=[];
 empty.ctx.window.igcMarkLocalSnapshotsDirty(["pending"]);
 assert.equal((await empty.ctx.pushListSnapshots()).lists,1,
   "Explicit empty Pending import must upload rather than silently skip");
 assert.equal(empty.remote.get("pending").item_count,0);
 await empty.ctx.pullListSnapshots();
 assert.equal(empty.ctx.pendingRequestsRaw.length,0);

 // Native Android Advanced Workspace must never upload stale caches; only
 // explicit imports may travel from Android to Desktop and back.
 const android=harness("android-a","android");
 android.remote.set("following",snapshot(android,"following",["cloud.following"],ago(60000)));
 android.ctx.followingRaw=[row("old.android.cache")];
 assert.equal((await android.ctx.pushListSnapshots()).lists,0,
  "Android must not publish an old WebView cache merely because it differs");
 await android.ctx.pullListSnapshots();
 assert.deepEqual(android.ctx.followingRaw.map(r=>r.username),["cloud.following"]);
 android.ctx.followingRaw=[row("new.android.zip")];
 android.ctx.window.igcMarkLocalSnapshotsDirty(["following"]);
 assert.equal((await android.ctx.pushListSnapshots()).lists,1,
  "An explicitly verified Android ZIP import must reach the cloud");
 assert.equal(android.remote.get("following").source_device,"android");
 assert.equal((await android.ctx.pushListSnapshots()).lists,0,
  "Android must not republish a previously synced import");
 assert.equal(android.remote.get("following").item_count,1);
 android.ctx.pendingRequestsRaw=[];
 android.remote.set("pending",snapshot(android,"pending",["old.unaccepted"],ago(90000)));
 android.ctx.window.igcMarkLocalSnapshotsDirty(["pending"]);
 assert.equal((await android.ctx.pushListSnapshots()).lists,1);
 assert.equal(android.remote.get("pending").item_count,0,
  "A verified empty Android Pending ZIP must clear older cloud Pending");

 // Production imports must mark origin only after a successful parse, not on view refresh.
 assert(html.includes("window.igcMarkLocalSnapshotsDirty?.(['following','followers'])"));
 assert(html.includes("window.igcMarkLocalSnapshotsDirty?.(['pending'])"));
 assert(html.includes("...(newFollowing!==null?['following']:[])"));
 console.log("PASS: no stale list republish; newer imports, independent Pending and Instagram account isolation");
})().catch(e=>{console.error(e);process.exitCode=1});
