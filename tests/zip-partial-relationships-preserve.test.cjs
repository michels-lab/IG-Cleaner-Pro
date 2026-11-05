"use strict";
/* GRANADA: source-real partial ZIP import atomicity; synthetic users only. */
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const a=html.indexOf("function zipImportScope(){"),
 b=html.indexOf("window.igcHandleZipInput=async function(file){",a);
assert(a>=0&&b>a,"Real integrated ZIP core must be available");
const logs=[],parseCalls=[],capture=[],pendingCalls=[],nodes=new Map();
const origFollowing=[{username:"prior.following"},{username:"protected.following"}];
const origFollowers=[{username:"prior.follower"}];
const ctx={console,Math,Map,Set,Array,Object,JSON,Date,Number,String,
  followingRaw:origFollowing,followersRaw:origFollowers,
  followingMap:new Map(origFollowing.map(r=>[r.username,r])),
  followersMap:new Map(origFollowers.map(r=>[r.username,r])),
  diagData:[{old:true}],selected:new Set(["previous-selection"]),
  q:id=>{if(!nodes.has(id))nodes.set(id,{checked:false});return nodes.get(id)},
  basename:p=>String(p).split("/").pop(),
  logAction:(kind,label,details)=>logs.push({kind,label,details}),
  parseFiles:async(files,kind)=>{parseCalls.push({kind,count:files.length});
    return files.flatMap(file=>file?.rows||[])},
  parseZipPending:async(items)=>{pendingCalls.push(items.length);
    if(items.some(x=>x.throwError))throw Error("Invalid pending file: protected snapshot");
    return items.some(x=>x.isPending)?5:0},
  parseZipExtras:async()=>[],
  buildRows:()=>{},setFullDateRange:()=>{},applyFilters:()=>{},
  autoCleanGarbageStates:()=>{},renderDiag:()=>{},renderFocusLab:()=>{},
  renderPendingRequests:()=>{},renderSectionRealtimePanels:()=>{},
  renderModuleDashboard:()=>{},renderProfileStats:()=>{},
  v113RefreshAll:()=>{},igcRenderPrecisionAudit:()=>{}
};
ctx.window=ctx;
ctx.igcCaptureZipRelationshipHistory=()=>capture.push("captured");
vm.createContext(ctx);vm.runInContext(html.slice(a,b),ctx,{timeout:4000});
const file=(name,rows,data,format="json")=>({entry:{name},file:{name,rows},
 payload:{format,data}});
const follow=(names)=>file("following.json",names.map(username=>({username})),
 {relationships_following:names.map(username=>({title:username}))});
const followers=(names)=>file("followers_1.json",names.map(username=>({username})),
 names.map(username=>({string_list_data:[{value:username}]})));
const same=(list,prior)=>assert.deepEqual(Array.from(list,x=>x.username),prior);
(async()=>{
 // A ZIP containing ONLY outgoing Pending must not drop saved follower/following
 // lists or manufacture their counts. No historical relationship capture.
 let out=await ctx.applyZipCore({pending_follow_requests:[{isPending:true}]}, "pending-only.zip");
 same(ctx.followingRaw,["prior.following","protected.following"]);
 same(ctx.followersRaw,["prior.follower"]);
 assert.deepEqual([out.following,out.followers,out.pending],[0,0,5]);
 assert.equal(out.preservedFollowing,true);
 assert.equal(out.preservedFollowers,true);
 assert.equal(capture.length,0);
 assert.equal(logs.at(-1).details.count,5);
 // Import Following alone: preserve existing followers and report only new rows.
 out=await ctx.applyZipCore({following:[follow(["new.one","new.two","new.three"])]}, "following-only.zip");
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 same(ctx.followersRaw,["prior.follower"]);
 assert.deepEqual([out.following,out.followers],[3,0]);
 assert.equal(out.preservedFollowers,true);
 assert.equal(ctx.followingMap.has("prior.following"),false);
 assert.equal(ctx.followersMap.has("prior.follower"),true);
 assert.equal(capture.length,1);
 // Import Followers alone: no clearing the newer Following.
 out=await ctx.applyZipCore({followers:[followers(["new.follower"])]},"followers-only.zip");
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 same(ctx.followersRaw,["new.follower"]);
 assert.deepEqual([out.following,out.followers],[0,1]);
 assert.equal(out.preservedFollowing,true);
 // One invalid follower file must reject the ENTIRE staged following+follower
 // import before modifying any list or relationship history.
 const beforeCapture=capture.length;
 await assert.rejects(()=>ctx.applyZipCore({following:[follow(["would.overwrite"])],
  followers:[file("followers_2.json",[],null,"invalid-json")]},
  "partial-invalid.zip"),/Se conservaron las listas anteriores/);
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 same(ctx.followersRaw,["new.follower"]);
 assert.equal(capture.length,beforeCapture);
 // Valid JSON with users but parser returning zero is NOT evidence of empty.
 await assert.rejects(()=>ctx.applyZipCore({
  following:[file("following.json",[],{relationships_following:[{title:"unreadable"}]})]
 },"wrong-structure.zip"),/sin usuarios verificables/);
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 // A malformed Pending source also cannot publish previously staged Following.
 await assert.rejects(()=>ctx.applyZipCore({
  following:[follow(["would.overwrite"])],pending_follow_requests:[{throwError:true}]
 },"bad-pending.zip"),/Invalid pending file/);
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 // An EXPLICIT JSON empty Followers list, unlike a missing file, is genuine
 // and may replace that one list while retaining the distinct Following list.
 out=await ctx.applyZipCore({followers:[followers([])]},"empty-followers.zip");
 same(ctx.followersRaw,[]);
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 assert.equal(out.followers,0);
 assert.equal(out.preservedFollowers,false);
 assert.equal(ctx.followersMap.size,0);
 // If only Pending is present again, the verified empty Followers remains empty.
 out=await ctx.applyZipCore({pending_follow_requests:[{isPending:true}]}, "another-pending.zip");
 same(ctx.followersRaw,[]);
 same(ctx.followingRaw,["new.one","new.two","new.three"]);
 assert.equal(capture.length,3);
 assert.equal(logs.at(-1).details.count,5);
 assert(!parseCalls.some(x=>x.count===0),"Absent list files must never invoke the parser");

 // A ZIP may take several seconds to read or parse. It must never publish
 // to whichever Instagram workspace happens to be selected at the end.
 ctx.IGC_INSTAGRAM_PROFILES={owner:"u_owner",active:"ig_first",verified:true};
 const frozen=ctx.zipImportScope(),oldParse=ctx.parseFiles,oldPendingCalls=pendingCalls.length;
 const priorFollowing=ctx.followingRaw.map(r=>r.username);
 const priorFollowers=ctx.followersRaw.map(r=>r.username);
 const priorSnapshots=capture.length;
 ctx.parseFiles=async()=>{ctx.IGC_INSTAGRAM_PROFILES.active="ig_second";
  return [{username:"wrong.account.import"}]};
 await assert.rejects(()=>ctx.applyZipCore({
  following:[follow(["wrong.account.import"])]},"slow-changed-owner.zip",frozen),
  /Cambió la cuenta o el perfil de Instagram/,
  "Switch during an awaited parse must abort before any ZIP list is published");
 same(ctx.followingRaw,priorFollowing);
 same(ctx.followersRaw,priorFollowers);
 assert.equal(pendingCalls.length,oldPendingCalls,
  "No Pending snapshot may be touched after a late owner-switch veto");
 assert.equal(capture.length,priorSnapshots);
 ctx.parseFiles=oldParse;
 ctx.IGC_INSTAGRAM_PROFILES.active="ig_first";
 const successful=await ctx.applyZipCore({
  following:[follow(["correct.workspace"])],pending_follow_requests:[{isPending:true}]
 },"same-owner.zip",frozen);
 assert.equal(successful.following,1,"Unchanged original scope may commit normally");
 same(ctx.followingRaw,["correct.workspace"]);
 ctx.IGC_INSTAGRAM_PROFILES.owner="u_other";
 await assert.rejects(()=>ctx.applyZipCore({
  following:[follow(["never.cross-owner"])]},"different-owner.zip",frozen),
  /Cambió la cuenta o el perfil de Instagram/,
  "Changing the app login also invalidates the captured ZIP target");
 same(ctx.followingRaw,["correct.workspace"]);
 console.log("PASS: partial ZIP retains lists, and delayed import aborts on workspace/account switch without Pending or Following writes");
})().catch(error=>{console.error(error);process.exitCode=1});
