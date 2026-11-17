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
assert(pend.indexOf("if(setActiveFocusBatch(")>0,"Pending double-check requires durable active batch");
assert(pend.indexOf("if(setActiveFocusBatch(")<pend.indexOf("seen.add("),
 "Pending second-review cycle cannot advance before active batch persists");
const legacy=src.slice(src.indexOf("function openDoubleCheckNoMeSigueN("),src.indexOf("function resetDoubleCheckCycle(",src.indexOf("function openDoubleCheckNoMeSigueN(")));
assert(legacy.indexOf("if(setActiveFocusBatch(")>0,"Legacy double check must reject failed persistence");
assert(legacy.indexOf("if(setActiveFocusBatch(")<legacy.indexOf("saveDoubleCheckSeen(seen)"),
 "Legacy double check cannot advance cycle before persistence");
console.log("PASS: every Focus callsite guards storage failure before opening tabs or advancing review cycles");
