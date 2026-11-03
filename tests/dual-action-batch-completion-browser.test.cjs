'use strict';
/* Browser proof for end-of-batch Review UX, using a local fake bridge only. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
 const root=path.resolve(__dirname,'..');
 const source=path.resolve(process.argv[2]||
  path.join(root,'desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 const folder=fs.mkdtempSync(path.join(os.tmpdir(),'igc-completion-review-'));
 const native=path.join(folder,'IG-Cleaner-Pro.html');
 const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');
 execFileSync(python,['-c',
  'import sys;sys.path.insert(0,"tools");from pathlib import Path;from ig_cleaner_desktop import prepare_html;prepare_html(Path(sys.argv[1]),Path(sys.argv[2]),dual_action_panel=True)',
  source,native],{cwd:root,stdio:'pipe'});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const ctx=await browser.newContext({viewport:{width:1350,height:920}});
  await ctx.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());
  const page=await ctx.newPage();
  page.on('dialog',d=>d.accept());
  await page.goto(pathToFileURL(native).href+'#igc-robot=37777.'+'a'.repeat(32),
    {waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{
   const now=Math.floor(Date.now()/1000);
   localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
    access_token:'offline',refresh_token:'offline',expires_at:now+3600,
    user:{id:'fixture',email:'completion-review@example.test'}}));
   localStorage.setItem('igc_v12027_supabase_config',
    JSON.stringify({email:'completion-review@example.test'}));
  });
  await page.reload({waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   localStorage.setItem('igc_multi_profile_registry_cache_'+p.owner,
    JSON.stringify([{account_key:'ig_first_1234567',username:'alpha.one'},
     {account_key:'ig_second_123456',username:'beta.two'}]));
   localStorage.setItem('igc_multi_profile_active_'+p.owner,'ig_first_1234567');
  });
  await page.reload({waitUntil:'domcontentloaded'});
  await page.evaluate(()=>window.showPage('automations'));
  await page.locator('#igcDualActionWorkspacePanel').waitFor({state:'visible'});
  await page.locator('#igcDualSecondary').selectOption('ig_second_123456');
  await page.evaluate(()=>{
   window.__completedCalls=[];
   window.__activeParallel=false;
   window.__laneStates={
    'ig_first_1234567':{account:'ig_first_1234567',state:'idle',running:false,
      task:'',processed:0,pending:0,issues:0},
    'ig_second_123456':{account:'ig_second_123456',state:'idle',running:false,
      task:'',processed:0,pending:0,issues:0},
   };
   const original=window.fetch;
   window.fetch=async(url,opts)=>{
    const target=String(url);
    if(!target.includes('/api/actions/dual-action-workspaces/'))
      return original(url,opts);
    const operation=target.split('/dual-action-workspaces/')[1].split('?')[0];
    const data=opts?.body?JSON.parse(opts.body):null;
    window.__completedCalls.push({operation,data});
    let payload;
    if(operation==='configure'){
      window.__activeParallel=data.parallel_actions_consent===true;
      payload={parallel_mutations_enabled:window.__activeParallel,lanes:[]};
    }else if(operation==='status')
      payload={parallel_mutations_enabled:window.__activeParallel,
        lanes:Object.values(window.__laneStates)};
    else if(operation==='preflight-new-one')
      payload={read_only:true,actions_enabled:false,offline_untouched_only:true,
        unresolved_saved_cohort:false,evidence_counts:{untouched:data.targets.length},
        targets:data.targets.map(username=>({username,offline_evidence:'untouched'}))};
    else if(operation==='start-one'){
      window.__laneStates[data.account]={
        account:data.account,state:'running',running:true,
        task:data.action.task,processed:0,pending:1,issues:0};
      payload={status:'running',account:data.account,task:data.action.task};
    }else if(operation==='review-one'){
      const first=data.account==='ig_first_1234567';
      payload={owner:data.owner,account:data.account,task:data.task,
        batch:{id:first?'first-wave':'second-wave',
          targets:first?['first.person','possible.click']:['pending.friend'],
          action_results:first?{
           'first.person':{status:'ok',at:'2026-10-30T18:00:00Z'},
           'possible.click':{status:'review',at:'2026-10-30T18:01:00Z'}
          }:{'pending.friend':{status:'review',at:'2026-10-30T18:03:00Z'}}
        }};
    }else payload={status:'idle'};
    return {ok:true,json:async()=>payload};
   };
  });
  const calls=()=>page.evaluate(()=>window.__completedCalls);
  const opt=page.locator('#igcDawParallelOptIn');
  await opt.check();
  await page.locator('#igcDawConfigure').click();
  await page.locator('#igcDawNewTargets0').fill('@first.person');
  await page.locator('#igcDawNewVerify0').click();
  await page.locator('#igcDawNewStart0').click();
  await page.locator('#igcDawTask1').selectOption('cancel');
  await page.locator('#igcDawNewTargets1').fill('@pending.friend');
  await page.locator('#igcDawNewVerify1').click();
  await page.locator('#igcDawNewStart1').click();
  await page.locator('#igcDawRefresh').click();
  assert.equal(await page.locator('#igcDawCompletionModal').isVisible(),false,
    'No completion modal while both account robots are still running.');

  await page.evaluate(()=>{
   window.__laneStates.ig_first_1234567={
    account:'ig_first_1234567',state:'complete',running:false,
    task:'unfollow',processed:2,pending:0,issues:1
   };
  });
  await page.locator('#igcDawRefresh').click();
  const modal=page.locator('#igcDawCompletionModal');
  await modal.waitFor({state:'visible',timeout:5000});
  assert.match(await modal.innerText(),/@alpha.one/);
  assert.match(await modal.innerText(),/1 requieren atención/);
  await modal.getByText('@possible.click').waitFor({state:'visible',timeout:5000});
  assert.match(await modal.innerText(),/REVIEW/);
  assert.match(await modal.innerText(),/2026-10-30T18:01:00Z/);
  assert.equal((await calls()).filter(x=>x.operation==='approve-one').length,0,
    'No implicit batch approval or status greenwashing in completion modal.');
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,2,
    'Completion modal never relaunches either original action job.');

  await modal.getByRole('button',{name:'Cerrar'}).click();
  await page.locator('#igcDawRefresh').click();
  assert.equal(await modal.isVisible(),false,
    'Same completed A job must not fire duplicate modal.');

  await page.evaluate(()=>{
   window.__laneStates.ig_second_123456={
    account:'ig_second_123456',state:'review',running:true,
    task:'cancel',processed:1,pending:0,issues:1
   };
  });
  await page.locator('#igcDawRefresh').click();
  await modal.waitFor({state:'visible',timeout:5000});
  assert.match(await modal.innerText(),/@beta.two/);
  await modal.getByText('@pending.friend').waitFor({state:'visible',timeout:5000});
  await modal.getByRole('button',{name:'Revisar lista completa'}).click();
  assert.equal(await modal.isVisible(),false);
  await page.locator('#igcDawTarget1 option[value="pending.friend"]').waitFor({state:'attached'});
  assert.equal((await calls()).filter(x=>x.operation==='approve-one').length,0);
  await page.evaluate(()=>{
   window.__laneStates.ig_second_123456={
    account:'ig_second_123456',state:'paused',running:false,
    task:'cancel',processed:1,pending:0,issues:1
   };
  });
  await page.locator('#igcDawRefresh').click();
  assert.equal(await modal.isVisible(),false,
    'Review->Paused is still the same B batch; no duplicate notification.');
  await ctx.close();
  console.log('PASS: two independent per-account completion popups show original WAL, retain unresolved, do not approve/reclick, no duplicate notification');
 }finally{
  await browser.close();fs.rmSync(folder,{recursive:true,force:true});
 }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
