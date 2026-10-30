'use strict';
/* Native Windows panel acceptance. Local fake bridge, no Instagram traffic. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
 const root=path.resolve(__dirname,'..');
 const source=path.resolve(process.argv[2]||path.join(root,'desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 assert(fs.existsSync(source));
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'igc-native-two-actions-'));
 const native=path.join(tmp,'IG-Cleaner-Pro.html');
 const python=process.env.PYTHON|| (process.platform==='win32'?'python':'python3');
 execFileSync(python,['-c',
  'import sys;sys.path.insert(0,"tools");from pathlib import Path;from ig_cleaner_desktop import prepare_html;prepare_html(Path(sys.argv[1]),Path(sys.argv[2]),dual_action_panel=True)',
  source,native],{cwd:root,stdio:'pipe'});
 assert(fs.readFileSync(native,'utf8').includes('igcDualActionWorkspacePanel'));
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const context=await browser.newContext({viewport:{width:1320,height:920}});
  await context.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());
  const page=await context.newPage();
  page.on('dialog',d=>d.accept());
  const url=pathToFileURL(native).href+'#igc-robot=37777.'+'a'.repeat(32);
  await page.goto(url,{waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{
   const now=Math.floor(Date.now()/1000);
   localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
    access_token:'offline',refresh_token:'offline',expires_at:now+3600,
    user:{id:'fixture',email:'two-action-profiles@example.test'}
   }));
   localStorage.setItem('igc_v12027_supabase_config',
    JSON.stringify({email:'two-action-profiles@example.test'}));
  });
  await page.reload({waitUntil:'domcontentloaded'});
  const owner=await page.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.owner);
  assert.match(owner,/^u_[a-z0-9]+_[0-9]{1,4}$/);
  await page.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   localStorage.setItem('igc_multi_profile_registry_cache_'+p.owner,
     JSON.stringify([{account_key:'ig_first_1234567',username:'alpha.one'},
                     {account_key:'ig_second_123456',username:'beta.two'}]));
   localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_first_1234567');
  });
  await page.reload({waitUntil:'domcontentloaded'});
  await page.evaluate(()=>window.showPage('automations'));
  const panel=page.locator('#igcDualActionWorkspacePanel');
  await panel.waitFor({state:'visible',timeout:12000});
  assert.equal(await panel.locator('.igc-daw-card').count(),2);
  assert.match(await panel.innerText(),/sin acciones simultáneas/i);
  await page.locator('#igcDualSecondary').selectOption('ig_second_123456');
  await page.evaluate(()=>{
   window.__dawRequests=[];
   const original=window.fetch;
   window.fetch=async(url,opts)=>{
     const target=String(url);
     if(target.includes('/api/actions/dual-action-workspaces/')){
       const operation=target.split('/dual-action-workspaces/')[1].split('?')[0];
       const data=opts?.body?JSON.parse(opts.body):null;
       window.__dawRequests.push({operation,token:opts?.headers?.['X-IGC-Bridge-Token'],data});
       const p=window.IGC_INSTAGRAM_PROFILES;
       const response=operation==='configure'?
         {owner:p.owner,two_workspaces:true,parallel_mutations_enabled:false,lanes:[]}:
       operation==='review-one'?{
         owner:p.owner,account:data.account,task:data.task,
         batch:{id:'saved-wave',action_results:{'review.target':{status:'review'}}}
       }:operation==='open-review-one'?{status:'opening',relationship_action:false}:
       operation==='pause-one'?{status:'paused'}:{
         owner:p.owner,parallel_mutations_enabled:false,lanes:[
           {account:'ig_first_1234567',status:'idle',state:'idle',running:false,
            task:'',processed:0,issues:1},
           {account:'ig_second_123456',state:'idle',running:false,
            task:'',processed:0,issues:0}
         ]
       };
       return {ok:true,json:async()=>response};
     }
     return original(url,opts);
   };
  });
  await page.locator('#igcDawConfigure').click();
  await page.locator('#igcDawGrid .igc-daw-card').first().getByText('@alpha.one').waitFor();
  const linked=await page.evaluate(()=>window.__dawRequests);
  assert.equal(linked[0].operation,'configure');
  assert.equal(linked[0].data.confirmation,'dual-action-workspaces:ig_first_1234567:ig_second_123456');
  assert.equal(linked[0].data.acknowledge_serial_actions,true);
  assert.equal(linked[0].token,'a'.repeat(32));
  assert.equal(linked[1].operation,'status');
  await page.locator('#igcDawReview0').click();
  await page.locator('#igcDawTarget0 option[value="review.target"]').waitFor();
  await page.locator('#igcDawOpen0').click();
  await page.locator('#igcDawStop0').click();
  const calls=await page.evaluate(()=>window.__dawRequests);
  assert.equal(calls[2].operation,'review-one');
  assert.equal(calls[2].data.account,'ig_first_1234567');
  assert.equal(calls[3].operation,'open-review-one');
  assert.equal(calls[3].data.username,'review.target');
  assert.equal(calls[3].data.confirmation,
    'action-workspace-review:'+owner+':ig_first_1234567:review.target');
  assert.equal(calls[4].operation,'pause-one');
  assert.equal(calls[4].data.account,'ig_first_1234567');
  assert(!calls.some(x=>x.operation==='start-one'),'Never execute relationship clicks from the review UI');
  assert(calls.every(x=>x.token==='a'.repeat(32)));
  const status=await page.locator('#igcDualActionWorkspaceFeedback').innerText();
  assert.match(status,/SERIALIZADAS/);
  await context.close();
  console.log('PASS: native Windows renders dual action cards; exact owner/session, Pending/Review, no parallel mutation, token and Chrome isolation UI');
 }finally{
  await browser.close();
  fs.rmSync(tmp,{recursive:true,force:true});
 }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
