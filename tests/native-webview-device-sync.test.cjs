'use strict';
// Test the actual shared WebView sync device identity resolver and Native bridge.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const java=fs.readFileSync(path.join(root,'android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java'),'utf8');
const start=html.indexOf('function currentDevice(){'),end=html.indexOf('function eventToDb(e){',start);
assert(start>=0&&end>start,'Expected the production device resolver');
const source=html.slice(start,end);
function device(local,bridge){
  const ctx={JSON,String,window:{AndroidBridge:bridge},
    localStorage:{getItem:()=>JSON.stringify(local)}};
  vm.createContext(ctx);
  vm.runInContext(source,ctx);
  return ctx.currentDevice();
}
assert.equal(device({id:'desktop_stale',type:'desktop'},null).type,'desktop');
const native=device({id:'desktop_stale',type:'desktop'},{
  getInstagramOwnerEmail:()=> 'fixture@example.test',
  getDeviceId:()=> 'android_native_unique'
});
assert.equal(native.type,'android');
assert.equal(native.id,'android_native_unique');
assert.equal(device({},{
  getInstagramOwnerEmail:()=> 'fixture@example.test',
  getDeviceId:()=> 'android_native_unique'
}).id,'android_native_unique');
assert(java.includes('public String getDeviceId()'),'Native bridge must expose stable deviceId');
assert(java.includes('.put("type", "android")'),'Android bootstrap must label its own identity');
assert(html.includes("if(d.type!=='desktop'&&!importedAt)continue;"),
 'Android caches must not be uploaded; explicit imports alone may sync');
console.log('PASS: Android native bridge device identity and guarded WebView list synchronization');
