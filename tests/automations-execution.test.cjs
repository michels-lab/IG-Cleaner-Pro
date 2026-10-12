'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const script=source.match(/<script id="igc-automations-plan">([\s\S]*?)<\/script>/);
assert(script,'Action script not found');
const store=new Map(),calls=[],texts=[];
const elements={};
for(const id of ['igcAutoRows','igcAutoMetrics','igcAutoExecutionMetrics'])elements[id]={
 children:[],replaceChildren(){this.children=[]},appendChild(node){this.children.push(node)}
};
for(const id of ['igcAutoStatus','igcAutoLiveStatus'])elements[id]={textContent:''};
for(const [id,value] of Object.entries({igcAutoSearch:'',igcAutoBatch:'2',igcAutoRest:'5',igcAutoGap:'5'}))elements[id]={value};
elements.igcAutoProgress={value:0};elements.igcAutoPause={disabled:false};elements.igcAutoResume={disabled:false};
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
 return {ok:true,json:async()=>type==='status'?p:{...p,message:'fixture action started'}};
};
const localStorage={getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)};
const ctx={document,localStorage,
 window:{IGC_INSTAGRAM_PROFILES:context,location:{hash:'#igc-robot=33333.0123456789abcdefghijabcdefgh'},
 showPage:()=>{},confirm:message=>(texts.push(message),true)},
 followingRaw:[{username:'skip.me'},{username:'keep.me'},{username:'mutual.person'}],
 followersRaw:[{username:'mutual.person'}],followersMap:new Map([['mutual.person',{}]]),
 pendingRequestsRaw:[{username:'request.one'}],protectedSet:new Set(),
 saveSet(){},LS_PROT:'protected',Set,Map,JSON,Math,Date,Number,String,encodeURIComponent,
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
 assert(texts[0].includes('DEJAR DE SEGUIR'));
 ctx.window.igcAutoChoose('cancel');
 await ctx.window.igcAutoStart();
 const requests=calls.filter(c=>c.type==='start');assert.equal(requests.length,2);
 assert.equal(requests[1].data.task,'cancel');
 assert.deepEqual(requests[1].data.targets,['request.one']);
 ctx.window.V119_HTML={partial:true};
 ctx.window.igcAutoChoose('unfollow');
 await ctx.window.igcAutoStart();
 assert.equal(calls.filter(c=>c.type==='start').length,2,'Partial HTML must reject an unfollow');
 ctx.window.V119_HTML={partial:false};
 await ctx.window.igcAutoPause();
 assert(calls.some(c=>c.type==='pause'),'Pause control must call local robot');
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
 assert.match(elements.igcAutoLiveStatus.textContent,/otra cuenta/,
  "Cross-owner status must be explained without exposing another account's queue");
 p.running=true;p.status='running';
 await ctx.window.igcAutoPoll();
 assert.equal(ctx.window.igcAutoSwitchGuard(),false,
  'Active job for a different account still blocks identity change');
 console.log('Automations action execution, owner switching guard, pause and partial HTML gate: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});