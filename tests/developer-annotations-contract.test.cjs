'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-developer-edition">([\s\S]*?)<\/script>/);
assert(match,'Developer Edition inline script missing');
assert(html.includes('igcDevAccount'),'Normal account access missing');
assert(html.includes('igcDevPick'),'Select-section interaction missing');
assert(html.includes('igcDevExportJson'),'Combined JSON export missing');

function harness(store=new Map(),identity={owner:'owner_1',active:'ig_00000001'}){
 const elements=new Map(),events=new Map(),downloads=[],intervals=[],files=[],copied=[];
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
  'igcDevRealProbe','igcDevLiveTask','igcDevLiveHandle','igcDevLiveCount',
  'igcDevLiveStart','igcDevLiveStop','igcDevLiveResults',
  'igcDevChatMessages','igcDevChatInput','igcDevChatSend','igcDevChatCompare','igcDevChatCopy',
  'igcDevRealActionTests','igcDevActionTask','igcDevActionTargets',
  'igcDevActionFollowersEvidence','igcDevActionStart','igcDevActionPause','igcDevActionStatus',
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
   if(selector.includes('button,input'))return null;
   if(selector.includes('.panel'))return section;
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
  navigator:{clipboard:{writeText:async value=>copied.push(value)}},
  setTimeout(fn){fn()},setInterval(fn){intervals.push(fn);return 1}};
 vm.runInNewContext(match[1],context,{timeout:5000});
 return {elements,downloads,files,copied,store,context,window,events,intervals,selectTarget,storage};
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
 e.get('igcDevChatInput').value='Audit local robot errors and prepare a report';
 await e.get('igcDevChatSend').listeners.click();
 const chatEntries=[...store.entries()].filter(([key])=>key.includes('__diagnostic_chat_v1'));
 assert.equal(chatEntries.length,1,'Scoped diagnostic instructions must be saved locally');
 const messages=JSON.parse(chatEntries[0][1]);
 assert(messages.some(x=>x.role==='owner'&&x.text.includes('Audit local robot errors')));
 assert(messages.some(x=>x.role==='local_assistant'&&x.text.includes('audit completed')));
 await e.get('igcDevChatCopy').listeners.click();
 assert.equal(h.copied.length,1,'ChatGPT handoff copies a single local report');
 assert(h.copied[0].includes('REDACTED AUDIT PROMPT'));
 assert(h.copied[0].includes('Audit local robot errors'));
 assert(!h.copied[0].includes('012345678901234567890123456789'));
 assert.equal(h.copied[0].includes('developer_real_action_test_summary'),true);
 assert(e.get('igcDevActionStart').listeners.click,'Explicit live-action control must be wired');
 assert(e.get('igcDevActionPause').listeners.click,'Explicit live-action Pause must be wired');
 await e.get('igcDevExportJson').listeners.click();
 const report=JSON.parse(await h.files.at(-1).text());
 assert.equal(report.owner_section_annotations[0].comment,entries[0].comment);
 assert.equal(report.audit.findings[0].code,'RETRYABLE_ZERO_CLICK');
 // Edit is intentionally supported without losing the original target.
 const editCard=e.get('igcDevNotes').children[0];
 await editCard.children[3].children[0].listeners.click();
 assert.equal(e.get('igcDevNoteInput').value,entries[0].comment);
 e.get('igcDevNoteInput').value='Batch changed to 40 after selecting a different tab.';
 e.get('igcDevSaveNote').listeners.click();
 entries=JSON.parse(store.get('igc_dev_section_notes_v1__owner_1__ig_00000001'));
 assert.equal(entries.length,1);
 assert.equal(entries[0].anchor.section,'igcAutoBatchApproval');
 assert.equal(entries[0].comment,'Batch changed to 40 after selecting a different tab.');
 const newSession=harness(store,identity);
 assert.match(newSession.elements.get('igcDevNotesCount').textContent,/1 saved section note/,
  'Developer notes must persist through app restart');
 identity.active='ig_00000002';
 h.intervals.at(-1)();
 assert.match(e.get('igcDevNotesCount').textContent,/0 saved section notes/,
  'Notes must not leak between Instagram workspaces');
 identity.active='ig_00000001';h.intervals.at(-1)();
 assert.match(e.get('igcDevNotesCount').textContent,/1 saved section note/);
 const deleteCard=e.get('igcDevNotes').children[0];
 await deleteCard.children[3].children[2].listeners.click();
 assert.equal(JSON.parse(store.get('igc_dev_section_notes_v1__owner_1__ig_00000001')).length,0,
  'Deleting one note must remove only the selected workspace record');
 const jstart=html.indexOf("function igcDeveloperReadOnly(){");
 const jend=html.indexOf("async function sendOtp(){",jstart);
 assert(jstart>0&&jend>jstart,'Original real cloud login flow missing');
 const outgoing=[];
 const cloudContext={window:{location:{hash:'#igc-robot=30000.012345678901234567890123456789&igc-developer=1'}},
  SUPABASE_URL:'https://unit.test',headers:()=>({}),
  fetch:async(url,options)=>{outgoing.push({url,options});return {ok:true,text:async()=>'{"access_token":"test"}'}}};
 const jfetch=vm.runInNewContext(html.slice(jstart,jend)+'\njfetch',cloudContext);
 await jfetch('/auth/v1/token?grant_type=password',{method:'POST'});
 assert.equal(outgoing.length,1,'Real account sign-in must remain available');
 await assert.rejects(()=>jfetch('/rest/v1/profile_state',{method:'POST',body:'{}'}),
  /production cloud writes are disabled/);
 await assert.rejects(()=>jfetch('/rest/v1/devices',{method:'DELETE'}),
  /production cloud writes are disabled/);
 await assert.rejects(()=>jfetch('/auth/v1/user',{method:'PUT'}),
  /production cloud writes are disabled/);
 assert.equal(outgoing.length,1,'Blocked Developer mutations must not reach cloud');
 const verifyStart=html.indexOf('async function verifyOtpAndSetPassword(){');
 const verifyEnd=html.indexOf('const AUTH_RECOVERY_MESSAGE=',verifyStart);
 assert(verifyStart>0&&verifyEnd>verifyStart,'Real OTP verifier function is missing');
 const otpSource=html.slice(verifyStart,verifyEnd);
 let otpVerified=0,otpWrites=0;
 const otpContext={verifyOtp:async()=>{otpVerified++},
   igcDeveloperReadOnly:()=>true,
   document:{getElementById:()=>({value:'password-123'})},
   jfetch:async()=>{otpWrites++}};
 const devOtp=vm.runInNewContext(otpSource+';verifyOtpAndSetPassword',otpContext);
 await devOtp();
 assert.equal(otpVerified,1,'Developer must still authenticate real OTP');
 assert.equal(otpWrites,0,'Developer must not update the production Auth password');
 const publicContext={...otpContext,igcDeveloperReadOnly:()=>false};
 const regularOtp=vm.runInNewContext(otpSource+';verifyOtpAndSetPassword',publicContext);
 await regularOtp();
 assert.equal(otpWrites,1,'The public sign-up flow must preserve normal password setup');
 // Selection must preserve a precise structural target when its control lacks an ID.
 const section=e.get('igcAutoBatchApproval');
 const idlessButton={id:'',tagName:'BUTTON',parentElement:section,previousElementSibling:null,
   closest(selector){
    if(selector.includes('button,input'))return this;
    if(selector.includes('.panel'))return section;
    if(selector.includes('.page'))return e.get('page-automations');
    return null;
   }};
 e.get('igcDevPick').listeners.click();
 h.events.get('click')({target:idlessButton,preventDefault(){},stopPropagation(){},stopImmediatePropagation(){}});
 e.get('igcDevNoteInput').value='Control without ID has incorrect spacing.';
 e.get('igcDevSaveNote').listeners.click();
 const structural=JSON.parse(store.get('igc_dev_section_notes_v1__owner_1__ig_00000001'))[0];
 assert.equal(structural.anchor.locator,'#igcAutoBatchApproval > button:nth-of-type(1)');
 assert.equal(structural.anchor.locator_kind,'structural');
 console.log('Developer Edition login, section selection (IDs and id-less targets), persisted notes, export and read-only cloud gate: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
