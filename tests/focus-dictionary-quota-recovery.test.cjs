"use strict";
// #371: execute real Desktop AND standalone Focus codec through three quota
// attempts. Never delete Reviewed, Pending, protected or any account history.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
for(const entry of ["desktop/ig_cleaner_pro_v120_27_synced_companion.html","index.html"]){
  const html=fs.readFileSync(path.join(__dirname,"..",entry),"utf8");
  const from=html.indexOf("function safeBatchRow(");
  const to=html.indexOf("function activeBatchUserSet(",from);
  assert(from>0&&to>from,entry+": production Focus codec missing");
  const persisted=new Map();
  let cap=Infinity,denied=false;
  const storage={
    getItem:key=>persisted.get(key)||null,
    removeItem:key=>persisted.delete(key),
    setItem(key,val){
      if(denied){const error=Error("Storage denied");error.name="SecurityError";throw error}
      const taken=[...persisted].filter(([k])=>k!==key)
        .reduce((n,[k,v])=>n+k.length+v.length,0);
      if(taken+key.length+String(val).length>cap){
        const error=Error("Quota exceeded");error.name="QuotaExceededError";throw error;
      }
      persisted.set(key,String(val));
    }
  };
  const ctx={Array,Set,Map,Number,Math,Date,JSON,Object,console,
    localStorage:storage,window:{},activeFocusBatch:null,
    LS_ACTIVE_FOCUS_BATCH:"A::focus"};
  vm.createContext(ctx);
  vm.runInContext(html.slice(from,to),ctx,{timeout:4000});
  const rows=Array.from({length:30},(_,i)=>({
    username:"person."+i,href:"https://www.instagram.com/person."+i+"/",
    name:"Person "+i,relation:"does_not_follow_back",riskScore:i,
    riskLevel:"high",riskReasons:["no followback","owner review","same explanation"],
    timestamp:1700000000+i,dateMain:1234,dateOther:5678,
    iFollow:true,isFollower:i%2===0,followsBack:i%3===0,
    relationGood:i%4===0
  }));
  rows[2].href="https://www.instagram.com/person.2/?custom=1";
  rows[3].href=null;
  rows[4].riskReasons="legacy text with no array";
  const batch={kind:"main",label:"Focus 30",openedAt:1600000000000,
    status:"opened_unconfirmed",rows:rows.map(r=>ctx.safeBatchRow(r))};
  const orig=JSON.parse(JSON.stringify(batch));
  const v2=JSON.stringify(ctx.igcEncodeActiveFocusBatch(batch));
  const v3=JSON.stringify(ctx.igcEncodeFocusBatchQuota(batch));
  const v4=JSON.stringify(ctx.igcEncodeFocusBatchDictionary(batch));
  assert(v4.length<v3.length*.85,entry+": v4 must substantially reduce v3 payload");
  assert(v3.length<v2.length,entry+": prior compaction must still reduce v2");
  assert.deepEqual(JSON.parse(JSON.stringify(ctx.igcDecodeActiveFocusBatch(JSON.parse(v4)))),
    orig,entry+": v4 dictionary must be lossless for every row, URL and flag");
  const otherState={reviewed:JSON.stringify(Array.from({length:789},(_,i)=>"prior."+i)),
    pending:JSON.stringify({stillPending:"unreviewed"}),
    protected:JSON.stringify(["mutual.forever"]),history:"old-action-WAL-unchanged"};
  for(const [key,val] of Object.entries(otherState))persisted.set("A::"+key,val);
  const baseline=[...persisted].reduce((n,[k,v])=>n+k.length+v.length,0);
  cap=baseline+"A::focus".length+Math.floor((v3.length+v4.length)/2);
  ctx.activeFocusBatch=batch;ctx.saveActiveFocusBatch();
  assert.equal(JSON.parse(persisted.get("A::focus")).storageFormat,4,
    entry+": only third lossless fallback fits the near-full browser");
  assert.equal(ctx.window.igcFocusWriteAttempt,null);
  const savedA=persisted.get("A::focus");
  ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
  assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),orig,
    entry+": reload must reconstruct exactly all 30 selected rows");
  for(const [key,val] of Object.entries(otherState))
    assert.equal(persisted.get("A::"+key),val,entry+": must preserve "+key);
  // A->B->A cannot make one account reopen or overwrite another cohort.
  ctx.LS_ACTIVE_FOCUS_BATCH="B::focus";ctx.activeFocusBatch={...batch,label:"B cohort"};
  cap=Infinity;ctx.saveActiveFocusBatch();
  assert.equal(JSON.parse(persisted.get("B::focus")).label,"B cohort");
  assert.equal(persisted.get("A::focus"),savedA);
  ctx.LS_ACTIVE_FOCUS_BATCH="A::focus";ctx.activeFocusBatch=null;
  ctx.loadActiveFocusBatch();
  assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),orig);
  const invalid=JSON.parse(savedA);
  invalid.rows[0][3]=invalid.dictionary.strings.length+100;
  persisted.set("A::focus",JSON.stringify(invalid));
  ctx.loadActiveFocusBatch();
  assert.equal(ctx.activeFocusBatch,null,
    entry+": invalid dictionary reference must fail closed, not invent a review");
  assert.equal(persisted.get("A::focus"),JSON.stringify(invalid),
    "Unverifiable prior data must not be overwritten by loading it");
  persisted.set("A::focus",savedA);
  cap=1;ctx.activeFocusBatch=batch;
  assert.throws(()=>ctx.saveActiveFocusBatch(),/QuotaExceededError/,
    entry+": insufficient quota must fail, not delete past decisions");
  assert.equal(persisted.get("A::focus"),savedA);
  assert.equal(ctx.window.igcFocusWriteAttempt.format,"v4");
  for(const [key,val] of Object.entries(otherState))
    assert.equal(persisted.get("A::"+key),val);
  denied=true;cap=Infinity;
  assert.throws(()=>ctx.saveActiveFocusBatch(),/SecurityError/,
    entry+": security denial must NOT be disguised as quota");
  assert.equal(ctx.window.igcFocusWriteAttempt.format,"v2");
  denied=false;
  ctx.saveActiveFocusBatch();
  assert.equal(ctx.window.igcFocusWriteAttempt,null);
  ctx.activeFocusBatch=null;ctx.loadActiveFocusBatch();
  assert.deepEqual(JSON.parse(JSON.stringify(ctx.activeFocusBatch)),orig);
  console.log("PASS "+entry+": quota v4, lossless 30 rows, 789 reviews, A/B, corruption, total denial");
}
