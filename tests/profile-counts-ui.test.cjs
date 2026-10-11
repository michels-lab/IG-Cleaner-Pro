'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=source.match(/<script id="igc-profile-counts-ui">([\s\S]*?)<\/script>/);
assert(match,'Profile Counts script missing from canonical Desktop source');
new vm.Script(match[1],{filename:'igc-profile-counts-ui.js'});
assert(source.includes('id="igcProfileCountsPanel"'),'Insights must expose Profile Counts');
assert(source.includes('id="igcCountsImport"'),'Import control missing');

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
 },document:{
  readyState:'loading',addEventListener(){},
  getElementById:id=>elements[id]||null,
  createElement:()=>({textContent:'',style:{},click(){clicked++},remove(){}}),
  body:{appendChild(){}}
 },followingRaw:[{username:'public.user'},{username:'second.user'}],
  URL:{createObjectURL:()=> 'blob:fixture',revokeObjectURL(){}},
  Blob:class {constructor(){}},setTimeout(){},Date,Number,Array,Set,Map,JSON,Math,
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
 assert.match(elements.igcCountsRows.innerHTML,/1\.234/);
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
 console.log('Profile Counts UI source parsing, CSV, and owner/profile isolation: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
