"use strict";
// Reproduction: 4,017 owner audit events must survive PostgREST's 1,000-row
// server cap. An incomplete or duplicate page must not corrupt the local log.
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Missing shared production sync source");
function cut(a,b){
 const from=script.indexOf(a),to=script.indexOf(b,from+a.length);
 assert(from>=0&&to>from,"Missing source boundary "+a);
 return script.slice(from,to);
}
const fixtures=Array.from({length:4017},(_,i)=>({
 id:"evt_"+String(i).padStart(5,"0"),event_at:"2026-11-12T18:00:00Z",
 username:"synthetic"+i,action:i%2?"reviewed":"opened",
 device_id:"fixture",device_type:"desktop",device_label:"Fixture",
 module:"main",batch_id:null,batch_label:"",batch_size:0,decision:"",
 origin_event_id:null,meta:{}
}));
function makeHarness(broken=false,duplicate=false){
 const merged=[];let pages=0;
 const ctx={console,Date,Number,String,Math,JSON,Array,
  S:{stats:{}},ms:s=>Date.parse(s)||0,
  window:{igcAuditMergeRemoteEvents:async rows=>merged.push(...rows)}};
 ctx.rest=async(q,opts)=>{
  assert.equal(opts.method,"GET");
  assert(q.startsWith("audit_events?select=*&order=event_at.desc,id.asc"));
  const url=new URLSearchParams(q.split("?")[1]);
  const offset=Number(url.get("offset")),limit=Number(url.get("limit"));
  assert.equal(limit,1000);
  pages++;
  if(broken&&offset===1000)return null;
  const p=fixtures.slice(offset,offset+1000);
  if(duplicate&&offset===1000)p[0]={...p[0],id:fixtures[0].id};
  return p;
 };
 vm.createContext(ctx);
 vm.runInContext(cut("function eventFromDb(r){","function rowContext(username,kind){"),ctx);
 return {ctx,merged,pages:()=>pages};
}
(async()=>{
 const full=makeHarness();
 assert.equal(await full.ctx.pullEvents(),4017);
 assert.equal(full.ctx.S.stats.eventsDown,4017);
 assert.equal(full.merged.length,4017);
 assert.equal(full.pages(),5);
 const failed=makeHarness(true);
 await assert.rejects(failed.ctx.pullEvents(),/Sync incompleto/);
 assert.equal(failed.merged.length,0);
 const repeated=makeHarness(false,true);
 await assert.rejects(repeated.ctx.pullEvents(),/Sync incompleto/);
 assert.equal(repeated.merged.length,0);
 console.log("PASS: complete 4017 audit entries; truncated/duplicate page cannot partially merge");
})().catch(e=>{console.error(e);process.exitCode=1});
