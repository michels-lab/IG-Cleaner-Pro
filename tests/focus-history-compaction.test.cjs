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
 LS_PROFILE_HISTORY:"history",profileHistory:{},
 localStorage:{
  getItem:key=>stored.get(key)||null,
  setItem(key,value){if(failWrites)throw Error("QuotaExceededError");stored.set(key,value)},
  removeItem:key=>stored.delete(key)
 }};
vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
const compact=ctx.igcCompactHistoryText(history);
assert(compact.length<ledgerBefore.length*0.75,
 "789 profiles with 25 events each should shrink materially");
ctx.loadProfileHistory();
assert.equal(JSON.stringify(ctx.profileHistory),ledgerBefore,
 "Legacy migration must recover all reviews, events and custom history without loss");
assert(stored.get("history").length<ledgerBefore.length*0.75,
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
console.log("PASS: 789 reviewed profiles, 25 events each, legacy migration, failed writes and protected ledgers");
