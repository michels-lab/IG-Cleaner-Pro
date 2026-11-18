'use strict';
/* Real Chromium acceptance: one account per InstaCleaner window, four clearly
 * separated Automations views. All interactions stay local and click no IG UI. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..');
 const source=process.argv[2]?path.resolve(process.argv[2]):
   path.join(root,'desktop','ig_cleaner_pro_v120_27_synced_companion.html');
 assert(fs.existsSync(source),'The real distributable HTML must be tested');
 const out=path.join(root,'artifacts','automation-center');
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const width of [390,1280]){
   const context=await browser.newContext({viewport:{width,height:850}});
   const page=await context.newPage();
   await page.goto(pathToFileURL(source).href,{waitUntil:'domcontentloaded',timeout:60000});
   await page.evaluate(()=>window.showPage('automations'));
   const tabs=['Analysis','Actions','Review','History'];
   const nav=page.locator('#igcAutomationCommandCenter');
   assert(await nav.isVisible(),'Automations navigation must be visible');
   assert.equal(await nav.locator('[role=tab]').count(),4);
   assert.equal(await page.locator('.igc-dual-workspace,#igcDualActionWorkspacePanel').count(),0,
     'Never show two accounts in a single app window');
   assert.equal(await page.locator('#igcAutoRun').count(),1,
     'Only one real Unfollow/Cancel action control');
   assert.equal(await page.locator('#igcAutoIssueRows').count(),1,
     'Review is reused, not duplicated');
   assert(await page.locator('#igcActionRobotSection').isVisible());
   assert(!await page.locator('#igcAnalysisRobotSection').isVisible());
   assert(!await page.locator('#igcAutomationReviewSection').isVisible());
   const geometry=await nav.locator('[role=tab]').evaluateAll(
     nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {
       left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width};}));
   const box=await nav.boundingBox();
   assert(geometry.every(x=>x.width>110&&x.left>=box.x-2&&x.right<=box.x+box.width+2),
      'Navigation must not clip at '+width);
   if(width===390)assert(geometry[2].top>=geometry[0].bottom-2,
     'Narrow window uses an easy-to-read 2×2 grid');
   else assert(Math.abs(geometry[0].top-geometry[3].top)<4,
     'Wide window keeps four navigational sections in one row');
   await page.locator('#igcAutomationTabAnalysis').click();
   assert(await page.locator('#igcAnalysisRobotSection').isVisible());
   assert(!await page.locator('#igcActionRobotSection').isVisible());
   assert.equal(await page.locator('#igcAutomationTabAnalysis').getAttribute('aria-selected'),'true');
   assert(await page.locator('#igcCountsRobotConnect').count()===1);
   await page.locator('#igcAutomationTabActions').click();
   assert(await page.locator('#igcActionRobotSection').isVisible());
   for(const action of ['Unfollow','Cancel','Protected','Audit'])
     assert.equal(await page.locator('#igcAutoMode'+action).count(),1);
   await page.locator('#igcAutoModeCancel').click();
   assert.equal(await page.locator('#igcAutoModeCancel').getAttribute('aria-pressed'),'true');
   assert(await page.locator('#igcAutoConfigCard').isVisible());
   await page.evaluate(()=>{
     const size=document.getElementById('igcAutoBatch');size.value='10';
     size.dispatchEvent(new Event('input',{bubbles:true}));
     document.getElementById('igcAutoBatchApprovalDetails').textContent=
       'Saved cohort: 40 targets · 38 untouched; approval pending';
   });
   assert.equal(await page.locator('#igcAutoBatch').inputValue(),'10',
     'New preference must not silently resize an old saved cohort');
   assert.match(await page.locator('#igcAutoBatchApprovalDetails').innerText(),/40 targets/);
   await page.locator('#igcAutomationTabReview').click();
   const drawer=page.locator('#igcAutoReviewDrawer');
   assert(await page.locator('#igcAutomationReviewSection').isVisible());
   assert(!await page.locator('#igcActionRobotSection').isVisible());
   assert(await drawer.isVisible());
   assert(await page.locator('#igcAutoIssueTask').isVisible());
   assert(await page.locator('#igcAutoIssueFilter').isVisible());
   await page.locator('#igcAutomationTabHistory').click();
   if(await page.locator('#igcAutomationActivityPanel').count()){
     assert(await page.locator('#igcAutomationActivitySection').isVisible());
     assert(!await page.locator('#igcActionRobotSection').isVisible());
     for(const key of ['session','today','d7'])
       assert(await page.locator('#igcActCount_'+key).isVisible());
     assert.equal(await page.locator('#igcActMorePeriods').evaluate(el=>el.open),false);
     await page.locator('#igcActMorePeriods summary').click();
     assert(await page.locator('#igcActCount_h2').isVisible(),
       'Detailed 2h counters open only on demand');
   }else{
     assert(await page.locator('#igcAutomationActivitySection').isVisible());
     assert(!await page.locator('#igcActionRobotSection').isVisible(),
       'Standalone History must not misleadingly jump back into Actions');
     assert.match(await page.locator('#igcAutomationActivitySection').innerText(),
       /installed Windows app/);
   }
   await nav.screenshot({path:path.join(out,'clear-navigation-'+width+'.png'),animations:'disabled'});
   await context.close();
  }
  console.log('GRANADA: one account UI, four Automations sections, safe cohort and narrow/wide layout PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
