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
 let identity=null,queries=0;
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
  if(req.url==="/api/start"&&req.method==="POST"){
   const chunks=[];for await(const chunk of req)chunks.push(chunk);
   const body=JSON.parse(Buffer.concat(chunks).toString("utf8"));
   assert.deepEqual(body.usernames,["public.user"]);
   assert.equal(body.per_hour,50);
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
   followingRaw=[{username:"public.user"}];
   showPage("profileStats");
   window.igcCountsRender();
  });
  await page.locator("#igcCountsRobotActions").waitFor({state:"visible",timeout:6000});
  await page.locator('#igcCountsRobotActions button[onclick="igcCountsRobotStart()"]').click();
  await page.waitForFunction(()=>document.querySelector("#igcCountsRobotStatus")?.textContent.includes("Starting fixture"),
   {timeout:10000});
  assert.equal(queries,1,"UI did not start local collector");
  await page.evaluate(()=>window.igcCountsRobotPoll());
  await page.waitForFunction(()=>document.querySelector("#igcCountsRows")?.textContent.includes("8,765"),
   {timeout:10000});
  const row=await page.locator("#igcCountsRows").innerText();
  assert(row.includes("public.user")&&row.includes("8,765")&&row.includes("432"),
   "Actual rendered profile counts missing: "+row);
  const localState=await page.evaluate(()=>{
   const ctx=window.IGC_INSTAGRAM_PROFILES;
   const key="igc_profile_counts_v1__"+encodeURIComponent(ctx.owner)+"__"+encodeURIComponent(ctx.active);
   return JSON.parse(window.localStorage.getItem(key));
  });
  assert.equal(localState.records["public.user"].followers,"8765");
  assert(errors.filter(e=>e.includes("igcCounts")).length===0,
   "UI JavaScript exceptions: "+JSON.stringify(errors));
  console.log("PASS: real file:// Desktop Chromium displayed localhost robot controls, sent authorized Start and persisted visible mock counts.");
  await context.close();
 }finally{await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(err=>{console.error(err);process.exitCode=1});
