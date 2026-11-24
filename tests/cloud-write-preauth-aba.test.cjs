'use strict';
// GRANADA: execute real Desktop cloud functions with deferred auth/network.
// No Instagram access, Supabase credentials, stored exports or relationship clicks.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
function fragment(start,end){
 const a=src.indexOf(start),b=src.indexOf(end,a+start.length);
 assert(a>=0&&b>a,'Must run real production source: '+start);
 return src.slice(a,b);
}
const productionOwner=fragment('function sessionOwner(session){','function expiresAtSeconds(session){');
const productionScope=fragment('function igcCaptureSyncScope(){','async function rest(path,opt={}){');
const productionRest=fragment('async function rest(path,opt={}){','const IGC_SYNC_TABLES=');
const productionPushEvents=fragment('async function pushEvents(){','async function pullEvents(){');
const productionPushLists=fragment('async function pushListSnapshots(){','async function pullListSnapshots(){');
const productionFocus=fragment('async function pushPreparedBatches(){','function normalizeLegacyReviewState(){');
const productionSync=fragment('async function syncNow(manual=true){','window.igcSyncPasswordSignIn=');
const A='ig_first_12345678',B='ig_second_12345678';
const gate=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve}};
function setup(){
 const calls=[],S={session:{user:{email:'first@example.com'},access_token:'old'},
   stats:{},busy:false};
 const reg={active:A,generation:7,verified:true,
   scopeRest(path,opt){calls.push({type:'scope',account:this.active,path});
     return {path:'instagram_'+path,opt};},
   setCloudStatus(){}};
 const window={IGC_INSTAGRAM_PROFILES:reg,igcAuditGetEvents:()=>[]};
 const ctx={window,S,Date,Math,Number,String,Map,Set,JSON,Error,
   sessionOwner(session){return String(session?.user?.email||session?.user?.id||'').toLowerCase()},
   jfetch:async(path,opt)=>{calls.push({type:'http',account:reg.active,path,body:opt?.body});return []},
   ensureAuth:async()=>true,refresh:async()=>true,console};
 const load=(code,expression)=>vm.runInNewContext(
   productionOwner+'\n'+productionScope+'\n'+(code||productionRest)+'\n'+expression,
   {...ctx,sessionOwner:undefined}, {timeout:3000});
 // By default, tests exercise exactly the production sessionOwner helper.
 const rest=load('','({rest,igcCaptureSyncScope})');
 const switchAccount=(name)=>{reg.active=name;reg.generation++};
 return {S,reg,window,ctx,calls,load,rest,switchAccount};
}
async function testPreAuthFence(){
 const t=setup(),wait=gate();
 t.ctx.ensureAuth=()=>wait.promise;
 const {rest}=t.load('','({rest})');
 const promise=rest('list_snapshots?select=*',{method:'POST',body:JSON.stringify([{list_name:'pending'}])});
 t.switchAccount(B);t.switchAccount(A);
 wait.resolve(true);
 await assert.rejects(promise,/cuenta o el perfil de Instagram cambió/);
 assert.equal(t.calls.length,0,'A-B-A during auth must not call scopeRest or HTTP');

 const o=setup(),ownerWait=gate();
 o.ctx.ensureAuth=()=>ownerWait.promise;
 const ownRest=o.load('','({rest})').rest;
 const stale=ownRest('profile_state?select=*',{method:'GET'});
 o.S.session.user.email='other@example.com';ownerWait.resolve(true);
 await assert.rejects(stale,/cuenta o el perfil de Instagram cambió/);
 assert.equal(o.calls.length,0,'Changing owner during JWT refresh must never send the request');

 const ok=setup(),auth=gate();
 ok.ctx.ensureAuth=async()=>{await auth.promise;ok.S.session.access_token='refreshed';return true};
 const current=ok.load('','({rest})').rest('list_snapshots?select=*',{method:'GET'});
 auth.resolve(true);await current;
 assert.equal(ok.calls.filter(c=>c.type==='http').length,1);
 assert.equal(ok.calls.find(c=>c.type==='http').account,A,
  'Token rotation without owner/account change must work');
}
async function testEventChunkFence(){
 const t=setup(),pending=gate();let n=0;
 t.window.igcAuditGetEvents=()=>Array.from({length:501},(_,i)=>({id:i}));
 t.ctx.eventToDb=e=>e;
 t.ctx.rest=async()=>{n++;if(n===1)await pending.promise;return []};
 const {pushEvents}=t.load(productionPushEvents,'({pushEvents})');
 const operation=pushEvents();
 assert.equal(n,1,'First 500-event batch starts immediately');
 t.switchAccount(B);t.switchAccount(A);pending.resolve([]);
 await assert.rejects(operation,/cuenta o el perfil de Instagram cambió/);
 assert.equal(n,1,'Stale second batch must not be uploaded to any account');
 assert.equal(t.S.stats.eventsUp,undefined,'No fake successful upload statistic');
 const fresh=setup();let uploads=0;
 fresh.window.igcAuditGetEvents=()=>Array.from({length:501},(_,i)=>({id:i}));
 fresh.ctx.eventToDb=e=>e;fresh.ctx.rest=async()=>{uploads++;return []};
 const fn=fresh.load(productionPushEvents,'({pushEvents})').pushEvents;
 assert.equal(await fn(),501);assert.equal(uploads,2);
}
async function testFocusBatchChunksFence(){
 const t=setup(),pending=gate();let calls=0;
 const batch={kind:'main',n:550,usernames:Array.from({length:550},(_,i)=>'user'+i),
   syncId:'batch-fixed',createdAt:Date.now(),signature:'fixture'};
 const store={batch:JSON.stringify({first:batch})};
 t.ctx.localStorage={getItem:key=>store[key]||null,setItem:(key,val)=>{store[key]=val}};
 t.ctx.BATCH_LS='batch';t.ctx.hash=()=> 'fixture';
 t.ctx.rowContext=()=>({row:{}});t.ctx.iso=n=>new Date(n).toISOString();
 t.ctx.currentDevice=()=>({type:'desktop'});
 t.ctx.rest=async()=>{calls++;if(calls===1)await pending.promise;return []};
 const fn=t.load(productionFocus,'({pushPreparedBatches})').pushPreparedBatches;
 const operation=fn();
 assert.equal(calls,1,'Batch header request started');
 t.switchAccount(B);pending.resolve([]);
 await assert.rejects(operation,/cuenta o el perfil de Instagram cambió/);
 assert.equal(calls,1,'No stale item chunk may follow a context switch');
 assert.equal(t.S.stats.batchesUp,undefined);
}
async function testListMetadataFence(){
 const t=setup(),wait=gate();let mutated=0,uploads=0;
 t.ctx.rest=async()=>wait.promise;
 t.ctx.currentDevice=()=>({type:'desktop'});
 t.ctx.listPayload=()=>{mutated++;return []};
 t.ctx.dataMeta={};t.ctx.hash=s=>s;t.ctx.ms=()=>0;
 t.ctx.saveDataMeta=()=>{mutated++};
 const fn=t.load(productionPushLists,'({pushListSnapshots})').pushListSnapshots;
 const op=fn();t.switchAccount(B);t.switchAccount(A);wait.resolve([]);
 await assert.rejects(op,/cuenta o el perfil de Instagram cambió/);
 assert.equal(mutated,0,'No B cache/list metadata edits after late A GET');

 const positive=setup();positive.ctx.rest=async()=>[];
 positive.ctx.currentDevice=()=>({type:'desktop'});
 positive.ctx.listPayload=()=>[];positive.ctx.dataMeta={};
 positive.ctx.hash=s=>s;positive.ctx.ms=()=>0;
 positive.ctx.saveDataMeta=()=>{uploads++};
 const good=positive.load(productionPushLists,'({pushListSnapshots})').pushListSnapshots;
 const result=await good();
 assert.equal(result.lists,0);assert.equal(uploads,1,'Unchanged account still saves valid meta');
}
async function testFullSyncPipelineFence(){
 const t=setup(),wait=gate();let stages=0,errors=[];
 t.ctx.igcDeveloperReadOnly=()=>false;t.ctx.cfgFromUi=()=>{};
 t.ctx.status=txt=>errors.push(txt);t.ctx.renderStats=()=>{};
 t.ctx.ensureAuth=async()=>true;
 t.ctx.refreshInstagramAccounts=async()=>{stages++;await wait.promise};
 t.ctx.normalizeLegacyReviewState=()=>{stages++};
 t.ctx.touchDevice=async()=>{stages++};
 t.ctx.console={error:()=>{}};
 const fn=t.load(productionSync,'({syncNow})').syncNow;
 const operation=fn(false);
 // Production runs in a separate VM realm: auth callbacks and promise
 // continuations are scheduled on that realm's microtask queue. Yield to the
 // event loop until its deferred registry fetch actually begins (bounded).
 for(let i=0;i<20&&stages===0&&t.S.busy;i++)
   await new Promise(resolve=>setImmediate(resolve));
 assert.equal(stages,1,'Sync reads registered Instagram account first; '+String(t.S.lastError||errors.join(' | ')));
 t.switchAccount(B);t.switchAccount(A);wait.resolve(true);
 await operation;
 assert.equal(stages,1,'A-B-A invalidates pipeline before any further stages');
 assert.equal(t.S.lastSync,undefined,'Never display Sync complete for mixed account data');
 assert(errors.some(x=>x.includes('Sync detenido')),'A visible failure replaces the false completion');
 assert.equal(t.S.busy,false,'UI sync lock always released');
}
(async()=>{
 await testPreAuthFence();
 await testEventChunkFence();
 await testFocusBatchChunksFence();
 await testListMetadataFence();
 await testFullSyncPipelineFence();
 console.log('Desktop cloud auth-refresh/HTTP A-B-A fence, Focus and event chunks, list metadata, and full pipeline PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
