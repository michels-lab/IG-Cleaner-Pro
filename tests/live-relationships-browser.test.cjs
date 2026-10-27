'use strict';
// Read-only live Followers/Following UI against LOCAL mocked loopback backend.
// Real Chromium + distributable HTML; no Instagram session or network traffic.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
 const source=path.resolve(process.argv[2]||path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 assert(source.endsWith('.html')&&fs.existsSync(source));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1250,height:900}});
  const page=await context.newPage(),seen=[];
  let appOwner='';
  const accepted={status:'starting',owner:'fixture-owner-placeholder',account:'ig_abc12345678',
      expected_handle:'my.account',relationship_action:false,
      message:'Read-only browser scan accepted'};
  const good={
    status:'complete',running:false,owner:'fixture-owner-placeholder',account:'ig_abc12345678',
    expected_handle:'my.account',complete:true,last_verified:true,
    verified_handle:'my.account',captured_at:'2026-10-27T12:00:00Z',
    message:'Verified complete',totals:{
      followers:3,following:4,not_following_back:2,fans:1}};
  await context.route('**/*',async route=>{
   const req=route.request(),url=req.url();
   if(url.startsWith('file:')){await route.continue();return}
   if(!url.startsWith('http://127.0.0.1:37777/api/actions/')){
     await route.abort('blockedbyclient');return;
   }
   const headers={'Access-Control-Allow-Origin':'null',
     'Access-Control-Allow-Headers':'X-IGC-Bridge-Token, Content-Type',
     'Access-Control-Allow-Methods':'POST, OPTIONS',
     'Access-Control-Allow-Private-Network':'true'};
   if(req.method()==='OPTIONS'){
     await route.fulfill({status:204,headers,body:''});
     return;
   }
   const endpoint=url.split('/').pop(),payload=JSON.parse(req.postData()||'{}');
   seen.push({endpoint,payload});
   if(endpoint==='live-start'){
     assert.equal(payload.confirmation,'live-relationships:my.account');
     assert.equal(payload.read_only_consent,true);
     assert.equal(payload.expected_handle,'my.account');
     assert.equal(payload.owner,appOwner);
     await route.fulfill({status:200,headers,contentType:'application/json',body:JSON.stringify({...accepted,owner:appOwner})});
   }else if(endpoint==='live-results'){
     const rows={
       followers:['alice','mutual','someone'],
       following:['carol','dan','mutual','someone'],
       not_following_back:['carol','dan'],
       fans:['alice']};
     await route.fulfill({status:200,headers,contentType:'application/json',
       body:JSON.stringify({...good,owner:appOwner,list:payload.list,offset:payload.offset,
          usernames:rows[payload.list]?.slice(payload.offset,payload.offset+100)||[],
          has_next:false})});
   }else if(endpoint==='live-stop'){
     await route.fulfill({status:200,headers,contentType:'application/json',
       body:JSON.stringify({status:'paused',message:'Paused read-only'})});
   }else{
     await route.fulfill({status:404,headers,contentType:'application/json',body:'{"error":"unknown"}'});
   }
  });
  page.on('dialog',dialog=>dialog.accept());
  const uri=pathToFileURL(source).href+'#igc-robot=37777.'+'a'.repeat(32);
  await page.goto(uri,{waitUntil:'domcontentloaded',timeout:60000});
  // Actual app registry uses READ-ONLY owner/active/accounts getters. Seed
  // the exact persisted session and selected workspace, then RELOAD the
  // physical standalone file; never mock those getters or assume a login.
  await page.evaluate(()=>{
    const now=Math.floor(Date.now()/1000);
    window.localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
      access_token:'offline-token',refresh_token:'offline-refresh',
      expires_at:now+3600,user:{id:'fixture-user',email:'first@example.test'}}));
    window.localStorage.setItem('igc_v12027_supabase_config',JSON.stringify({
      email:'first@example.test',auto:false}));
  });
  await page.reload({waitUntil:'domcontentloaded'});
  appOwner=await page.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.owner);
  assert(appOwner.startsWith('u_'),'Expected a properly derived app login owner');
  await page.evaluate(()=>{
    const p=window.IGC_INSTAGRAM_PROFILES;
    window.localStorage.setItem('igc_multi_profile_registry_cache_'+p.owner,
      JSON.stringify([{account_key:'ig_abc12345678',username:'my.account'}]));
    window.localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_abc12345678');
  });
  await page.reload({waitUntil:'domcontentloaded'});
  await page.evaluate(()=>window.showPage('automations'));
  const liveOwner=await page.evaluate(()=>({
    owner:window.IGC_INSTAGRAM_PROFILES.owner,
    account:window.IGC_INSTAGRAM_PROFILES.active,
    handle:window.IGC_INSTAGRAM_PROFILES.accounts[0]?.username
  }));
  assert.deepEqual(liveOwner,{owner:appOwner,account:'ig_abc12345678',handle:'my.account'});
  assert.equal(await page.locator('#igcAutoLivePanel').count(),1);
  assert.equal(await page.locator('#igcRelLiveStatus').count(),1);
  assert.equal(await page.locator('#igcAutoLiveStatus').count(),1,
    'Existing action-robot status must not be replaced by new snapshot');
  await page.getByRole('button',{name:/Verify live Followers and Following/}).click();
  await page.waitForFunction(()=>document.querySelectorAll('#igcAutoLiveRows li').length===2,
    null,{timeout:10000}).catch(async error=>{
    const state=await page.evaluate(()=>({
      status:document.querySelector('#igcRelLiveStatus')?.textContent,
      scope:window.IGC_INSTAGRAM_PROFILES?.active,
      count:document.querySelectorAll('#igcAutoLiveRows li').length
    }));
    throw new Error('Live read-only UI did not display its complete results: '+
      JSON.stringify({state,requests:seen.map(x=>x.endpoint)})+'; '+error.message);
  });
  const negatives=await page.locator('#igcAutoLiveRows li').allTextContents();
  assert.deepEqual(negatives,['@carol','@dan']);
  assert.match(await page.locator('#igcAutoLiveTotals').innerText(),/Not following me back: 2/);
  assert.match(await page.locator('#igcRelLiveStatus').innerText(),/Complete snapshot verified/);
  await page.locator('#igcAutoLiveKind').selectOption('followers');
  await page.waitForFunction(()=>document.querySelectorAll('#igcAutoLiveRows li').length===3,
    null,{timeout:10000});
  assert.deepEqual(await page.locator('#igcAutoLiveRows li').allTextContents(),
    ['@alice','@mutual','@someone']);
  assert.equal(seen.filter(x=>x.endpoint==='live-start').length,1,
    'Changing visible list must not start another implicit Instagram scan');
  assert(seen.filter(x=>x.endpoint==='live-results').every(x=>
    x.payload.owner===appOwner&&x.payload.account==='ig_abc12345678'));
  assert(!seen.some(x=>/unfollow|cancel|follow/i.test(x.endpoint)&&x.endpoint!=='live-results'),
    'No relationship-changing command in read-only UI flow');
  await context.close();
  console.log('PASS: real Chromium one-click live relationship snapshot, four categories, owner scope, no ZIP or mutation');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
