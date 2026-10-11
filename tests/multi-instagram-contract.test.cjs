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
 removeItem:k=>backing.delete(String(k))
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
console.log('Multi-Instagram local storage, audit DB, REST write isolation and registry contracts passed.');
