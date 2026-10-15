"use strict";
/* Real file:// Chromium ↔ authorized 127.0.0.1 controller acceptance.
   Instagram itself is NOT contacted; test uses an honest local fixture. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const http=require("node:http");
const {pathToFileURL}=require("node:url");
const {chromium}=require("playwright");

(async()=>{
 const html=path.resolve(process.argv[2]||"");
 assert(fs.existsSync(html) && html.endsWith(".html"),"Pass generated standalone HTML");
 const token="integration-test-only-secret-abcdefghijklmnopqrstuvwxyz";
 let identity=null,queries=0,staging=null,appendCalls=0;
 const results=[{username:"public.user",followers:"8765",following:"432",
  checked_at:"2026-10-12T02:00:00+00:00",source:"instagram_visible_profile_browser",
  approximate:"false",status:"ok"}];
 const server=http.createServer(async(req,res)=>{
  const h={
   "Access-Control-Allow-Origin":"null",
   "Access-Control-Allow-Headers":"Content-Type, X-IGC-Bridge-Token",
   "Access-Control-Allow-Methods":"GET, POST, OPTIONS",
   "Access-Control-Allow-Private-Network":"true",
   "Cache-Control":"no-store","Content-Type":"application/json; charset=utf-8"
  };
  function send(code,payload){res.writeHead(code,h);res.end(JSON.stringify(payload))}
  if(req.method==="OPTIONS"){res.writeHead(204,h);res.end();return}
  if(req.headers.origin && req.headers.origin!=="null"){send(403,{error:"Non-local Origin"});return}
  if(req.headers["x-igc-bridge-token"]!==token){send(403,{error:"Invalid token"});return}
  if(req.url==="/api/status"){send(200,identity?{status:"running",message:"Running fixture",
   owner:identity.owner,account:identity.account,progress:1,total:1,per_hour:50}:
   {status:"idle",message:"Ready",owner:"",account:"",progress:0,total:0,per_hour:50});return}
  if(req.url==="/api/results"){send(200,{rows:results});return}
  if(req.url==="/api/following"){send(200,{handle:"fixture.owner",complete:false,usernames:[]});return}
  if(req.url==="/api/queue/init"&&req.method==="POST"){
   const chunks=[];for await(const chunk of req)chunks.push(chunk);
   const body=JSON.parse(Buffer.concat(chunks).toString("utf8"));
   assert.equal(body.total,1);
   staging={owner:body.owner,account:body.account,transfer:"test-transfer",usernames:[]};
   send(200,{transfer:staging.transfer,total:body.total,received:0});
   return;
  }
  if(req.url==="/api/queue/append"&&req.method==="POST"){
   const chunks=[];for await(const chunk of req)chunks.push(chunk);
   const body=JSON.parse(Buffer.concat(chunks).toString("utf8"));
   assert.equal(body.transfer,staging.transfer);
   assert.equal(body.offset,staging.usernames.length);
   staging.usernames.push(...body.usernames);
   appendCalls++;
   send(200,{received:staging.usernames.length,total:1});
   return;
  }
  if(req.url==="/api/auto"&&req.method==="POST"){
   const chunks=[];for await(const chunk of req)chunks.push(chunk);
   const body=JSON.parse(Buffer.concat(chunks).toString("utf8"));
   assert.deepEqual(body.usernames,[],"Imported list is transferred through validated chunks");
   assert.equal(body.use_staged_import,true);
   assert.equal(body.transfer,staging.transfer);
   assert.deepEqual(staging.usernames,["public.user"],"All imported usernames must reach the robot");
   assert.equal(body.discover_following,false,"Following browser discovery must be opt-in");
   assert.equal(body.max_per_window,50);
   assert.equal(body.window_minutes,60);
   assert.equal(body.min_delay_seconds,72);
   assert.equal(body.pause_every,0);
   assert.equal(body.pause_minutes,0);
   identity={owner:body.owner,account:body.account};
   queries++;
   send(200,{message:"Starting fixture",status:"starting",total:1,progress:0});
   return;
  }
  send(404,{error:"Unknown route"});
 });
 await new Promise(resolve=>server.listen(0,"127.0.0.1",resolve));
 const port=server.address().port;
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  const context=await browser.newContext({viewport:{width:1360,height:900}});
  const page=await context.newPage();
  const errors=[];page.on("pageerror",e=>errors.push(e.message));
  await page.goto(pathToFileURL(html).href+"#igc-robot="+port+"."+token,
   {waitUntil:"domcontentloaded",timeout:60000});
  await page.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
  await page.evaluate(()=>{
   followingRaw=[{username:"public.user"}]; // Use existing imported Following list.
   showPage("automations");
   window.igcCountsRender();
  });
  assert(await page.locator("#page-automations #igcCountsRobotActions").isVisible(),
   "Pacing, Pause and Resume controls must be visible");
  assert(await page.locator("#page-automations #igcCountsResume").isVisible());
  assert(await page.locator("#page-profileStats #igcCountsRobotActions").count()===0,
   "Insights must not contain robot controls");
  assert(await page.locator("#page-profileStats #igcCountsSummary").count()===0,
   "Insights must not host individual Profile Counts results");
  assert(await page.locator("#page-automations #igcCountsSummary").count()===1,
   "Automations must host all Profile Counts results and monitoring controls");
  await page.locator("#page-automations #igcCountsRobotConnect button").first().click();
  // Explicit connect starts counts on the existing import; no Following dialog.

  const deadline=Date.now()+8000;
  while(queries<1&&Date.now()<deadline)
    await new Promise(resolve=>setTimeout(resolve,100));
  if(queries!==1){
    const diagnostics=await page.evaluate(()=>({
      status:document.getElementById("igcCountsRobotStatus")?.textContent,
      preview:document.getElementById("igcCountsRobotPaceNote")?.textContent,
      config:["igcCountsRobotMax","igcCountsRobotWindow","igcCountsRobotGap","igcCountsRobotRestEvery","igcCountsRobotRestMinutes"]
         .map(x=>[x,document.getElementById(x)?.value]),
      active:window.IGC_INSTAGRAM_PROFILES?.active
    }));
    throw Error("Real browser never automatically connected: "+JSON.stringify({diagnostics,queries,errors}));
  }
  assert.equal(appendCalls,1,"The imported profile must be uploaded in a staging chunk");
  await page.evaluate(()=>{showPage("automations");return window.igcCountsRobotPoll()});
  await page.waitForFunction(()=>document.querySelector("#igcCountsRows")?.textContent.includes("8,765"),
   {timeout:10000});
  const row=await page.locator("#igcCountsRows").innerText();
  assert(row.includes("public.user")&&row.includes("8,765")&&row.includes("432"),
   "Actual rendered profile counts missing: "+row);
  const storedRecord=await page.evaluate(async()=>{
   const ctx=window.IGC_INSTAGRAM_PROFILES;
   await window.igcCountsStorageReady();
   const scope="igc_profile_counts_v1__"+encodeURIComponent(ctx.owner)+"__"+encodeURIComponent(ctx.active);
   return new Promise((resolve,reject)=>{
    const q=indexedDB.open("ig_cleaner_profile_counts_v2",1);
    q.onsuccess=()=>{
     const db=q.result,tx=db.transaction("records","readonly");
     const item=tx.objectStore("records").get(scope+String.fromCharCode(0)+"public.user");
     item.onsuccess=()=>{resolve(item.result?.record);db.close()};
     item.onerror=()=>reject(item.error);
    };q.onerror=()=>reject(q.error)
   });
  });
  assert.equal(storedRecord.followers,"8765","Visible results must persist to IndexedDB");
  assert(errors.filter(e=>e.includes("igcCounts")).length===0,
   "UI JavaScript exceptions: "+JSON.stringify(errors));
  console.log("PASS: real file:// Chromium sent imported Following to robot without rediscovery and stored follower counts.");
  await context.close();
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(err=>{console.error(err);process.exitCode=1});
