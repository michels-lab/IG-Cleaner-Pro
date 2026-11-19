"use strict";
// GRANADA: a failed second attempt is NOT an undo of a prior review.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const a=html.indexOf("function igcPersistUnconfirmedAttempt("),b=html.indexOf("function confirmSafeFocusReviewed(",a);
assert(a>=0&&b>a,"Missing non-destructive Focus recovery");
const source=html.slice(a,b);
function scenario(kind,{double=false,quota=false,pendingSaveFail=false}={}){
 const oldReview={reviewedAt:101,decision:"keep",reviewSource:"prior_saved_review"};
 const oldHistory={username:"already.reviewed",opened:5,reviewed:1,events:[{event:"review",details:{kind:"prior"}}]};
 const active={kind,label:"Recheck 30",reviewMode:double?"double":undefined,
   rows:[{username:"already.reviewed"},{username:"not.reviewed"}],openedAt:102};
 let cleared=false;
 const storage=new Map();
 const messages=[];
 const c={
  Date,JSON,Set,console:{error(){}},
  LS_PENDING_OPENED:'pending-opened',
  localStorage:{
    getItem:key=>storage.get(key)??null,
    setItem(key,value){if(pendingSaveFail)throw Error('QuotaExceededError');storage.set(key,String(value))},
    removeItem:key=>storage.delete(key)
  },
  activeFocusBatch:active,activeExtraReviewBatch:active,
  profileHistory:{"already.reviewed":JSON.parse(JSON.stringify(oldHistory))},
  pendingOpenedSet:new Set(["already.reviewed","not.reviewed"]),
  pendingReviewedMeta:{"already.reviewed":JSON.parse(JSON.stringify(oldReview))},
  reviewedMeta:{"already.reviewed":JSON.parse(JSON.stringify(oldReview))},
  doneSet:new Set(["already.reviewed"]),
  recordProfileHistory(name,event,details){
   if(!c.profileHistory[name])c.profileHistory[name]={username:name,events:[]};
   c.profileHistory[name].events.push({event,details});
  },
  saveProfileHistory(){if(quota)throw Error("QuotaExceededError")},
  recordRowsHistory(rows,event,details){
    const previous=JSON.stringify(c.profileHistory);
    try{rows.forEach(row=>c.recordProfileHistory(row.username,event,details));c.saveProfileHistory();}
    catch(error){c.profileHistory=JSON.parse(previous);throw error;}
  },
  savePendingOpened(){if(pendingSaveFail)throw Error("QuotaExceededError")},
  saveReviewedMeta(){throw Error("A retry must NEVER rewrite the Reviewed ledger")},
  savePendingReviewedMeta(){throw Error("A retry must NEVER rewrite the Pending review ledger")},
  saveSet(){throw Error("A retry must NEVER rewrite the Done set")},
  msg:m=>messages.push(String(m)),
  logAction(){},buildRows(){},applyFilters(){},renderModuleDashboard(){},
  renderPendingRequests(){},renderFollowersAllWorkspace(){},renderFollowersMutualTab(){},
  clearActiveFocusBatch(){cleared=true;c.activeFocusBatch=null;c.activeExtraReviewBatch=null},
  closeSafeFocusPopup(){},closeExtraFocusModal(){},maybeContinueGuidedSession(){},
  forceClearStuckFocusBatch(){throw Error("Should have a valid cohort")}
 };
 vm.createContext(c);vm.runInContext(source,c);
 return {c,oldHistory,oldReview,messages,run:()=>c.markSafeFocusNotReviewed(),get cleared(){return cleared}};
}
for(const kind of ["pending","followers","mutual","main"]){
 const x=scenario(kind);
 assert.doesNotThrow(()=>x.run(),"Not-review action must not crash: "+kind);
 assert.equal(x.cleared,true,"Successful retry release closes cohort: "+kind);
 assert.equal(x.c.doneSet.has("already.reviewed"),true,"Historical Done is monotonic: "+kind);
 assert.deepEqual(JSON.parse(JSON.stringify(x.c.reviewedMeta["already.reviewed"])),x.oldReview,
   "Historical Reviewed metadata remains intact: "+kind);
 assert.deepEqual(JSON.parse(JSON.stringify(x.c.pendingReviewedMeta["already.reviewed"])),x.oldReview,
   "Historical Pending decision remains intact: "+kind);
 assert.equal(x.c.profileHistory["already.reviewed"].events[0].event,"review",
   "Historical review event remains first: "+kind);
 assert.equal(x.c.profileHistory["already.reviewed"].events.at(-1).event,"unconfirmed",
   "New attempt is only an unconfirmed event: "+kind);
 if(kind==="pending"){
  assert.equal(x.c.pendingOpenedSet.has("already.reviewed"),true,
    "Previously confirmed pending opens are not released");
  assert.equal(x.c.pendingOpenedSet.has("not.reviewed"),false,
    "Only genuinely unreviewed pending attempts become retryable");
 }
}
{
 const x=scenario("pending",{double:true});x.run();
 assert.equal(x.cleared,true);
 assert.equal(x.c.pendingOpenedSet.has("already.reviewed"),true);
 assert.equal(x.c.pendingOpenedSet.has("not.reviewed"),true,
   "Double Check must not erase either earlier Pending open reservation");
 assert.deepEqual(JSON.parse(JSON.stringify(x.c.pendingReviewedMeta["already.reviewed"])),x.oldReview);
}
for(const kind of ["pending","followers","mutual","main"]){
 const x=scenario(kind,{quota:true}),before=JSON.stringify(x.c.profileHistory);
 x.run();
 assert.equal(x.cleared,false,"Failed history save keeps original cohort: "+kind);
 assert.equal(JSON.stringify(x.c.profileHistory),before,
   "Failed history save rolls back unsaved attempt in memory: "+kind);
 assert.equal(x.c.pendingOpenedSet.size,2);
 assert(x.messages.some(m=>/almacenamiento|guardar/i.test(m)));
}
{
 const x=scenario("pending",{pendingSaveFail:true});x.run();
 assert.equal(x.cleared,false,"Blocked Pending open-ledger update keeps active cohort");
 assert.equal(x.c.pendingOpenedSet.size,2,"No half-updated Pending open set in memory");
 assert(x.messages.some(m=>/almacenamiento/i.test(m)));
}
console.log("PASS: inconclusive Focus never undoes prior Reviewed/Pending in all modes or quota errors");
