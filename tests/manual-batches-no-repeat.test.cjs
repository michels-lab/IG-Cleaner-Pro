"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const src=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function code(start,next){
 const a=src.indexOf(start);assert(a>=0,"Missing "+start);
 const b=src.indexOf(next,a+start.length);assert(b>a,"Missing end marker "+next);
 return src.slice(a,b);
}
const history={},doneSet=new Set(["reviewed.stale"]),reviewedMeta={"meta.reviewed":{mode:"followers"}};
const row=u=>({username:u,href:"https://www.instagram.com/"+u+"/",followsBack:false,relationGood:false,htmlUnknown:false,done:false,protected:false,opened:false,reviewed:false,snoozed:false,riskLevel:"medio",dateMain:1});
const ctx={
 console,Date,Math,Set,Object,Number,String,
 doneSet,reviewedMeta,protectedSet:new Set(),pendingOpenedSet:new Set(),pendingReviewedMeta:{},history,
 profileHistoryOf:user=>history[typeof user==="string"?user:user.username]||null,
 isSnoozed:()=>false,isInActiveFocus:()=>false,tooRepeatedForNormalFocus:()=>false,
 activeBatchRowResolved:()=>false,
 isPendingOpenableForFocus:r=>!r.opened&&!r.reviewed&&!r.snoozed
};
vm.createContext(ctx);
for(const part of [
 code("function isPreviouslyHandledForNormalFocus(","function allMainFocusOpenableRows()"),
 code("function isMutualOpenableForFocus(","function focusFunnelData("),
 code("function isFollowerOpenableForFocus(","function followersReviewedTodayCount("),
 code("function focusBatchFill(","function pendingAnyFocusCandidates()")
])vm.runInContext(part,ctx,{timeout:1500});
const fresh=row("fresh.user"),stale=row("reviewed.stale"),meta=row("meta.reviewed"),
 previouslyOpened=row("opened.user"),olderFollower=row("old.follower"),
 oldMutual=row("old.mutual");
history["opened.user"]={opened:2,lastSection:"main",events:[{event:"open",details:{kind:"main"}}]};
history["old.follower"]={opened:1,lastSection:"followers",events:[{event:"open",details:{kind:"followers"}}]};
history["old.mutual"]={reviewed:1,lastSection:"mutual",events:[{event:"review",details:{kind:"mutual"}}]};
assert(ctx.isMainFocusOpenable(fresh));
for(const r of [stale,meta,previouslyOpened])assert.equal(ctx.isMainFocusOpenable(r),false,
 "Main manual may not recycle "+r.username);
assert.equal(ctx.isMainFocusOpenable({...fresh,htmlUnknown:true}),false);
assert.equal(ctx.isFollowerOpenableForFocus(olderFollower),false);
assert.equal(ctx.isMutualOpenableForFocus(oldMutual),false);
assert.equal(ctx.isFollowerOpenableForFocus(fresh),true);
assert.equal(ctx.isMutualOpenableForFocus(fresh),true);
ctx.pendingOpenedSet.add("pending.open");
assert.equal(ctx.isPreviouslyHandledForNormalFocus(row("pending.open"),"pending"),true);
assert.equal(ctx.isPreviouslyHandledForNormalFocus(row("pending.new"),"pending"),false);
const arr=x=>Array.from(x,r=>r.username);
assert.deepEqual(arr(ctx.focusBatchFill([stale,fresh],[meta,previouslyOpened],20,"main")),["fresh.user"]);
assert.deepEqual(arr(ctx.focusBatchFill([olderFollower,fresh],[meta],20,"followers")),["fresh.user"]);
assert.deepEqual(arr(ctx.focusBatchFill([oldMutual,fresh],[stale],20,"mutual")),["fresh.user"]);
assert.equal(ctx.isFollowerOpenableForFocus(previouslyOpened),true,
 "Opening Review cannot contaminate independent follower-side opener");
const manual=code("function openSelectedPendingTabs()","function openAllSelectedTabs()");
const opened=[];const filtered=[fresh,previouslyOpened,stale,meta];
Object.assign(ctx,{
 filteredRows:filtered,selected:new Set(filtered.map(r=>r.username)),currentMode:"following",
 document:{getElementById:()=>({value:"not_following_back"})},
 nextOpenContext:null,window:{open:href=>opened.push(href)},sessionStats:{opened:0,openBatches:0},
 recordRowsHistory:(rows,event,details)=>rows.forEach(r=>
   history[r.username]={opened:1,lastSection:details.kind,events:[{event,details}]}),
 actionSummaryCounts:()=>({bad:1,good:0}),contextLabel:()=>"manual",
 forceLiveRefresh:()=>{},logAction:()=>{},showVerifyPopup:()=>{},addBatchHistory:()=>{},
 msg:()=>{}
});
vm.runInContext(manual,ctx,{timeout:1500});
ctx.openSelectedPendingTabs();
assert.equal(opened.length,1,"Manual normal batch only opens an unseen account");
ctx.openSelectedPendingTabs();
assert.equal(opened.length,1,"The next batch must not reopen a previously opened profile");
assert.equal(history["fresh.user"].lastSection,"main");
for(const kind of ["main","mutual","followers","pending"]){
 const predicate={main:"isMainFocusOpenable",mutual:"isMutualOpenableForFocus",
  followers:"isFollowerOpenableForFocus",pending:"isPendingOpenableForFocus"}[kind];
 assert(src.includes("igcIsNewChange(r,'"+kind+"')&&"+predicate+"(r)"),
  "New Changes must enforce no-repeat guard for "+kind);
}
assert(src.includes("function openRecheckNotFollowingN("),
 "Explicit Recheck must still exist");
assert(src.includes("Recheck explícito: \${already.length} de \${rows.length}"),
 "Open all selected must warn about already reviewed profiles before explicit re-open");
assert(src.includes("recordRowsHistory(already,'reopen',{kind,label:'manual all selected'})"),
 "Explicit re-open still records the visit in the scoped journal");
console.log("PASS: Review, Mutuals, Followers, Pending ordinary batches never repeat handled profiles; explicit Recheck preserved");
