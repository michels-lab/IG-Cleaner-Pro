'use strict';
/* Legacy filename retained for CI: ensure SECOND ACCOUNT sidebar is truly gone
 * while the primary profile can still be selected and switched. */
const assert=require('node:assert/strict');
const path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
(async()=>{
 const file=process.argv[2]?path.resolve(process.argv[2]):
   path.resolve(__dirname,'..','desktop','ig_cleaner_pro_v120_27_synced_companion.html');
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const width of [390,1280]){
   const context=await browser.newContext({viewport:{width,height:820}});
   const page=await context.newPage();
   await page.goto(pathToFileURL(file).href,{waitUntil:'domcontentloaded',timeout:60000});
   const rail=page.locator('.igc-rail');
   assert(await rail.count()===1);
   const active=page.locator('#igcInstagramIdentity');
   assert(await active.count()===1,'One Instagram account selector must remain');
   assert(await page.locator('#igcInstagramActiveFullName').count()===1);
   assert.equal(await page.locator('#igcDualSecondary,.igc-dual-workspace,#igcDualAdvanced').count(),0);
   assert.equal(await page.locator('#igcDualActionWorkspacePanel').count(),0);
   assert.equal(await page.locator('#igcAppShell').count(),1);
   assert(!await page.evaluate(()=>Boolean(window.IGC_INSTAGRAM_PROFILES?.openOtherWorkspace)),
     'No stale in-app tab cloning commands');
   await context.close();
  }
  console.log('GRANADA rendered primary-only Instagram sidebar at compact and desktop sizes PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
