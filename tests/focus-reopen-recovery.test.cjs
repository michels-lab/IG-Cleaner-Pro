"use strict";
// GRANADA: both real Focus reopen buttons must preserve the original cohort,
// render Reviewed BEFORE tab requests and never stop at a rejected first tab.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const section=(from,to)=>{
 const a=html.indexOf(from),b=html.indexOf(to,a+from.length);
 assert(a>=0&&b>a,"Production Focus recovery source missing: "+from);
 return html.slice(a,b);
};
assert(!html.includes("function openFocusRows("),
 "Do not retain the dead timer-based popup path that falsely claimed profiles were opened");
const runtime=section("function igcReopenSavedFocusBatch(","function markActiveFocusNotReviewed(")
 +"\n"+section("function reopenSafeFocusBatch()","// \"Couldn't review yet\"");
new vm.Script(runtime);
const rows=[
 {username:"confirmed",href:"https://www.instagram.com/confirmed/"},
 {username:"first",href:"https://www.instagram.com/first/"},
 {username:"second",href:"https://www.instagram.com/second/"},
 {username:"third",href:"https://www.instagram.com/third/"}
];
const batch={kind:"main",label:"Focus recovery",rows,openedAt:100,status:"opened_unconfirmed"};
let failedModal=false,falseModal=false,failedHistory=false,failedLog=false,allResolved=false,denyTab=false;
const trace=[],messages=[];
const ctx={
 console:{error:(...x)=>trace.push("error")},
 Date,Array,Set,String,Number,
 activeFocusBatch:batch,activeExtraReviewBatch:batch,
 activeBatchRowResolved:r=>allResolved||r.username==="confirmed",
 showSafeFocusPopup(kind,target,label){
  trace.push("modal");
  assert.equal(kind,"main");
  assert.equal(label,"Focus recovery");
  assert.deepEqual(Array.from(target,r=>r.username),["first","second","third"]);
  if(failedModal)throw Error("DialogUnavailable");
  if(falseModal)return false;
  return true;
 },
 window:{open(url){
  const user=String(url).split("/")[3];
  trace.push("tab:"+user);
  if(denyTab&&user==="first")throw Error("PopupDenied");
  return null; // Chrome noopener may return null after SUCCESS.
 }},
 recordRowsHistory(target,event,details){
  trace.push("history");
  assert.equal(event,"reopen");
  assert.equal(details.kind,"main");
  assert.deepEqual(Array.from(target,r=>r.username),["first","second","third"]);
  if(failedHistory)throw Error("QuotaExceededError");
 },
 logAction(type,message,details){
  trace.push("audit");
  assert.equal(type,"reopen");
  assert.equal(details.count,3);
  if(failedLog)throw Error("QuotaExceededError");
 },
 forceLiveRefresh:()=>trace.push("refresh"),
 msg:(value,level)=>messages.push({value:String(value),level})
};
vm.createContext(ctx);vm.runInContext(runtime,ctx);
const clean=()=>{trace.length=0;messages.length=0};
const noRequests=()=>assert.equal(trace.filter(x=>x.startsWith("tab:")).length,0);
const preserved=()=>assert.equal(ctx.activeFocusBatch,batch,"Original owner cohort remains recoverable");

failedModal=true;
assert.equal(ctx.reopenActiveFocusBatch(),false);
noRequests();assert(!trace.includes("history"));preserved();
assert(messages.some(x=>/mostrar Reviewed/i.test(x.value)));
failedModal=false;clean();

falseModal=true;
assert.equal(ctx.reopenSafeFocusBatch(),false);
noRequests();assert(!trace.includes("history"));preserved();
falseModal=false;clean();

allResolved=true;
assert.equal(ctx.reopenActiveFocusBatch(),false);
assert.equal(trace.length,0,"Resolved/Reviewed profiles cannot be reopened");
allResolved=false;clean();

denyTab=true;
assert.equal(ctx.reopenActiveFocusBatch(),true);
assert.deepEqual(trace.filter(x=>x.startsWith("tab:")),
 ["tab:first","tab:second","tab:third"],
 "A rejected first popup must NOT prevent later profile requests");
assert.equal(trace[0],"modal","Reviewed dialog must be shown BEFORE all Chrome tab requests");
assert(trace.indexOf("history")>trace.indexOf("tab:third"),
 "Reopen history is recorded only AFTER all attempts, not before");
assert(!trace.includes("tab:confirmed"),"Never re-open an already resolved profile");
assert(messages.some(x=>/rechazó 1/i.test(x.value)),
 "One failed popup must be reported with manual direct-link guidance");
assert(trace.includes("audit")&&trace.includes("refresh"));preserved();
denyTab=false;clean();

failedHistory=true;failedLog=true;
assert.equal(ctx.reopenSafeFocusBatch(),true,
 "Secondary history/audit quota errors must not erase an otherwise recoverable cohort");
assert(trace[0]==="modal"&&trace.includes("tab:third"));
assert(messages.some(x=>/historial de reapertura/i.test(x.value)));
assert(messages.some(x=>/auditoría de reapertura/i.test(x.value)));
preserved();failedHistory=false;failedLog=false;clean();

assert.equal(ctx.reopenSafeFocusBatch(),true,
 "Safe Focus Reopen shares the same recoverable, review-first implementation");
assert.deepEqual(trace.filter(x=>x.startsWith("tab:")),["tab:first","tab:second","tab:third"]);
assert.equal(trace[0],"modal");assert(trace.indexOf("history")>trace.indexOf("tab:third"));
assert.equal(ctx.activeFocusBatch,batch);
ctx.activeExtraReviewBatch=null;clean();
assert.equal(ctx.reopenSafeFocusBatch(),false);
noRequests();
console.log("PASS: real Active/Safe Focus reopen, review-first, no resolved reopens, per-popup exception isolation, durable batch and quota warnings");
