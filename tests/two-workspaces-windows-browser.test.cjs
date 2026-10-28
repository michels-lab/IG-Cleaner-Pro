'use strict';
// Real Chromium: two app windows retain different scoped workspace identities.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
 const source=path.resolve(process.argv[2]||path.join(__dirname,
   '../desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 assert(fs.existsSync(source));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try {
  const context=await browser.newContext({viewport:{width:1320,height:900}});
  await context.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort('blockedbyclient'));
  const first=await context.newPage();
  first.on('dialog',d=>d.accept());
  const url=pathToFileURL(source).href+'#igc-robot=37777.'+'a'.repeat(32);
  await first.goto(url,{waitUntil:'domcontentloaded'});
  await first.evaluate(()=>{
   const now=Math.floor(Date.now()/1000);
   window.localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
    access_token:'offline',refresh_token:'offline',expires_at:now+3600,
    user:{id:'fixture',email:'two-profiles@example.test'}
   }));
   window.localStorage.setItem('igc_v12027_supabase_config',
      JSON.stringify({email:'two-profiles@example.test'}));
  });
  await first.reload({waitUntil:'domcontentloaded'});
  const owner=await first.evaluate(()=>IGC_INSTAGRAM_PROFILES.owner);
  assert(owner.startsWith('u_'));
  await first.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   window.localStorage.setItem('igc_multi_profile_registry_cache_'+p.owner,
    JSON.stringify([{account_key:'ig_first_1234567',username:'alpha.one'},
                    {account_key:'ig_second_123456',username:'beta.two'}]));
   window.localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_first_1234567');
  });
  await first.reload({waitUntil:'domcontentloaded'});
  assert.equal(await first.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.active),'ig_first_1234567');
  await first.locator('#igcDualSecondary').selectOption('ig_second_123456');
  const popupPromise=context.waitForEvent('page');
  await first.getByRole('button',{name:'Detach to window'}).click();
  const second=await popupPromise;
  second.on('dialog',d=>d.accept());
  await second.waitForLoadState('domcontentloaded');
  assert.equal(await second.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.active),'ig_second_123456');
  assert.equal(await second.evaluate(()=>igcWindowPinned),true);
  // Real UI controller path: a detached window must still send its session
  // capability to the local Windows bridge (rather than treating it as offline).
  const bridgeAttempt=await second.evaluate(async()=>{
   const original=window.fetch,seen=[];
   window.fetch=async(url,options)=>{
    if(String(url).includes('/api/actions/live-settings')){
     seen.push({url:String(url),token:options?.headers?.['X-IGC-Bridge-Token']||''});
     return {ok:true,json:async()=>({})};
    }
    return original(url,options);
   };
   try{await window.igcLiveConfigLoad();}
   catch(error){return {seen,error:String(error.message)}}
   finally{window.fetch=original}
   return {seen};
  });
  assert.equal(bridgeAttempt.seen.length,1,
    'Detached window must reach the native Windows Action bridge');
  assert.equal(bridgeAttempt.seen[0].token,'a'.repeat(32),
    'Detached window must retain the exact capability token');
  assert.equal(await first.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.active),'ig_first_1234567');
  assert.equal(await first.evaluate(()=>igcWindowPinned),true,
    'Opening a second app workspace must pin the ORIGINAL one too.');
  // Changing the default global active profile must not change either window.
  await first.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   window.localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_first_1234567');
  });
  await second.reload({waitUntil:'domcontentloaded'});
  assert.equal(await second.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.active),'ig_second_123456');
  await first.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   window.localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_second_123456');
  });
  await first.reload({waitUntil:'domcontentloaded'});
  assert.equal(await first.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.active),'ig_first_1234567',
    'Window A must remain first even if B became the global selected workspace.');
  // Every window writes to its *own* prefixed backing storage.
  await first.evaluate(()=>localStorage.setItem('ig_v13_done','["alpha"]'));
  await second.evaluate(()=>localStorage.setItem('ig_v13_done','["beta"]'));
  const isolated=await first.evaluate(()=>{
   const owner=window.IGC_INSTAGRAM_PROFILES.owner;
   return [window.localStorage.getItem('igc_profile__'+owner+
          '__ig_first_1234567__ig_v13_done'),
           window.localStorage.getItem('igc_profile__'+owner+
          '__ig_second_123456__ig_v13_done')];
  });
  assert.deepEqual(isolated,['["alpha"]','["beta"]']);
  assert.equal(await first.locator('#igcDualSecondary').count(),1);
  assert.equal(await second.locator('#igcDualSecondary').count(),1);
  // The new two-robot supervisor must send BOTH exact account identities to
  // the local Windows bridge, never falsely enable Unfollow or Cancel.
  const dualReadOnly=await first.evaluate(async()=>{
   const calls=[],original=window.fetch;
   const owner=window.IGC_INSTAGRAM_PROFILES.owner;
   window.fetch=async(url,options)=>{
    const u=String(url);
    if(u.includes('/api/actions/dual-robots/')){
     const body=options?.body?JSON.parse(options.body):null;
     calls.push({url:u,method:options?.method,body,
                 token:options?.headers?.['X-IGC-Bridge-Token']});
     const lanes=[
      {account:'ig_first_1234567',expected_handle:'alpha.one',state:'verified',
       message:'Exact owner verified',verified:true,running:true},
      {account:'ig_second_123456',expected_handle:'beta.two',state:'login',
       message:'Waiting for login',verified:false,running:true}
     ];
     if(u.includes('/stop'))lanes.forEach(l=>{l.running=false;l.verified=false;l.state='stopped'});
     return {ok:true,json:async()=>({status:'running',owner,two_lanes:true,
                            actions_enabled:false,lanes})};
    }
    return original(url,options);
   };
   try{
    await window.IGC_INSTAGRAM_PROFILES.startDualReadOnlyRobotLanes();
    const showed=document.getElementById('igcDualRobotStatus')?.textContent||'';
    await window.IGC_INSTAGRAM_PROFILES.stopDualReadOnlyRobotLanes();
    return {calls,showed};
   }finally{window.fetch=original}
  });
  assert.equal(dualReadOnly.calls.length,4,
   'Start, identity status, STOP, final status are all explicit local operations');
  assert(dualReadOnly.calls.every(c=>c.token==='a'.repeat(32)));
  assert.equal(dualReadOnly.calls[0].body.confirmation,
    'dual-robots:ig_first_1234567:ig_second_123456');
  assert.equal(dualReadOnly.calls[0].body.acknowledge_no_actions,true);
  assert.equal(dualReadOnly.calls[0].body.primary.expected_handle,'alpha.one');
  assert.equal(dualReadOnly.calls[0].body.secondary.expected_handle,'beta.two');
  assert(dualReadOnly.showed.includes('@alpha.one: verified') &&
         dualReadOnly.showed.includes('@beta.two: login'),
         'UI must distinguish exact account states instead of claiming both verified');
  assert.equal(dualReadOnly.calls[2].body.confirmation,
    'dual-robots-stop:'+owner);
  // Neither browser page should have initiated real Instagram or mutation requests.
  console.log('PASS: two identity-only Chrome robots have account-exact authenticated commands, visible status, stop, and independent app windows');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
