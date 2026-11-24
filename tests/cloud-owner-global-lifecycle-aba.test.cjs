"use strict";
// GRANADA: production-code negative races for whole-owner operations.
// Never call real Instagram, Supabase, delete local user data or log usernames.
const assert=require("node:assert/strict"),fs=require("node:fs");
const path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function source(a,b){
  const i=html.indexOf(a),j=html.indexOf(b,i+a.length);
  assert(i>=0&&j>i,"Missing actual production source: "+a);
  return html.slice(i,j);
}
const owner=source("function sessionOwner(session){","function expiresAtSeconds(session){");
const scope=source("function igcCaptureSyncScope(){","async function rest(path,opt={}){");
const privacy=source("async function fetchAllCloudRows(table){","function iso(v){");
const registry=source("let instagramRegistryLoaded=false;","async function igcSetInstagramUsername(");
const perProfile=source("async function igcReadInstagramBackupTable(","window.igcRenameLegacyInstagramProfile=");
const timer=source("let doubleCyclePushTimer=null;","async function touchDevice(){");
const purge=source(" async purgeLocalWorkspace(key,assertSameWorkspace=()=>{}){"," switch(key){");
const A="ig_alpha_12345678",B="ig_beta_12345678";
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
async function tick(){await new Promise(r=>setImmediate(r));}
function setup(code){
 const messages=[],calls=[],saved=[],reg={
  active:A,generation:8,accounts:[{account_key:"legacy"},{account_key:A,username:"alpha"}],_verified:false,
  setAccounts(rows){saved.push(JSON.parse(JSON.stringify(rows)));this.accounts=rows},
  setCloudStatus(txt,level){messages.push([txt,level])},
  switch(key){this.active=key;this.generation++},
  purgeLocalWorkspace(){throw Error("UNEXPECTED LOCAL PURGE")}
 };
 const S={session:{user:{email:"owner-a@example.test"},access_token:"token-a"},busy:false,stats:{},cfg:{email:"owner-a@example.test"}};
 const w={IGC_INSTAGRAM_PROFILES:reg};
 const ctx={window:w,S,JSON,Date,Set,Map,Array,Number,String,Math,Object,Error,console:{warn(){},error(){}},
  confirm:()=>true,prompt:()=>null,alert:()=>{},
  status:(...v)=>messages.push(v),privacyDataStatus:(...v)=>messages.push(v),
  renderStats(){},ensureAuth:async()=>true,
  rest:async(p,opt)=>{calls.push({path:p,method:opt.method,owner:S.session?.user?.email,account:reg.active});return []},
  refreshInstagramAccounts:async()=>true,igcReadInstagramBackupTable:async()=>[],
  deliverPrivacyJson:async(name,payload)=>{saved.push({name,payload})},
  currentDevice:()=>({id:"fixture",type:"desktop"}),
  IGC_SYNC_TABLES:["devices","profile_state","list_snapshots"],
  dataMeta:{existing:"preserved"},saveDataMeta:()=>{},
  saveSession:()=>{},notifyHostSession:()=>{},renderAuthUi:()=>{},schedule:()=>{},
  setTimeout:()=>1,clearTimeout:()=>{},
  pullDoubleCheckCycle:async()=>{},pushDoubleCheckCycle:async()=>{}
 };
 vm.createContext(ctx);vm.runInContext(owner+"\n"+scope+"\n"+code,ctx,{timeout:4000});
 return {ctx,S,reg,w,messages,calls,saved,
  swap(){reg.active=B;reg.generation++;reg.active=A;reg.generation++},
  otherOwner(){S.session={user:{email:"owner-b@example.test"},access_token:"token-b"};}
 };
}
async function testGlobalDeletionStopsAtOriginalOwner(){
 const t=setup(privacy);const gate=deferred();
 let n=0;t.ctx.prompt=()=> "DELETE CLOUD";
 t.ctx.confirm=()=>true;
 t.ctx.rest=async(path,opt)=>{t.calls.push({path,method:opt.method,owner:t.S.session.user.email});n++;if(n===1)await gate.promise;return []};
 const action=t.w.igcPrivacyDeleteCloudData();
 await tick();assert.equal(n,1,"First confirmed DELETE starts with owner A");
 t.otherOwner();gate.resolve(true);await action;
 assert.equal(n,1,"No second DELETE is allowed under owner B");
 assert.equal(t.S.session.user.email,"owner-b@example.test","Never log out B after an A deletion");
 assert.equal(t.ctx.dataMeta.existing,"preserved","Do not clear new owner's UI cache");
 assert(t.messages.some(x=>String(x[0]).includes("Borrado no completado")));
 const aba=setup(privacy),pending=deferred();
 aba.ctx.prompt=()=> "DELETE CLOUD";aba.ctx.rest=async()=>{aba.calls.push(1);await pending.promise;return []};
 const op=aba.w.igcPrivacyDeleteCloudData();await tick();aba.swap();pending.resolve([]);await op;
 assert.equal(aba.calls.length,1,"Returning to account A does not revive a stale DELETE");
 assert(aba.S.session,"A-B-A must not sign out an unverified current session");
}
async function testExportNeverMixesPagesOrOwners(){
 const t=setup(privacy);const gate=deferred();let calls=0;
 t.ctx.rest=async()=>{calls++;if(calls===1)return Array.from({length:1000},(_,i)=>({id:i}));if(calls===2)await gate.promise;return []};
 const exportJob=t.w.igcPrivacyExportCloudData();
 await tick();assert.equal(calls,2,"Second page should be in flight");
 t.swap();gate.resolve([]);await exportJob;
 assert.equal(t.saved.length,0,"Never download a cross-generation mixed-owner export");
 assert.equal(calls,2,"Abort pagination before third REST");
 assert(t.messages.some(x=>String(x[0]).includes("No se pudo exportar")));
 // Authentication token rotation for the SAME owner and generation is valid.
 const ok=setup(privacy);ok.ctx.rest=async()=>[{id:1}];
 await ok.w.igcPrivacyExportCloudData();
 assert.equal(ok.saved.length,1);
 assert.deepEqual(Object.keys(ok.saved[0].payload.tables),ok.ctx.IGC_SYNC_TABLES);
}
async function testRegistryIsNonDestructiveAndLatestWins(){
 const good=setup(registry);const stateKey="igc_profile__fixture__"+A+"__ig_v13_done";
 const disk=new Map([[stateKey,'["old-reviewed"]']]);
 good.ctx.localStorage={getItem:key=>disk.get(key)};
 good.ctx.rest=async path=>path.startsWith("rpc/")?[]:[{account_key:"legacy"}];
 await good.ctx.refreshInstagramAccounts();
 assert.equal(good.saved.length,1,"Commit the latest verified registry");
 assert.equal(disk.get(stateKey),'["old-reviewed"]',"Missing profile must never auto-delete history");
 assert.equal(good.reg.accounts.some(x=>x.account_key===A),false,"Old picker entry may be pruned without deleting its history");
 assert.equal(good.reg._verified,true);
 const stale=setup(registry),old=deferred();let requests=0;
 stale.ctx.rest=async path=>{
  if(path.startsWith("rpc/"))return [];
  requests++;return requests===1?old.promise:[{account_key:"legacy"},{account_key:B,username:"beta"}];
 };
 const prior=stale.ctx.refreshInstagramAccounts();await tick();
 const current=stale.ctx.refreshInstagramAccounts();await current;
 old.resolve([{account_key:"legacy"},{account_key:A,username:"outdated"}]);
 await assert.rejects(prior,/reemplazada por una actualización/);
 assert.equal(stale.saved.length,1,"Older response cannot overwrite a newer registry");
 assert.equal(stale.reg.accounts[1].account_key,B);
 const aba=setup(registry),pending=deferred();
 aba.ctx.rest=async()=>pending.promise;
 const job=aba.ctx.refreshInstagramAccounts();aba.swap();pending.resolve([{account_key:"legacy"}]);
 await assert.rejects(job,/cuenta o el perfil de Instagram cambió/);
 assert.equal(aba.saved.length,0,"A-B-A stale remote registry cannot commit");
}
async function testIndividualBackupAndDeleteOwnerFence(){
 const backup=setup(perProfile),gate=deferred();let files=0,queries=0;
 backup.ctx.refreshInstagramAccounts=async()=>true;
 backup.ctx.rest=async()=>{queries++;if(queries===1)await gate.promise;return [{username:"fixture"}]};
 backup.ctx.deliverPrivacyJson=async()=>{files++};
 const promise=backup.w.igcExportSelectedInstagramProfile();await tick();
 backup.swap();gate.resolve(true);
 await assert.rejects(promise,/cuenta o el perfil de Instagram cambió/);
 assert.equal(files,0);assert.equal(queries,1,"No other account may enter backup");
 const deletion=setup(perProfile),wait=deferred();
 deletion.ctx.refreshInstagramAccounts=async()=>true;
 deletion.ctx.confirm=()=>false;deletion.ctx.prompt=()=> "ELIMINAR @alpha";
 deletion.ctx.rest=async()=>{deletion.calls.push("rpc-delete");await wait.promise;return true};
 let purged=0;deletion.reg.purgeLocalWorkspace=async()=>{purged++};
 const op=deletion.w.igcDeleteInstagramProfile();await tick();
 assert.equal(deletion.calls.length,1,"Explicit delete request begins with A");
 deletion.otherOwner();wait.resolve(true);await op;
 assert.equal(purged,0,"Never purge A's local histories from changed owner B");
 assert.equal(deletion.saved.length,0,"Never remove B's profile registry after stale A deletion");
}
async function testScheduledDoubleCheckCannotHijackOtherAccount(){
 const jobs=[];const t=setup(timer);let pulled=0,pushed=0,auth=0;
 t.ctx.setTimeout=fn=>{jobs.push(fn);return jobs.length};
 t.ctx.ensureAuth=async()=>{auth++};
 t.ctx.pullDoubleCheckCycle=async()=>{pulled++};
 t.ctx.pushDoubleCheckCycle=async()=>{pushed++};
 t.w.igcQueueDoubleCheckCycle();
 t.swap();await jobs.shift()();
 assert.equal(auth,0,"Expired A timer must not authenticate B or changed A generation");
 assert.equal(pulled,0);assert.equal(pushed,0);
 t.w.igcQueueDoubleCheckCycle();
 await jobs.shift()();
 assert.equal(auth,1);assert.equal(pulled,1);assert.equal(pushed,1);
 assert.equal(t.S.busy,false);
}
async function testConfirmedPurgeCannotResumeAfterIdentitySwitch(){
 const t=setup("");
 const disk=new Map([["igc_profile__fixture__"+A+"__ig_v13_done","old-history"]]);
 const raw={get length(){return disk.size},key:i=>[...disk.keys()][i],removeItem:k=>disk.delete(k)};
 const wait=deferred();let deletions=0;
 t.ctx.IGC_INSTAGRAM_OWNER="fixture";t.ctx.igcRawProfileStorage=raw;
 t.w.indexedDB={databases:()=>wait.promise,deleteDatabase:()=>{deletions++;throw Error("UNSAFE DELETION")}};
 const purger=vm.runInContext("({"+purge+"})",t.ctx);
 const assertScope=t.ctx.igcCaptureSyncScope();
 const job=purger.purgeLocalWorkspace(A,assertScope);
 t.otherOwner();wait.resolve([{name:"igc_profile__fixture__"+A+"__history"}]);
 await assert.rejects(job,/cuenta o el perfil de Instagram cambió/);
 assert.equal(deletions,0,"Stale owner cannot resume IndexedDB deletion after await");
}
(async()=>{
 await testGlobalDeletionStopsAtOriginalOwner();
 await testExportNeverMixesPagesOrOwners();
 await testRegistryIsNonDestructiveAndLatestWins();
 await testIndividualBackupAndDeleteOwnerFence();
 await testScheduledDoubleCheckCannotHijackOtherAccount();
 await testConfirmedPurgeCannotResumeAfterIdentitySwitch();
 console.log("PASS: actual Desktop privacy cloud DELETE and exports, registry, individual backup/delete, Double Check timer and guarded IndexedDB A-B-A");
})().catch(e=>{console.error(e);process.exitCode=1});