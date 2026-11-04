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
  assert.match(await panel.innerText(),/serial por defecto/i);
  await page.locator('#igcDualSecondary').selectOption('ig_second_123456');
  await page.evaluate(()=>{
   window.__dawRequests=[];
   const original=window.fetch;
   window.fetch=async(url,opts)=>{
     const target=String(url);
     if(target.includes('/api/actions/dual-action-workspaces/status?')){
       const owner=window.IGC_INSTAGRAM_PROFILES.owner;
       return {ok:true,json:async()=>({owner,lanes:[
         {account:'ig_first_1234567',state:'running',running:true,task:'unfollow',
           processed:8,pending:3,issues:2,owner_profile_visits:3,owner_sibling_proofs:2},
         {account:'ig_second_123456',state:'paused',running:false,task:'cancel',
           processed:4,pending:6,issues:1,owner_profile_visits:1,owner_sibling_proofs:5}
       ]})};
     }
     if(target.endsWith('/api/actions/status')){
       return {ok:true,json:async()=>({owner:'',account:'',task:'',status:'idle',
         processed:0,pending:0,issue_count:0})};
     }
     if(target.includes('/api/actions/history')){
       if(window.__igcHistoryUnavailable)return {ok:false,json:async()=>({error:'offline fixture'})};
       const data=opts?.body?JSON.parse(opts.body):{};
       const now=new Date().toISOString();
       const today=new Date(),yesterday=new Date(today.getFullYear(),today.getMonth(),
         today.getDate()-1,23,59,0).toISOString();
       const first=data.account==='ig_first_1234567';
       const history_rows=first?
         (data.task==='unfollow'?[
           {username:'done.recent',status:'ok',at:now,origin:'robot'},
           {username:'already.done',status:'already_not_following',at:now,origin:'robot'},
           {username:'warn.now',status:'review',at:now,origin:'robot'},
           {username:'done.recent',status:'ok',at:now,origin:'robot'}
         ]:[
           {username:'cancel.yesterday',status:'ok',at:yesterday,origin:'robot'},
           {username:'legacy.unattributed',status:'ok',at:yesterday},
           {username:'warn.pending',status:'blocked',at:now,origin:'robot'},
           {username:'cancel.unknown',status:'ok',at:'bad-timestamp',origin:'robot'}
         ]):
         (data.task==='cancel'?[{username:'other.person',status:'ok',at:now,origin:'robot'}]:[]);
       return {ok:true,json:async()=>({owner:data.owner,account:data.account,
         task:data.task,history_rows})};
     }
     if(target.includes('/api/actions/dual-action-workspaces/')){
       const operation=target.split('/dual-action-workspaces/')[1].split('?')[0];
       const data=opts?.body?JSON.parse(opts.body):null;
       window.__dawRequests.push({operation,token:opts?.headers?.['X-IGC-Bridge-Token'],data});
       const p=window.IGC_INSTAGRAM_PROFILES;
       const response=operation==='configure'?
         {owner:p.owner,two_workspaces:true,parallel_mutations_enabled:false,lanes:[]}:
       operation==='review-one'?{
         owner:p.owner,account:data.account,task:data.task,
         batch:{id:'saved-wave',targets:['done.profile','untouched.one','review.target'],
           action_results:{
             'review.target':{status:'review',possible_click:true,at:'2026-10-30T15:43:00Z'},
             'done.profile':{status:'ok',at:'2026-10-30T15:40:00Z',message:'Confirmed'},
             ...(window.__dawReviewCompleted?{'untouched.one':{
               status:'already_not_following',at:'2026-10-30T15:45:00Z',message:'Observed'}}:{})
           }}
       }:operation==='open-review-one'?{status:'opening',relationship_action:false}:
       operation==='pause-one'?{status:'paused'}:
       operation==='approve-one'?{approved_usernames:['done.profile','untouched.one'],
         unresolved_usernames:['review.target']}:
       operation==='start-one'?{status:'starting',account:data.account,task:data.action.task}:{
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
  // The Automations statistics sidebar reads the original canonical WAL.
   // No Instagram requests or relationship-changing calls are needed.
   const activity=page.locator('#igcAutomationActivityPanel');
   await activity.waitFor({state:'visible',timeout:12000});
   assert.equal(await page.locator('#igcAutomationActivityLayout').count(),1);
   await page.locator('#igcActRefresh').click();
   await page.waitForFunction(()=>
     document.querySelector('#igcActCount_h24')?.textContent==='2');
   assert(['1','2'].includes(await page.locator('#igcActCount_h1').innerText()),
     'Just-before-midnight completion may fall inside the rolling last hour');
   assert.equal(await page.locator('#igcActCount_today').innerText(),'1');
   // Same six priority windows/order as Manual Actions.
   assert.deepEqual(await activity.locator('.igc-act-window').evaluateAll(
     items=>items.slice(0,6).map(item=>item.querySelector('span')?.textContent)),
     ['Esta sesión','Hoy','Últimos 7 días','Última hora','Últimas 2 horas','Últimas 3 horas']);
   assert.equal(await activity.locator('.igc-act-window.igc-act-primary').count(),3);
   assert([1,2].includes(Number(await page.locator('#igcActCount_h2').innerText())),
     '2h is a rolling window and may cross local midnight');
   assert.equal(await page.locator('#igcActCount_all').innerText(),'2');
   await page.locator('#igcActBreakdownPeriod').selectOption('all');
   assert.equal(await page.locator('#igcActMetric_legacy_unknown').innerText(),'1',
     'Unknown legacy source must not be represented as a confirmed robot action');
   assert.match(await page.locator('#igcActHistory').innerText(),/origen sin registrar/);
   await page.locator('#igcActBreakdownPeriod').selectOption('today');
   await page.waitForFunction(()=>document.querySelector('#igcActBatch')?.textContent?.includes('Procesados: 8'));
   assert.match(await page.locator('#igcActBatch').innerText(),/Pendientes: 3.*Review: 2/);
   assert.match(await page.locator('#igcActBatch').innerText(),/visitas a mi perfil: 3/);
   assert.match(await page.locator('#igcActBatch').innerText(),/identidad desde otra pestaña: 2/);
   assert.match(await page.locator('#igcActBatchTitle').innerText(),/Unfollow.*en ejecución/);
   assert.equal(await page.locator('#igcActMetric_unfollow').innerText(),'1');
   assert.equal(await page.locator('#igcActMetric_warning').innerText(),'2');
   assert.equal(await page.locator('#igcActMetric_no_action').innerText(),'1');
   assert.match(await page.locator('#igcActLast').innerText(),/Último registro/);
   // Duplicate journal snapshots must not duplicate visible list rows.
   assert.equal(await page.locator('#igcActHistory .igc-act-history-row').count(),6);
   assert.match(await page.locator('#igcActHistory').innerText(),/OK confirmado/);
   assert.match(await page.locator('#igcActHistory').innerText(),/Review \/ advertencia/);
   // Action type and collapse filters must alter view only, never robot actions.
   await page.locator('#igcActTask').selectOption('cancel');
   assert.equal(await page.locator('#igcActCount_today').innerText(),'0');
   assert.equal(await page.locator('#igcActCount_h24').innerText(),'1');
   assert.equal(await page.locator('#igcActHistory .igc-act-history-row').count(),3);
   assert.doesNotMatch(await page.locator('#igcActHistory').innerText(),/done.recent/);
   await page.locator('#igcActTask').selectOption('unfollow');
   assert.equal(await page.locator('#igcActCount_today').innerText(),'1');
   assert.equal(await page.locator('#igcActHistory .igc-act-history-row').count(),3);
   await page.locator('#igcActTask').selectOption('all');
   await page.locator('#igcActToggle').click();
   assert.equal(await page.locator('#igcActToggle').getAttribute('aria-expanded'),'false');
   assert.equal(await page.locator('#igcAutomationActivityLayout.igc-act-collapsed').count(),1);
   await page.locator('#igcActToggle').click();
   assert.equal(await page.locator('#igcActToggle').getAttribute('aria-expanded'),'true');
      await page.locator('#igcActBreakdownPeriod').selectOption('h24');
   assert.equal(await page.locator('#igcActMetric_cancel').innerText(),'1');
   await page.locator('#igcActAccount').selectOption('ig_second_123456');
   await page.waitForFunction(()=>
     document.querySelector('#igcActCount_h24')?.textContent==='1');
   assert.equal(await page.locator('#igcActMetric_unfollow').innerText(),'0');
   assert.equal(await page.locator('#igcActMetric_cancel').innerText(),'1');
   await page.waitForFunction(()=>document.querySelector('#igcActBatch')?.textContent?.includes('Procesados: 4'));
   assert.match(await page.locator('#igcActBatch').innerText(),/Pendientes: 6.*Review: 1/);
   assert.match(await page.locator('#igcActBatch').innerText(),/visitas a mi perfil: 1/);
   assert.match(await page.locator('#igcActBatch').innerText(),/identidad desde otra pestaña: 5/);
   assert.match(await page.locator('#igcActBatchTitle').innerText(),/Cancel Pending.*detenido/);
   assert.equal(await page.locator('#igcActHistory .igc-act-history-row').count(),1);
   assert.doesNotMatch(await page.locator('#igcActHistory').innerText(),/done.recent/);
   await page.locator('#igcActAccount').selectOption('ig_first_1234567');
   await page.waitForFunction(()=>
     document.querySelector('#igcActBatch')?.textContent?.includes('Procesados: 8'));
   // Switching the *app's* pinned Instagram workspace must immediately
   // rebind Automations statistics, unlike the read-only stats dropdown.
   await page.evaluate(()=>{window.IGC_INSTAGRAM_PROFILES.active='ig_second_123456'});
   await page.waitForFunction(()=>
     document.querySelector('#igcActAccount')?.value==='ig_second_123456',
     null,{timeout:5000});
   await page.waitForFunction(()=>
     document.querySelector('#igcActBatch')?.textContent?.includes('Procesados: 4'));
   assert.equal(await page.locator('#igcActMetric_unfollow').innerText(),'0');
   await page.evaluate(()=>{window.IGC_INSTAGRAM_PROFILES.active='ig_first_1234567'});
   await page.waitForFunction(()=>
     document.querySelector('#igcActAccount')?.value==='ig_first_1234567',
     null,{timeout:5000});
   await page.waitForFunction(()=>
     document.querySelector('#igcActBatch')?.textContent?.includes('Procesados: 8'));
   // Even with no saved history, current per-account progress still exists.
   await page.evaluate(()=>window.__igcHistoryUnavailable=true);
   await page.locator('#igcActRefresh').click();
   await page.waitForFunction(()=>document.querySelector('#igcActStatus')?.textContent
     .includes('Sin historial verificable'));
   assert.equal(await page.locator('#igcActCount_today').innerText(),'—');
   await page.waitForFunction(()=>document.querySelector('#igcActBatch')?.textContent
     .includes('Procesados: 8'));
   assert.match(await page.locator('#igcActBatch').innerText(),
     /Procesados: 8.*Pendientes: 3.*Review: 2/);
   await page.evaluate(()=>window.__igcHistoryUnavailable=false);
   await page.locator('#igcActRefresh').click();
   await page.waitForFunction(()=>document.querySelector('#igcActCount_all')?.textContent==='2');
   await page.locator('#igcDawConfigure').click();
  await page.locator('#igcDawGrid .igc-daw-card').first().getByText('@alpha.one').waitFor();
  const linked=await page.evaluate(()=>window.__dawRequests);
  assert.equal(linked[0].operation,'configure');
  assert.equal(linked[0].data.confirmation,'dual-action-workspaces:ig_first_1234567:ig_second_123456');
  assert.equal(linked[0].data.acknowledge_serial_actions,true);
  assert.equal(linked[0].token,'a'.repeat(32));
  assert.equal(linked[1].operation,'status');
  await page.locator('#igcDawReview0').click();
  await page.locator('#igcDawTarget0 option[value="review.target"]').waitFor({state:'attached'});
  const unresolved=page.locator('#igcDawReviewList0 .igc-daw-unresolved');
  const confirmed=page.locator('#igcDawReviewList0 .igc-daw-reviewed');
  assert.equal(await unresolved.count(),2);
  assert.equal(await confirmed.count(),1);
  assert.match(await confirmed.first().innerText(),/done.profile.*OK/s);
  // Stored cohort intentionally begins with a green OK. Visible Review
  // rows must move above it without modifying start-one cohort ordering.
  assert.deepEqual(await page.locator('#igcDawReviewList0 .igc-daw-review-row')
    .evaluateAll(rows=>rows.map(x=>x.querySelector('span')?.textContent)),[
    '@review.target','@untouched.one','@done.profile']);
  assert.match(await page.locator('#igcDawReviewList0').innerText(),/Review primero/);
  assert.match(await unresolved.first().innerText(),/2026-10-30T15:43:00Z/);
  assert.equal(await page.locator('#igcDawTarget0 option[value="done.profile"]').count(),0,
    'Never re-open green confirmed profiles as new Review targets');
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
  assert(!calls.some(x=>x.operation==='start-one'),'No implicit relationship actions during Review/Pause');
  await page.locator('#igcDawApprove0').click();
  const beforeActualApproval=await page.evaluate(()=>window.__dawRequests);
  assert(!beforeActualApproval.some(x=>x.operation==='approve-one'),
    'Cannot mark an untouched saved target reviewed.');
  await page.locator('#igcDawContinue0').click();
  const afterContinue=await page.evaluate(()=>window.__dawRequests);
  const starts=afterContinue.filter(x=>x.operation==='start-one');
  assert.equal(starts.length,1,'The user explicitly approved one saved cohort');
  assert.equal(starts[0].data.account,'ig_first_1234567');
  assert.equal(starts[0].data.action.expected_handle,'alpha.one');
  assert.equal(starts[0].data.action.batch_id,'saved-wave');
  assert.deepEqual(starts[0].data.action.targets,['done.profile','untouched.one','review.target'],
    'Never silently trim the original saved cohort.');
  assert.equal(starts[0].data.action.confirmation,'unfollow:3');
  assert.equal(starts[0].data.action.followers_evidence,true,
    'Only after a separate owner confirmation of complete Followers evidence.');
  assert.equal(starts[0].data.confirmation,
    'action-workspace-start:'+owner+':ig_first_1234567:unfollow');
  assert(afterContinue.every(x=>x.token==='a'.repeat(32)));
  await page.evaluate(()=>window.__dawReviewCompleted=true);
  await page.locator('#igcDawReview0').click();
  await page.locator('#igcDawApprove0').click();
  const afterApproval=await page.evaluate(()=>window.__dawRequests);
  const approvals=afterApproval.filter(x=>x.operation==='approve-one');
  assert.equal(approvals.length,1);
  assert.equal(approvals[0].data.account,'ig_first_1234567');
  assert.equal(approvals[0].data.task,'unfollow');
  assert.equal(approvals[0].data.batch_id,'saved-wave');
  assert.equal(approvals[0].data.confirmation,
    'action-workspace-approve:'+owner+':ig_first_1234567:unfollow:saved-wave');
  assert(afterApproval.every(x=>x.token==='a'.repeat(32)));
  const status=await page.locator('#igcDualActionWorkspaceFeedback').innerText();
  assert.match(status,/permanecen sin confirmación/);
  // Regression: user opens Automations after the old 7.5 s startup window.
  // The panel must mount even when Command Center is created much later.
  const html=fs.readFileSync(native,'utf8');
  const fragmentStart=html.indexOf('<style>\n#igcDualActionWorkspacePanel');
  const fragmentEnd=html.indexOf('</script>',fragmentStart)+9;
  assert(fragmentStart>0&&fragmentEnd>fragmentStart,'Native panel script missing.');
  const late=await context.newPage();
  await late.setContent('<html><body>'+html.slice(fragmentStart,fragmentEnd)+'</body></html>');
  await late.waitForTimeout(8300);
  await late.evaluate(()=>{
    const command=document.createElement('div');
    command.id='igcAutomationCommandCenter';
    document.body.appendChild(command);
  });
  await late.locator('#igcDualActionWorkspacePanel').waitFor({state:'attached',timeout:3000});
  assert.equal(await late.locator('#igcDualActionWorkspacePanel').count(),1);
  await late.close();
  // Regression: app restart must restore only the exact server-pinned pair,
  // without silently starting a worker, changing an account or replaying WAL.
  const restoredCalls=[];
  await context.route('**/api/actions/dual-action-workspaces/status*',async route=>{
    const method=route.request().method();
    restoredCalls.push(method);
    const headers={'Access-Control-Allow-Origin':'*',
      'Access-Control-Allow-Methods':'GET, OPTIONS',
      'Access-Control-Allow-Headers':'X-IGC-Bridge-Token, Content-Type'};
    if(method==='OPTIONS')return route.fulfill({status:204,headers});
    assert.equal(method,'GET','Recovery is status-only, never a POST');
    return route.fulfill({status:200,headers,contentType:'application/json',
      body:JSON.stringify({owner,two_workspaces:true,
        parallel_mutations_enabled:true,lanes:[
        {account:'ig_first_1234567',expected_handle:'alpha.one',
          running:true,state:'running',task:'unfollow',processed:4,issues:1,
          owner_profile_visits:3,owner_sibling_proofs:2},
        {account:'ig_second_123456',expected_handle:'beta.two',
          running:false,state:'paused',task:'cancel',processed:3,issues:0,
          owner_profile_visits:1,owner_sibling_proofs:5}
      ]})});
  });
  const restored=await context.newPage();
  await restored.goto(url,{waitUntil:'domcontentloaded'});
  await restored.locator('#igcAppShell').waitFor({state:'visible',timeout:15000});
  await restored.evaluate(()=>window.showPage('automations'));
  const restoredPanel=restored.locator('#igcDualActionWorkspacePanel');
  await restoredPanel.waitFor({state:'visible',timeout:12000});
  await restoredPanel.getByText('@alpha.one').waitFor({state:'visible',timeout:12000});
  assert.match(await restoredPanel.innerText(),/@beta\.two/);
  assert.equal(await restored.locator('#igcDawParallelOptIn').isChecked(),true,
    'Existing exact controller mode must display correctly after reload');
  assert.match(await restored.locator('#igcDawStatus0').innerText(),/Robot activo/);
  assert.match(await restored.locator('#igcDawStatus1').innerText(),/Robot detenido/);
  assert.match(await restored.locator('#igcDawStatus0').innerText(),/visitas a mi perfil: 3/);
  assert.match(await restored.locator('#igcDawStatus0').innerText(),/identidad desde otra pestaña: 2/);
  assert.match(await restored.locator('#igcDawStatus1').innerText(),/visitas a mi perfil: 1/);
  assert.match(await restored.locator('#igcDawStatus1').innerText(),/identidad desde otra pestaña: 5/);
  assert(!/visitas a mi perfil: 4/.test(await restored.locator('#igcDawStatus0').innerText()),
    'The processed-target count must never be reported as owner-profile navigations');
  assert(restoredCalls.includes('GET')&&restoredCalls.every(x=>x==='GET'||x==='OPTIONS'),
    'No new action, review approval, Chrome launch or account mutation on rehydrate');
  // A login change in the application must promptly clear previous-owner
  // robot controls, rather than leaving actionable accounts on screen.
  await restored.evaluate(()=>{window.IGC_INSTAGRAM_PROFILES.owner='u_other_42'});
  await restored.waitForFunction(()=>
    !document.querySelector('#igcDawGrid')?.textContent?.includes('@alpha.one'),
    null,{timeout:11000});
  assert.doesNotMatch(await restoredPanel.innerText(),/@alpha\.one|@beta\.two/);
  await restored.close();
  await context.close();
  console.log('PASS: native Windows renders dual action cards; exact owner/session, Pending/Review, no parallel mutation, token and Chrome isolation UI');
 }finally{
  await browser.close();
  fs.rmSync(tmp,{recursive:true,force:true});
 }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
