'use strict';
/* Real Supabase sync-script behavior, with local deterministic HTTP responses.
   No network requests, credentials, production user data or remote mutation. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/);
assert(match,'Must test the actual shared Desktop/Android cloud-sync script');
const injected=match[1].replace(/\n\}\)\(\);\s*$/, '\nwindow.__authTest={S,rest,ensureAuth,refresh,expiresAtSeconds,renderAuthUi};\n})();');
assert.notEqual(injected,match[1],'Could not expose actual sync internals to test context');
const KEY='igc_v12027_supabase_session';
const epoch=()=>Math.floor(Date.now()/1000);
function response(status,data){return {ok:status>=200&&status<300,status,statusText:status===200?'OK':'Error',
 text:async()=>JSON.stringify(data)}}
function harness(session,handle){
 const entries=new Map([[KEY,JSON.stringify(session)],['ig_v13_done','["saved_review"]']]);
 const localStorage={getItem:key=>entries.get(key)||null,setItem:(key,val)=>entries.set(key,String(val)),
    removeItem:key=>entries.delete(key)};
 const elements=new Map(['igcSyncSignedOut','igcSyncSignedIn','igcSyncAccount'].map(id=>[id,{style:{},textContent:''}]));
 const document={getElementById:id=>elements.get(id)||null,addEventListener(){},hidden:false};
 const win={localStorage,addEventListener(){},
   IGC_INSTAGRAM_PROFILES:{scopeRest:(p,opt)=>({path:p,opt}),setCloudStatus(){},accounts:[],active:'legacy'}};
 const requests=[];
 const ctx={window:win,document,localStorage,console:{warn(){}},setTimeout(){},clearTimeout(){},
   setInterval(){},clearInterval(){},Date,JSON,Error,String,Array,Math,Number,
   fetch:async(url,opt)=>{requests.push({url,opt});return handle(url,opt,requests.length)}};
 vm.createContext(ctx);
 vm.runInContext(injected,ctx,{timeout:5000});
 return {api:win.__authTest,requests,entries,elements,window:win};
}
const session=(overrides={})=>({access_token:'old-jwt',refresh_token:'refresh-old',
 expires_at:epoch()-10,user:{id:'owner-id',email:'owner@example.com'},...overrides});
const rotated=()=>({access_token:'new-jwt',refresh_token:'refresh-new',
 expires_at:epoch()+3600,user:{id:'owner-id',email:'owner@example.com'}});
async function testProactive(){
 let refreshCount=0;
 const x=harness(session(),async(url,opt)=>{
  if(url.includes('/auth/v1/token?grant_type=refresh_token')){
   refreshCount++;
   assert.equal(JSON.parse(opt.body).refresh_token,'refresh-old');
   return response(200,rotated());
  }
  if(url.includes('/rest/v1/')){
   assert.equal(opt.headers.Authorization,'Bearer new-jwt','Refresh must precede first REST call');
   return response(200,[{account_key:'legacy'}]);
  }
  throw Error('unexpected '+url);
 });
 const rows=await x.api.rest('instagram_accounts?select=account_key',{method:'GET'});
 assert.equal(rows.length,1);
 assert.equal(refreshCount,1);
 assert.equal(JSON.parse(x.entries.get(KEY)).refresh_token,'refresh-new');
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]');
 assert.equal(x.api.S.needsReauth,false);
}
async function testConcurrent(){
 let refreshCount=0;
 const x=harness(session(),async(url,opt)=>{
  if(url.includes('/auth/v1/token?grant_type=refresh_token')){
   refreshCount++;
   await Promise.resolve();
   return response(200,rotated());
  }
  if(url.includes('/rest/v1/')){
   assert.equal(opt.headers.Authorization,'Bearer new-jwt');
   return response(200,[]);
  }
  throw Error('unexpected '+url);
 });
 await Promise.all([x.api.rest('instagram_accounts?select=*',{method:'GET'}),
                    x.api.rest('list_snapshots?select=*',{method:'GET'})]);
 assert.equal(refreshCount,1,'Concurrent requests must share a single rotated refresh token');
}
async function testReactive401(){
 let getCount=0,refreshCount=0;
 const x=harness(session({expires_at:epoch()+3600}),async(url,opt)=>{
  if(url.includes('/auth/v1/token?grant_type=refresh_token')){
   refreshCount++;return response(200,rotated());
  }
  getCount++;
  if(getCount===1){assert.equal(opt.headers.Authorization,'Bearer old-jwt');return response(401,{message:'JWT expired'});}
  assert.equal(opt.headers.Authorization,'Bearer new-jwt');
  return response(200,[]);
 });
 await x.api.rest('instagram_accounts?select=*',{method:'GET'});
 assert.equal(getCount,2);
 assert.equal(refreshCount,1);
}
async function testRls403IsNotExpiry(){
 let refreshCount=0;
 const x=harness(session({expires_at:epoch()+3600}),async(url)=>{
  if(url.includes('refresh_token'))refreshCount++;
  return response(403,{message:'permission denied for relation'});
 });
 await assert.rejects(x.api.rest('instagram_accounts?select=*',{method:'GET'}),/permission denied/);
 assert.equal(refreshCount,0,'A real RLS denial must not cause token rotation');
}
async function testExpiredRefreshShowsSignIn(){
 let networkCalls=0;
 const x=harness(session(),async(url)=>{
  networkCalls++;
  assert(url.includes('/auth/v1/token?grant_type=refresh_token'));
  return response(400,{msg:'Invalid Refresh Token'});
 });
 await assert.rejects(x.api.rest('instagram_accounts?select=*',{method:'GET'}),/Vuelve a entrar/);
 assert.equal(networkCalls,1);
 assert.equal(x.api.S.needsReauth,true);
 assert.equal(x.elements.get('igcSyncSignedOut').style.display,'');
 assert.equal(x.elements.get('igcSyncSignedIn').style.display,'none');
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]','Original reviews must not be erased');
 assert.equal(JSON.parse(x.entries.get(KEY)).user.email,'owner@example.com');
}
async function testTransientRefreshFailureKeepsSession(){
 const x=harness(session(),async()=>{throw Error('network unavailable');});
 await assert.rejects(x.api.rest('instagram_accounts?select=*',{method:'GET'}),/problema de conexión/);
 assert.equal(x.api.S.needsReauth,false,'An offline failure is not an invalid login');
 assert.equal(x.elements.get('igcSyncSignedIn').style.display,undefined);
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]');
}
async function testMissingRefreshTokenOffersLogin(){
 const x=harness(session({refresh_token:''}),async()=>{throw Error('No requests should be made');});
 await assert.rejects(x.api.rest('instagram_accounts?select=*',{method:'GET'}),/Vuelve a entrar/);
 assert.equal(x.api.S.needsReauth,true);
 assert.equal(x.elements.get('igcSyncSignedOut').style.display,'');
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]');
}
async function testSwitchDuringFlight(){
 let done;
 const deferred=new Promise(resolve=>done=resolve);
 const x=harness(session(),async(url)=>{
  if(url.includes('refresh_token')){await deferred;return response(200,rotated());}
  throw Error('Unexpected REST before refresh');
 });
 const attempt=x.api.rest('instagram_accounts?select=*',{method:'GET'});
 x.api.S.session=null; // Simulate switching accounts while the HTTP request is in flight.
 done();
 await assert.rejects(attempt,/Vuelve a entrar/);
 assert.equal(x.api.S.session,null,'The old response must not restore a signed-out owner');
}
async function testInstagramSwitchDuringFlight(){
 let finish,started;
 const entered=new Promise(resolve=>started=resolve);
 const delayed=new Promise(resolve=>finish=resolve);
 const x=harness(session({expires_at:epoch()+3600}),async(url)=>{
  if(!url.includes('/rest/v1/'))throw Error('Unexpected request '+url);
  const requestSlot=x.window.IGC_INSTAGRAM_PROFILES.active;
  started();
  await delayed;
  return response(200,[{username:requestSlot}]);
 });
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_a';
 const request=x.api.rest('list_snapshots?select=*',{method:'GET'});
 await entered;
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_b';
 finish();
 await assert.rejects(request,/perfil de Instagram cambió/,
  'A response completed after the A->B switch must never be applied to B');
 assert.equal(x.requests.length,1,'Old response must not trigger a second request');
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]',
  'A-to-B switch must not alter saved historical reviews');
 const fromB=await x.api.rest('list_snapshots?select=*',{method:'GET'});
 assert.equal(fromB[0].username,'ig_account_b',
  'New owner-approved B request uses fresh current scope and succeeds');
 assert.equal(x.requests.length,2);
}
async function testInstagramABAWhileRequestPending(){
 let finish,started;
 const entered=new Promise(resolve=>started=resolve);
 const delayed=new Promise(resolve=>finish=resolve);
 const x=harness(session({expires_at:epoch()+3600}),async(url)=>{
  if(!url.includes('/rest/v1/'))throw Error('Unexpected request '+url);
  started();
  await delayed;
  return response(200,[{username:'stale-account-a'}]);
 });
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_a';
 x.window.IGC_INSTAGRAM_PROFILES.generation=0;
 const request=x.api.rest('list_snapshots?select=*',{method:'GET'});
 await entered;
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_b';
 x.window.IGC_INSTAGRAM_PROFILES.generation++;
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_a';
 x.window.IGC_INSTAGRAM_PROFILES.generation++;
 finish();
 await assert.rejects(request,/perfil de Instagram cambió/,
  'A-to-B-to-A must reject stale results even if the account key returned to A');
 assert.equal(x.entries.get('ig_v13_done'),'["saved_review"]');
 assert.equal(x.requests.length,1);
}
async function testInstagramSwitchBeforeRetry(){
 let refreshCount=0;
 const x=harness(session({expires_at:epoch()+3600}),async(url)=>{
  if(url.includes('refresh_token')){refreshCount++;return response(200,rotated());}
  x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_b';
  return response(401,{message:'JWT expired'});
 });
 x.window.IGC_INSTAGRAM_PROFILES.active='ig_account_a';
 await assert.rejects(x.api.rest('profile_state?select=*',{method:'GET'}),
  /perfil de Instagram cambió/,
  'A 401 belonging to A must not trigger a token refresh/retry under B');
 assert.equal(refreshCount,0);
 assert.equal(x.requests.length,1);
}
(async()=>{
 await testProactive();
 await testConcurrent();
 await testReactive401();
 await testRls403IsNotExpiry();
 await testExpiredRefreshShowsSignIn();
 await testTransientRefreshFailureKeepsSession();
 await testMissingRefreshTokenOffersLogin();
 await testSwitchDuringFlight();
 await testInstagramSwitchDuringFlight();
 await testInstagramSwitchBeforeRetry();
 await testInstagramABAWhileRequestPending();
 console.log('PASS: shared Desktop/Android sync refresh, retries, RLS, cross-owner race and preserved offline data');
})().catch(error=>{console.error(error);process.exitCode=1});
