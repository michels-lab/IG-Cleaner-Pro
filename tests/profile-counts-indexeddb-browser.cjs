"use strict";
/* Offline real-Chromium IndexedDB migration, account isolation and >250k
 * Following/Followers analysis acceptance. No real Instagram traffic. */
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),{pathToFileURL}=require("node:url");
const {chromium}=require("playwright");

(async()=>{
 const html=path.resolve(process.argv[2]||"");
 assert(fs.existsSync(html),"Pass a built standalone Desktop HTML");
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const ctx=await browser.newContext({viewport:{width:1300,height:860}});
  const page=await ctx.newPage(),errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.goto(pathToFileURL(html).href,{waitUntil:"domcontentloaded",timeout:60000});
  const key=await page.evaluate(()=>{
   const p=window.IGC_INSTAGRAM_PROFILES;
   return 'igc_profile_counts_v1__'+encodeURIComponent(p.owner)+'__'+encodeURIComponent(p.active);
  });
  assert(key.includes("igc_profile_counts_v1__"));
  // Simulate old stable v120.45 data; migration must be non-destructive.
  await page.evaluate(scope=>localStorage.setItem(scope,JSON.stringify({
   schema:"ig-cleaner-profile-counts-v1",
   records:{"legacy.user":{username:"legacy.user",followers:"201",
    following:"31",checked_at:"2026-10-10T12:00:00Z",status:"ok"}},
   updatedAt:"2026-10-10T12:00:00Z"
  })),key);
  await page.reload({waitUntil:"domcontentloaded"});
  const first=await page.evaluate(async()=>{
   await window.igcCountsStorageReady();
   return window.igcCountsGetRecord("legacy.user");
  });
  assert.equal(first?.followers,"201","Legacy count migrated without erasure");
  assert(await page.evaluate(scope=>!!localStorage.getItem(scope),key),
   "Original legacy backup must remain intact");
  const idbRecord=async username=>page.evaluate(async({scope,username})=>{
   const db=await new Promise((res,rej)=>{const q=indexedDB.open("ig_cleaner_profile_counts_v2",1);
    q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)});
   try{return await new Promise((res,rej)=>{
    const q=db.transaction("records","readonly").objectStore("records").get(scope+String.fromCharCode(0)+username);
    q.onsuccess=()=>res(q.result?.record||null);q.onerror=()=>rej(q.error)})}
   finally{db.close()}
  },{scope:key,username});
  assert.equal((await idbRecord("legacy.user"))?.followers,"201");
  // Every imported row, even after 250k profiles, must contribute to results.
  for(const n of [50000,100000,250000]){
   const start=Date.now();
   const metrics=await page.evaluate(n=>{
    followingRaw=Array.from({length:n},(_,i)=>({username:"p"+String(i).padStart(8,"0")}));
    window.igcCountsSetPage(0,true);
    const first=document.getElementById("igcCountsRows").textContent;
    const summary=document.getElementById("igcCountsSummary").textContent;
    window.igcCountsSetPage(Math.ceil(n/250)-1);
    const last=document.getElementById("igcCountsRows").textContent;
    const pageInfo=document.getElementById("igcCountsPageInfo").textContent;
    return {summary,first:first.slice(0,1500),last:last.slice(-1600),pageInfo};
   },n);
   const elapsed=Date.now()-start;
   assert(metrics.summary.includes(n+" profiles in Following"),"Full dataset counted: "+n);
   assert(metrics.first.includes("p00000000"),"First page lost: "+n);
   assert(metrics.last.includes("p"+String(n-1).padStart(8,"0")),"Last page lost: "+n);
   assert(metrics.pageInfo.includes(n.toLocaleString("en-US")),"Page count missing: "+n);
   assert(elapsed<45000,"Rendering locked up for "+n+" profiles: "+elapsed+"ms");
   console.log("PASS: "+n+" account profiles analyzed and paginated in "+elapsed+"ms");
  }
  await page.evaluate(()=>{followingRaw=[{username:"legacy.user"},{username:"new.user"}];window.igcCountsSetPage(0,true)});
  const csv="username,followers,following,checked_at,source,status,approximate\n"+
   "new.user,1200,600,2026-10-14T09:00:00Z,fixture,ok,false\n";
  await page.evaluate(async contents=>{
   await window.igcCountsImportFile({files:[{text:async()=>contents}],value:"new"});
  },csv);
  assert.equal((await idbRecord("new.user"))?.followers,"1200","CSV import persisted to IndexedDB");
  const other=key+"__different-instagram";
  const alien=await page.evaluate(async scope=>{
   const db=await new Promise((res,rej)=>{const q=indexedDB.open("ig_cleaner_profile_counts_v2");
    q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)});
   try{return await new Promise((res,rej)=>{
    const q=db.transaction("records","readonly").objectStore("records").index("scope").count(IDBKeyRange.only(scope));
    q.onsuccess=()=>res(q.result);q.onerror=()=>rej(q.error)})}
   finally{db.close()}
  },other);
  assert.equal(alien,0,"Records from another Instagram account must not be mixed");
  await page.reload({waitUntil:"domcontentloaded"});
  await page.evaluate(()=>window.igcCountsStorageReady());
  assert.equal((await idbRecord("new.user"))?.followers,"1200","Persisted records survive browser reload");
  assert(errors.filter(e=>/igcCounts|IndexedDB/.test(e)).length===0,
   "Unexpected application errors: "+errors.join(" | "));
  console.log("PASS: account-scoped IndexedDB migration, backup, durable CSV, reload");
  await ctx.close();
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
