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
  // A legitimate startup synchronization can be in progress when the chooser
  // is opened. The chooser is read-only; selecting an account is not permitted
  // until both the action robot and account sync report safe admission.
  await page.waitForFunction(()=>window.igcSyncSwitchState?.().ready===true,
    null,{timeout:20000}).catch(async error=>{
    const gate=await page.evaluate(()=>window.igcSyncSwitchState?.()||{code:"missing"});
    throw new Error("Switch Account remained unsafe to select ("+gate.code+"): "+error.message);
  });
  const options=modal.locator("button");
  assert((await options.count())>=4,"Two logins, add and cancel expected");
  await options.filter({hasText:"second@example.test"}).click();
  // The account activation and reload are asynchronous. A Playwright click
  // may return before navigation; the old DOM is still valid at that moment.
  await page.waitForFunction(()=>{
   try{return JSON.parse(localStorage.getItem("igc_v12027_supabase_session")||"null")?.user?.email==="second@example.test"}
   catch{return false}
  },null,{timeout:15000});
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
  // Regression #264: a robot can become active AFTER the chooser checks its
  // admission gate but BEFORE the saved-account activation checks its own.
  // Previously the UI closed the chooser first and then silently vetoed the
  // account change, leaving the operator with no selector or explanation.
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const racedChooser=page.locator("#igcLoginChooser");
  await racedChooser.waitFor({state:"visible",timeout:5000});
  await page.evaluate(()=>{
    window.__switchRaceChecks=0;
    window.igcAutoSwitchGuard=()=>++window.__switchRaceChecks===1;
  });
  await racedChooser.locator("button").filter({hasText:"first@example.test"}).click();
  await page.waitForFunction(()=>
    window.__switchRaceChecks>=2 &&
    document.querySelector("#igcLoginChooser")?.open &&
    document.querySelector("#igcLoginChooser")?.textContent?.includes("Pause the Instagram robot"),
    null,{timeout:10000});
  assert(await racedChooser.isVisible(),
    "An activation denied by a LATE robot guard must keep saved accounts visible");
  assert(await racedChooser.locator("button").filter({hasText:"first@example.test"}).isEnabled(),
    "The rejected switch must restore controls for a later valid choice");
  assert.equal(await page.evaluate(()=>
    JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","Late robot veto must NEVER mutate the signed-in user");
  assert.equal(await page.evaluate(()=>localStorage.getItem("ig_v13_done")),
    '["review-stays-local"]',"Late guard veto preserves local review history");
  await page.evaluate(()=>{window.igcAutoSwitchGuard=()=>true});
  await racedChooser.getByText("Cancelar",{exact:true}).click();
  // Simulate a token refresh failure on a remembered but expired session.
  // Async failure must also keep the chooser; no phantom logout or change.
  await page.evaluate(()=>{
    const key="igc_v120_login_accounts_v1";
    const wallet=JSON.parse(localStorage.getItem(key));
    wallet["first@example.test"].expires_at=1;
    localStorage.setItem(key,JSON.stringify(wallet));
  });
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const expiredChooser=page.locator("#igcLoginChooser");
  await expiredChooser.waitFor({state:"visible",timeout:5000});
  await expiredChooser.locator("button").filter({hasText:"first@example.test"}).click();
  await page.waitForFunction(()=>
    document.querySelector("#igcLoginChooser")?.open &&
    document.querySelector("#igcLoginChooser")?.textContent?.includes("No se cambió de cuenta."),
    null,{timeout:15000});
  assert.equal(await page.evaluate(()=>
    JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","Failed expired-session refresh cannot change owners");
  assert(await expiredChooser.locator("button").filter({hasText:"first@example.test"}).isEnabled());
  await expiredChooser.getByText("Cancelar",{exact:true}).click();
  // Regression: a REMEMBERED session refresh must NOT provisionally overwrite
  // the currently signed-in owner during a pending HTTP response. If a robot
  // starts in the meantime, the final gate denies switching after response.
  await page.evaluate(()=>{
    const original=window.fetch;
    window.__originalSwitchFetch=original;
    window.__switchRefreshRequested=false;
    window.fetch=(url,opts)=>{
      if(String(url).includes("/auth/v1/token?grant_type=refresh_token")){
        window.__switchRefreshRequested=true;
        return new Promise(resolve=>{
          window.__resolveSwitchRefresh=()=>resolve({ok:true,text:async()=>JSON.stringify({
            access_token:"offline-renewed-first",refresh_token:"offline-new-refresh",
            expires_at:Math.floor(Date.now()/1000)+3600,
            user:{id:"fixture-user-first",email:"first@example.test"}
          })});
        });
      }
      return original(url,opts);
    };
  });
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const pendingChooser=page.locator("#igcLoginChooser");
  await pendingChooser.waitFor({state:"visible"});
  await pendingChooser.locator("button").filter({hasText:"first@example.test"}).click();
  await page.waitForFunction(()=>window.__switchRefreshRequested &&
    typeof window.__resolveSwitchRefresh==="function",null,{timeout:10000});
  assert.equal(await page.evaluate(()=>
    JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","An in-flight token refresh may NOT persist another owner early");
  assert.equal(await page.locator("#igcSyncAccount").innerText(),"second@example.test");
  await page.evaluate(()=>{
    window.igcAutoSwitchGuard=()=>false;
    window.__resolveSwitchRefresh();
  });
  await page.waitForFunction(()=>
    document.querySelector("#igcLoginChooser")?.open &&
    document.querySelector("#igcLoginChooser")?.textContent?.includes("Pause the Instagram robot"),
    null,{timeout:10000});
  assert.equal(await page.evaluate(()=>
    JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","A newly activated robot vetoes a completed refresh before commit");
  await page.evaluate(()=>{
    window.fetch=window.__originalSwitchFetch;
    window.igcAutoSwitchGuard=()=>true;
  });
  await pendingChooser.getByText("Cancelar",{exact:true}).click();
  await page.evaluate(()=>{
    const key="igc_v120_login_accounts_v1";
    const wallet=JSON.parse(localStorage.getItem(key));
    wallet["first@example.test"].expires_at=Math.floor(Date.now()/1000)+3600;
    localStorage.setItem(key,JSON.stringify(wallet));
  });
  // Simulate a real action robot starting AFTER the chooser was displayed.
  // The account button must not close it or change session mid-action.
  await page.waitForFunction(()=>window.igcSyncSwitchState?.().ready===true,
    null,{timeout:20000});
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const protectedChooser=page.locator("#igcLoginChooser");
  await protectedChooser.waitFor({state:"visible",timeout:5000});
  await page.evaluate(()=>{window.igcAutoSwitchGuard=()=>false});
  assert.equal(await page.evaluate(()=>window.igcSyncSwitchState().code),"automation_active");
  await protectedChooser.locator("button").filter({hasText:"first@example.test"}).click();
  assert(await protectedChooser.isVisible(),"Robot action veto must preserve the chooser for later manual review");
  assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","Robot veto must not switch current saved owner");
  await page.evaluate(()=>{window.igcAutoSwitchGuard=()=>true});
  await protectedChooser.getByText("Cancelar",{exact:true}).click();
  // The robot may become active between paint of the account button and
  // the click. Showing the read-only chooser must not be vetoed; changing
  // accounts from it is still guarded on every selection.
  await page.evaluate(()=>{window.igcAutoSwitchGuard=()=>false});
  await page.getByRole("button",{name:"Cambiar cuenta"}).click();
  const activeChooser=page.locator("#igcLoginChooser");
  await activeChooser.waitFor({state:"visible",timeout:5000});
  assert.match(await activeChooser.innerText(),/Pause the Instagram robot/);
  await activeChooser.locator("button").filter({hasText:"first@example.test"}).click();
  assert.equal(await page.evaluate(()=>
    JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
    "second@example.test","An active robot must NEVER change the signed-in owner.");
  assert(await activeChooser.isVisible(),"A vetoed choice must leave the chooser readable");
  await page.evaluate(()=>{window.igcAutoSwitchGuard=()=>true});
  await activeChooser.getByText("Cancelar",{exact:true}).click();
  // Repeat cold-start reloads after the legitimate account change. Both
  // sessions and local history must survive, with no phantom logout or
  // intermittent missing chooser while initialization/sync is settling.
  for(let cycle=1;cycle<=4;cycle++){
   await page.reload({waitUntil:"domcontentloaded"});
   await page.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
   await page.evaluate(()=>showPage("sync"));
   await page.locator("#igcSyncSignedIn").waitFor({state:"visible",timeout:15000});
   await page.getByRole("button",{name:"Cambiar cuenta"}).click();
   const reopened=page.locator("#igcLoginChooser");
   await reopened.waitFor({state:"visible",timeout:8000}).catch(async error=>{
    const gate=await page.evaluate(()=>window.igcSyncSwitchState?.()?.code||"missing");
    throw new Error("Cold-start cycle "+cycle+" failed to show chooser, gate="+gate+
      ": "+error.message);
   });
   assert.match(await reopened.innerText(),/first@example\.test/);
   assert.match(await reopened.innerText(),/second@example\.test/);
   assert.equal(await page.evaluate(()=>
     JSON.parse(localStorage.getItem("igc_v12027_supabase_session")).user.email),
     "second@example.test","The chooser must not switch owner without selecting one.");
   assert.equal(await page.evaluate(()=>
     localStorage.getItem("ig_v13_done")),'["review-stays-local"]');
   await reopened.getByText("Cancelar",{exact:true}).click();
  }
  console.log("PASS: four cold-start account chooser reloads, active robot read-only chooser, no unsafe change");
  console.log("PASS: real Chromium chooser supports startup sync, account change and late robot veto");
  await context.close();
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
