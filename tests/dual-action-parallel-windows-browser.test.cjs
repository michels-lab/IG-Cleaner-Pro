'use strict';
/* Exact dual-account parallel opt-in + per-account action consent. NO INSTAGRAM. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');

(async()=>{
 const root=path.resolve(__dirname,'..');
 const source=path.resolve(process.argv[2]||
  path.join(root,'desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'igc-granada-parallel-'));
 const native=path.join(tmp,'IG-Cleaner-Pro.html');
 const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');
 execFileSync(python,['-c',
  'import sys;sys.path.insert(0,"tools");from pathlib import Path;from ig_cleaner_desktop import prepare_html;prepare_html(Path(sys.argv[1]),Path(sys.argv[2]),dual_action_panel=True)',
  source,native],{cwd:root,stdio:'pipe'});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  const ctx=await browser.newContext({viewport:{width:1440,height:900}});
  await ctx.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());
  const page=await ctx.newPage();
  const dialogs=[];
  page.on('dialog',async d=>{dialogs.push(d.message());await d.accept()});
  await page.goto(pathToFileURL(native).href+'#igc-robot=37777.'+'a'.repeat(32),
    {waitUntil:'domcontentloaded'});
  await page.evaluate(()=>{
   const now=Math.floor(Date.now()/1000);
   localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
    access_token:'offline',refresh_token:'offline',expires_at:now+3600,
    user:{id:'fixture',email:'parallel-accounts@example.test'}}));
   localStorage.setItem('igc_v12027_supabase_config',
    JSON.stringify({email:'parallel-accounts@example.test'}));
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
  const panel=page.locator('#igcDualActionWorkspacePanel');
  await panel.waitFor({state:'visible',timeout:13000});
  await page.locator('#igcDualSecondary').selectOption('ig_second_123456');
  await page.evaluate(()=>{
   window.__parallelCalls=[];window.__parallelMode=false;
   const orig=window.fetch;
   window.fetch=async(url,opts)=>{
    const text=String(url);
    if(!text.includes('/api/actions/dual-action-workspaces/'))return orig(url,opts);
    const operation=text.split('/dual-action-workspaces/')[1].split('?')[0];
    const data=opts?.body?JSON.parse(opts.body):null;
    window.__parallelCalls.push({operation,data,token:opts?.headers?.['X-IGC-Bridge-Token']});
    let payload;
    if(operation==='configure'){
     window.__parallelMode=data.parallel_actions_consent===true;
     payload={parallel_mutations_enabled:window.__parallelMode,lanes:[],mode:'fake'};
    }else if(operation==='status'){
     if(window.__parallelStatusOffline)
       return {ok:false,json:async()=>({error:'offline fixture'})};
     payload=window.__parallelLiveMessages?
       {owner:window.IGC_INSTAGRAM_PROFILES.owner,
        parallel_mutations_enabled:window.__parallelMode,
        lanes:[
          {account:'ig_first_1234567',state:'running',running:true,
           expected_handle:window.__parallelWrongHandle?'another.login':'alpha.one',
           task:'unfollow',processed:3,issues:1,
           current_profile:'alpha.pending',message:'Esperando confirmación A'},
          {account:'ig_second_123456',state:'running',running:true,
           task:'cancel',processed:7,issues:2,
           current_profile:'beta.pending',message:'Esperando confirmación B'}
        ]}:
       {parallel_mutations_enabled:window.__parallelMode,lanes:[]};
    }else if(operation==='review-one'){
     // Model a slow read-only inspection on A while the owner urgently
     // pauses B. The second account must not wait for A's network reply.
     if(window.__parallelHoldReview&&data.account==='ig_first_1234567')
       await new Promise(resolve=>{window.__releaseReview=resolve});
     payload={owner:data.owner,account:data.account,task:data.task,
       batch:{id:'offline-review',targets:[],action_results:{}}};
    }else if(operation==='preflight-new-one')
     payload={read_only:true,actions_enabled:false,offline_untouched_only:true,
      unresolved_saved_cohort:false,evidence_counts:{untouched:data.targets.length},
      targets:data.targets.map(username=>({username,offline_evidence:'untouched'}))};
    else if(operation==='start-one')
     payload={status:'starting',account:data.account,task:data.action.task};
    else payload={status:'idle'};
    return {ok:true,json:async()=>payload};
   };
  });
  const owner=await page.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.owner);
  const calls=()=>page.evaluate(()=>window.__parallelCalls);
  const opt=page.locator('#igcDawParallelOptIn');
  assert.equal(await opt.isChecked(),false,'Serial must be the DEFAULT');
  await page.locator('#igcDawConfigure').click();
  let sent=await calls();
  assert.equal(sent[0].operation,'configure');
  assert.equal(sent[0].data.parallel_actions_consent,false);
  assert.equal(sent[0].data.acknowledge_serial_actions,true);
  assert.equal(sent[0].data.acknowledge_parallel_actions,false);
  assert.equal(sent[0].data.confirmation,
    'dual-action-workspaces:ig_first_1234567:ig_second_123456');
  assert(!await panel.innerText().then(x=>x.includes('MODO PARALELO ACTIVADO')),
    'No implicit parallel mode in serial setup');

  await opt.check();
  await page.locator('#igcDawConfigure').click();
  sent=await calls();
  const setup=sent.filter(x=>x.operation==='configure');
  assert.equal(setup.length,2);
  const p=setup[1].data;
  assert.equal(p.parallel_actions_consent,true);
  assert.equal(p.acknowledge_parallel_actions,true);
  assert.equal(p.acknowledge_serial_actions,false);
  assert.equal(p.confirmation,
    'dual-action-workspaces-parallel:ig_first_1234567:ig_second_123456');
  assert(dialogs.some(x=>x.includes('MODO PARALELO')));
  assert.match(await page.locator('#igcDualActionWorkspaceFeedback').innerText(),
    /MODO PARALELO ACTIVADO/);

  // Two distinct accounts and independent tasks may run, but each
  // requires its own preflight and confirmation. Backend is mocked.
  await page.locator('#igcDawNewTargets0').fill('@alpha.target');
  await page.locator('#igcDawNewVerify0').click();
  await page.locator('#igcDawNewStart0').click();
  await page.locator('#igcDawTask1').selectOption('cancel');
  await page.locator('#igcDawNewTargets1').fill('@beta.target');
  await page.locator('#igcDawNewVerify1').click();
  await page.locator('#igcDawNewStart1').click();
  sent=await calls();
  const starts=sent.filter(x=>x.operation==='start-one');
  assert.equal(starts.length,2,'Both accounts explicitly request their OWN action jobs.');
  assert.equal(starts[0].data.account,'ig_first_1234567');
  assert.equal(starts[0].data.action.expected_handle,'alpha.one');
  assert.equal(starts[0].data.action.task,'unfollow');
  assert.deepEqual(starts[0].data.action.targets,['alpha.target']);
  assert.equal(starts[0].data.parallel_action_confirmation,
    'parallel-action-workspace-start:'+owner+':ig_first_1234567:unfollow');
  assert.equal(starts[1].data.account,'ig_second_123456');
  assert.equal(starts[1].data.action.expected_handle,'beta.two');
  assert.equal(starts[1].data.action.task,'cancel');
  assert.deepEqual(starts[1].data.action.targets,['beta.target']);
  assert.equal(starts[1].data.parallel_action_confirmation,
    'parallel-action-workspace-start:'+owner+':ig_second_123456:cancel');
  assert(starts.every(x=>x.token==='a'.repeat(32)));
  assert(dialogs.some(x=>x.includes('Modo PARALELO')));
  assert(dialogs.some(x=>x.includes('lista COMPLETA')));
  assert(!sent.some(x=>x.operation==='pause-one'),'Not stopped without user request.');
  await page.locator('#igcDawStop0').click();
  sent=await calls();const pauses=sent.filter(x=>x.operation==='pause-one');
  assert.equal(pauses.length,1);
  assert.equal(pauses[0].data.account,'ig_first_1234567');
  assert.equal(pauses[0].data.confirmation,
    'action-workspace-pause:'+owner+':ig_first_1234567');
  // A disconnected local bridge must NOT leave stale badges claiming that
  // either Chrome worker has stopped or completed, or silently relaunch one.
  const actionsBeforeDisconnect=(await calls()).filter(x=>x.operation==='start-one').length;
  await page.evaluate(()=>{window.__parallelStatusOffline=true});
  await page.locator('#igcDawRefresh').click();
  for(const i of [0,1]){
    assert.match(await page.locator('#igcDawStatus'+i).innerText(),
      /ESTADO NO VERIFICABLE.*La tanda podría seguir activa/);
  }
  assert.match(await page.locator('#igcDualActionWorkspaceFeedback').innerText(),
    /tanda autorizada podría seguir activa/,
    'A failed status GET after a prior start must never promise zero actions');
  assert.doesNotMatch(await page.locator('#igcDualActionWorkspaceFeedback').innerText(),
    /No se ejecutó ninguna nueva acción/);
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,
    actionsBeforeDisconnect,'Read-only status disconnect must not start or replay actions');
  await page.evaluate(()=>{window.__parallelStatusOffline=false});
  await page.locator('#igcDawRefresh').click();
  assert.match(await page.locator('#igcDawStatus0').innerText(),
    /Sin estado para esta cuenta/,'Reconnect must replace unknown status with fresh response');
  // Long-running read-only command for A must never disable account B's Pause.
  await page.evaluate(()=>{window.__parallelHoldReview=true});
  await page.locator('#igcDawReview0').click();
  await page.waitForFunction(()=>
    window.__parallelCalls.some(x=>x.operation==='review-one') &&
    typeof window.__releaseReview==='function',null,{timeout:10000});
  assert.equal(await page.locator('#igcDawStop1').isEnabled(),true,
    'B must remain independently pausable while A awaits a network response');
  assert.equal(await page.locator('#igcDawReview1').isEnabled(),true,
    'B read-only review must remain usable while account A awaits its own reply');
  assert.equal(await page.locator('#igcDawReview0').isEnabled(),false,
    'A must not dispatch duplicate API calls during its in-flight read');
  assert.equal(await page.locator('#igcDawConfigure').isEnabled(),false,
    'Changing account assignments during an in-flight A review is not allowed');
  await page.locator('#igcDawReview1').click();
  await page.locator('#igcDawReviewList1').getByText('Clic incierto primero').waitFor({
    state:'visible',timeout:10000});
  assert.equal((await calls()).filter(x=>x.operation==='review-one'&&
    x.data.account==='ig_second_123456').length,1,
    'B must fetch its own original WAL while A is still pending');
  assert.equal(await page.locator('#igcDawReview0').isEnabled(),false,
    'A cannot be used twice before its delayed reply completes');
  await page.locator('#igcDawStop1').click();
  await page.waitForFunction(()=>
    window.__parallelCalls.filter(x=>x.operation==='pause-one'&&
      x.data.account==='ig_second_123456').length===1,null,{timeout:10000});
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,2,
    'Pausing B during A inspection must never relaunch either action batch');
  await page.evaluate(()=>window.__releaseReview?.());
  await page.waitForFunction(()=>
    document.querySelector('#igcDawReviewList0')?.textContent?.includes('Clic incierto primero'));
  assert.equal(await page.locator('#igcDawConfigure').isEnabled(),true,
    'Both lanes idle: account-linking controls become available again');
  // Human-readable diagnosis must be target- and account-scoped inside each
  // robot card, not visible only in the separate activity statistics panel.
  await page.evaluate(()=>{window.__parallelLiveMessages=true});
  await page.locator('#igcDawRefresh').click();
  assert.match(await page.locator('#igcDawStatus0').innerText(),
    /Perfil actual: @alpha.pending.*Diagnóstico: Esperando confirmación A/);
  assert.doesNotMatch(await page.locator('#igcDawStatus0').innerText(),/beta.pending/);
  assert.match(await page.locator('#igcDawStatus1').innerText(),
    /Perfil actual: @beta.pending.*Diagnóstico: Esperando confirmación B/);
  assert.doesNotMatch(await page.locator('#igcDawStatus1').innerText(),/alpha.pending/);
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,2,
    'Live diagnostic polling cannot initiate an extra Instagram action');
  await page.evaluate(()=>{window.__parallelWrongHandle=true});
  await page.locator('#igcDawRefresh').click();
  assert.match(await page.locator('#igcDawStatus0').innerText(),
    /IDENTIDAD NO VERIFICADA.*alpha.one/,
    'A stale server response bound to another Instagram login must not appear as valid A');
  assert.doesNotMatch(await page.locator('#igcDawStatus1').innerText(),
    /IDENTIDAD NO VERIFICADA/,'B must retain its own independent valid identity');
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,2,
    'Mismatched owner proof must not re-launch a robot');
  await ctx.close();
  console.log('PASS: serial default, parallel exact opt-in, two independent action approvals, account-scoped pause and fail-closed status disconnect/recovery');
 }finally{
  await browser.close();fs.rmSync(tmp,{recursive:true,force:true});
 }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
