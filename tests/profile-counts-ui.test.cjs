'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=source.match(/<script id="igc-profile-counts-ui">([\s\S]*?)<\/script>/);
assert(match,'Profile Counts script missing from canonical Desktop source');
new vm.Script(match[1],{filename:'igc-profile-counts-ui.js'});
assert(source.includes('id="igcProfileCountsPanel"'),'Insights must expose Profile Counts');
assert(source.includes('id="igcCountsImport"'),'Import control missing');
assert(source.includes('id="igcCountsRobotActions"'),'Direct browser robot controls missing');

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
 assert(summary.some(s=>s.includes('2 perfiles')),'Render should read Following from active workspace');
 assert.match(elements.igcCountsRows.innerHTML,/public\.user/);
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
 assert(summary.some(s=>s.includes('1 con datos')));
 const onlyKey=Array.from(store.keys())[0];
 assert(onlyKey.includes('owner_A')&&onlyKey.includes('ig_A'));
 const saved=JSON.parse(store.get(onlyKey));
 assert.equal(saved.records['public.user'].followers,'1234');
 assert.equal(saved.records['unrelated'],undefined,'Do not import profiles outside active Following');
 identity.active='ig_B';
 ctx.window.igcCountsRender();
 assert(summary.some(s=>s.includes('0 con datos')),'Sibling Instagram must not inherit counts');
 identity.active='ig_A';identity.owner='owner_B';
 ctx.window.igcCountsRender();
 assert(summary.some(s=>s.includes('0 con datos')),'Different app login must not inherit counts');

 // Simulate the actual local control protocol, including account-scoped sync.
 const bridgeStore=new Map(),requests=[];
 const robotElements={
  igcCountsRows:{innerHTML:''},
  igcCountsSummary:{replaceChildren(){},appendChild(){}},
  igcCountsFootnote:{textContent:'',style:{}},
  igcCountsQuery:{value:''},igcCountsFilter:{value:'all'},
  igcCountsRobotStatus:{textContent:'',style:{}},
  igcCountsRobotProgress:{value:0},
  igcCountsRobotActions:{style:{display:'none'}},
  igcCountsRobotRate:{value:'50'}
 };
 const bridgeIdentity={owner:'owner_A',active:'ig_A'};
 const mockFetch=async(url,options)=>{
  requests.push({url,options});
  assert.match(url,/^http:\/\/127\.0\.0\.1:32111\/api\//);
  assert.equal(options.headers['X-IGC-Bridge-Token'],'0123456789abcdefghijklmnop');
  const action=url.split('/').pop();
  let value={};
  if(action==='start'){
   value={status:'starting',message:'Starting',total:1,progress:0};
  } else if(action==='load'){
   value={status:'idle',message:'Saved rows loaded',owner:'owner_A',account:'ig_A',total:1,progress:1};
  } else if(action==='status'){
   value={status:'complete',message:'Done',owner:'owner_A',account:'ig_A',total:1,progress:1,per_hour:50};
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
 assert.equal(robotElements.igcCountsRobotActions.style.display,'flex');
 await bridgeCtx.window.igcCountsRobotStart();
 const start=requests.find(r=>r.url.endsWith('/start'));
 assert(start,'Direct Start must submit a localhost POST');
 assert.equal(start.options.method,'POST');
 const startBody=JSON.parse(start.options.body);
 assert.equal(startBody.owner,'owner_A');assert.equal(startBody.account,'ig_A');
 assert.deepEqual(Array.from(startBody.usernames),['public.user']);
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.equal(robotElements.igcCountsRobotProgress.value,100,'Robot completion percentage must be visible');
 await bridgeCtx.window.igcCountsRobotLoad();
 const restore=requests.find(r=>r.url.endsWith('/load'));
 assert(restore,'UI must recover saved rows without launching browser');
 assert.equal(JSON.parse(restore.options.body).account,'ig_A');
 const bridgeSaved=JSON.parse(bridgeStore.get(Array.from(bridgeStore.keys())[0]));
 assert.equal(bridgeSaved.records['public.user'].followers,'3456');
 assert.equal(bridgeSaved.records.outside,undefined,'Bridge must not import outside current Following');
 bridgeIdentity.active='ig_B';
 await bridgeCtx.window.igcCountsRobotPoll();
 assert.equal(bridgeStore.size,1,'Polling another active Instagram must not save foreign results');
 assert.match(robotElements.igcCountsRobotStatus.textContent,/otro Instagram/);
 console.log('Profile Counts local bridge Start/Poll, token and account isolation: PASS');
 console.log('Profile Counts UI source parsing, CSV, and owner/profile isolation: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
