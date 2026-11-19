"use strict";
// A failed-open cohort must not become permanently visited: when the owner
// EXPLICITLY selects "Couldn't review yet", only that unconfirmed set may be
// retried. Real reviews and completed/previously-opened rows stay excluded.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const begin=html.indexOf("function isPreviouslyHandledForNormalFocus(");
const end=html.indexOf("function isMainFocusOpenable(",begin);
assert(begin!==-1&&end>begin,"Normal Focus history guard missing");
const source=html.slice(begin,end);
const ctx={doneSet:new Set(),reviewedMeta:{},pendingOpenedSet:new Set(),pendingReviewedMeta:{},stored:{}};
ctx.profileHistoryOf=u=>ctx.stored[u]||null;vm.createContext(ctx);vm.runInContext(source,ctx);
const fake={username:"pending.alpha"};
const ev=(event,kind="main")=>({event,details:{kind}});
const run=(events,lastSection="main")=>{
 ctx.stored["pending.alpha"]={opened:1,reopened:0,reviewed:0,lastSection,events};
 return ctx.isPreviouslyHandledForNormalFocus(fake,"main");
};
// Without explicit owner declaration, old attempts stay excluded (no repeats).
assert.equal(run([ev("open")]),true);
assert.equal(run([ev("open"),ev("reopen")]),true);
// Owner explicitly could NOT review -> eligible to retry, never counted as Reviewed.
assert.equal(run([ev("open"),ev("unconfirmed")]),false);
assert.equal(run([ev("open"),ev("unconfirmed"),ev("open")]),true,
 "Once a real new attempt happens, don't automatically repeat it");
assert.equal(run([ev("open"),ev("unconfirmed"),ev("review")]),true);
// Unconfirmed in unrelated module cannot release a main attempt.
assert.equal(run([ev("open"),ev("unconfirmed","pending")]),true);
// Saved review wins even if an explicit unconfirmed event follows.
ctx.doneSet.add(fake.username);
assert.equal(run([ev("open"),ev("review"),ev("unconfirmed")]),true);
ctx.doneSet.clear();ctx.reviewedMeta[fake.username]={reviewedAt:Date.now()};
assert.equal(run([ev("open"),ev("unconfirmed")]),true);
ctx.reviewedMeta={};
// Legacy opened rows without events remain blocked from normal Focus.
assert.equal(run([]),true);

const unconfirmedStart=html.indexOf("function igcPersistUnconfirmedAttempt(");
const unconfirmedEnd=html.indexOf("function confirmSafeFocusReviewed(",unconfirmedStart);
assert(unconfirmedStart!==-1&&unconfirmedEnd>unconfirmedStart);
const unconfirmedSource=html.slice(unconfirmedStart,unconfirmedEnd);
function checkRetrySaveFailure(fail){
 let closed=false;
 const messages=[],user="pending.alpha",prior={username:user,opened:1,events:[{event:"open",details:{kind:"main"}}]};
 const batch={kind:"main",rows:[{username:user}],label:"foco 30",openedAt:Date.now()};
 const q={
  profileHistory:{[user]:JSON.parse(JSON.stringify(prior))},
  activeExtraReviewBatch:batch,activeFocusBatch:batch,Date,JSON,console:{error(){}},
  recordProfileHistory(u,event,details){q.profileHistory[u].events.push({event,details})},
  saveProfileHistory(){if(fail)throw Error("QuotaExceededError")},
  recordRowsHistory(rows,event,details){
   // Production history writer restores RAM if the browser rejects the write.
   const original=JSON.stringify(q.profileHistory);
   try{rows.forEach(row=>q.recordProfileHistory(row.username,event,details));q.saveProfileHistory();}
   catch(error){q.profileHistory=JSON.parse(original);throw error;}
  },
  msg:m=>messages.push(String(m)),
  logAction(){},buildRows(){},applyFilters(){},renderModuleDashboard(){},
  clearActiveFocusBatch(){closed=true;q.activeExtraReviewBatch=null;q.activeFocusBatch=null},
  closeSafeFocusPopup(){},closeExtraFocusModal(){},maybeContinueGuidedSession(){}
 };
 vm.createContext(q);vm.runInContext(unconfirmedSource,q);
 assert.doesNotThrow(()=>q.markSafeFocusNotReviewed());
 return {closed,messages,prior,history:q.profileHistory[user],batch:q.activeFocusBatch};
}
{
 const failure=checkRetrySaveFailure(true);
 assert.equal(failure.closed,false,"If requeue cannot persist, keep batch recoverable");
 assert.equal(JSON.stringify(failure.history),JSON.stringify(failure.prior),"Rollback in-memory unconfirmed event on failed save");
 assert(failure.batch,"Do not discard unconfirmed batch when save failed");
 assert(failure.messages.some(m=>/almacenamiento|guardar|storage/i.test(m)),"Explain storage issue to owner");
}
{
 const success=checkRetrySaveFailure(false);
 assert.equal(success.closed,true,"Persisted explicit owner release clears batch");
 assert.equal(success.history.events.at(-1).event,"unconfirmed");
}

console.log("PASS: a failed owner-confirmed Focus attempt can be retried without recycling reviewed or unrelated profiles");
