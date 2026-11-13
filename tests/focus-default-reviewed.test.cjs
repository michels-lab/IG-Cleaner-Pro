"use strict";
// Regression: a newly opened review-confirmation dialog may never inherit a
// previous Pending decision or silently default to Still pending.
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const src=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function body(begin,end){
 const from=src.indexOf(begin),to=src.indexOf(end,from+begin.length);
 assert(from>=0&&to>from,"Missing dialog function "+begin);
 return src.slice(from,to);
}
const nodes=new Map();
function node(id){
 if(!nodes.has(id))nodes.set(id,{
  value:"still_pending",textContent:"",innerHTML:"",style:{},className:"",
  classList:{add(){},remove(){}},setAttribute(){}
 });
 return nodes.get(id);
}
const ctx={
 document:{getElementById:node},activeFocusBatch:null,activeExtraReviewBatch:null,
 setActiveFocusBatch(kind,rows,label){ctx.activeFocusBatch={kind,rows,label,openedAt:Date.now()}},
 activeBatchRowResolved:()=>false,
 igcBatchQuality:rows=>({confirmed:rows.length,total:rows.length,changes:0,historical:0,unverifiable:0,stable:0}),
 igcWhyOpened:()=>"",igcProfileHistoryText:()=>"",igcReviewChangeInfo:()=>({text:"",changed:false}),
 igcStableRelationInfo:()=>({stable:false}),focusContextHtml:()=>"",
 closeSafeFocusPopup:()=>{},clearActiveFocusBatch:()=>{},msg:()=>{},esc:String,
 lastPendingBatch:[],lastMutualBatch:[]
};ctx.window=ctx;
vm.createContext(ctx);
vm.runInContext(body("function showExtraFocusModal(","function reopenExtraFocusBatch()"),ctx);
vm.runInContext(body("function showSafeFocusPopup(","function reopenSafeFocusBatch()"),ctx);
const rows=[{username:"only.fictional",href:"https://www.instagram.com/only.fictional/",relation:"No me sigue"}];
for(const kind of ["main","mutual","followers","pending"]){
 node("extraFocusDecision").value="still_pending";
 ctx.showExtraFocusModal(kind,rows,"focus-"+kind);
 assert.equal(node("extraFocusDecision").value,"reviewed",
  "Extra Focus "+kind+" must reset to Reviewed before manual confirmation");
 node("safeFocusDecision").value="still_pending";
 ctx.activeFocusBatch=null;ctx.activeExtraReviewBatch=null;
 ctx.showSafeFocusPopup(kind,rows,"safe-focus-"+kind);
 assert.equal(node("safeFocusDecision").value,"reviewed",
  "Safe Focus "+kind+" must reset to Reviewed before manual confirmation");
}
assert(src.includes('<option value="reviewed">Reviewed / verified</option>'));
assert(src.includes('<option value="still_pending">Still pending</option>'),
 "Still Pending must remain an explicit user-selectable decision");
assert(src.includes("const decision=document.getElementById('safeFocusDecision')?.value||'reviewed'"),
 "Confirmation must respect owner's actual selected decision");
assert(src.includes("const decision=document.getElementById('extraFocusDecision')?.value||'reviewed'"),
 "Secondary confirmation must also respect owner-selected decision");
console.log("PASS: all Review/Followers/Mutuals/Pending confirmation popups default to Reviewed and retain explicit choice");
