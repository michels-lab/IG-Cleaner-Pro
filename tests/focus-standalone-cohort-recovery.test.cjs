"use strict";
// Real-source quota/fail-closed acceptance for BOTH app entrypoints. The
// standalone browser must not use a larger/less-safe Focus format than Desktop.
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const assert=require("node:assert/strict");

for(const entry of ["index.html","desktop/ig_cleaner_pro_v120_27_synced_companion.html"]){
  const src=fs.readFileSync(path.join(__dirname,"..",entry),"utf8");
  const extract=(a,b)=>{
    const start=src.indexOf(a),end=src.indexOf(b,start+a.length);
    assert(start>0&&end>start,entry+": missing "+a);
    return src.slice(start,end);
  };
  const codec=extract("function safeBatchRow(","function activeBatchUserSet(");
  const lifecycle=extract("function igcFocusStorageDiagnostic(","function activeBatchRowResolved(");
  new vm.Script(codec+"\n"+lifecycle);
  const memory=new Map([
    ["reviewed",JSON.stringify({permanent:{reviewedAt:100}})],
    ["pending","P".repeat(8000)],
    ["history","H".repeat(12000)]
  ]);
  let cap=Infinity,denyRemoval=false;
  const localStorage={
    getItem:key=>memory.get(key)??null,
    setItem(key,value){
      const total=[...memory].filter(([k])=>k!==key).reduce((n,[k,v])=>n+k.length+v.length,0);
      if(total+key.length+String(value).length>cap){
        const e=Error("quota");e.name="QuotaExceededError";throw e;
      }
      memory.set(key,String(value));
    },
    removeItem(key){
      if(denyRemoval){const e=Error("security");e.name="SecurityError";throw e}
      memory.delete(key);
    }
  };
  const warnings=[],window={igcFocusWriteAttempt:null},trace=[];
  const state={
    JSON,Array,Number,Math,Date,Set,Object,console:{error:()=>{},warn:()=>{}},
    localStorage,window,LS_ACTIVE_FOCUS_BATCH:"focus-cohort",
    activeFocusBatch:null,activeExtraReviewBatch:null,
    renderActiveBatchDock:()=>trace.push("render"),
    recordRowsHistory:()=>trace.push("history"),
    msg:(text)=>warnings.push(String(text))
  };
  vm.createContext(state);vm.runInContext(codec+"\n"+lifecycle,state,{timeout:3000});
  const rows=Array.from({length:30},(_,i)=>({
    username:"target."+i,href:"https://www.instagram.com/target."+i+"/",
    name:"Target "+i,relation:"not_following_back",riskScore:i,
    riskLevel:"high",riskReasons:["suspicious","no_followback"],
    timestamp:123456+i,dateMain:100,dateOther:101,
    iFollow:true,isFollower:i%2===0,followsBack:i%3===0,relationGood:i%4===0
  }));
  const stableBefore=new Map(memory);
  const preview={kind:"main",label:"Focus 30",rows:rows.map(r=>state.safeBatchRow(r)),
    openedAt:Date.now(),status:"opened_unconfirmed"};
  const normal=JSON.stringify(state.igcEncodeActiveFocusBatch(preview));
  const smaller=JSON.stringify(state.igcEncodeFocusBatchQuota(preview));
  assert(smaller.length<normal.length,entry+": compact fallback must reduce active cohort");
  const base=[...memory].reduce((n,[k,v])=>n+k.length+v.length,0);
  cap=base+"focus-cohort".length+smaller.length+10;
  assert.equal(state.setActiveFocusBatch("main",rows,"Focus 30","",true),true);
  assert.equal(trace.filter(x=>x==="history").length,0,
    "Deferred history must not imply browser tabs opened");
  const persisted=memory.get("focus-cohort");
  assert.equal(JSON.parse(persisted).storageFormat,3,
    entry+": quota-limited active Focus must use v3 instead of raw rows");
  assert.equal(memory.get("reviewed"),stableBefore.get("reviewed"));
  assert.equal(memory.get("pending"),stableBefore.get("pending"));
  assert.equal(memory.get("history"),stableBefore.get("history"));
  const originalRef=state.activeFocusBatch;
  cap=1;
  assert.equal(state.setActiveFocusBatch("main",rows,"Rejected cohort","",true),false,
    entry+": exhausted storage must reject a different cohort");
  assert.equal(state.activeFocusBatch,originalRef);
  assert.equal(state.activeExtraReviewBatch,originalRef);
  assert.equal(memory.get("focus-cohort"),persisted);
  assert(warnings.some(x=>x.includes("almacenamiento")),entry+": owner must see storage warning");
  assert(!state.window.igcLastFocusStorageError?.includes("target."),
    "Diagnostics cannot expose private target handles");
  state.activeFocusBatch=null;
  state.loadActiveFocusBatch();
  assert.equal(state.activeFocusBatch.rows.length,30);
  assert.deepEqual(JSON.parse(JSON.stringify(state.activeFocusBatch.rows)),
    JSON.parse(JSON.stringify(preview.rows)));
  denyRemoval=true;
  const savedRef=state.activeFocusBatch;
  assert.throws(()=>state.clearActiveFocusBatch(),/security/);
  assert.equal(state.activeFocusBatch,savedRef,
    "A failed durable removal cannot erase the recoverable RAM cohort");
  assert.equal(memory.get("focus-cohort"),persisted);
  denyRemoval=false;state.clearActiveFocusBatch();
  assert.equal(state.activeFocusBatch,null);
  assert.equal(memory.has("focus-cohort"),false);

  if(entry==="index.html"){
    // Execute the actual standalone Focus button path, not a copied function.
    const mainSource=extract("function openConfirmedFocusRows(","\n</script>");
    new vm.Script(mainSource);
    let opens=0;
    state.window.open=()=>{trace.push("open");opens++};
    state.allMainFocusOpenableRows=()=>rows;
    state.focusBatchFill=actual=>actual;
    state.showSafeFocusPopup=()=>trace.push("review");
    state.logAction=()=>trace.push("log");
    state.forceLiveRefresh=()=>{};
    state.closeSafeFocusPopup=()=>{};
    vm.runInContext(mainSource,state);
    cap=1;
    assert.equal(state.openConfirmedFocusRows(rows,"Focus 30","main",30),false);
    assert.equal(opens,0,"Rejected cohort MUST NOT request any Chrome tab");
    assert(!trace.includes("review"),"Rejected cohort cannot offer a false confirmation");
    cap=Infinity;
    assert.equal(state.openConfirmedFocusRows(rows,"Focus 30","main",30),true);
    assert.equal(opens,30,"Recovered Focus must request all 30 profile tabs");
    assert(trace.indexOf("review")>=0&&trace.indexOf("review")<trace.indexOf("open"),
      "Reviewed recovery must be visible before popups are requested");
  }
  console.log("PASS "+entry+": saved v3 Focus, full quota, retry, exact old reviews, durable removal and standalone browser guard");
}
