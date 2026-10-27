'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-v12030-supabase-sync-js">([\s\S]*?)<\/script>/);
assert(match,'Production auth script must exist');
const injected=match[1].replace(/\n\}\)\(\);\s*$/,
 '\nwindow.__switchTest={S,activateRemembered,addAnotherLogin,readRemembered,saveRemembered,forgetRemembered,desktopLoginStore};\n})();');
assert.notEqual(injected,match[1]);
const SES='igc_v12027_supabase_session',WALLET='igc_v120_login_accounts_v1';
const now=Math.floor(Date.now()/1000);
const account=(email,part)=>({access_token:'access-'+part,refresh_token:'refresh-'+part,
 expires_at:now+3600,user:{id:'owner-'+part,email}});
function harness(){
 const entries=new Map([[SES,JSON.stringify(account('first@example.test','first'))],
  ['ig_v13_done','["original-review-must-remain"]']]);
 const storage={getItem:k=>entries.get(k)||null,setItem:(k,v)=>entries.set(k,String(v)),removeItem:k=>entries.delete(k)};
 const refs=new Map(['igcSyncSignedOut','igcSyncSignedIn','igcSyncAccount'].map(id=>[id,{style:{},textContent:''}]));
 const created=[],events=[],reloads=[];
 function makeNode(tag){const node={tag,children:[],style:{},textContent:'',disabled:false,
  appendChild(child){this.children.push(child);return child},
  remove(){this.removed=true},close(){this.closed=true},
  showModal(){this.opened=true},addEventListener(name,cb){this[name]=cb}};created.push(node);return node}
 const document={getElementById:id=>refs.get(id)||null,createElement:makeNode,
  body:{appendChild(node){refs.set(node.id,node);return node}},addEventListener(){},hidden:false};
 const window={IGC_INSTAGRAM_PROFILES:{scopeRest:(path,opt)=>({path,opt}),setCloudStatus(){},active:'legacy',accounts:[]},
   location:{reload:()=>reloads.push(true)},addEventListener(){}};
 const ctx={window,location:window.location,localStorage:storage,igcRawProfileStorage:storage,document,
  setTimeout(){},clearTimeout(){},setInterval(){},clearInterval(){},
  fetch:async()=>{throw Error('Switch of unexpired sessions must not need network')},
  console:{warn(){}},Date,JSON,Math,Error,Number,String,Array,Map,Set};
 vm.createContext(ctx);vm.runInContext(injected,ctx,{timeout:5000});
 return {test:window.__switchTest,window,entries,created,refs,reloads,events};
}
(async()=>{
 const x=harness();
 const other=account('second@example.test','second');
 x.test.saveRemembered(x.test.S.session);
 x.test.saveRemembered(other);
 const saved=x.test.readRemembered();
 assert.deepEqual(Object.keys(saved).sort(),['first@example.test','second@example.test']);
 assert(!JSON.stringify(saved).includes('password'), 'Never persist passwords');
 x.window.igcSyncSwitchAccount();
 const dialog=x.created.find(y=>y.tag==='dialog');
 assert(dialog&&dialog.opened,'Switch account should open a true chooser, not logout');
 const list=dialog.children.find(y=>y.tag==='div');
 assert(list&&list.children.length===3,'Both logins plus Add another account visible');
 assert(list.children[0].disabled,'Current account must not be selectable');
 const target=list.children.find(y=>y.textContent.includes('second@example.test'));
 target.click();
 await Promise.resolve();await Promise.resolve();
 assert.equal(x.test.S.session.user.email,'second@example.test');
 assert.equal(JSON.parse(x.entries.get(SES)).user.email,'second@example.test');
 assert.equal(x.reloads.length,1,'Switch must reload the owner namespace');
 assert.equal(x.entries.get('ig_v13_done'),'["original-review-must-remain"]');
 assert.equal(Object.keys(x.test.readRemembered()).length,2,'Old login must stay remembered');
 x.test.addAnotherLogin();
 assert.equal(x.test.S.session,null);
 assert.equal(x.reloads.length,2);
 assert.equal(Object.keys(x.test.readRemembered()).length,2,'Add account must not sign out all');
 // Returning to a remembered account must work without password.
 await x.test.activateRemembered('first@example.test');
 assert.equal(x.test.S.session.user.email,'first@example.test');
 assert.equal(x.reloads.length,3);
 x.window.igcSyncDisconnect();
 assert.equal(x.test.S.session,null);
 const remaining=x.test.readRemembered();
 assert(!remaining['first@example.test'],'Sign out must forget only active login');
 assert(remaining['second@example.test'],'Another login should stay remembered');
 assert.equal(x.entries.get('ig_v13_done'),'["original-review-must-remain"]');
 // A malicious wallet entry with the wrong authenticated email must not switch owners.
 x.test.saveRemembered(account('second@example.test','second'));
 const data=x.test.readRemembered();
 data['third@example.test']=account('attacker@example.test','attacker');
 x.entries.set(WALLET,JSON.stringify(data));
 await x.test.activateRemembered('third@example.test');
 assert.equal(x.test.S.session,null);
 assert.equal(x.reloads.length,4,'Failed switch must not reload');
 // A background cloud sync must allow inspection, but cannot commit an
 // owner change. The same chooser stays open after an unsafe selection, and
 // never replays it once the state later becomes safe.
 const busy=harness();
 busy.test.saveRemembered(account('second@example.test','second'));
 busy.test.S.busy=true;
 assert.equal(busy.window.igcSyncSwitchState().code,'sync_busy');
 busy.window.igcSyncSwitchAccount();
 const pending=busy.created.find(node=>node.tag==='dialog');
 assert(pending&&pending.opened,'Read-only chooser stays accessible during active sync');
 const pendingList=pending.children.find(node=>node.tag==='div');
 const candidate=pendingList.children.find(node=>node.textContent.includes('second@example.test'));
 candidate.click();
 assert(!pending.closed,'Blocked busy selection must not close chooser');
 assert.equal(busy.test.S.session.user.email,'first@example.test');
 assert.equal(busy.reloads.length,0,'No delayed automatic account switch during busy state');
 assert.equal(busy.entries.get('ig_v13_done'),'["original-review-must-remain"]');
 busy.test.S.busy=false;
 busy.window.igcAutoSwitchGuard=()=>false;
 assert.equal(busy.window.igcSyncSwitchState().code,'automation_active');
 candidate.click();
 assert(!pending.closed,'Robot switch veto must keep read-only chooser');
 assert.equal(busy.reloads.length,0,'Active robot cannot switch auth account');
 busy.window.igcAutoSwitchGuard=()=>true;
 assert.equal(busy.window.igcSyncSwitchState().code,'ready');
 candidate.click();
 await Promise.resolve();await Promise.resolve();
 assert.equal(busy.test.S.session.user.email,'second@example.test');
 assert.equal(busy.reloads.length,1,'Only the new manually approved click may switch owner');
 assert.equal(busy.entries.get('ig_v13_done'),'["original-review-must-remain"]');
 console.log('PASS: busy/robot vetoes preserve read-only chooser and cannot silently rebind owner');
 console.log('PASS: Desktop chooser, two remembered logins, owner reload, add, sign out and mismatch isolation');
})().catch(e=>{console.error(e);process.exitCode=1});
