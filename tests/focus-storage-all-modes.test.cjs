"use strict";
const fs=require("node:fs"),path=require("node:path"),assert=require("node:assert/strict");
const src=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const lines=src.split("\n");
const spots=lines.map((v,i)=>v.includes("setActiveFocusBatch(")?[i+1,v.trim()]:null).filter(Boolean);
assert(spots.length>=9,"Expected all normal, Recheck, Double Check, and Pending callsites");
for(const [line,text] of spots){
 if(text.startsWith("function setActiveFocusBatch("))continue;
 assert(/if\s*\(\s*setActiveFocusBatch\(|if\s*\(\s*.*setActiveFocusBatch\(/.test(text),
  `Every Focus caller must check persistence before it can open profiles: line ${line}: ${text}`);
 assert(/===false/.test(text),`Caller must explicitly stop on failed save: line ${line}`);
}
const pend=src.slice(src.indexOf("function igcPendingDoubleStart("),src.indexOf("function igcPendingDoubleCheckOne("));
const doubleCohort=pend.indexOf("if(setActiveFocusBatch(");
const cycleCommit=pend.indexOf("try{igcPendingDoubleSaveSeen(nextSeen)}");
const modalReady=pend.lastIndexOf("try{showSafeFocusPopup('pending',chosen,label)}");
const tabRequest=pend.indexOf("chosen.forEach(r=>{try{window.open(");
const openHistory=pend.indexOf("recordRowsHistory(chosen,'open'");
assert(doubleCohort>0,"Pending double-check requires durable active batch");
assert(cycleCommit>doubleCohort&&modalReady>cycleCommit&&tabRequest>modalReady&&openHistory>tabRequest,
 "Double Check must persist the cohort, then its cycle, show Reviewed, request tabs and ONLY THEN journal history");
assert(pend.includes("if(setActiveFocusBatch('pending',chosen,label,'double',true)===false)"),
 "Double Check mode and deferred history must be part of the FIRST durable cohort");
const legacy=src.slice(src.indexOf("function openDoubleCheckNoMeSigueN("),src.indexOf("function resetDoubleCheckCycle(",src.indexOf("function openDoubleCheckNoMeSigueN(")));
assert(legacy.indexOf("if(setActiveFocusBatch(")>0,"Legacy double check must reject failed persistence");
assert(legacy.indexOf("if(setActiveFocusBatch(")<legacy.indexOf("saveDoubleCheckSeen(seen)"),
 "Legacy double check cannot advance cycle before persistence");
console.log("PASS: every Focus callsite guards storage failure before opening tabs or advancing review cycles");
