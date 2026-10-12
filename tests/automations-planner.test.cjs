'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const script=source.match(/<script id="igc-automations-plan">([\s\S]*?)<\/script>/);
assert(script,'Automations planning script must exist');
new vm.Script(script[1],{filename:'igc-automations-plan.js'});
assert(source.includes('id="tab-automations"'),'Automations must have a separate nav tab');
assert(source.includes('id="page-automations"'),'Automations must have its own page');
assert(!/onclick="[^"]*(?:igcAuto|automations)[^"]*"/.test(source.slice(source.indexOf('id="page-followersMutual"'),source.indexOf('id="page-followersFans"'))),
 'Mutuals must stay Focus-only, not action automation');
const store=new Map(),persistCalls=[];
const dom={};
for(const name of ['igcAutoRows','igcAutoMetrics'])dom[name]={children:[],replaceChildren(){this.children=[]},appendChild(x){this.children.push(x)}};
for(const name of ['igcAutoStatus'])dom[name]={textContent:''};
dom.igcAutoSearch={value:''};dom.igcAutoBatch={value:'30'};dom.igcAutoRest={value:'5'};dom.igcAutoGap={value:'10'};
const document={getElementById:key=>dom[key]||null,
 createElement:tag=>({tag,children:[],textContent:'',appendChild(x){this.children.push(x)},
  addEventListener(name,cb){if(name==='click')this.click=cb}})};
const protectedSet=new Set(),scope={owner:'owner_A',active:'ig_A'};
const localStorage={getItem:key=>store.get(key)||null,setItem:(key,value)=>store.set(key,value)};
const ctx={window:{IGC_INSTAGRAM_PROFILES:scope,showPage(id){return id}},
 document,localStorage,protectedSet,saveSet:(key,values)=>persistCalls.push([key,[...values]]),
 LS_PROT:'ig_v13_protected',
 followingRaw:[{username:'no.follow'},{username:'my.mutual'},{username:'no.follow2'}],
 followersRaw:[{username:'my.mutual'}],followersMap:new Map([['my.mutual',{}]]),
 pendingRequestsRaw:[{username:'request.one'}],Set,Map,JSON,Math,Number,String,Date,encodeURIComponent};
vm.createContext(ctx);vm.runInContext(script[1],ctx);
ctx.window.igcAutoRender();
assert.equal(dom.igcAutoRows.children.length,2,'Only non-mutual accounts should enter unfollow queue');
let buttons=dom.igcAutoRows.children[0].children[2].children;
buttons[1].click();
assert.match(dom.igcAutoMetrics.children[3].textContent,/Omitidos: 1/);
ctx.window.igcAutoClearSkipped();
assert.match(dom.igcAutoMetrics.children[3].textContent,/Omitidos: 0/);
buttons=dom.igcAutoRows.children[0].children[2].children;
buttons[0].click();
assert(protectedSet.has('no.follow'),'Protected favorite must be respected by existing Review/Mutuals');
assert(persistCalls.length>0,'Protect in automation queue should persist to existing protected list');
ctx.window.igcAutoChoose('protected');
assert(dom.igcAutoRows.children.some(r=>r.children[0].children[0].textContent==='@no.follow'));
const protectedRows=dom.igcAutoRows.children;
protectedRows[0].children[2].children[0].click();
assert(!protectedSet.has('no.follow'));
ctx.window.igcAutoChoose('cancel');
assert.equal(dom.igcAutoRows.children.length,1);
dom.igcAutoRows.children[0].children[2].children[0].click();
assert.equal(dom.igcAutoRows.children[0].children[1].textContent,'★ Favorito protegido');
ctx.window.igcAutoSaveTiming();
assert([...store.keys()].some(k=>k.includes('igc_action_timing_v1__owner_A__ig_A__cancel')));
scope.active='ig_B';
ctx.window.igcAutoRender();
assert.equal(dom.igcAutoRows.children[0].children[1].textContent,'Pendiente de revisión',
 'Favorites for another Instagram must not leak');
assert(!('fetch' in ctx),'Planner must not contact Instagram or mutate accounts');
console.log('Automations per-list skip/protect/pacing and scope isolation: PASS');
