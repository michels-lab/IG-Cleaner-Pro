"use strict";
// GRANADA: historical events can grow enough to exhaust localStorage before
// Focus saves its active batch. Compaction must be lossless and reversible.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const start=html.indexOf("function igcHistoryFieldNames("),end=html.indexOf("function saveGuidedSession100(",start);
assert(start>=0&&end>start,"Missing compact history implementation");
const history={};
for(let i=0;i<789;i++){
 const user="profile."+i;
 history[user]={
  username:user,opened:25,reopened:2,reviewed:1,unconfirmed:0,snoozed:0,
  lastOpened:1234+i,lastReviewed:987654+i,lastDecision:"reviewed",lastSection:"main",
  events:Array.from({length:25},(_,j)=>({ts:1234+i+j,event:"open",
    details:{kind:"main",label:"focus 30",reason:"regular review"}}))
 };
}
history["custom.history"]={
 username:"custom.history",reviewed:9,lastReviewed:null,
 events:[{ts:1,event:"review",details:{decision:"keep"},unknownField:"preserve"},
         ["existing","array",123],
         {ts:4,event:"open",details:{kind:"pending"}}],
 arbitraryCustom:{ownerNote:"keep any other metadata"},
};
const ledgerBefore=JSON.stringify(history);
const stored=new Map([["history",ledgerBefore],["reviewed-ledger",'{"keep.me":{"reviewedAt":1000}}']]);
let failWrites=false;
const log=[];
const ctx={JSON,Date,Array,Number,Object,console:{error:()=>{},warn:(...a)=>log.push(a)},
 LS_PROFILE_HISTORY:"history",profileHistory:{},igcProfileHistoryLoadError:false,
 localStorage:{
  getItem:key=>stored.get(key)||null,
  setItem(key,value){if(failWrites)throw Error("QuotaExceededError");stored.set(key,value)},
  removeItem:key=>stored.delete(key)
 }};
vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
const compact=ctx.igcCompactHistoryText(history);
assert(compact.length<ledgerBefore.length*0.80,
 "789 profiles with 25 events each should shrink by at least 20%");
ctx.loadProfileHistory();
assert.equal(JSON.stringify(ctx.profileHistory),ledgerBefore,
 "Legacy migration must recover all reviews, events and custom history without loss");
assert(stored.get("history").length<ledgerBefore.length*0.80,
 "Legacy storage should be compacted immediately on load to free room for Focus");
assert.equal(stored.get("reviewed-ledger"),'{"keep.me":{"reviewedAt":1000}}',
 "The independent confirmed reviewed ledger must remain unchanged");
ctx.profileHistory["profile.100"].reviewed=2;
ctx.saveProfileHistory();
ctx.profileHistory={};
ctx.loadProfileHistory();
assert.equal(ctx.profileHistory["profile.100"].reviewed,2,
 "Reviews saved after compaction must round-trip");
// Failed migration must leave the old record byte-for-byte unchanged.
stored.set("history",ledgerBefore);failWrites=true;ctx.profileHistory={};
ctx.loadProfileHistory();
assert.equal(JSON.stringify(ctx.profileHistory),ledgerBefore);
assert.equal(stored.get("history"),ledgerBefore);
assert(log.some(a=>a.some(x=>String(x).includes("deferred"))));
// Unknown or structurally invalid data cannot silently erase saved storage.
failWrites=false;stored.set("history",'{"__igcHistoryCompact":2,"rows":[["broken",9]]}');
ctx.loadProfileHistory();
assert.equal(stored.get("history"),'{"__igcHistoryCompact":2,"rows":[["broken",9]]}',
 "Invalid history must not be destructively rewritten");
assert.equal(ctx.igcProfileHistoryLoadError,true,"Invalid saved data must disable profileHistory writes");
assert.throws(()=>ctx.saveProfileHistory(),/Cannot overwrite unreadable saved profile history/,
 "A later action cannot replace unreadable storage with an empty history");
assert.equal(stored.get("history"),'{"__igcHistoryCompact":2,"rows":[["broken",9]]}');
stored.set("history",ledgerBefore);ctx.loadProfileHistory();
assert.equal(ctx.igcProfileHistoryLoadError,false,"Restoring a valid backup should unblock writes");
assert.doesNotThrow(()=>ctx.saveProfileHistory());
console.log("PASS: 789 reviewed profiles, 25 events each, legacy migration, failed writes and protected ledgers");

 
// GRANADA #360/#371: the production bulk history writer must roll back RAM
// when browser storage refuses the append. A later successful save must not
// resurrect uncommitted open/reopen events or duplicate attempted profiles.
const recordsFrom=html.indexOf("function ensureProfileHistory(");
const recordsTo=html.indexOf("function profileHistoryOf(",recordsFrom);
assert(recordsFrom>0&&recordsTo>recordsFrom,"Real bulk history writer missing");
ctx.cleanUsername=username=>String(username||"").trim().toLowerCase();
vm.runInContext(html.slice(recordsFrom,recordsTo),ctx);
const beforeBatch=JSON.stringify(ctx.profileHistory);
const beforeDisk=stored.get("history");
const originalRecord=ctx.profileHistory["profile.100"];
const originalEvents=originalRecord.events;
failWrites=true;
assert.throws(()=>ctx.recordRowsHistory([
 {username:"profile.100"},{username:"brand.new"},{username:"profile.100"}
],"open",{kind:"main",label:"Focus 30"}),/QuotaExceededError/,
 "Rejected history write must report a failure");
assert.equal(JSON.stringify(ctx.profileHistory),beforeBatch,
 "Failed 30-person history append must restore every prior in-memory counter");
assert.equal(stored.get("history"),beforeDisk,
 "Failed history must not modify the durable original");
assert.equal(ctx.profileHistory["profile.100"],originalRecord,
 "Rollback must preserve references to an existing profile record");
assert.equal(ctx.profileHistory["profile.100"].events,originalEvents,
 "Rollback must restore the exact original event array");
assert.equal(ctx.profileHistory["brand.new"],undefined,
 "Rejected new profile events must not survive in memory");
failWrites=false;
ctx.recordRowsHistory([
 {username:"profile.100"},{username:"brand.new"},{username:"profile.100"}
],"open",{kind:"main",label:"Focus 30"});
assert.equal(ctx.profileHistory["profile.100"].opened,27,
 "Successful retry counts two actual repeated rows, not previous failed events");
assert.equal(ctx.profileHistory["brand.new"].opened,1,
 "Previously rejected new row gets exactly one successful open");
const successful=JSON.stringify(ctx.profileHistory);
ctx.profileHistory={};
ctx.loadProfileHistory();
assert.equal(JSON.stringify(ctx.profileHistory),successful,
 "Successful batch must be reconstructible after page reload");
ctx.igcProfileHistoryLoadError=true;
const protectedBefore=JSON.stringify(ctx.profileHistory);
assert.throws(()=>ctx.recordRowsHistory([{username:"phantom"}],"open"),
 /Cannot modify unreadable saved profile history/,
 "Unreadable persisted history must reject append BEFORE any mutation");
assert.equal(JSON.stringify(ctx.profileHistory),protectedBefore);
ctx.igcProfileHistoryLoadError=false;
console.log("PASS: production Focus history bulk writes are atomic in RAM and durable storage across quota/retry/reload");
