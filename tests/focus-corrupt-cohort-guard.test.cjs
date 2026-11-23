"use strict";
// P0 #371/#360 - evaluate actual production Focus persistence and recovery.
// A malformed saved cohort must NEVER be overwritten as an apparently empty
// queue, even after retries, account switching, rejected removal or reload.
const assert=require("node:assert/strict"),fs=require("node:fs");
const path=require("node:path"),vm=require("node:vm");
for(const entry of ["index.html","desktop/ig_cleaner_pro_v120_27_synced_companion.html"]){
  const html=fs.readFileSync(path.join(__dirname,"..",entry),"utf8");
  function part(a,b){
    const x=html.indexOf(a),y=html.indexOf(b,x+a.length);
    assert(x>=0&&y>x,entry+": missing production function "+a);
    return html.slice(x,y);
  }
  const storage=new Map(), alerts=[],seen=[];
  let current="A",denyRead=false,denyWrite=false,denyRemove=false,approve=false;
  const key=k=>current+"::"+k;
  const store={
    getItem(k){if(denyRead)throw Error("SecurityError: denied read");return storage.get(key(k))??null},
    setItem(k,v){if(denyWrite)throw Error("QuotaExceededError: denied write");storage.set(key(k),String(v))},
    removeItem(k){if(denyRemove)throw Error("SecurityError: denied remove");storage.delete(key(k))}
  };
  const ctx={
    localStorage:store,console:{error(){},warn(){}},window:{},JSON,Date,Map,Set,Array,Math,Object,Number,
    LS_ACTIVE_FOCUS_BATCH:"activeFocus",activeFocusBatch:null,activeExtraReviewBatch:null,
    recordRowsHistory:()=>seen.push("history"),renderActiveBatchDock:()=>seen.push("render"),
    renderPendingRequests:()=>{},renderFollowersMutualTab:()=>{},renderModuleDashboard:()=>{},
    msg:(m,t)=>alerts.push([m,t]),confirm:()=>approve
  };
  vm.createContext(ctx);
  vm.runInContext(part("function safeBatchRow(","function activeBatchUserSet("),ctx);
  vm.runInContext(part("function setActiveFocusBatch(","function clearActiveFocusBatch("),ctx);
  vm.runInContext(part("function clearActiveFocusBatch(","function activeBatchRowResolved("),ctx);
  vm.runInContext(part("function forceClearStuckFocusBatch(","function recoverActiveFocusBatch("),ctx);
  const cohort={kind:"main",label:"owner-approved-focus-30",openedAt:5555,status:"opened_unconfirmed",
    rows:Array.from({length:30},(_,i)=>ctx.safeBatchRow({
      username:"person."+i,href:"https://www.instagram.com/person."+i+"/",
      name:"Person "+i,relation:"no_followback",riskScore:i,
      riskLevel:"high",riskReasons:["repeated reason","second reason"],
      iFollow:true,isFollower:i%2===0,followsBack:false
    }))};
  const originalHistory="UNCHANGED-CHRONOLOGY-789",originalReviews="789-previous-decisions";
  storage.set("A::activeFocus",'{invalid-json-saved-original');
  storage.set("A::reviewed",originalReviews);
  storage.set("A::pending","PENDING-ORIGINAL");
  storage.set("A::protected","PROTECTED-ORIGINAL");
  storage.set("A::history",originalHistory);
  const damaged=storage.get("A::activeFocus");
  ctx.loadActiveFocusBatch();
  assert.equal(ctx.igcFocusUnreadableBatch,true,entry+": corrupt cohort must be a blocker");
  assert.equal(ctx.activeFocusBatch,null);
  // A fresh, apparently valid cohort must never replace an unreadable previous one.
  ctx.activeFocusBatch=cohort;
  assert.throws(()=>ctx.saveActiveFocusBatch(),/Una tanda guardada ilegible/);
  assert.equal(storage.get("A::activeFocus"),damaged);
  ctx.activeFocusBatch=null;
  assert.equal(ctx.setActiveFocusBatch("main",cohort.rows,"new batch"),false,
    entry+": Focus opening cannot claim a new saved batch over damaged data");
  assert.equal(ctx.activeFocusBatch,null);
  assert.equal(seen.includes("history"),false);
  assert.equal(storage.get("A::activeFocus"),damaged);
  assert.throws(()=>ctx.clearActiveFocusBatch(),/explicit owner recovery/);
  assert.equal(storage.get("A::activeFocus"),damaged);
  assert.equal(ctx.forceClearStuckFocusBatch(),false,"Deleting damaged evidence needs approval");
  assert.equal(storage.get("A::activeFocus"),damaged);
  approve=true;denyRemove=true;
  assert.equal(ctx.forceClearStuckFocusBatch(),false,
    "Denied disk removal never clears the unreadable saved batch");
  assert.equal(storage.get("A::activeFocus"),damaged);
  assert.equal(ctx.igcFocusUnreadableBatch,true);
  denyRemove=false;approve=false;
  // An independent second account must still operate, without modifying A.
  current="B";ctx.activeFocusBatch=cohort;ctx.saveActiveFocusBatch();
  const exactB=storage.get("B::activeFocus");
  ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
  assert.equal(ctx.igcFocusUnreadableBatch,false,entry+": B must not inherit A's guard");
  assert.equal(ctx.activeFocusBatch.rows.length,30);
  assert.equal(storage.get("A::activeFocus"),damaged);
  // Returning A re-reads its actual saved record; B cannot mask the corruption.
  current="A";ctx.loadActiveFocusBatch();
  assert.equal(ctx.igcFocusUnreadableBatch,true);
  assert.equal(ctx.activeFocusBatch,null);
  // Only the explicit, owner-confirmed destructive cleanup may abandon A's
  // damaged unconfirmed cohort; all earlier decisions/history are untouched.
  approve=true;
  assert.equal(ctx.forceClearStuckFocusBatch(),true);
  assert.equal(storage.has("A::activeFocus"),false);
  assert.equal(ctx.igcFocusUnreadableBatch,false);
  assert.equal(ctx.activeFocusBatch,null);
  assert.equal(storage.get("A::reviewed"),originalReviews);
  assert.equal(storage.get("A::pending"),"PENDING-ORIGINAL");
  assert.equal(storage.get("A::protected"),"PROTECTED-ORIGINAL");
  assert.equal(storage.get("A::history"),originalHistory);
  assert.equal(storage.get("B::activeFocus"),exactB);
  // After successful explicit cleanup, normal saves and reloads work again.
  ctx.activeFocusBatch=cohort;ctx.saveActiveFocusBatch();
  ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
  assert.equal(ctx.activeFocusBatch.rows.length,30);
  assert.equal(ctx.igcFocusUnreadableBatch,false);
  // Read permission errors are also fail-closed and never treated as empty.
  denyRead=true;ctx.loadActiveFocusBatch();
  assert.equal(ctx.igcFocusUnreadableBatch,true);
  assert.throws(()=>ctx.saveActiveFocusBatch(),/Una tanda guardada ilegible/);
  denyRead=false;
  const safe=storage.get("A::activeFocus");
  assert.equal(safe!==null,true);
  ctx.loadActiveFocusBatch();assert.equal(ctx.igcFocusUnreadableBatch,false);
  current="C";ctx.loadActiveFocusBatch();
  assert.equal(ctx.igcFocusUnreadableBatch,false);
  assert.equal(ctx.activeFocusBatch,null,"Genuinely missing C cohort is not corruption");
  assert(alerts.some(([m])=>m.includes("rechazó eliminar la tanda")));
  console.log("PASS "+entry+": malformed Focus preserves bytes and 789 history, blocked overwrite, A-B-A, denied/owner confirmed delete");
}
