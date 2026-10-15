'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=source.match(/<script id="igc-profile-counts-ui">([\s\S]*?)<\/script>/);
assert(match,'Profile Counts script missing from canonical Desktop source');
new vm.Script(match[1],{filename:'igc-profile-counts-ui.js'});
assert(source.includes('id="igcProfileCountsPanel"'),'Automations must expose Profile Counts results');
assert(source.includes('id="igcCountsImport"'),'Import control missing');
assert(source.includes('id="igcCountsRobotActions"'),'Direct browser robot controls missing');
const automationStart=source.indexOf('id="page-automations"');
const insightsStart=source.indexOf('id="page-profileStats"');
const robotStart=source.indexOf('id="igcCountsRobotBridge"');
const countsStart=source.indexOf('id="igcCountsRows"');
assert(automationStart>=0 && automationStart<robotStart && robotStart<insightsStart,
 'Every robot, including Profile Counts, must live within Automations');
assert(robotStart<countsStart && countsStart<insightsStart &&
 source.indexOf('id="igcProfileCountsPanel"',insightsStart)===-1 &&
 source.indexOf('id="igcCountsRobotBridge"',insightsStart)===-1,
 'All Profile Counts controls, rows and exports must be in Automations; Insights is analytics only');


(async ()=>{
 const store=new Map(),summary=[],elements={
  igcCountsRows:{innerHTML:''},
  igcCountsSummary:{replaceChildren(){summary.length=0},appendChild(e){summary.push(e.textContent)}},
  igcCountsFootnote:{textContent:'',style:{}},
  igcCountsQuery:{value:''},
  igcCountsFilter:{value:'all'}
 };
 let clicked=0;const identity={owner:'owner_A',active:'ig_A'};
 const ctx={window:{
   localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)},
   IGC_INSTAGRAM_PROFILES:identity,
   location:{hash:''},
 },document:{
  readyState:'loading',addEventListener(){},
  getElementById:id=>elements[id]||null,
  createElement:()=>({textContent:'',style:{},click(){clicked++},remove(){}}),
  body:{appendChild(){}}
 },followingRaw:[{username:'public.user'},{username:'second.user'}],
  URL:{createObjectURL:()=> 'blob:fixture',revokeObjectURL(){}},
  Blob:class {constructor(){}},setTimeout(){},setInterval(){},Date,Number,Array,Set,Map,JSON,Math,
  encodeURIComponent,String,Error
 };
 vm.createContext(ctx);vm.runInContext(match[1],ctx);
 ctx.window.igcCountsRender();
 assert(summary.some(s=>s.includes('2 profiles')),'Render should read Following from active workspace');
 assert.match(elements.igcCountsRows.innerHTML,/public\.user/);
 // A large Following/Followers dataset must not be clipped by the visual page size.
 const smallImport=ctx.followingRaw;
 ctx.followingRaw=Array.from({length:50003},(_,i)=>({username:'large'+String(i).padStart(6,'0')}));
 ctx.window.igcCountsSetPage(0,true);
 assert(summary.some(t=>t.includes('50003 profiles')),
  'Insights must include the entire 50k+ dataset, not just the visible page');
 assert.match(elements.igcCountsRows.innerHTML,/large000000/);
 ctx.window.igcCountsSetPage(1);
 assert.match(elements.igcCountsRows.innerHTML,/large000250/,
  'Results beyond the first 250 rows must be available by pagination');
 ctx.followingRaw=smallImport;
 ctx.window.igcCountsSetPage(0,true);

 ctx.window.igcCountsExportQueue();
 assert.equal(clicked,1,'Export should trigger actual browser download');
 const csv='username,followers,following,checked_at,source,status,approximate\n'+
  'public.user,1234,222,2026-10-11T12:00:00+00:00,instagram_visible_profile_browser,ok,false\n'+
  'unrelated,999,999,2026-10-11T12:00:00+00:00,fixture,ok,false\n'+
  'second.user,,,2026-10-11T12:00:00+00:00,instagram_visible_profile_browser,unavailable,false\n';
 const input={files:[{text:async()=>csv}],value:'attached'};
 await ctx.window.igcCountsImportFile(input);
 assert.equal(input.value,'');
 assert.match(elements.igcCountsRows.innerHTML,/1,234/, 'Import must render counts: '+elements.igcCountsFootnote.textContent+' keys='+JSON.stringify(Array.from(store.keys())));
 assert(summary.some(s=>s.includes('1 with data')));
 const onlyKey=Array.from(store.keys())[0];
 assert(onlyKey.includes('owner_A')&&onlyKey.includes('ig_A'));
 const saved=JSON.parse(store.get(onlyKey));
 assert.equal(saved.records['public.user'].followers,'1234');
 assert.equal(saved.records['unrelated'],undefined,'Do not import profiles outside active Following');
 identity.active='ig_B';
 ctx.window.igcCountsRender();
 assert(summary.some(s=>s.includes('0 with data')),'Sibling Instagram must not inherit counts');
 identity.active='ig_A';identity.owner='owner_B';
 ctx.window.igcCountsRender();
 assert(summary.some(s=>s.includes('0 with data')),'Different app login must not inherit counts');

 // Simulate the actual local control protocol, including account-scoped sync.
 const bridgeStore=new Map(),requests=[];
 let staged=null;
 const robotElements={
  igcCountsRows:{innerHTML:''},
  igcCountsSummary:{replaceChildren(){},appendChild(){}},
  igcCountsFootnote:{textContent:'',style:{}},
  igcCountsQuery:{value:''},igcCountsFilter:{value:'all'},
  igcCountsRobotStatus:{textContent:'',style:{}},
  igcCountsRobotProgress:{value:0},
  igcCountsRobotActions:{style:{display:'none'}},
  igcCountsManualCSV:{style:{display:'none'}},
  igcCountsManualHelp:{style:{display:'none'}},
  igcCountsAuthFallback:{style:{display:'none'}},
  igcCountsRobotMax:{value:'200'},
  igcCountsRobotWindow:{value:'5'},
  igcCountsRobotGap:{value:'5'},
  igcCountsRobotRestEvery:{value:'10'},
  igcCountsRobotRestMinutes:{value:'2'},
  igcCountsRobotPaceNote:{textContent:'',style:{}},
  igcCountsMetricAnalyzed:{textContent:''},igcCountsMetricSuccess:{textContent:''},
  igcCountsMetricPending:{textContent:''},igcCountsMetricErrors:{textContent:''},
  igcCountsMetricUnavailable:{textContent:''},igcCountsMetricRemaining:{textContent:''},
  igcCountsRobotCurrent:{textContent:''},igcCountsRobotPercent:{textContent:''},
  igcCountsPause:{disabled:false},igcCountsResume:{disabled:false}
 };
 const bridgeIdentity={owner:'owner_A',active:'ig_A'};
 let statusOverride=null;
 const mockFetch=async(url,options)=>{
  requests.push({url,options});
  assert.match(url,/^http:\/\/127\.0\.0\.1:32111\/api\//);
  assert.equal(options.headers['X-IGC-Bridge-Token'],'0123456789abcdefghijklmnop');
  const action=url.split('/').pop();
  let value={};
  if(action==='init' && url.endsWith('/queue/init')){
   const b=JSON.parse(options.body);
   staged={owner:b.owner,account:b.account,total:b.total,transfer:'fixture-token',usernames:[]};
   value={transfer:staged.transfer,total:staged.total,received:0};
  } else if(action==='append' && url.endsWith('/queue/append')){
   const b=JSON.parse(options.body);
   assert.equal(b.owner,staged.owner);
   assert.equal(b.account,staged.account);
   assert.equal(b.transfer,staged.transfer);
   assert.equal(b.offset,staged.usernames.length);
   staged.usernames.push(...b.usernames);
   value={received:staged.usernames.length,total:staged.total};
  } else if(action==='start'){
   value={status:'starting',message:'Starting',total:1,progress:0};
  } else if(action==='auto'){
   value={status:'starting',message:'Auto-detecting Instagram login',total:0,progress:0};
  } else if(action==='following'){
   value={handle:'account.owner',complete:true,usernames:['public.user']};
  } else if(action==='load'){
   value={status:'idle',message:'Saved rows loaded',owner:'owner_A',account:'ig_A',total:1,progress:1};
  } else if(action==='status'){
   value=statusOverride||{status:'complete',message:'Done',owner:'owner_A',account:'ig_A',queue_source:'imported',total:1,progress:1,max_per_window:200,window_minutes:5,min_delay_seconds:5,pause_every:10,pause_minutes:2};
  } else if(action==='results'){
   value={rows:[
    {username:'public.user',followers:'3456',following:'789',status:'ok',
     checked_at:'2026-10-12T01:00:00+00:00',approximate:'false'},
    {username:'outside',followers:'999',following:'999',status:'ok',
     checked_at:'2026-10-12T01:00:00+00:00',approximate:'false'}
   ]};
  }
  return {ok:true,json:async()=>value};
 };
 const bridgeCtx={
  window:{localStorage:{getItem:k=>bridgeStore.get(k)||null,setItem:(k,v)=>bridgeStore.set(k,v)},
   IGC_INSTAGRAM_PROFILES:bridgeIdentity,
   location:{hash:'#igc-robot=32111.0123456789abcdefghijklmnop'}},
  document:{readyState:'loading',addEventListener(){},hidden:false,
   getElementById:id=>robotElements[id]||null,
   createElement:()=>({textContent:'',style:{}})},
  followingRaw:[{username:'public.user'}],fetch:mockFetch,setInterval(){},setTimeout(){},
  Date,Number,Array,Set,Map,JSON,Math,String,Error,encodeURIComponent
 };
 vm.createContext(bridgeCtx);vm.runInContext(match[1],bridgeCtx);
 assert.equal(robotElements.igcCountsRobotActions.style.display,'flex','Pacing, pause and resume must be visible');
 assert.equal(robotElements.igcCountsManualCSV.style.display,'flex',
  'Manual import/export must be visible even when Windows bot is connected');
 assert.equal(robotElements.igcCountsManualHelp.style.display,'block',
  'Manual recovery instructions must remain visible while the bot is connected');
 assert.match(source,/id="igcCountsAuthFallback"/);
 assert.match(source,/Review Pending manually/);
 assert.match(source,/Review Following manually/);
 assert.match(source,/onclick="showPage\('pendingRequests'\)"/);
 assert.match(source,/onclick="showPage\('list'\)"/);
 assert.match(source,/id="igcCountsResume"/,'Explicit Resume button should be visible');
 await bridgeCtx.window.igcCountsRobotConnect();
 const auto=requests.find(r=>r.url.endsWith('/auto'));
 assert(auto,'Automatic detection must begin without any Start click');
 assert.equal(JSON.parse(auto.options.body).account,'ig_A');
 assert.deepEqual(JSON.parse(auto.options.body).usernames,[]);
 assert.equal(JSON.parse(auto.options.body).use_staged_import,true);
 assert.equal(JSON.parse(auto.options.body).transfer,staged.transfer);
 assert.deepEqual(staged.usernames,['public.user']);
 assert.equal(JSON.parse(auto.options.body).discover_following,false);
 await bridgeCtx.window.igcCountsRobotDiscover();
 const optional=requests.filter(r=>r.url.endsWith('/auto')).at(-1);
 assert.equal(JSON.parse(optional.options.body).discover_following,true,'Following refresh must require an explicit owner click');
 assert.deepEqual(JSON.parse(optional.options.body).usernames,[]);
 await bridgeCtx.window.igcCountsRobotStart();
 const start=requests.find(r=>r.url.endsWith('/start'));
 assert(start,'Direct Start must submit a localhost POST');
 assert.equal(start.options.method,'POST');
 const startBody=JSON.parse(start.options.body);
 assert.equal(startBody.owner,'owner_A');assert.equal(startBody.account,'ig_A');
 assert.deepEqual(Array.from(startBody.usernames),['public.user']);
 assert.equal(startBody.max_per_window,200);
 assert.equal(startBody.window_minutes,5);
 assert.equal(startBody.min_delay_seconds,5);
 assert.equal(startBody.pause_every,10);
 assert.equal(startBody.pause_minutes,2);
 assert(bridgeStore.has('igc_robot_pacing_v1__owner_A__ig_A'),'User-selected pacing should be saved per Instagram');
 bridgeCtx.window.igcCountsRobotRestoreConfig();
 assert.equal(robotElements.igcCountsRobotMax.value,'200');
 assert.match(robotElements.igcCountsRobotPaceNote.textContent,/60 profiles/);
 assert.match(robotElements.igcCountsRobotPaceNote.textContent,/2 min after every 10/);
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.match(robotElements.igcCountsMetricSuccess.textContent,/Verified: 1/);
 assert.equal(robotElements.igcCountsAuthFallback.style.display,'none',
  'Manual CAPTCHA advice should not obscure ordinary successful collections');
 statusOverride={status:'needs_verification',message:'Instagram requires manual CAPTCHA/security verification.',running:true,
  owner:'owner_A',account:'ig_A',total:1,progress:0,successful:0,analyzed:0,pending:1,
  max_per_window:200,window_minutes:5,min_delay_seconds:5,pause_every:10,pause_minutes:2};
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.equal(robotElements.igcCountsAuthFallback.style.display,'block',
  'CAPTCHA must expose a functional manual-workflow fallback');
 assert.match(robotElements.igcCountsRobotStatus.textContent,/CAPTCHA/);
 assert.equal(robotElements.igcCountsResume.disabled,true,'An active CAPTCHA must not enable Resume');
 statusOverride=null;
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.equal(robotElements.igcCountsAuthFallback.style.display,'none',
  'Manual auth warning must clear when ordinary robot status returns');
 assert.equal(robotElements.igcCountsRobotProgress.value,100,'Robot completion percentage must be visible');
 await bridgeCtx.window.igcCountsRobotSaveConfig();
 assert(requests.some(r=>r.url.endsWith('/config')),'Saved pacing must reach active controller');
 await bridgeCtx.window.igcCountsRobotStop();
 assert(requests.some(r=>r.url.endsWith('/stop')),'Pause must call bridge');
 await bridgeCtx.window.igcCountsRobotContinue();
 assert(requests.some(r=>r.url.endsWith('/continue')),'Resume must call bridge');
 await bridgeCtx.window.igcCountsRobotLoad();
 const restore=requests.find(r=>r.url.endsWith('/load'));
 assert(restore,'UI must recover saved rows without launching browser');
 assert.equal(JSON.parse(restore.options.body).account,'ig_A');
 const dataKey=Array.from(bridgeStore.keys()).find(k=>k.startsWith('igc_profile_counts_v1__'));
 assert(dataKey,'Profile counts must be saved independent of pacing preferences');
 const bridgeSaved=JSON.parse(bridgeStore.get(dataKey));
 assert.equal(bridgeSaved.records['public.user'].followers,'3456');
 const followingKey=Array.from(bridgeStore.keys()).find(k=>k.startsWith('igc_profile_discovered_v1__'));
 assert.equal(followingKey,undefined,'Imported snapshots must not be mislabeled as a fresh browser discovery');
 assert.equal(bridgeSaved.records.outside,undefined,'Bridge must not import outside current Following');
 bridgeIdentity.active='ig_B';
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.equal(Array.from(bridgeStore.keys()).filter(k=>k.startsWith('igc_profile_counts_v1__')).length,1,
  'Polling another active Instagram must not save foreign profile-count results');
 assert.match(robotElements.igcCountsRobotStatus.textContent,/another Instagram/);
 console.log('Profile Counts local bridge Start/Poll, token and account isolation: PASS');
 console.log('Profile Counts UI source parsing, CSV, and owner/profile isolation: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
