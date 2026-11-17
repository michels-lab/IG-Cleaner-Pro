"use strict";
// Granadas: compact Focus storage must round-trip without mutating reviewed ledgers.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const from=html.indexOf("function safeBatchRow("),to=html.indexOf("function activeBatchUserSet(",from);
assert(from>=0&&to>from,"Missing Focus cohort storage implementation");
const source=html.slice(from,to);
const storage=new Map();
let limit=Infinity;
const ctx={
 JSON,Array,Set,Date,console,
 LS_ACTIVE_FOCUS_BATCH:"focus-test",
 activeFocusBatch:null,
 localStorage:{
  setItem(key,value){if(value.length>limit)throw Error("QuotaExceededError");storage.set(key,value)},
  getItem:key=>storage.get(key)||null,
  removeItem:key=>storage.delete(key)
 }
};
vm.createContext(ctx);vm.runInContext(source,ctx);
const rows=Array.from({length:30},(_,i)=>({
 username:"member"+i,href:"https://www.instagram.com/member"+i+"/",
 name:"Member "+i,relation:"not_following_back",riskScore:i,riskLevel:"medium",
 riskReasons:["reason a","reason b"],timestamp:123456+i,dateMain:100,dateOther:101,
 iFollow:true,isFollower:false,followsBack:false,relationGood:false
}));
const cohort={kind:"main",label:"foco 30",openedAt:1234,status:"opened_unconfirmed",
 rows:rows.map(r=>ctx.safeBatchRow(r))};
const oldString=JSON.stringify(cohort);
const compact=JSON.stringify(ctx.igcEncodeActiveFocusBatch(cohort));
assert(compact.length<oldString.length*0.80,"Compact payload should save >20% for typical 30-person cohort");
limit=Math.floor((oldString.length+compact.length)/2);
ctx.activeFocusBatch=cohort;
ctx.saveActiveFocusBatch();
assert.equal(JSON.parse(storage.get("focus-test")).storageFormat,2);
ctx.activeFocusBatch=null;
ctx.loadActiveFocusBatch();
assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),JSON.parse(JSON.stringify(cohort)),
 "Compact save/reload must restore every safeBatchRow field losslessly");
assert(!storage.has("reviewed")&&!storage.has("pending"),
 "Focus persistence must not write review or pending ledgers");
// Legacy v120.78 records still load, without destructive migration or changes.
storage.set("focus-test",oldString);ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),JSON.parse(JSON.stringify(cohort)));
ctx.saveActiveFocusBatch();
assert.equal(JSON.parse(storage.get("focus-test")).storageFormat,2);
// A quota too small even for compact storage must fail closed without overwriting history.
const prior=storage.get("focus-test");
limit=1;
assert.throws(()=>ctx.saveActiveFocusBatch(),/QuotaExceededError/);
assert.equal(storage.get("focus-test"),prior,"Storage failures must preserve last durable batch");
console.log("PASS: compact Focus storage, 30 profiles, legacy format, near-quota recovery and fail-closed persistence");
