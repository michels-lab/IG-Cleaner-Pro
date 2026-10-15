'use strict';
/* Test the real embedded Windows Updater UI in a VM, without downloading or touching Instagram. */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-windows-updater-ui">([\s\S]*?)<\/script>/);
assert(match,'Windows native update controller script must be embedded in the canonical Desktop HTML');
new vm.Script(match[1],{filename:'igc-windows-updater-ui.js'});
assert(html.includes('id="igcWindowsUpdatesButton"'),'Native Windows Updates must be accessible from the fixed header');
assert(html.includes('id="aboutDeveloperBtn"'),'Existing persistent About must remain independently visible');
assert(html.includes('id="igcWindowsUpdatesDialog"'),'Updates dialog must be user-operated');
assert(html.includes('Check for updates')&&html.includes('Download verified Setup')&&html.includes('Run Setup'),'Explicit update flow missing');
const ids=['igcWindowsUpdatesButton','igcWindowsUpdatesOverlay','igcWindowsUpdatesHeading',
 'igcWindowsUpdatesVersions','igcWindowsUpdatesStatus','igcWindowsUpdatesProgress','igcWindowsUpdatesNotes',
 'igcWindowsUpdatesRelease','igcWindowsUpdatesCheck','igcWindowsUpdatesDownload',
 'igcWindowsUpdatesCancel','igcWindowsUpdatesInstall','igcWindowsUpdatesClose'];
const build=()=>{
 const handlers={};
 const elements=Object.fromEntries(ids.map(id=>[id,{
   style:{},textContent:'',href:'',disabled:false,value:0,
   handlers:{},addEventListener(event,fn){this.handlers[event]=fn},
   focus(){this.focused=true},
   setAttribute(k,v){this[k]=v},
   classList:{add(k){this.open=true},remove(k){this.open=false}}
 }]));
 const calls=[];
 let current={status:'idle',message:'Not checked',current:'120.47',latest:null,progress:0};
 const ctx={
   document:{getElementById:id=>elements[id],hidden:false},
   window:{confirm:()=>false},
   location:{hash:'#igc-robot=32111.abcdefghijklmnopqrstuvwx'},
   fetch:async(url,opts)=>{
    calls.push({url,opts});
    assert.match(url,/^http:\/\/127\.0\.0\.1:32111\/api\/update\//);
    assert.equal(opts.headers['X-IGC-Bridge-Token'],'abcdefghijklmnopqrstuvwx');
    if(url.endsWith('/check'))current={...current,status:'checking',message:'Checking'};
    if(url.endsWith('/download'))current={...current,status:'downloading',message:'Downloading'};
    if(url.endsWith('/cancel'))current={...current,status:'postponed',message:'Postponed'};
    if(url.endsWith('/install'))current={...current,status:'installer_started',message:'Installer launched'};
    return {ok:true,json:async()=>current};
   },
   setInterval(){},Math,Number,String,Error
 };
 vm.createContext(ctx);vm.runInContext(match[1],ctx);
 return {ctx,calls,elements,setCurrent:v=>{current=v}};
};
(async()=>{
 const normal=build();
 assert.equal(normal.elements.igcWindowsUpdatesButton.style.display,'inline-flex',
   'Native Windows app must expose Updates in fixed header');
 normal.elements.igcWindowsUpdatesButton.handlers.click();
 await Promise.resolve();
 assert.equal(normal.elements.igcWindowsUpdatesOverlay['aria-hidden'],'false');
 assert(normal.calls.some(x=>x.url.endsWith('/status')));
 normal.elements.igcWindowsUpdatesCheck.handlers.click();
 await Promise.resolve();
 assert(normal.calls.some(x=>x.url.endsWith('/check')&&x.opts.method==='POST'));
 normal.setCurrent({status:'update_available',current:'120.47',latest:'v120.48',progress:0,
  message:'A verified Setup exists',notes:'<script>alert(1)</script>',
  release_url:'https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.48'});
 normal.elements.igcWindowsUpdatesButton.handlers.click();
 await Promise.resolve();
 assert.equal(normal.elements.igcWindowsUpdatesNotes.textContent,'<script>alert(1)</script>',
   'Untrusted release notes must be text, never injected as HTML');
 assert.equal(normal.elements.igcWindowsUpdatesButton.textContent,'↻ Updates available');
 assert.equal(normal.elements.igcWindowsUpdatesDownload.disabled,false);
 normal.elements.igcWindowsUpdatesDownload.handlers.click();
 await Promise.resolve();
 assert(normal.calls.some(x=>x.url.endsWith('/download')&&x.opts.method==='POST'));
 normal.setCurrent({status:'ready_to_install',current:'120.47',latest:'v120.48',progress:100,
  message:'Verified installer'});
 normal.elements.igcWindowsUpdatesButton.handlers.click();
 await Promise.resolve();
 const before=normal.calls.filter(x=>x.url.endsWith('/install')).length;
 normal.elements.igcWindowsUpdatesInstall.handlers.click();
 await Promise.resolve();
 assert.equal(normal.calls.filter(x=>x.url.endsWith('/install')).length,before,
   'Owner declining Setup cannot trigger install');
 normal.ctx.window.confirm=()=>true;
 normal.elements.igcWindowsUpdatesInstall.handlers.click();
 await Promise.resolve();
 const installs=normal.calls.filter(x=>x.url.endsWith('/install'));
 assert.equal(installs.length,1,'Confirmed Setup launch must call local protected endpoint once');
 assert.equal(JSON.parse(installs[0].opts.body).confirm,'run_installer');
 normal.elements.igcWindowsUpdatesClose.handlers.click();
 assert.equal(normal.elements.igcWindowsUpdatesOverlay['aria-hidden'],'true');
 const ctx={location:{hash:''},document:{getElementById:id=>{throw Error('Standalone HTML must not access native update UI: '+id)}}};
 vm.createContext(ctx);vm.runInContext(match[1],ctx);
 console.log('PASS: Windows-only header, check, opt-in download, owner-confirmed install, safe notes and standalone isolation');
})().catch(e=>{console.error(e);process.exitCode=1});