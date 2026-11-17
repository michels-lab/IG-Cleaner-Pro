"use strict";
// v120.77 regression: native BATCH PREVIEW accepted but no tabs or Reviewed dialog.
// The core must not stop invisibly on quota failures or on window.open exceptions.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function section(start,end){
  const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
  assert(a!==-1&&b>a,"Missing source section: "+start);
  return html.slice(a,b);
}
const src=[
  section("function setActiveFocusBatch(","function clearActiveFocusBatch()"),
  section("function showSafeFocusPopup(","function reopenSafeFocusBatch()"),
  section("function openConfirmedFocusRows(","\n</script>")
].join("\n");
new vm.Script(src);
function scenario({quota=false,openThrows=false}={}){
  const trace=[],messages=[],nodes=new Map();
  const node=id=>{
    if(!nodes.has(id))nodes.set(id,{
      id,textContent:"",innerHTML:"",value:"",disabled:false,style:{display:"none"},
      classList:{add(x){trace.push("class:"+id+":"+x)},remove(){}}
    });
    return nodes.get(id);
  };
  const rows=[
    {username:"example.one",href:"https://www.instagram.com/example.one/",followsBack:false,relationGood:false},
    {username:"example.two",href:"https://www.instagram.com/example.two/",followsBack:false,relationGood:false}
  ];
  const ctx={
    console:{error(e){trace.push("error:"+String(e?.message||e))}},
    Date,Number,Math,JSON,Set,Array,String,
    document:{getElementById:node},
    activeFocusBatch:null,activeExtraReviewBatch:null,
    safeBatchRow:x=>({...x}),recordRowsHistory(){if(quota)throw Error("QuotaExceededError")},
    saveActiveFocusBatch(){if(quota)throw Error("QuotaExceededError")},
    renderActiveBatchDock(){},
    activeBatchRowResolved:()=>false,
    igcWhyOpened:()=>"",igcProfileHistoryText:()=>"",igcReviewChangeInfo:()=>({text:"",changed:false}),
    igcStableRelationInfo:()=>({stable:false}),focusContextHtml:()=>"",
    igcBatchQuality:rs=>({total:rs.length,confirmed:rs.length,changes:0,historical:0,unverifiable:0,stable:0}),
    esc:String,clearActiveFocusBatch(){ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null},
    closeSafeFocusPopup(){node("safeFocusPopup").style.display="none"},
    allMainFocusOpenableRows:()=>rows,focusBatchFill:r=>r,
    igcConfirmBatchQuality(){trace.push("quality");return true},
    msg(txt){messages.push(String(txt))},
    logAction(){},forceLiveRefresh(){},
    pendingOpenedSet:new Set(),savePendingOpened(){},
    window:{open(){trace.push("window.open");if(openThrows)throw Error("BrowserDenied")}},
    lastPendingBatch:[],lastMutualBatch:[]
  };
  vm.createContext(ctx);
  vm.runInContext(src,ctx,{timeout:2000});
  return {ctx,rows,trace,messages,node};
}
// Quota failure must be explicit, not silently stop after owner accepts the dialog.
{
  const x=scenario({quota:true});
  assert.doesNotThrow(()=>x.ctx.openConfirmedFocusRows(x.rows,"foco 30","main",30));
  assert.equal(x.trace.filter(t=>t==="window.open").length,0,
    "Do not visit accounts when the active unconfirmed batch cannot be persisted");
  assert.equal(x.node("safeFocusPopup").style.display,"flex",
    "Show the review/recovery panel even if localStorage is full");
  assert.equal(x.node("safeFocusConfirmBtn").disabled,true,
    "A batch which cannot be persisted must never be marked Reviewed");
  assert(x.messages.some(m=>/almacenamiento|storage/i.test(m)),
    "Explain the failure visibly instead of appearing unresponsive");
}
// Browser rejects every tab: Reviewed/recovery modal still visible, no automatic review.
{
  const x=scenario({openThrows:true});
  assert.equal(x.ctx.openConfirmedFocusRows(x.rows,"foco 30","main",30),true);
  assert.equal(x.node("safeFocusPopup").style.display,"flex");
  assert(x.trace.indexOf("class:safeFocusPopup:show")<x.trace.indexOf("window.open"),
    "Render owner confirmation and direct per-profile links BEFORE attempting popups");
  assert.equal(x.node("safeFocusConfirmBtn").disabled,false);
  assert.equal(x.ctx.activeFocusBatch.rows.length,2);
  assert(x.messages.some(m=>/bloque|navegador|browser|pestañas|popups/i.test(m)));
}
// Normal operation still opens profiles and leaves confirmation pending.
{
  const x=scenario();
  assert.equal(x.ctx.openConfirmedFocusRows(x.rows,"foco 30","main",30),true);
  assert.equal(x.trace.filter(t=>t==="window.open").length,2);
  assert.equal(x.node("safeFocusPopup").style.display,"flex");
  assert.equal(x.node("safeFocusConfirmBtn").disabled,false);
}
console.log("PASS: Focus confirms recoverably under quota failure, browser popup exceptions, and normal batches");
