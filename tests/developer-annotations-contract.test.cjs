'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-developer-edition">([\s\S]*?)<\/script>/);
assert(match,'Developer Edition inline script missing');
assert(html.includes('igcDevAccount'),'Normal account access missing');
assert(html.includes('igcDevPick'),'Select-section interaction missing');
assert(html.includes('igcDevExportJson'),'Combined JSON export missing');

function harness(store=new Map(),identity={owner:'owner_1',active:'ig_00000001'}){
 const elements=new Map(),events=new Map(),downloads=[],intervals=[],files=[];
 function node(id=''){
  const e={id,tagName:'SECTION',style:{},children:[],textContent:'',value:'',disabled:false,
   attributes:new Map(),listeners:{},contains(){return false},addEventListener(type,handler){
    this.listeners[type]=handler;
   },getAttribute(k){return this.attributes.get(k)||null},setAttribute(k,v){this.attributes.set(k,v)},
   appendChild(child){this.children.push(child)},append(...nodes){this.children.push(...nodes)},
   replaceChildren(){this.children=[]},remove(){},focus(){},scrollIntoView(){},
   getBoundingClientRect(){return {left:1,top:2,width:500,height:100}},
   click(){downloads.push({name:this.download,url:this.href})}};
  return e;
 }
 const ids=['igcDevConsole','igcDevResults','igcDevSelectionOutline','igcDevNoteInput',
  'igcDevScope','igcDevPick','igcDevClear','igcDevSelected','igcDevSaveNote',
  'igcDevCancelEdit','igcDevNotesCount','igcDevNotes','igcDevRun',
  'igcDevExport','igcDevExportJson','igcDevAccount','igcDevCollapse',
  'igcAutoBatch','igcAutoRun','igcAutoRows','igcAutoExecutionMetrics','igcAutoBatchApproval',
  'page-automations'];
 ids.forEach(id=>elements.set(id,node(id)));
 let capturedFile;
 const URL={createObjectURL(value){capturedFile=value;files.push(value);return 'blob:test-1'},
  revokeObjectURL(){}};
 const host=elements.get('igcDevConsole');
 const storage={getItem:key=>store.get(key)||null,setItem:(key,value)=>store.set(key,value)};
 const listeners={};
 const window={IGC_INSTAGRAM_PROFILES:identity,innerWidth:1200,
  addEventListener(event,handler){listeners[event]=handler},
  confirm(){return true},showPage(id){window.lastPage=id}};
 const activePage=elements.get('page-automations');
 const section=node('igcAutoBatchApproval');
 elements.set(section.id,section);
 const selectTarget={
  closest(selector){
   if(selector.includes('button[id]'))return null;
   if(selector.includes('.panel[id]'))return section;
   if(selector.includes('.page'))return activePage;
   return section;
  }
 };
 const document={title:'Instagram Cleaner Pro v120.54',body:{appendChild(){}},
  getElementById:id=>elements.get(id)||null,createElement:()=>node(),
  querySelector:query=>query==='.page.active'?activePage:null,
  querySelectorAll:query=>query==='[id]'?[...elements.values()]:[],
  addEventListener(type,handler){events.set(type,handler)}};
 const context={document,window,location:{hash:'#igc-robot=31110.012345678901234567890123456789&igc-developer=1'},
  localStorage:storage,fetch:async()=>({ok:true,json:async()=>({
   ai_prompt:'REDACTED AUDIT PROMPT',report:{generated_at:'2026-10-19',journals:1,
    profiles:3,findings:[{code:'RETRYABLE_ZERO_CLICK',count:1}],limitations:[]}})}),
  Blob,URL,Date,Math,JSON,Set,Array,Number,String,
  setTimeout(fn){fn()},setInterval(fn){intervals.push(fn);return 1}};
 vm.runInNewContext(match[1],context,{timeout:5000});
 return {elements,downloads,files,store,context,window,events,intervals,selectTarget,storage};
}
(async()=>{
 const store=new Map(),identity={owner:'owner_1',active:'ig_00000001'};
 const h=harness(store,identity),e=h.elements;
 assert.equal(e.get('igcDevConsole').style.display,'flex');
 e.get('igcDevAccount').listeners.click();
 assert.equal(h.window.lastPage,'sync','Developer login must reuse public account screen');
 e.get('igcDevPick').listeners.click();
 let prevented=false,stopped=false;
 h.events.get('click')({
  target:h.selectTarget,preventDefault(){prevented=true},stopPropagation(){stopped=true},
  stopImmediatePropagation(){}});
 assert(prevented&&stopped,'Section selection must not execute real user actions');
 assert.match(e.get('igcDevSelected').textContent,/igcAutoBatchApproval/);
 e.get('igcDevNoteInput').value='Batch size resets from 20 to 40 on Refresh.';
 e.get('igcDevSaveNote').listeners.click();
 let entries=JSON.parse(store.get('igc_dev_section_notes_v1__owner_1__ig_00000001'));
 assert.equal(entries.length,1);
 assert.equal(entries[0].anchor.section,'igcAutoBatchApproval');
 assert.equal(entries[0].anchor.screen,'page-automations');
 assert.equal(entries[0].comment,'Batch size resets from 20 to 40 on Refresh.');
 assert(entries[0].created_at&&entries[0].updated_at);
 assert.match(e.get('igcDevNotesCount').textContent,/1 saved section note/);
 await e.get('igcDevRun').listeners.click();
 await e.get('igcDevExport').listeners.click();
 const prompt=await h.files.at(-1).text();
 assert(prompt.includes('REDACTED AUDIT PROMPT'));
 assert(prompt.includes('igcAutoBatchApproval'));
 assert(prompt.includes('Batch size resets from 20 to 40 on Refresh.'));
 assert(prompt.includes('owner_observation_not_automatically_verified'));
 await e.get('igcDevExportJson').listeners.click();
 const report=JSON.parse(await h.files.at(-1).text());
 assert.equal(report.owner_section_annotations[0].comment,entries[0].comment);
 assert.equal(report.audit.findings[0].code,'RETRYABLE_ZERO_CLICK');
 const newSession=harness(store,identity);
 assert.match(newSession.elements.get('igcDevNotesCount').textContent,/1 saved section note/,
  'Developer notes must persist through app restart');
 identity.active='ig_00000002';
 h.intervals[0]();
 assert.match(e.get('igcDevNotesCount').textContent,/0 saved section notes/,
  'Notes must not leak between Instagram workspaces');
 console.log('Developer Edition login, section selection, saved annotations, export, restart, and account isolation: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
