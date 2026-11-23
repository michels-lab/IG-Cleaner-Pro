'use strict';
// Installed Windows History: reject late A -> B -> A and changed-owner
// action journals. The actual bundled native JavaScript is exercised in
// Chromium; all bridge replies are local fixtures and no IG action is sent.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright');

const source=fs.readFileSync(path.join(__dirname,'..','tools','automation_activity_ui.py'),'utf8');
const match=source.match(/<script id="igc-automation-activity">([\s\S]*?)<\/script>/);
assert(match,'Native Windows Automations History script missing');
const script=match[1];
const A='ig_first_12345678',B='ig_second_12345678',OWNER='u_owner_42',SECOND='u_second_42';
const row=(username)=>({username,status:'ok',origin:'robot',at:new Date().toISOString()});
const pause=(ms)=>new Promise(r=>setTimeout(r,ms));

async function scenario(){
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage();
  await page.setContent('<main id="page-automations"><div class="igc-page-flow"><section id="igcAutomationCommandCenter"></section></div></main>');
  await page.evaluate(({A,B,OWNER})=>{
   window.location.hash='#igc-robot=1234.'+'a'.repeat(32);
   window.IGC_INSTAGRAM_PROFILES={
     owner:OWNER,
     active:A,
     accounts:[{account_key:A,username:'first.account'},{account_key:B,username:'second.account'}]
   };
   window.__historyRequests=[];
   window.fetch=async (url,options={})=>{
    if(String(url).includes('/api/actions/history')){
     const identity=JSON.parse(options.body);
     return new Promise(resolve=>window.__historyRequests.push({identity,resolve}));
    }
    // Read-only idle state, no supervisor or Instagram action.
    return {ok:true,json:async()=>({owner:window.IGC_INSTAGRAM_PROFILES.owner,lanes:[]})};
   };
   window.__releaseHistory=(index,rows)=>{
     const pending=window.__historyRequests[index];
     if(!pending)throw Error('Missing history request '+index);
     const {identity}=pending;
     pending.resolve({ok:true,json:async()=>({
       owner:identity.owner,account:identity.account,task:identity.task,history_rows:rows
     })});
   };
  },{A,B,OWNER});
  await page.addScriptTag({content:script});
  await page.waitForFunction(()=>window.__historyRequests.length===2);
  const first=await page.evaluate(()=>window.__historyRequests.map(r=>r.identity));
  assert(first.every(r=>r.owner===OWNER&&r.account===A),'First journal request belongs only to account A');

  // This precise ABA race fooled the previous check (same final account
  // value, but a different window session generation).
  await page.evaluate(({A,B})=>{
    window.IGC_INSTAGRAM_PROFILES.active=B;
    window.igcAutomationActivityRefresh();
    window.IGC_INSTAGRAM_PROFILES.active=A;
    window.igcAutomationActivityRefresh();
    window.__releaseHistory(0,[{username:'stale.old',status:'ok',
      origin:'robot',at:new Date().toISOString()}]);
    window.__releaseHistory(1,[]);
  },{A,B});
  await page.waitForFunction(()=>window.__historyRequests.length===4);
  assert.equal(await page.locator('#igcActCount_today').innerText(),'—',
    'Late first A journal must never render after A-B-A');
  await page.evaluate(()=>{window.__releaseHistory(2,[{
    username:'fresh.current',status:'ok',origin:'robot',at:new Date().toISOString()
  }]);window.__releaseHistory(3,[])});
  await page.waitForFunction(()=>document.querySelector('#igcActCount_today')?.textContent==='1');

  // A fresh B refresh is allowed, but a previous A count must disappear.
  await page.evaluate(B=>{
    window.IGC_INSTAGRAM_PROFILES.active=B;
    window.igcAutomationActivityRefresh();
  },B);
  await page.waitForFunction(()=>window.__historyRequests.length===6);
  assert.equal(await page.locator('#igcActCount_today').innerText(),'—');
  await page.evaluate(()=>{window.__releaseHistory(4,[{
    username:'second.one',status:'ok',origin:'robot',at:new Date().toISOString()
  },{username:'second.two',status:'ok',origin:'robot',at:new Date().toISOString()}]);
    window.__releaseHistory(5,[])});
  await page.waitForFunction(()=>document.querySelector('#igcActCount_today')?.textContent==='2');

  // Switching authenticated app owner invalidates the previous account
  // snapshot and every still-pending owner-bound request.
  await page.evaluate(({A,SECOND})=>{
    window.IGC_INSTAGRAM_PROFILES={owner:SECOND,active:A,
      accounts:[{account_key:A,username:'another.owner'}]};
    window.igcAutomationActivityRefresh();
  },{A,SECOND});
  await page.waitForFunction(()=>window.__historyRequests.length===8);
  const afterOwner=await page.evaluate(()=>window.__historyRequests.slice(6).map(r=>r.identity));
  assert(afterOwner.every(r=>r.owner===SECOND&&r.account===A),
    'New requests must bind the new owner before async fetch');
  await page.evaluate(()=>{window.__releaseHistory(6,[]);window.__releaseHistory(7,[])});
  await page.waitForFunction(()=>document.querySelector('#igcActCount_today')?.textContent==='0');
  assert.equal(await page.locator('#igcActMetric_verified').innerText(),'0');
  await page.close();
  console.log('Windows Automations history A-B-A, new B, owner switch and fixed-owner request PASS');
 }finally{await browser.close()}
}
scenario().catch(error=>{console.error(error);process.exitCode=1});
