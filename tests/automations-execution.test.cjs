'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const script=source.match(/<script id="igc-automations-plan">([\s\S]*?)<\/script>/);
assert(script,'Action script not found');
const store=new Map(),calls=[],texts=[],opened=[];
let batchFixture=null, startFailure=null;
const elements={};
for(const id of ['igcAutoRows','igcAutoMetrics','igcAutoExecutionMetrics'])elements[id]={
 children:[],replaceChildren(){this.children=[]},appendChild(node){this.children.push(node)}
};
for(const id of ['igcAutoStatus','igcAutoLiveStatus'])elements[id]={textContent:''};
elements.igcAutoCommandFeedback={textContent:'',style:{display:'none'}};
elements.igcAutoOpenTabs={textContent:'',style:{display:'none'}};
for(const [id,value] of Object.entries({igcAutoSearch:'',igcAutoBatch:'2',igcAutoRest:'5',igcAutoGap:'5'}))elements[id]={value};
elements.igcAutoProgress={value:0};elements.igcAutoPause={disabled:false};elements.igcAutoResume={disabled:false};elements.igcAutoRun={disabled:false};
elements.igcActionAuthFallback={style:{display:'none'}};
elements.igcAutoBatchApproval={style:{display:'none'}};
elements.igcAutoBatchApprovalDetails={textContent:''};
for(const id of ['igcAutoApproveBatch','igcAutoRecheckBatch','igcAutoOpenBatchIssues'])elements[id]={disabled:false};
const document={hidden:false,getElementById:id=>elements[id]||null,
 createElement:tag=>({tag,children:[],textContent:'',appendChild(node){this.children.push(node)},
  addEventListener(type,fn){if(type==='click')this.click=fn}})};
const context={owner:'owner_A',active:'ig_A',accounts:[{account_key:'ig_A',username:'my.profile'}]};
const p={
 status:'running',message:'fixture',owner:'owner_A',account:'ig_A',task:'unfollow',
 total:2,successful:0,remaining:2,errors:0,protected:0,skipped:0,
 rows:[{username:'skip.me',status:'pending'},{username:'keep.me',status:'pending'}],
 running:true
};
const mockFetch=async(url,options)=>{
 const type=url.split('/').pop();
 const data=options.body?JSON.parse(options.body):null;
 calls.push({type,data,url});
 assert.equal(options.headers['X-IGC-Bridge-Token'],'0123456789abcdefghijabcdefgh');
 if(type==='history')return {ok:true,json:async()=>({
   owner:context.owner,account:context.active,task:data.task,attempted_usernames:[]
 })};
 if(type==='review-batch')return {ok:true,json:async()=>({
    owner:context.owner,account:context.active,task:data.task,batch:batchFixture
 })};
 if(type==='start'&&startFailure)return {ok:false,json:async()=>({error:startFailure})};
 if(type==='approve-batch'){
  const result={approved_usernames:['keep.me'],unresolved_usernames:['skip.me']};
  batchFixture=null;
  return {ok:true,json:async()=>result};
 }
 return {ok:true,json:async()=>type==='status'?p:
   type==='start'?{...p,message:'fixture action started',status:p.status==='idle'?'idle':'starting',running:p.status!=='idle'}:
   {...p,message:'fixture action started'}};
};
const localStorage={getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)};
const ctx={document,localStorage,
 window:{IGC_INSTAGRAM_PROFILES:context,location:{hash:'#igc-robot=33333.0123456789abcdefghijabcdefgh'},
 showPage:()=>{},confirm:message=>(texts.push(message),true),
 open:(...params)=>opened.push(params)},
 followingRaw:[{username:'skip.me'},{username:'keep.me'},{username:'mutual.person'}],
 followersRaw:[{username:'mutual.person'}],followersMap:new Map([['mutual.person',{}]]),
 pendingRequestsRaw:[{username:'request.one'}],protectedSet:new Set(),
 saveSet(){},LS_PROT:'protected',Set,Map,JSON,Math,Date,Number,String,encodeURIComponent,
 allRows:[{username:'keep.me',relation:'not_following',relationGood:false,followsBack:false,
 isFollower:false,dateMain:0}],doneSet:new Set(),reviewedMeta:{},
 currentMode:'following',makeReviewMeta:(row,reason,source)=>({mode:'following',
 relation:row.relation,relationGood:false,followsBack:false,isFollower:false,
 reviewedAt:Date.now(),reviewReason:reason,reviewSource:source}),
 saveReviewedState(){},renderAll(){},
 fetch:mockFetch,setInterval(){},Error};
vm.createContext(ctx);vm.runInContext(script[1],ctx);
assert.equal(ctx.window.igcAutoSwitchGuard(),false,
 'Unknown active robot status must block switching to another account');
(async()=>{
 ctx.window.igcAutoRender();
 ctx.window.igcAutoSkip('unfollow','skip.me');
 await ctx.window.igcAutoStart();
 const request=calls.find(c=>c.type==='start');assert(request);
 assert.deepEqual(request.data.targets,['keep.me']);
 assert.equal(request.data.confirmation,'unfollow:1');
 assert.equal(request.data.expected_handle,'my.profile');
 assert.equal(request.data.followers_evidence,true);
 assert.equal(request.data.gap_seconds,5);
 assert(texts[0].includes('UNFOLLOW'));
 ctx.window.igcAutoChoose('cancel');
 await ctx.window.igcAutoStart();
 const requests=calls.filter(c=>c.type==='start');assert.equal(requests.length,2);
 assert.equal(requests[1].data.task,'cancel');
 assert.deepEqual(requests[1].data.targets,['request.one']);
 ctx.window.V119_HTML={partial:true};
 ctx.window.igcAutoChoose('audit');
 await ctx.window.igcAutoStart();
 const readOnly=calls.filter(c=>c.type==='start').at(-1);
 assert.equal(readOnly.data.task,'audit');
 assert.equal(readOnly.data.followers_evidence,false,'Optional audit must not require complete exports');
 assert(texts.at(-1).includes('READ-ONLY'));
 ctx.window.igcAutoChoose('unfollow');
 await ctx.window.igcAutoStart();
 assert.equal(calls.filter(c=>c.type==='start').length,3,'Partial HTML must reject an unfollow but allow optional audit');
 ctx.window.V119_HTML={partial:false};
 p.open_review_tabs=[{username:'needs.review',status:'review'},
                     {username:'pending.inspect',status:'checking'}];
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcAutoOpenTabs.style.display,'block');
 assert.match(elements.igcAutoOpenTabs.textContent,/@needs.review/);
 assert(elements.igcAutoOpenTabs.textContent.includes('2/10'));
 assert.equal(elements.igcAutoRun.disabled,true,'Run disabled while robot is active');
 assert.match(elements.igcAutoStatus.textContent,/ROBOT · UNFOLLOW · RUNNING/);
 p.current_wait={username:'needs.review',phase:'waiting_relationship_control',
                 elapsed_seconds:7,timeout_seconds:20};
 await ctx.window.igcAutoPoll();
 assert.match(elements.igcAutoLiveStatus.textContent,/Waiting for @needs.review/);
 assert.match(elements.igcAutoLiveStatus.textContent,/Following \/ Siguiendo button/);
 assert.match(elements.igcAutoLiveStatus.textContent,/7\/20 s/);
 p.current_wait={username:'needs.review',phase:'loading_profile',
                 elapsed_seconds:2,timeout_seconds:20};
 await ctx.window.igcAutoPoll();
 assert.match(elements.igcAutoLiveStatus.textContent,/Instagram profile to load/);
 p.current_wait=null;
 await ctx.window.igcAutoPause();
 assert(calls.some(c=>c.type==='pause'),'Pause control must call local robot');
 assert(texts.some(value=>value.includes('will close its Chrome window')),
   'Pausing with unverified action tabs must require a warning');
 p.open_review_tabs=[];
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcAutoOpenTabs.style.display,'none');
 await ctx.window.igcAutoPoll();
 assert.equal(ctx.window.igcAutoSwitchGuard(),false,
  'Running Chrome actions must block switching account/profile');
 p.running=false;p.status='paused';
 await ctx.window.igcAutoPoll();
 assert.equal(ctx.window.igcAutoSwitchGuard(),true,
  'After the backend confirms paused, owner switch may proceed');
 assert.equal(elements.igcAutoProgress.value,0);
 // If owner B is selected while A's job is paused, the UI must still
 // know A is paused and allow returning to A. When A resumes, deny switch.
 context.owner='owner_B';context.active='ig_B';
 await ctx.window.igcAutoPoll();
 assert.equal(ctx.window.igcAutoSwitchGuard(),true,
  'Paused job in owner A must allow navigating back from owner B');
 assert.match(elements.igcAutoLiveStatus.textContent,/another account/,
  "Cross-owner status must be explained without exposing another account's queue");
 p.running=true;p.status='running';
 await ctx.window.igcAutoPoll();
 assert.equal(ctx.window.igcAutoSwitchGuard(),false,
  'Active job for a different account still blocks identity change');
 context.owner='owner_A';context.active='ig_A';
 p.running=false;p.status='blocked';
 p.message='Instagram requested a reCAPTCHA or account security check. The robot stopped before performing actions.';
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcActionAuthFallback.style.display,'block',
   'Human CAPTCHA block must expose safe manual Pending/Following options');
 assert.equal(elements.igcAutoResume.disabled,true,
   'Blocked CAPTCHA should not be retried through Resume');
 assert.equal(elements.igcAutoRun.disabled,true,'Blocked CAPTCHA cannot restart via Run');
 assert.match(elements.igcAutoStatus.textContent,/security check/);
 assert.match(elements.igcAutoLiveStatus.textContent,/security check/);
 context.owner='owner_B';context.active='ig_B';
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcActionAuthFallback.style.display,'none',
  'CAPTCHA recovery UI must not leak across Instagram accounts');
 context.owner='owner_A';context.active='ig_A';
 p.status='paused';p.message='Progress saved';
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcActionAuthFallback.style.display,'none');
 assert.equal(elements.igcAutoResume.disabled,false);
 assert.equal(elements.igcAutoRun.disabled,false,'Paused robot allows next owner-authorized Run');
 // The backend action journal is separate from owner-approved reviewed state.
 p.status='partial';p.running=false;p.task='unfollow';p.owner='owner_A';p.account='ig_A';
 batchFixture={id:'batch123',targets:['keep.me','skip.me','untouched.three'],approved_at:null,
  action_results:{'keep.me':{status:'ok'},'skip.me':{status:'review'},
                  'untouched.three':{status:'pending'}},
  recheck_results:{}};
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcAutoBatchApproval.style.display,'block');
 assert.match(elements.igcAutoBatchApprovalDetails.textContent,/Batch incomplete/);
 assert.equal(elements.igcAutoApproveBatch.disabled,true,'Cannot approve an incomplete batch');
 assert.equal(ctx.doneSet.size,0,'Robot success must not mark anything reviewed without owner approval');
 // Run continues untouched action targets, not a read-only verification pass.
 ctx.window.igcAutoChoose('unfollow');
 // Continue the saved three-profile cohort only when the selected size
 // matches it. Mismatches must not silently launch an older 40-person batch.
 elements.igcAutoBatch.value='3';
 await ctx.window.igcAutoStart();
 elements.igcAutoBatch.value='2';
 assert.equal(calls.filter(c=>c.type==='start').length,4,
   'Run must start actual actions for the saved unapproved cohort');
 assert.equal(calls.filter(c=>c.type==='recheck-batch').length,0,
   'Run must never silently switch to read-only recheck');
 const retry=calls.filter(c=>c.type==='start').at(-1);assert(retry);
 assert.equal(retry.data.batch_id,'batch123');
 assert.deepEqual(retry.data.targets,['keep.me','skip.me','untouched.three']);
 assert.equal(retry.data.confirmation,'unfollow:3');
 assert(texts.at(-1).includes('Only these safe profiles will be attempted'));
 await ctx.window.igcAutoOpenBatchIssues();
 const manualOpen=calls.filter(c=>c.type==='open-profile');
 assert.equal(manualOpen.length,1,'Only issue profiles may open, never untouched accounts');
 assert.equal(manualOpen[0].data.username,'skip.me');
 assert.equal(manualOpen[0].data.task,'unfollow');
 assert.equal(opened.length,0,'Integrated Windows must not open separate logged-out browser');
 await ctx.window.igcAutoApproveBatch();
 assert.equal(calls.filter(c=>c.type==='approve-batch').length,0,
   'Cannot approve while one profile was never attempted');
 batchFixture.action_results['untouched.three']={status:'already_not_following'};
 await ctx.window.igcAutoPoll();
 assert.match(elements.igcAutoBatchApprovalDetails.textContent,/already not following \(no click\)/);
 assert.equal(elements.igcAutoApproveBatch.disabled,false,
   'Explicitly verified already-not-following is complete, not an issue');
 await ctx.window.igcAutoApproveBatch();
 const approved=calls.find(c=>c.type==='approve-batch');assert(approved);
 assert.equal(approved.data.confirmation,'reviewed:batch123');
 assert(ctx.doneSet.has('keep.me'),'Owner-confirmed verified profile must become reviewed');
 assert(!ctx.doneSet.has('skip.me'),'Unresolved result must remain not reviewed');
 assert.equal(elements.igcAutoBatchApproval.style.display,'none');
 await ctx.window.igcAutoRecheckHistory();
 const historical=calls.find(c=>c.type==='recheck-history');
 assert(historical,'Historical read-only action journal recovery must be reachable from UI');
 assert.equal(historical.data.task,'unfollow');
 assert.equal(historical.data.expected_handle,'my.profile');
 assert.equal(historical.data.confirmation,'history-read-only:unfollow');
 assert(!historical.data.targets,'UI must not select/click per-person actions for historical read-only scan');
 assert(texts.at(-1).includes('No Unfollow/Cancel action'),
   'History scan must require one explicit explanation of its no-click behavior');
 assert(!calls.some(c=>c.type==='approve-batch' && c.data.confirmation==='history-read-only:unfollow'));
 // Verified absent requests are completed non-click outcomes, not cancel clicks.
 p.status='complete';p.running=false;p.task='cancel';p.total=1;
 p.successful=0;p.already_not_requested=1;p.remaining=0;
 batchFixture={id:'cancel-verified',targets:['request.one'],approved_at:null,
  action_results:{'request.one':{status:'already_not_requested'}},recheck_results:{}};
 ctx.window.igcAutoChoose('cancel');
 await ctx.window.igcAutoPoll();
 assert.match(elements.igcAutoExecutionMetrics.children.map(x=>x.textContent).join(' | '),
  /Cancellations confirmed: 0.*Already no pending request: 1/);
 assert.match(elements.igcAutoBatchApprovalDetails.textContent,/verified no pending request \(no click\)/);
 assert.equal(elements.igcAutoApproveBatch.disabled,false,
  'Completed no-click result may be approved explicitly, never auto-Reviewed');

 // Screenshot-equivalent saved cohort: 10 targets, 2 unresolved and 8
 // untouched must be sent to the Windows action endpoint, not read-only audit.
 const ten=Array.from({length:10},(_,i)=>'saved.'+i);
 batchFixture={id:'screen-ten',targets:ten,approved_at:null,
   action_results:{'saved.0':{status:'review'},'saved.1':{status:'review'}},
   recheck_results:{}};
 p.running=false;p.status='paused';p.task='unfollow';p.owner=context.owner;
 p.account=context.active;
 ctx.window.igcAutoChoose('unfollow');
 // Mode switch hydrates the account's saved size preference. Mimic the
 // owner's CURRENT visible choice after switching the action lane.
 elements.igcAutoBatch.value='10';
 const startCount=calls.filter(c=>c.type==='start').length;
 await ctx.window.igcAutoStart();
 const submitted=calls.filter(c=>c.type==='start');
 assert.equal(submitted.length,startCount+1,
   'Screenshot-equivalent saved batch must reach real action start endpoint');
 assert.equal(submitted.at(-1).data.batch_id,'screen-ten');
 assert.equal(submitted.at(-1).data.targets.length,10);
 assert.equal(submitted.at(-1).data.task,'unfollow');
 assert(texts.at(-1).includes('8 targets are untouched or proven no-click'),
   'Owner consent must distinguish 8 eligible versus 2 unresolved targets');
 assert.match(elements.igcAutoCommandFeedback.textContent,/ACTION ACCEPTED/);
 batchFixture=null;
 // P0: An actual rejected Windows admission must remain visible after
 // background poll/rerender instead of silently appearing as Queue prepared.
 p.running=false;p.status='idle';p.owner=context.owner;p.account=context.active;
 p.task='unfollow';p.message='No active Chrome worker';
 batchFixture=null;
 startFailure='The saved Windows cohort is blocked by a local journal conflict.';
 ctx.window.igcAutoChoose('unfollow');
 await ctx.window.igcAutoStart();
 assert.match(elements.igcAutoCommandFeedback.textContent,/ACTION BLOCKED/);
 assert.match(elements.igcAutoCommandFeedback.textContent,/journal conflict/);
 assert.equal(elements.igcAutoCommandFeedback.style.display,'block');
 await ctx.window.igcAutoPoll();
 ctx.window.igcAutoRender();
 assert.match(elements.igcAutoCommandFeedback.textContent,/journal conflict/);
 assert.match(elements.igcAutoStatus.textContent,/ACTION BLOCKED/);
 assert.equal(elements.igcAutoRun.disabled,false,
   'Rejected start can be retried by explicit click after resolving the issue');
 startFailure=null;
 // A backend returning a success HTTP status without an active worker
 // must not be presented as "Unfollow started".
 await ctx.window.igcAutoStart();
 assert.match(elements.igcAutoCommandFeedback.textContent,/Windows did not start the robot/);
 assert.match(elements.igcAutoCommandFeedback.textContent,/No active Chrome worker/);
 assert(!/Queue prepared/.test(elements.igcAutoStatus.textContent));

 console.log('Automations execution, visible Windows start failure, exact admission proof and batch approval: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});