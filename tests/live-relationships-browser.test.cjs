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
  const accepted={status:'starting',owner:'app-owner',account:'ig_abc12345678',
      expected_handle:'my.account',relationship_action:false,
      message:'Read-only browser scan accepted'};
  const good={
    status:'complete',running:false,owner:'app-owner',account:'ig_abc12345678',
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
   const endpoint=url.split('/').pop(),payload=JSON.parse(req.postData()||'{}');
   seen.push({endpoint,payload});
   if(endpoint==='live-start'){
     assert.equal(payload.confirmation,'live-relationships:my.account');
     assert.equal(payload.read_only_consent,true);
     assert.equal(payload.expected_handle,'my.account');
     assert.equal(payload.owner,'app-owner');
     await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(accepted)});
   }else if(endpoint==='live-results'){
     const rows={
       followers:['alice','mutual','someone'],
       following:['carol','dan','mutual','someone'],
       not_following_back:['carol','dan'],
       fans:['alice']};
     await route.fulfill({status:200,contentType:'application/json',
       body:JSON.stringify({...good,list:payload.list,offset:payload.offset,
          usernames:rows[payload.list]?.slice(payload.offset,payload.offset+100)||[],
          has_next:false})});
   }else if(endpoint==='live-stop'){
     await route.fulfill({status:200,contentType:'application/json',
       body:JSON.stringify({status:'paused',message:'Paused read-only'})});
   }else{
     await route.fulfill({status:404,contentType:'application/json',body:'{"error":"unknown"}'});
   }
  });
  page.on('dialog',dialog=>dialog.accept());
  const uri=pathToFileURL(source).href+'#igc-robot=37777.'+'a'.repeat(32);
  await page.goto(uri,{waitUntil:'domcontentloaded',timeout:60000});
  await page.evaluate(()=>{
    const p=window.IGC_INSTAGRAM_PROFILES;
    p.owner='app-owner';p.active='ig_abc12345678';
    p.accounts=[{account_key:'ig_abc12345678',username:'my.account'}];
    window.showPage('automations');
  });
  assert.equal(await page.locator('#igcAutoLivePanel').count(),1);
  assert.equal(await page.locator('#igcRelLiveStatus').count(),1);
  assert.equal(await page.locator('#igcAutoLiveStatus').count(),1,
    'Existing action-robot status must not be replaced by new snapshot');
  await page.getByRole('button',{name:/Verificar seguidores y seguidos ahora/}).click();
  await page.waitForFunction(()=>document.querySelectorAll('#igcAutoLiveRows li').length===2,
    null,{timeout:10000});
  const negatives=await page.locator('#igcAutoLiveRows li').allTextContents();
  assert.deepEqual(negatives,['@carol','@dan']);
  assert.match(await page.locator('#igcAutoLiveTotals').innerText(),/No me siguen de vuelta: 2/);
  assert.match(await page.locator('#igcRelLiveStatus').innerText(),/Instantánea verificada/);
  await page.locator('#igcAutoLiveKind').selectOption('followers');
  await page.waitForFunction(()=>document.querySelectorAll('#igcAutoLiveRows li').length===3,
    null,{timeout:10000});
  assert.deepEqual(await page.locator('#igcAutoLiveRows li').allTextContents(),
    ['@alice','@mutual','@someone']);
  assert.equal(seen.filter(x=>x.endpoint==='live-start').length,1,
    'Changing visible list must not start another implicit Instagram scan');
  assert(seen.filter(x=>x.endpoint==='live-results').every(x=>
    x.payload.owner==='app-owner'&&x.payload.account==='ig_abc12345678'));
  assert(!seen.some(x=>/unfollow|cancel|follow/i.test(x.endpoint)&&x.endpoint!=='live-results'),
    'No relationship-changing command in read-only UI flow');
  await context.close();
  console.log('PASS: real Chromium one-click live relationship snapshot, four categories, owner scope, no ZIP or mutation');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
