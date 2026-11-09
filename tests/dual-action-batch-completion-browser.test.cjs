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
   window.__staleStartStatus=false;
   window.__wrongReviewScope=false;
   window.__delayReview=false;
   window.__largeSavedReview=false;
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
      payload={owner:window.IGC_INSTAGRAM_PROFILES.owner,
        parallel_mutations_enabled:window.__activeParallel,
        lanes:Object.values(window.__laneStates).map(l=>window.__staleStartStatus&&
          l.account==='ig_first_1234567'?{...l,state:'idle',running:false,task:''}:l)};
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
      if(window.__delayReview)await new Promise(resolve=>window.__releaseReview=resolve);
      const first=data.account==='ig_first_1234567';
      payload={owner:window.__wrongReviewScope?'another_owner':data.owner,
        account:data.account,task:data.task,
        batch:{id:first?'first-wave':'second-wave',
          targets:first?[
            'first.person','previous.follow','no.click',
            'possible.click','ambiguous.closed','missing.profile']:
            ['pending.friend','old.pending'],
          action_results:first?{
           'first.person':{status:'ok',possible_click:true,
             message:'Verified Unfollow after refresh',
             at:'2026-10-30T18:00:00Z'},
           'previous.follow':{status:'already_not_following',
             possible_click:false,message:'No Unfollow clicked: already not following.'},
           'no.click':{status:'error',possible_click:false,safe_no_click:true,
             message:'Exact target was unavailable before any click.'},
           'possible.click':{status:'review',possible_click:true,
             message:'Durable relationship click phase was armed; outcome unknown.',
             at:'2026-10-30T18:01:00Z'},
           'ambiguous.closed':{status:'profile_unavailable',possible_click:true,
             message:'Closed now; prior relationship click outcome unknown.'},
           'missing.profile':{status:'profile_unavailable',possible_click:false,
             message:'Exact page-unavailable notice; no action clicked.'}
          }:{
            'pending.friend':{status:'review',at:'2026-10-30T18:03:00Z'},
            'old.pending':{status:'already_not_requested',possible_click:false,
              message:'No Cancel Request clicked: no active request.'}
          }
        }};
      if(window.__largeSavedReview&&first){
        // 725 original saved profiles: a late uncertain click must lead the
        // display and a green historical OK must remain reachable on page 15.
        const targets=Array.from({length:725},(_,i)=>
          'bulk.'+String(i).padStart(3,'0'));
        payload.batch={id:'saved-725',targets,action_results:{
          'bulk.724':{status:'review',possible_click:true,
            message:'Previous click outcome unknown. No automatic replay.'},
          'bulk.000':{status:'ok',message:'Earlier confirmed action.'}
        }};
      }
    }else payload={status:'idle'};
    return {ok:true,json:async()=>payload};
   };
  });
  const calls=()=>page.evaluate(()=>window.__completedCalls);
  const opt=page.locator('#igcDawParallelOptIn');
  await opt.check();
  await page.locator('#igcDawConfigure').click();
  // No worker has run in this UI session, as after a Windows app restart.
  // The owner can still reopen each saved original WAL without new actions.
  const savedModal=page.locator('#igcDawCompletionModal');
  let before=(await calls()).filter(x=>x.operation==='review-one').length;
  await page.locator('#igcDawSavedSummary0').click();
  await savedModal.waitFor({state:'visible',timeout:5000});
  assert.match(await savedModal.innerText(),/Revisión guardada.*@alpha.one/);
  await savedModal.getByText('@possible.click').waitFor({state:'visible',timeout:5000});
  assert.deepEqual(await savedModal.locator('.igc-daw-review-row').evaluateAll(
    rows=>rows.map(r=>r.querySelector('span')?.textContent)),
    ['@possible.click','@ambiguous.closed','@no.click',
     '@missing.profile','@previous.follow','@first.person']);
  const aRows=savedModal.locator('.igc-daw-review-row');
  assert.match(await aRows.nth(0).innerText(),/REVIEW · CLIC INCIERTO/);
  assert.match(await aRows.nth(0).innerText(),/Durable relationship click phase/);
  assert.match(await aRows.nth(1).innerText(),/REVIEW · CLIC INCIERTO/);
  assert.match(await aRows.nth(1).innerText(),/Closed now; prior relationship click/);
  assert.match(await aRows.nth(2).innerText(),/REVIEW · SIN CLIC/);
  assert.match(await aRows.nth(3).innerText(),/PERFIL NO DISPONIBLE/);
  assert.match(await aRows.nth(4).innerText(),/SIN ACCIÓN · YA NO SIGUES/);
  assert.match(await aRows.nth(5).innerText(),/OK · ACCIÓN CONFIRMADA/);
  assert.match(await aRows.nth(0).getAttribute('class'),/igc-daw-uncertain/);
  assert.match(await aRows.nth(1).getAttribute('class'),/igc-daw-uncertain/);
  assert.match(await aRows.nth(4).getAttribute('class'),/igc-daw-no-change/);
  assert.doesNotMatch(await aRows.nth(4).getAttribute('class'),/igc-daw-reviewed/);
  assert.equal((await calls()).filter(x=>x.operation==='review-one').length,
    before+1,'Saved summary reads the WAL once, not by repeated profile visits.');
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,0);
  assert.equal((await calls()).filter(x=>x.operation==='approve-one').length,0);
  await savedModal.getByRole('button',{name:'Cerrar'}).click();
  await page.locator('#igcDawReview0').click();
  await page.waitForFunction(()=>
    document.querySelector('#igcDawTarget0')?.options?.length===3);
  assert.deepEqual(await page.locator('#igcDawTarget0 option').evaluateAll(
    rows=>rows.map(r=>r.value)),['possible.click','ambiguous.closed','no.click'],
    'Only unresolved rows are manually inspectable, never green or blue no-action rows.');
  await page.locator('#igcDawTask1').selectOption('cancel');
  await page.locator('#igcDawSavedSummary1').click();
  await savedModal.waitFor({state:'visible',timeout:5000});
  assert.match(await savedModal.innerText(),/Revisión guardada.*@beta.two/);
  await savedModal.getByText('@pending.friend').waitFor({state:'visible',timeout:5000});
  assert.match(await savedModal.locator('.igc-daw-review-row').nth(1).innerText(),
    /SIN ACCIÓN · SIN SOLICITUD/);
  assert.match(await savedModal.locator('.igc-daw-review-row').nth(1).getAttribute('class'),
    /igc-daw-no-change/);
  await savedModal.getByRole('button',{name:'Cerrar'}).click();
  // Malformed/wrong-owner local bridge response cannot leak other account
  // records into the visible summary, or authorize any action.
  await page.evaluate(()=>window.__wrongReviewScope=true);
  await page.locator('#igcDawSavedSummary0').click();
  assert.equal(await savedModal.isVisible(),false);
  await page.evaluate(()=>window.__wrongReviewScope=false);
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,0);
  // An outstanding read-only result must be discarded if the operator
  // changes the selected task while it is in flight.
  await page.evaluate(()=>window.__delayReview=true);
  await page.locator('#igcDawSavedSummary0').click();
  await page.waitForFunction(()=>typeof window.__releaseReview==='function');
  await page.locator('#igcDawTask0').selectOption('cancel');
  await page.evaluate(()=>{window.__delayReview=false;window.__releaseReview();});
  await page.waitForFunction(()=>
    !document.querySelector('#igcDawSavedSummary0')?.disabled);
  assert.equal(await savedModal.isVisible(),false,
    'Stale Unfollow summary must not appear after changing task to Cancel Pending.');
  await page.locator('#igcDawTask0').selectOption('unfollow');
  // A start-one acknowledgement cannot be confused with the worker actually
  // running; mock a temporary idle status during backend thread startup.
  await page.evaluate(()=>window.__staleStartStatus=true);
  await page.locator('#igcDawNewTargets0').fill('@first.person');
  await page.locator('#igcDawNewVerify0').click();
  await page.locator('#igcDawNewStart0').click();
  assert.equal(await page.locator('#igcDawCompletionModal').isVisible(),false,
    'Start authorization followed by old idle status must not show phantom completion.');
  await page.evaluate(()=>window.__staleStartStatus=false);
  await page.locator('#igcDawRefresh').click();
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
    task:'unfollow',processed:6,pending:0,issues:3
   };
  });
  await page.locator('#igcDawRefresh').click();
  const modal=page.locator('#igcDawCompletionModal');
  await modal.waitFor({state:'visible',timeout:5000});
  assert.match(await modal.innerText(),/@alpha.one/);
  assert.match(await modal.innerText(),/3 requieren atención/);
  await modal.getByText('@possible.click').waitFor({state:'visible',timeout:5000});
  const exactOwner=await page.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.owner);
  const firstCompletionRead=(await calls()).filter(x=>x.operation==='review-one').at(-1);
  assert.equal(firstCompletionRead.data.owner,exactOwner,
    'Completion A MUST include the current app OWNER, not the current Chrome profile string');
  assert.equal(firstCompletionRead.data.account,'ig_first_1234567');
  assert.equal(firstCompletionRead.data.task,'unfollow');
  assert.deepEqual(await modal.locator('.igc-daw-review-row').evaluateAll(rows=>
    rows.map(r=>r.querySelector('span')?.textContent)),[
    '@possible.click','@ambiguous.closed','@no.click',
    '@missing.profile','@previous.follow','@first.person'],
    'Review must appear ahead of green OK, without changing the original batch order.');
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
  const secondCompletionRead=(await calls()).filter(x=>x.operation==='review-one').at(-1);
  assert.equal(secondCompletionRead.data.owner,exactOwner,
    'Completion B MUST also use the same exact app owner, scoped to account B');
  assert.equal(secondCompletionRead.data.account,'ig_second_123456');
  assert.equal(secondCompletionRead.data.task,'cancel');
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
  // Large real-world cohort UX: all 725 original targets must be reachable
  // without a new browser action, fresh review approval, or mutation of WAL.
  await page.evaluate(()=>window.__largeSavedReview=true);
  const beforeLarge=(await calls()).filter(x=>x.operation==='start-one').length;
  const beforeApproval=(await calls()).filter(x=>x.operation==='approve-one').length;
  await page.locator('#igcDawSavedSummary0').click();
  await savedModal.waitFor({state:'visible',timeout:5000});
  assert.equal(await savedModal.locator('.igc-daw-review-row').count(),50,
    'Do not render 725 browser rows and freeze the completion dialog');
  assert.match(await savedModal.locator('.igc-daw-pager-count').innerText(),
    /Resultados 1–50 de 725 · página 1 de 15/);
  assert.match(await savedModal.locator('.igc-daw-review-row').first().innerText(),
    /@bulk\.724.*REVIEW · CLIC INCIERTO/s);
  await savedModal.locator('.igc-daw-page-jump').selectOption('15');
  assert.match(await savedModal.locator('.igc-daw-pager-count').innerText(),
    /Resultados 701–725 de 725 · página 15 de 15/);
  assert.equal(await savedModal.locator('.igc-daw-review-row').count(),25);
  assert.match(await savedModal.locator('.igc-daw-review-row').last().innerText(),
    /@bulk\.000.*OK · ACCIÓN CONFIRMADA/s);
  assert.equal(await savedModal.locator('.igc-daw-page-next').isDisabled(),true);
  await savedModal.locator('.igc-daw-page-prev').click();
  assert.match(await savedModal.locator('.igc-daw-pager-count').innerText(),
    /Resultados 651–700 de 725/);
  // Search across the WHOLE saved 725 (not only 50 rendered), preserving
  // input focus and with no browser, server or action requests on each key.
  const beforeSearch=(await calls()).length;
  await savedModal.locator('.igc-daw-review-search').fill('@bulk.724');
  assert.equal(await savedModal.locator('.igc-daw-review-row').count(),1);
  assert.match(await savedModal.locator('.igc-daw-pager-count').innerText(),
    /Resultados 1–1 de 1 \(de 725 originales\)/);
  assert.equal(await savedModal.locator('.igc-daw-review-search').inputValue(),
    '@bulk.724','Typing must not lose text when page rows rerender');
  await savedModal.locator('.igc-daw-review-search').fill('absent.person');
  assert.equal(await savedModal.locator('.igc-daw-review-row').count(),0);
  assert.match(await savedModal.innerText(),/Sin coincidencias en esta tanda/);
  await savedModal.locator('.igc-daw-review-search').fill('');
  assert.equal(await savedModal.locator('.igc-daw-review-row').count(),50);
  assert.equal((await calls()).length,beforeSearch,
    'Searching historical saved outcomes must not fetch or change Instagram');
  await savedModal.getByRole('button',{name:'Cerrar'}).click();

  await page.locator('#igcDawReview0').click();
  await page.waitForFunction(()=>
    document.querySelector('#igcDawTarget0')?.options?.length===724,null,
    {timeout:10000});
  assert.equal(await page.locator('#igcDawReviewList0 .igc-daw-review-row').count(),50);
  assert.match(await page.locator('#igcDawReviewList0 .igc-daw-pager-count').innerText(),
    /Resultados 1–50 de 725/);
  assert.equal(await page.locator('#igcDawTarget0 option[value="bulk.724"]').count(),1,
    'Uncertain clicked target remains available for manual inspection');
  assert.equal(await page.locator('#igcDawTarget0 option[value="bulk.000"]').count(),0,
    'Green confirmed target may be displayed but never offered for action');
  await page.locator('#igcDawReviewList0 .igc-daw-page-jump').selectOption('15');
  assert.match(await page.locator('#igcDawReviewList0 .igc-daw-pager-count').innerText(),
    /Resultados 701–725 de 725/);
  assert.match(await page.locator('#igcDawReviewList0 .igc-daw-review-row').last().innerText(),
    /@bulk\.000.*OK · ACCIÓN CONFIRMADA/s);
  assert.equal((await calls()).filter(x=>x.operation==='start-one').length,beforeLarge,
    'Paging through the saved WAL must never start or replay a robot action');
  assert.equal((await calls()).filter(x=>x.operation==='approve-one').length,beforeApproval,
    'Paging must never silently approve saved Review results');
  await ctx.close();
  console.log('PASS: per-account completion + 725 saved targets pageable in dialog and Review, unchanged WAL, zero replay and zero approval');
 }finally{
  await browser.close();fs.rmSync(folder,{recursive:true,force:true});
 }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
