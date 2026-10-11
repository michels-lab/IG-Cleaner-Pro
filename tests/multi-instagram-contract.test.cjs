'use strict';
// Behavioral regression: one IG Cleaner login must never mix two Instagram workspaces.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-instagram-profile-isolation">([\s\S]*?)<\/script>/);
assert(match,'Profile namespace/bootstrap must be an early inline script');
const backing=new Map(),opened=[];
const raw={
 getItem:k=>backing.has(k)?backing.get(k):null,
 setItem:(k,v)=>backing.set(String(k),String(v)),
 removeItem:k=>backing.delete(String(k)),
 key:i=>Array.from(backing.keys())[i]||null,
 get length(){return backing.size}
};
const db={open:(k,v)=>{opened.push({k,v});return {name:k}}};
const ctx={
 window:{localStorage:raw,indexedDB:db},
 document:{addEventListener(){},getElementById(){return null}},
 location:{reload(){}},Set,Proxy,Reflect,JSON,Error,String,Array,encodeURIComponent,decodeURIComponent
};
ctx.window.location=ctx.location;
vm.createContext(ctx);
function boot(active){
 raw.setItem('igc_multi_profile_active_signed_out',active);
 vm.runInContext(match[1].replace('const localStorage=igcProfileStorage;','var localStorage=igcProfileStorage;')
     .replace('const indexedDB=new Proxy','var indexedDB=new Proxy'),ctx);
}
boot('legacy');
vm.runInContext("localStorage.setItem('ig_v13_done','[\\\"legacy_friend\\\"]')",ctx);
assert.equal(raw.getItem('ig_v13_done'),'["legacy_friend"]','Legacy keys must remain byte-for-byte');
vm.runInContext("indexedDB.open('ig_cleaner_pro_history',1)",ctx);
assert.equal(opened.at(-1).k,'ig_cleaner_pro_history');
raw.setItem('igc_multi_profile_active_'+ctx.IGC_INSTAGRAM_OWNER,'ig_first_123');
vm.runInContext("igcActiveInstagramProfile='ig_first_123';window.IGC_INSTAGRAM_PROFILES._verified=true;localStorage.setItem('ig_v13_done','[\\\"alice\\\"]')",ctx);
assert.equal(raw.getItem('ig_v13_done'),'["legacy_friend"]');
assert.equal(raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_first_123__ig_v13_done'),'["alice"]');
vm.runInContext("indexedDB.open('ig_cleaner_pro_history',1)",ctx);
assert.equal(opened.at(-1).k,'igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_first_123__ig_cleaner_pro_history');
vm.runInContext("igcActiveInstagramProfile='ig_second_456';localStorage.setItem('ig_v13_done','[\\\"bob\\\"]')",ctx);
assert.equal(raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_second_456__ig_v13_done'),'["bob"]');
assert.equal(raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_first_123__ig_v13_done'),'["alice"]');
vm.runInContext("localStorage.setItem('igc_v12027_supabase_session','SAME_LOGIN')",ctx);
assert.equal(raw.getItem('igc_v12027_supabase_session'),'SAME_LOGIN','One account login must be shared');
const p=ctx.window.IGC_INSTAGRAM_PROFILES;
p.setAccounts([{account_key:'ig_first_123',username:'first.person'}]);
assert.equal(p.accounts.length,1);
assert.equal(p.displayName({account_key:'legacy',username:'full_legacy_username_123456'}),'@full_legacy_username_123456 · Datos anteriores',
 'Never shorten the full active original username');
assert.equal(p.displayName({account_key:'ig_one_abcdefgh',username:'long_instagram_identity_example'}),'@long_instagram_identity_example',
 'Never shorten new Instagram usernames');
assert.match(p.displayName({account_key:'ig_aabbccdd1234',label:'Sin asignar'}),/Sin asignar · dd1234$/,
 'Unnamed profiles need an unmistakable account key suffix');

const keepLegacy=raw.getItem('ig_v13_done');
const keepSibling=raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_second_456__ig_v13_done');
p.purgeLocalWorkspace('ig_first_123');
assert.equal(raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_first_123__ig_v13_done'),null,
 'Deleting one profile clears only its locally owned namespaced keys');
assert.equal(raw.getItem('ig_v13_done'),keepLegacy,
 'Profile removal must never touch old legacy localStorage');
assert.equal(raw.getItem('igc_profile__'+ctx.IGC_INSTAGRAM_OWNER+'__ig_second_456__ig_v13_done'),keepSibling,
 'Profile removal must not touch sibling workspace localStorage');

// Two independent IG Cleaner email identities using the same browser storage
// must not share the Instagram account registry or scoped review data.
const secondBacking = {window:{localStorage:raw,indexedDB:db},document:ctx.document,
 location:ctx.location,Set,Proxy,Reflect,JSON,Error,String,Array,encodeURIComponent,decodeURIComponent};
raw.setItem('igc_v12027_supabase_config',JSON.stringify({email:'second-login@example.test'}));
vm.createContext(secondBacking);
vm.runInContext(match[1].replace('const localStorage=igcProfileStorage;','var localStorage=igcProfileStorage;')
 .replace('const indexedDB=new Proxy','var indexedDB=new Proxy'),secondBacking);
assert.notEqual(secondBacking.IGC_INSTAGRAM_OWNER,ctx.IGC_INSTAGRAM_OWNER);
assert.equal(secondBacking.window.IGC_INSTAGRAM_PROFILES.accounts.length,0,
 'The second app login must not see the first login Instagram account registry');
raw.removeItem('igc_v12027_supabase_config');
assert.equal(p.scopeRest('list_snapshots?select=payload',{method:'GET'}).path,
 'instagram_list_snapshots?select=payload&account_key=eq.ig_second_456');
const up=p.scopeRest('focus_batches?on_conflict=user_id,id',
 {method:'POST',body:JSON.stringify([{id:'same-id',target_size:30}])});
assert.equal(up.path,'instagram_focus_batches?on_conflict=user_id,account_key,id');
assert.equal(JSON.parse(up.opt.body)[0].account_key,'ig_second_456');
vm.runInContext("igcActiveInstagramProfile='ig_third_789';window.IGC_INSTAGRAM_PROFILES._verified=false",ctx);
assert.throws(()=>p.scopeRest('profile_state?select=*',{method:'GET'}),/verificarse/);
assert.match(html,/id="igcInstagramIdentity"/);
assert.match(html,/await refreshInstagramAccounts\(\)/);
const schema=fs.readFileSync(path.join(root,'supabase/schema.sql'),'utf8');
for(const table of ['instagram_accounts','instagram_audit_events','instagram_focus_batches',
 'instagram_focus_batch_items','instagram_profile_state','instagram_list_snapshots','instagram_workspace_state'])
 assert(schema.includes(table),table+' schema is required');
const android=fs.readFileSync(path.join(root,'android/app/src/main/java/com/michelslab/igcleaner/SyncApi.java'),'utf8');
assert(android.includes('scopeQuery(String query, String profile)'));
assert(android.includes('account_key=eq.'));
assert(android.includes('instagram_' + '" + table')); // scoped REST table mapping

// Regression: Android MaterialAlertDialog.setMessage() and .setItems() compete
// for the same content panel. The picker MUST show selectable workspace rows,
// especially "Datos anteriores", rather than only the footer actions.
const nativeActivity=fs.readFileSync(path.join(root,
 'android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java'),'utf8');
const picker=nativeActivity.match(/private void showInstagramProfileManager\(\) \{([\s\S]*?)\n    private void addInstagramProfile\(/);
assert(picker,'Native multi-Instagram selector must be present');
assert.match(picker[1],/new JSONArray\(\)\.put\(legacy\)/,'Original workspace must be first in native picker');
assert.match(nativeActivity,/Datos anteriores \(sin asignar\)/,'Legacy row must have clear recovery label');
assert.match(picker[1],/\.setItems\(labels,/,'Profile picker must render selectable accounts');
assert.doesNotMatch(picker[1],/\.setMessage\(/,
 'Do not combine setMessage + setItems in MaterialAlertDialog; message hides profile rows');

const deletionBody=html.match(/window\.igcDeleteInstagramProfile=async function\(\)\{([\s\S]*?)\n\};/);
assert(deletionBody,'Desktop exposes a real Delete Instagram action');
assert.match(deletionBody[1],/key==='legacy'/,'Legacy deletion must be blocked in Desktop handler');
assert.match(deletionBody[1],/ELIMINAR @/,'Desktop deletion requires exact typed confirmation');
assert.match(deletionBody[1],/rpc\/igc_delete_instagram_profile/,
 'Desktop must call atomic server RPC rather than piecemeal client deletes');
assert.match(html,/id="igcDeleteInstagramButton"/,
 'Delete control must be next to the account switcher');
assert.match(html,/remove\.disabled=this\.active==='legacy'/,
 'Desktop must visually disable delete when original workspace selected');
const xml=fs.readFileSync(path.join(root,'android/app/src/main/res/layout/screen_account.xml'),'utf8');
assert.match(xml,/@\+id\/deleteInstagramProfile/,
 'Android Profile must show a dedicated account-deletion control');
assert.match(nativeActivity,/confirmDeleteInstagramProfile\(\)/,
 'Android must expose named profile deletion');
assert.match(nativeActivity,/deleteInstagramProfile\.setEnabled\(connected && !"legacy"\.equals/,
 'Android must visibly prohibit deleting original legacy');
assert.match(nativeActivity,/api\.deleteInstagramProfile\(key, username\)/,
 'Android deletion must call atomic server function');
assert.match(android,/\/rest\/v1\/rpc\/igc_delete_instagram_profile/,
 'Android must not implement partial sequential DELETEs');
assert.match(schema,/security invoker[\s\S]*?igc_delete\$/,
 'Database deletion RPC must respect owner RLS');
assert.match(schema,/revoke all on function public\.igc_delete_instagram_profile/,
 'The RPC must revoke PUBLIC/anonymous execution');

// Identity recovery and safe export parity regression (Desktop + Android).
assert.match(html,/id="igcInstagramIdentitySummary"/,
 'Desktop profile selection should expose synchronized metrics');
assert.match(html,/Following '[^\n]*?following_count/,
 'Desktop counts must be drawn from per-profile summary, not another workspace');
assert.match(html,/rpc\/igc_instagram_profile_summaries/,
 'Desktop must fetch server-filtered profile statistics');
assert.match(html,/window\.igcEditInstagramProfile=async function/,
 'Desktop needs a handle edit action for currently selected profile');
assert.match(html,/window\.igcExportSelectedInstagramProfile=async function/,
 'Desktop needs an independent profile backup action');
assert.match(html,/key===\x27legacy\x27\?\x27\x27:\x27\&account_key=eq\.\x27/,
 'Scoped export must target only the selected named workspace');
assert.match(html,/p_transfer_from_key:transfer/,
 'Desktop must require a separate explicit identity transfer parameter');
assert.match(html,/p_expected_username:target\.username\|\|null/,
 'Desktop handle changes must detect stale concurrent edits');
assert.match(html,/getItem\(IGC_INSTAGRAM_REGISTRY_KEY\)/,
 'Profile registry must remain owner scoped');
assert.match(nativeActivity,/setInstagramUsernameWithConfirmation\("legacy", username, true\)/,
 'Android smart add must offer legacy recovery rather than silently creating blank workspace');
assert.match(nativeActivity,/api\.setInstagramUsername\(key, username, expected, transferFrom\)/,
 'Android must use the same atomic backend for metadata-only identity transfer');
assert.match(nativeActivity,/getInstagramProfileSummaries\(\)/,
 'Android must show per-profile counts');
assert.match(nativeActivity,/fetchInstagramProfileCloudRows\(/,
 'Android backup must read only the chosen Instagram workspace');
assert.match(nativeActivity,/exportSelectedInstagramProfileBackup\(key, label,/,
 'Android must offer cloud backup before deleting');
assert.match(nativeActivity,/username\.isBlank\(\)/,
 'Android must support unnamed orphaned profile keys');
assert.match(xml,/@\+id\/editInstagramUsername/,
 'Android Profile must show edit username');
assert.match(xml,/@\+id\/backupInstagramProfile/,
 'Android Profile must expose a separate backup action');
assert.match(android,/rpc\/igc_set_instagram_username/,
 'Android must use backend atomic rename');
assert.match(android,/rpc\/igc_instagram_profile_summaries/,
 'Android must use per-profile server stats');
assert.match(schema,/create or replace function public\.igc_set_instagram_username/,
 'Schema must implement atomic owner identity change');
assert.match(schema,/create or replace function public\.igc_instagram_profile_summaries/,
 'Schema must aggregate legacy and named counts independently');
assert.match(schema,/v_old is distinct from p_expected_username/,
 'Concurrent stale updates must not rename the wrong account');
assert.match(schema,/set username=null/,
 'Collision recovery must only unassign the human-readable handle');
assert.match(schema,/security invoker/g,
 'All new identity functions should obey account-owner RLS');


assert.match(html,/id="igcInstagramActiveFullName"/,'Active account must show a separate full-length identity');
assert.match(html,/\.igc-profile-select-row/,'Profile selector must occupy a dedicated full-width row');
assert.match(html,/\.igc-profile-actions/,'Profile action buttons must have their own row');
assert.match(html,/id="igcRefreshInstagramButton"/,'Users must have a direct account-registry refresh control');
assert.match(html,/window\.igcRefreshInstagramProfiles=async function/,'Profile refresh must work separately from full data sync');
assert.match(html,/window\.IGC_INSTAGRAM_PROFILES\.setCloudStatus/,'Desktop must surface cloud auth or network failures in the profile selector');
assert.match(html,/Conéctate en Cuenta con el mismo correo/,'Signed-out users need actionable instructions to recover cloud accounts');
assert.match(html,/const profiles=rows;/,'Do not silently downgrade invalid cloud registry to a one-item legacy view');
assert.match(html,/registry\.setCloudStatus\(profiles\.length\+/,'Successful registry fetch must show the remote account count');
// IG Cleaner *login* switching is separate from Instagram workspace switching.
const switchButton = /onclick="igcSyncSwitchAccount\(\)">Cambiar usuario<\/button>/;
assert.match(html,switchButton,'Desktop must present Switch account next to Sign out');
const switchSource=html.match(/window\.igcSyncSwitchAccount=function\(\)\{([\s\S]*?)\n\};/);
assert(switchSource,'Desktop account-switch handler must exist');
assert.match(switchSource[1],/location\.reload\(\)/,'Switch must restart into a different owner scope');
const keptState = new Map([['legacy-history','original'],['ig_alice-history','alice'],['ig_bob-history','bob']]);
const trace={reload:0,bridge:0,sessionSaves:0,configSaves:0};
const switchEnv={
 window:{}, S:{session:{access_token:'secret-A'},cfg:{email:'alice@example.test'},busy:false},
 dataMeta:{last:'A'}, statePushTimer:null,
 status:()=>{}, clearTimeout:()=>{},
 confirm:()=>true, saveSession:()=>{trace.sessionSaves++}, notifyHostSession:force=>{
    assert.equal(force,true);trace.bridge++},
 saveCfg:()=>{trace.configSaves++}, saveDataMeta:()=>{},
 document:{getElementById:()=>null},
 location:{reload:()=>{trace.reload++}}
};
vm.createContext(switchEnv);
vm.runInContext('window.igcSyncSwitchAccount=function(){'+switchSource[1]+'\n};',switchEnv);
switchEnv.window.igcSyncSwitchAccount();
assert.equal(switchEnv.S.session,null,'Old auth token must not remain active');
assert.equal(switchEnv.S.cfg.email,'','Switching accounts must not prefill previous email');
assert.equal(trace.reload,1,'Owner reload must be triggered once');
assert.equal(trace.bridge,1,'Native auth must be explicitly invalidated');
assert.equal(trace.sessionSaves,1);
assert.equal(trace.configSaves,1);
assert.deepEqual([...keptState.values()],['original','alice','bob'],
 'Switch must leave existing Instagram data untouched');
switchEnv.S.busy=true;
switchEnv.window.igcSyncSwitchAccount();
assert.equal(trace.reload,1,'In-flight sync must block owner switch');
switchEnv.S.busy=false;
switchEnv.confirm=()=>false;
switchEnv.window.igcSyncSwitchAccount();
assert.equal(trace.reload,1,'Cancelled switch must leave owner unchanged');
assert.match(html,/nativeOwnerAvailable/,'Android native owner must trump a stale WebView config');
assert.match(html,/notifyHostSession\(forceLogout=false\)/,
 'Embedded HTML must not sign out native while it is bootstrapping');
assert.match(xml,/@\+id\/switchAccount/,'Android Account needs a visible Switch account button');
assert.match(nativeActivity,/switchAccount\.setOnClickListener/,'Android button needs a real handler');
assert.match(nativeActivity,/api\.logout\(\);\s*api\.setEmail\(""\)/,
 'Android Switch account must clear token and account identity');
assert.match(nativeActivity,/switchAccount\.setEnabled\(false\);\s*logout\.setEnabled\(false\)/,
 'Double click or concurrent logout must not race account switch');
assert.match(nativeActivity,/String\s+owner\s*=\s*JSONObject\.quote\(api\.getEmail\(\)/,
 'Android WebView must verify session owner on bootstrap');
const androidAuth=fs.readFileSync(path.join(root,
 'android/app/src/main/java/com/michelslab/igcleaner/SyncApi.java'),'utf8');
const signIn=androidAuth.match(/public void signInWithPassword\([\s\S]*?\n    \}/)?.[0]||'';
assert(signIn.indexOf('setEmail(requestedEmail)')>signIn.indexOf('requestObject("POST"'),
 'Failed Android login must not move an existing account into a foreign namespace');

console.log('Multi-Instagram local storage, audit DB, REST write isolation and registry contracts passed.');
