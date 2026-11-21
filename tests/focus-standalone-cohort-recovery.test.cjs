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
    // Execute the real standalone pause/Retry/Focus path, NOT test copies.
    // Deliberately use a mutable DOM mock to verify the user cannot click
    // Reviewed, reopen, or snooze an unsaved/never-opened failed cohort.
    const mainSource=extract("let igcFailedFocusBatch=null;","\n</script>");
    new vm.Script(mainSource);
    const ids=[
      "safeFocusPopup","safeFocusTitle","safeFocusText","safeConfirmPreview",
      "safeFocusList","safeFocusConfirmBtn","safeFocusReopenBtn",
      "safeFocusNotReviewedBtn","safeFocusSnooze7Btn","safeFocusSnooze30Btn",
      "safeFocusDecision","safeFocusRetryStorageBtn"
    ];
    const ui=new Map(ids.map(id=>[id,{
      style:{display:"none"},classList:{add(){},remove(){}},
      textContent:"",innerHTML:"",disabled:false
    }]));
    state.document={getElementById:id=>ui.get(id)||null};
    state.esc=str=>String(str).replaceAll("&","&amp;").replaceAll("<","&lt;");
    state.currentMode="following";
    state.window.IGC_INSTAGRAM_PROFILES={active:"A"};
    let opens=0;
    state.window.open=()=>{trace.push("open");opens++};
    state.allMainFocusOpenableRows=()=>rows;
    state.focusBatchFill=actual=>actual;
    state.showSafeFocusPopup=()=>trace.push("review");
    const actions=[];
    state.logAction=(type,text)=>actions.push(String(text));
    state.forceLiveRefresh=()=>{};
    state.closeSafeFocusPopup=()=>{};
    vm.runInContext(mainSource,state,{timeout:3000});
    for(const id of [
      "safeFocusConfirmBtn","safeFocusReopenBtn","safeFocusNotReviewedBtn",
      "safeFocusSnooze7Btn","safeFocusSnooze30Btn","safeFocusRetryStorageBtn"
    ])assert(src.includes('id="'+id+'"'),entry+": visible recovery control "+id);
    cap=1;
    const beforeBlocked=new Map(memory);
    assert.equal(state.openConfirmedFocusRows(rows,"Focus 30","main",30),false);
    assert.equal(opens,0,"Rejected cohort MUST NOT request any Chrome tab");
    assert(!trace.includes("review"),"Rejected cohort cannot offer a false confirmation");
    assert.equal(ui.get("safeFocusTitle").textContent,"Focus pausado · almacenamiento");
    assert.equal(ui.get("safeFocusRetryStorageBtn").style.display,"block");
    assert.equal(ui.get("safeFocusConfirmBtn").disabled,true);
    assert.equal(ui.get("safeFocusReopenBtn").disabled,true);
    assert.equal(ui.get("safeFocusNotReviewedBtn").disabled,true);
    assert.equal(ui.get("safeFocusDecision").disabled,true);
    assert.equal(ui.get("safeFocusList").innerHTML.includes("Sin abrir · guardado fallido"),true);
    assert.equal(ui.get("safeFocusText").textContent.includes("Reintentar guardar y abrir"),true);
    assert(!ui.get("safeFocusText").textContent.includes("target."),
      "Storage error diagnostics must never disclose private usernames");
    assert.deepEqual([...memory],[...beforeBlocked],"Quota error must preserve every stored byte");
    assert.equal(vm.runInContext("igcFailedFocusBatch.rows.length",state),30);

    // Owner switches accounts after a failure. Retry must never borrow A's
    // saved preview to open in B or in a different mode.
    cap=Infinity;
    state.window.IGC_INSTAGRAM_PROFILES.active="B";
    assert.equal(state.igcRetryFailedFocus(),false);
    assert.equal(opens,0);
    state.window.IGC_INSTAGRAM_PROFILES.active="A";
    state.currentMode="pending";
    assert.equal(state.igcRetryFailedFocus(),false);
    assert.equal(opens,0);
    state.currentMode="following";

    // Even if current live list / ZIP changes between failure and retry,
    // the explicit Retry must use exactly the original 30 saved usernames.
    state.focusBatchFill=()=>{throw Error("Retry may NOT refill from changed ZIP")};
    assert.equal(state.igcRetryFailedFocus(),true);
    assert.equal(opens,30,"Explicit Retry must request precisely 30 original Chrome tabs");
    assert(trace.indexOf("review")>=0&&trace.indexOf("review")<trace.indexOf("open"),
      "Reviewed recovery must be visible before popups are requested");
    assert.equal(ui.get("safeFocusConfirmBtn").disabled,false);
    assert.equal(ui.get("safeFocusRetryStorageBtn").style.display,"none");
    assert.equal(vm.runInContext("igcFailedFocusBatch",state),null);
    const persistedAfterRetry=state.igcDecodeActiveFocusBatch(JSON.parse(memory.get("focus-cohort")));
    assert.deepEqual(persistedAfterRetry.rows.map(x=>x.username),rows.map(x=>x.username));
    assert.deepEqual(memory.get("reviewed"),stableBefore.get("reviewed"));
    assert.deepEqual(memory.get("pending"),stableBefore.get("pending"));
    assert.deepEqual(memory.get("history"),stableBefore.get("history"));
    assert(actions.every(t=>!t.includes("perfiles abiertos")),
      "Window.open with noopener does not prove that Chrome really opened a tab");
    assert(actions.some(t=>t.includes("pestañas solicitadas")),
      "The audit must count requests, not claim that accounts were visited");

    // Pending has an extra opened/visited-cycle ledger. A quota rejection
    // there MUST roll back the RAM counter and request NO Chrome tabs, even
    // though the separate active cohort was already saved successfully.
    state.clearActiveFocusBatch();
    const existingPending=["prior.pending"];
    state.pendingOpenedSet=new Set(existingPending);
    memory.set("pending-opened",JSON.stringify(existingPending));
    let rejectPendingLedger=true;
    state.savePendingOpened=()=>{
      if(rejectPendingLedger){const e=Error("quota");e.name="QuotaExceededError";throw e}
      localStorage.setItem("pending-opened",JSON.stringify([...state.pendingOpenedSet]));
    };
    state.pendingAnyFocusCandidates=()=>rows;
    state.focusBatchFill=selected=>selected;
    const opensBeforePending=opens,historyBefore=memory.get("history");
    assert.equal(state.openConfirmedFocusRows(rows,"Pending Focus 30","pending",30),false);
    assert.equal(opens,opensBeforePending,
      "Pending second-ledger quota rejection cannot request Chrome tabs");
    assert.equal(ui.get("safeFocusTitle").textContent,
      "Pending Focus pausado · guardado incompleto");
    assert.deepEqual([...state.pendingOpenedSet],existingPending,
      "Pending RAM counter must be rolled back after save refusal");
    assert.equal(memory.get("pending-opened"),JSON.stringify(existingPending),
      "Saved Pending previous decisions cannot change when second key fails");
    assert.equal(state.activeFocusBatch.kind,"pending",
      "Already-durable Pending cohort stays recoverable for manual review");
    assert.equal(memory.get("history"),historyBefore,
      "No phantom open history for rejected Pending cycle");
    state.clearActiveFocusBatch();
    rejectPendingLedger=false;
    assert.equal(state.openConfirmedFocusRows(rows,"Pending Focus 30","pending",30),true);
    assert.equal(opens,opensBeforePending+30);
    assert.equal(JSON.parse(memory.get("pending-opened")).length,31);
    assert(JSON.parse(memory.get("pending-opened")).includes("prior.pending"));
    assert.equal(memory.get("reviewed"),stableBefore.get("reviewed"),
      "Pending opening must not mutate Reviewed confirmations");
  }
  console.log("PASS "+entry+": saved v3 Focus, full quota, retry, exact old reviews, durable removal and standalone browser guard");
}
