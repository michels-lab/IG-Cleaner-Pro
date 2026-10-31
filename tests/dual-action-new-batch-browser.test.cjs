'use strict';
/* Native Windows two-account NEW-cohort UI acceptance: FAKE bridge, no Instagram. */
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
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'igc-granada-new-cohort-'));
  const native=path.join(tmp,'IG-Cleaner-Pro.html');
  const python=process.env.PYTHON||(process.platform==='win32'?'python':'python3');
  execFileSync(python,['-c',
    'import sys;sys.path.insert(0,"tools");from pathlib import Path;from ig_cleaner_desktop import prepare_html;prepare_html(Path(sys.argv[1]),Path(sys.argv[2]),dual_action_panel=True)',
    source,native],{cwd:root,stdio:'pipe'});
  const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
  try{
    const context=await browser.newContext({viewport:{width:1300,height:850}});
    await context.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort());
    const page=await context.newPage();
    page.on('dialog',d=>d.accept());
    await page.goto(pathToFileURL(native).href+'#igc-robot=37777.'+'a'.repeat(32),
      {waitUntil:'domcontentloaded'});
    await page.evaluate(()=>{
      const now=Math.floor(Date.now()/1000);
      localStorage.setItem('igc_v12027_supabase_session',JSON.stringify({
        access_token:'offline',refresh_token:'offline',expires_at:now+3600,
        user:{id:'fixture',email:'new-batch@example.test'}}));
      localStorage.setItem('igc_v12027_supabase_config',
        JSON.stringify({email:'new-batch@example.test'}));
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
    const owner=await page.evaluate(()=>window.IGC_INSTAGRAM_PROFILES.owner);
    await page.evaluate(()=>{
      window.__newBatchCalls=[];
      window.__markHistoryBlocked=false;
      window.__latePending=false;
      window.__failedFresh=false;
      const original=window.fetch;
      window.fetch=async(url,opts)=>{
        const target=String(url);
        if(!target.includes('/api/actions/dual-action-workspaces/'))
          return original(url,opts);
        const operation=target.split('/dual-action-workspaces/')[1].split('?')[0];
        const data=opts?.body?JSON.parse(opts.body):null;
        window.__newBatchCalls.push({operation,data,token:opts?.headers?.['X-IGC-Bridge-Token']});
        let response;
        if(operation==='configure')
          response={two_workspaces:true,parallel_mutations_enabled:false,lanes:[]};
        else if(operation==='preflight-new-one'){
          const blocked=window.__markHistoryBlocked||window.__latePending;
          const pending=window.__latePending;
          const fresh=window.__failedFresh;
          window.__failedFresh=false;
          const isBlocked=data.targets.some(x=>x==='already.seen')||blocked||fresh;
          response={
            owner:data.owner,account:data.account,expected_handle:data.expected_handle,
            task:data.task,read_only:true,actions_enabled:false,
            offline_untouched_only:!isBlocked,
            unresolved_saved_cohort:!!pending,
            evidence_counts:{untouched:isBlocked?0:data.targets.length,
              protected:0,previously_inspected:isBlocked?1:0},
            targets:data.targets.map(x=>({username:x,
              offline_evidence:isBlocked?'previously_inspected':'untouched'}))
          };
        }else if(operation==='start-one')
          response={status:'starting',account:data.account,task:data.action.task};
        else response={owner:window.IGC_INSTAGRAM_PROFILES.owner,
          parallel_mutations_enabled:false,lanes:[]};
        return {ok:true,json:async()=>response};
      };
    });
    await page.locator('#igcDawConfigure').click();
    const requests=()=>page.evaluate(()=>window.__newBatchCalls);
    let calls=await requests();
    assert.deepEqual(calls.map(x=>x.operation),['configure','status']);
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,0,
      'No start is possible without an explicit exact-list local preflight.');

    await page.locator('#igcDawNewTargets0').fill('@same.person, @same.person');
    await page.locator('#igcDawNewVerify0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='preflight-new-one').length,0,
      'Duplicate usernames are rejected BEFORE even a backend preflight.');
    await page.locator('#igcDawNewTargets0').fill('@already.seen\n@new.one');
    await page.locator('#igcDawNewVerify0').click();
    assert.equal(await page.locator('#igcDawNewList0 .igc-daw-unresolved').count(),2);
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,0,
      'Never autorun a protected/visited/uncertain/historical target.');

    await page.locator('#igcDawNewTargets0').fill('@new.one\n@new.two');
    await page.locator('#igcDawNewVerify0').click();
    assert.equal(await page.locator('#igcDawNewList0 .igc-daw-reviewed').count(),2);
    await page.locator('#igcDawNewTargets0').fill('@changed.one');
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,0,
      'The exact list must remain unchanged after preflight.');

    await page.locator('#igcDawNewTargets0').fill('@new.one\n@new.two');
    await page.locator('#igcDawNewVerify0').click();
    await page.locator('#igcDawNewBatch0').fill('17');
    await page.locator('#igcDawNewGap0').fill('20');
    await page.locator('#igcDawNewRest0').fill('12');
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,0,
      'Changing pacing requires fresh owner-specific preflight.');

    await page.locator('#igcDawNewVerify0').click();
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    let starts=calls.filter(x=>x.operation==='start-one');
    assert.equal(starts.length,1,'Explicit new batch only starts once after local preflight.');
    const first=starts[0].data;
    assert.equal(first.owner,owner);
    assert.equal(first.account,'ig_first_1234567');
    assert.equal(first.action.expected_handle,'alpha.one');
    assert.equal(first.action.task,'unfollow');
    assert.deepEqual(first.action.targets,['new.one','new.two']);
    assert.equal(first.action.batch_size,17);
    assert.equal(first.action.gap_seconds,20);
    assert.equal(first.action.rest_minutes,12);
    assert.equal(first.action.followers_evidence,true);
    assert.equal(first.action.confirmation,'unfollow:2');
    assert.equal(first.confirmation,
      'action-workspace-start:'+owner+':ig_first_1234567:unfollow');
    assert(calls.every(x=>x.token==='a'.repeat(32)));
    await page.locator('#igcDawNewStart0').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,1,
      'Start is one-shot; never replay the same preflight/confirmation.');

    // Second Chrome account has a distinct task/targets and cannot leak A.
    await page.locator('#igcDawTask1').selectOption('cancel');
    await page.locator('#igcDawNewTargets1').fill('@pending.friend');
    await page.locator('#igcDawNewVerify1').click();
    await page.locator('#igcDawNewStart1').click();
    calls=await requests();starts=calls.filter(x=>x.operation==='start-one');
    assert.equal(starts.length,2);
    const second=starts[1].data;
    assert.equal(second.account,'ig_second_123456');
    assert.equal(second.action.expected_handle,'beta.two');
    assert.equal(second.action.task,'cancel');
    assert.deepEqual(second.action.targets,['pending.friend']);
    assert.equal(second.action.followers_evidence,false);
    assert.equal(second.action.confirmation,'cancel:1');
    assert.equal(second.confirmation,
      'action-workspace-start:'+owner+':ig_second_123456:cancel');

    // A new saved pending cohort or a changed local action record is fail-closed
    // even if the previous offline check said the list was untouched.
    await page.locator('#igcDawNewTargets1').fill('@still.new');
    await page.locator('#igcDawNewVerify1').click();
    await page.evaluate(()=>window.__latePending=true);
    await page.locator('#igcDawNewStart1').click();
    calls=await requests();
    assert.equal(calls.filter(x=>x.operation==='start-one').length,2);
    assert(calls.some(x=>x.operation==='preflight-new-one'&&x.data.account==='ig_second_123456'));
    assert.equal(await page.locator('#igcDawGrid .igc-daw-card').count(),2);
    await context.close();
    console.log('PASS: dual-account new batch exact owner/WAL preflight, duplicate/visited/pending denial, pacing and one-shot manual consent');
  }finally{
    await browser.close();
    fs.rmSync(tmp,{recursive:true,force:true});
  }
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1});
