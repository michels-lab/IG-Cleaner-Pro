"use strict";
/* Opens the exact distributable file in Chromium and clicks Switch Account.
 * No real Supabase / Instagram requests, credentials or account changes. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path");
const {pathToFileURL}=require("node:url");
const {chromium}=require("playwright");

(async()=>{
 const file=path.resolve(process.argv[2]||"");
 assert(file.endsWith(".html")&&fs.existsSync(file),"Pass built standalone HTML");
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 const now=Math.floor(Date.now()/1000);
 const session=(email,id)=>({access_token:"offline-token-"+id,
   refresh_token:"offline-refresh-"+id,expires_at:now+3600,
   user:{id:"fixture-user-"+id,email}});
 const first=session("first@example.test","first"),second=session("second@example.test","second");
 try{
  const context=await browser.newContext({viewport:{width:1366,height:900}});
  // Network isolation: this checks session selection, never a live backend.
  await context.route("**/*",async route=>{
   if(route.request().url().startsWith("file:"))await route.continue();
   else await route.abort("blockedbyclient");
  });
  const page=await context.newPage();
  const errors=[];
  page.on("pageerror",error=>errors.push(error.message));
  await page.goto(pathToFileURL(file).href,{waitUntil:"domcontentloaded",timeout:60000});
  // Seed once in file:// localStorage before reloading into the owner scope;
  // unlike addInitScript, this cannot accidentally overwrite the switch.
  await page.evaluate(({first,second})=>{
    localStorage.setItem("igc_v12027_supabase_session",JSON.stringify(first));
    localStorage.setItem("igc_v12027_supabase_config",JSON.stringify({email:first.user.email,auto:true}));
    localStorage.setItem("igc_v120_login_accounts_v1",JSON.stringify({
      [first.user.email]:first,[second.user.email]:second}));
    localStorage.setItem("ig_v13_done",'["review-stays-local"]');
  },{first,second});
  await page.reload({waitUntil:"domcontentloaded"});
  await page.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
  await page.evaluate(()=>showPage("sync"));
  await page.locator("#igcSyncSignedIn").waitFor({state:"visible"});
  assert.match(await page.locator("#igcSyncAccount").innerText(),/first@example\.test/);
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const modal=page.locator("#igcLoginChooser");
  // The chooser is scheduled by the UI after the button click; assert the
  // settled visible result, not a race against the next microtask/frame.
  await modal.waitFor({state:"visible",timeout:15000}).catch(async error=>{
   const snapshot=await page.evaluate(()=>({
    signedIn:document.querySelector("#igcSyncSignedIn")?.offsetParent!==null,
    chooser:document.querySelector("#igcLoginChooser")?.getAttribute("style"),
    owner:JSON.parse(localStorage.getItem("igc_v12027_supabase_session")||"null")?.user?.email
   }));
   throw new Error("Switch Account chooser never became visible: "+
      JSON.stringify(snapshot)+"; "+error.message);
  });
  assert(await modal.isVisible(),"Switch Account must open a chooser, not sign out");
  const options=modal.locator("button");
  assert((await options.count())>=4,"Two logins, add and cancel expected");
  await options.filter({hasText:"second@example.test"}).click();
  // The account activation and reload are asynchronous. A Playwright click
  // may return before navigation; the old DOM is still valid at that moment.
  await page.waitForFunction(()=>{
   try{return JSON.parse(localStorage.getItem("igc_v12027_supabase_session")||"null")?.user?.email==="second@example.test"}
   catch{return false}
  },null,{timeout:15000}).catch(async error=>{
   const snapshot=await page.evaluate(()=>({
    owner:JSON.parse(localStorage.getItem("igc_v12027_supabase_session")||"null")?.user?.email,
    remembered:Object.keys(JSON.parse(localStorage.getItem("igc_v120_login_accounts_v1")||"{}")),
    chooser:!!document.querySelector("#igcLoginChooser"),
    status:document.querySelector("#igcSyncStatus")?.textContent,
    visibleAccount:document.querySelector("#igcSyncAccount")?.textContent,
    developer:!!window.igcDevAudit
   }));
   throw new Error("Saved account switch did not complete: "+
     JSON.stringify(snapshot)+"; page errors="+JSON.stringify(errors)+"; "+error.message);
  });
  await page.waitForFunction(()=>window.IGC_INSTAGRAM_PROFILES?.owner&&
      document.querySelector("#igcAppShell")?.offsetParent!==null,
      null,{timeout:15000});
  await page.evaluate(()=>showPage("sync"));
  await page.waitForFunction(()=>document.querySelector("#igcSyncAccount")?.textContent?.includes("second@example.test"),
   null,{timeout:15000});
  assert.match(await page.locator("#igcSyncAccount").innerText(),/second@example\.test/,
    "Switch should move into the selected owner, not Sign out");
  const stored=await page.evaluate(()=>({
    owner:JSON.parse(localStorage.getItem("igc_v12027_supabase_session")||"null")?.user?.email,
    wallet:Object.keys(JSON.parse(localStorage.getItem("igc_v120_login_accounts_v1")||"{}")),
    review:localStorage.getItem("ig_v13_done")
  }));
  assert.equal(stored.owner,"second@example.test");
  assert(stored.wallet.includes("first@example.test")&&stored.wallet.includes("second@example.test"));
  assert.equal(stored.review,'["review-stays-local"]');
  assert(!errors.some(x=>/igcSyncSwitchAccount|activateRemembered|SyntaxError/.test(x)),
      "No Switch Account script errors: "+JSON.stringify(errors));
  console.log("PASS: real Chromium shows account chooser, selects second user, retains first login and reviews");
  await context.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
