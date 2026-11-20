"use strict";
// GRANADA #371/#360: exercise the SAME production codec and history writer
// in both public standalone HTML and integrated Desktop HTML. No test reimplementation.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

for(const entry of ["index.html","desktop/ig_cleaner_pro_v120_27_synced_companion.html"]){
  const html=fs.readFileSync(path.join(__dirname,"..",entry),"utf8");
  const first=html.indexOf("function igcHistoryFieldNames(");
  const last=html.indexOf("function profileHistoryOf(",first);
  assert(first>0&&last>first,entry+": missing unified production history logic");
  const source=html.slice(first,last);
  new vm.Script(source);

  const records=Object.fromEntries(Array.from({length:789},(_,i)=>{
    const user="person."+i;
    return [user,{
      username:user,opened:25,reopened:2,reviewed:1,unconfirmed:0,snoozed:0,
      lastOpened:1000+i,lastReviewed:1000000+i,
      lastDecision:"reviewed",lastSection:"main",
      events:Array.from({length:25},(_,j)=>({
        ts:1000+i*30+j,event:"open",
        details:{kind:"main",label:"Focus 30",reason:"regular review"}
      }))
    }];
  }));
  // Unknown per-profile/event fields, noncanonical arrays and user-supplied
  // information must remain lossless: no data pruning to make Focus work.
  records["custom.user"]={
    username:"custom.user",reviewed:9,arbitraryCustom:{notes:"do not lose"},
    events:[
      {ts:1,event:"review",details:{decision:"keep"},unknownField:"preserve"},
      ["legacy","array",123],{ts:9,event:"open",details:{kind:"pending"}}
    ]
  };
  const exact=JSON.stringify(records);
  let account="A",denied=false,quota=Infinity;
  const persisted=new Map([["A::history",exact]]);
  const keyOf=k=>account+"::"+k;
  const localStorage={
    getItem(k){return persisted.get(keyOf(k))??null},
    setItem(k,v){
      if(denied){const error=Error("Storage denied");error.name="QuotaExceededError";throw error}
      const key=keyOf(k),str=String(v);
      const other=[...persisted].filter(([name])=>name!==key)
        .reduce((n,[name,data])=>n+name.length+data.length,0);
      if(other+key.length+str.length>quota){
        const error=Error("Storage quota exceeded");error.name="QuotaExceededError";throw error;
      }
      persisted.set(key,str);
    },
    removeItem(k){persisted.delete(keyOf(k))}
  };
  const warnings=[],ctx={
    JSON,Array,Object,Number,Set,Map,Date,console:{
      warn:(...args)=>warnings.push(args.map(String).join(" ")),
      error:(...args)=>warnings.push(args.map(String).join(" "))
    },
    LS_PROFILE_HISTORY:"history",localStorage,profileHistory:{},
    igcProfileHistoryLoadError:false,
    cleanUsername:s=>String(s||"").trim().toLowerCase()
  };
  vm.createContext(ctx);
  vm.runInContext(source,ctx,{timeout:4000});
  const v2=JSON.stringify(ctx.igcPackProfileHistory(records));
  const v3=JSON.stringify(ctx.igcPackProfileHistoryV3(records));
  assert(v3.length<v2.length*0.8,entry+": dictionary should save >20% over v2");
  assert(v3.length<exact.length*.70,entry+": v3 should save >30% vs uncompressed");
  assert.equal(JSON.stringify(ctx.igcUnpackProfileHistory(JSON.parse(v3))),exact,
    entry+": dictionary must restore every prior field and chronological event");

  // Migration from existing plain JSON commits to exactly the same key, never
  // deletes existing Reviewed/Pending ledgers and never changes in-memory data.
  const extra="A::reviewed";
  persisted.set(extra,JSON.stringify({confirmed:{reviewedAt:1234}}));
  const savedReviewed=persisted.get(extra);
  ctx.loadProfileHistory();
  assert.equal(JSON.stringify(ctx.profileHistory),exact);
  assert.equal(ctx.igcProfileHistoryLoadError,false);
  assert.equal(JSON.parse(persisted.get("A::history")).__igcHistoryCompact,3);
  assert.equal(persisted.get(extra),savedReviewed);

  // Old v2 compact data must be migratable again (the earlier code skipped
  // compaction for ALL existing v2 ledgers). A refused migration preserves it.
  persisted.set("A::history",v2);
  denied=true;ctx.loadProfileHistory();
  assert.equal(JSON.stringify(ctx.profileHistory),exact);
  assert.equal(persisted.get("A::history"),v2);
  assert.equal(ctx.igcProfileHistoryLoadError,false);
  denied=false;ctx.loadProfileHistory();
  assert.equal(JSON.parse(persisted.get("A::history")).__igcHistoryCompact,3);
  assert.equal(JSON.stringify(ctx.profileHistory),exact);

  // Existing 789+custom reviews MUST survive rejected open-history writes:
  // never decrement Focus counters in RAM or save phantom "opened" events.
  const durable=persisted.get("A::history"),before=JSON.stringify(ctx.profileHistory);
  quota=[...persisted].reduce((n,[name,data])=>n+name.length+data.length,0)+10;
  assert.throws(()=>ctx.recordRowsHistory(
    Array.from({length:30},(_,i)=>({username:"new."+i})),
    "open",{kind:"main",label:"Focus 30"}),/QuotaExceededError/);
  assert.equal(persisted.get("A::history"),durable);
  assert.equal(JSON.stringify(ctx.profileHistory),before);
  assert.equal(ctx.profileHistory["new.0"],undefined);
  quota=Infinity;
  ctx.recordRowsHistory(
    Array.from({length:30},(_,i)=>({username:"new."+i})),
    "open",{kind:"main",label:"Focus 30"});
  assert.equal(Object.keys(ctx.profileHistory).length,820);
  const afterSuccess=JSON.stringify(ctx.profileHistory);
  ctx.profileHistory={};ctx.loadProfileHistory();
  assert.equal(JSON.stringify(ctx.profileHistory),afterSuccess,
    entry+": retry must reload all 789 past + custom + 30 new events");

  // A -> B -> A real scoped-storage contract. A must never pick up B's events.
  const savedA=persisted.get("A::history");
  account="B";
  persisted.set("B::history",JSON.stringify({uniqueB:{username:"uniqueB",reviewed:1,events:[]}}));
  ctx.loadProfileHistory();
  assert.deepEqual(Object.keys(ctx.profileHistory),["uniqueB"]);
  ctx.recordRowsHistory([{username:"anotherB"}],"open",{kind:"main",label:"B"});
  assert.equal(persisted.get("A::history"),savedA);
  account="A";ctx.loadProfileHistory();
  assert.equal(JSON.stringify(ctx.profileHistory),afterSuccess);

  // Corrupted v3 references must fail closed: never overwrite an unreadable
  // historical account with an empty object or a partial repair.
  const malformed=JSON.parse(persisted.get("A::history"));
  const eventField=2+ctx.igcHistoryFieldNames().indexOf("events");
  malformed.rows[0][eventField][0]=[0,1234,malformed.dictionary.length+123];
  const corrupted=JSON.stringify(malformed);
  persisted.set("A::history",corrupted);
  ctx.loadProfileHistory();
  assert.equal(ctx.igcProfileHistoryLoadError,true);
  assert.throws(()=>ctx.saveProfileHistory(),/Cannot overwrite unreadable/);
  assert.throws(()=>ctx.recordRowsHistory([{username:"not.safely.opened"}],"open"),
    /Cannot modify unreadable/);
  assert.equal(persisted.get("A::history"),corrupted);
  persisted.set("A::history",savedA);
  ctx.loadProfileHistory();
  assert.equal(ctx.igcProfileHistoryLoadError,false);
  assert.equal(JSON.stringify(ctx.profileHistory),afterSuccess);

  assert(warnings.some(t=>t.includes("compaction deferred")),
    entry+": failed v2 migration needs explicit non-destructive diagnostics");
  console.log("PASS "+entry+": v3 lossless 789x25 events, prior v2 migration, quota/retry, 30-person Focus, A-B-A and invalid data protection");
}
