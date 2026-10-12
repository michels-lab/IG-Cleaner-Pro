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
  await page.addInitScript(({first,second})=>{
   if(!window.localStorage)return;
   localStorage.setItem("igc_v12027_supabase_session",JSON.stringify(first));
   localStorage.setItem("igc_v12027_supabase_config",JSON.stringify({email:first.user.email,auto:true}));
   localStorage.setItem("igc_v120_login_accounts_v1",JSON.stringify({
      [first.user.email]:first,[second.user.email]:second}));
   localStorage.setItem("ig_v13_done",'["review-stays-local"]');
  },{first,second});
  // The init script above is intentionally applied only once to allow reload
  // to use the session saved by the app itself, not reseed the old owner.
  // Playwright's init scripts run on reload: remove it before switching.
  // Seed in one page and then navigate in a second page in the SAME context.
  await page.goto(pathToFileURL(file).href,{waitUntil:"domcontentloaded",timeout:60000});
  await page.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
  await page.evaluate(()=>showPage("sync"));
  await page.locator("#igcSyncSignedIn").waitFor({state:"visible"});
  assert.match(await page.locator("#igcSyncAccount").innerText(),/first@example\.test/);
  // Remove init-script effects on future navigation by switching to a new
  // browser page/context profile with persistent storage (no new init script).
  const secondPage=await context.newPage();
  secondPage.on("pageerror",error=>errors.push(error.message));
  await page.close();
  // create the second page in the same context; storage carries over.
  await secondPage.goto(pathToFileURL(file).href,{waitUntil:"domcontentloaded",timeout:60000});
  await secondPage.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
  await secondPage.evaluate(()=>showPage("sync"));
  await secondPage.getByRole("button",{name:"Cambiar cuenta"}).click();
  const modal=secondPage.locator("#igcLoginChooser");
  assert(await modal.isVisible(),"Switch Account must open a chooser, not sign out");
  const options=modal.locator("button");
  assert((await options.count())>=4,"Two logins, add and cancel expected");
  await options.filter({hasText:"second@example.test"}).click();
  await secondPage.waitForLoadState("domcontentloaded");
  await secondPage.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
  await secondPage.evaluate(()=>showPage("sync"));
  assert.match(await secondPage.locator("#igcSyncAccount").innerText(),/second@example\.test/,
    "Switch should move into the selected owner, not Sign out");
  const stored=await secondPage.evaluate(()=>({
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
