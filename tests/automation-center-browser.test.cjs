'use strict';
/* GRANADA: real running Chromium acceptance for the integrated Windows
 * Automation Center. Fixtures never touch Instagram or change relationships.
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');

(async()=>{
 const root=path.resolve(__dirname,'..');
 const source=process.argv[2] ? path.resolve(process.argv[2]) :
   path.join(root,'desktop','ig_cleaner_pro_v120_27_synced_companion.html');
 assert(fs.existsSync(source),'Test the actual distributed Desktop HTML');
 const output=path.join(root,'artifacts','automation-center');
 fs.mkdirSync(output,{recursive:true});
 const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{
  for(const width of [390,1280]){
   const context=await browser.newContext({viewport:{width,height:850}});
   const page=await context.newPage();
   await page.goto(pathToFileURL(source).href,{waitUntil:'domcontentloaded',timeout:60000});
   await page.evaluate(()=>window.showPage('automations'));
   const center=page.locator('#igcAutomationCommandCenter');
   assert(await center.isVisible(),'Robot command center not shown in Automations');
   const analysis=page.locator('#igcAutomationAnalysisLane'),
         action=page.locator('#igcAutomationActionLane');
   assert(await analysis.isVisible()&&await action.isVisible(),
     'Analysis and Action must both remain visible');
   assert.equal(await page.locator('#igcAutomationCommandCenter .igc-robot-lane').count(),2);
   assert.equal(await page.locator('#igcAutoRun').count(),1,
     'There must be one real relationship-action Run control, not duplicate UI proxies');
   assert.equal(await page.locator('#igcCountsRobotConnect').count(),1);
   assert.equal(await page.locator('#igcAutoIssueRows').count(),1);
   assert(!await page.locator('#igcAutoReviewDrawer').evaluate(el=>el.open),
     'Large manual Issue Review must be initially collapsible');
   const geom=await page.evaluate(()=>{
    const outer=document.getElementById('igcAutomationCommandCenter').getBoundingClientRect();
    const cards=[...document.querySelectorAll('#igcAutomationCommandCenter .igc-robot-lane')]
     .map(el=>el.getBoundingClientRect());
    return {outer:{x:outer.x,right:outer.right,width:outer.width},
      cards:cards.map(r=>({x:r.x,right:r.right,width:r.width,top:r.top,bottom:r.bottom}))};
   });
   assert(geom.cards.every(x=>x.width>=150&&x.x>=geom.outer.x-2&&x.right<=geom.outer.right+2),
      'Cards clipped/overflowed their available workspace: '+JSON.stringify(geom));
   if(width===390)assert(geom.cards[1].top>=geom.cards[0].bottom-2,
     'Compact Windows viewport must stack two lanes');
   else assert(Math.abs(geom.cards[1].top-geom.cards[0].top)<4,
     'Desktop viewport should align both lanes horizontally');
   const safety=await page.locator('#igcAutomationConcurrencyNotice').innerText();
   assert.match(safety,/cannot navigate Instagram simultaneously/);
   assert.match(safety,/Do not retry an uncertain click/);
   await page.evaluate(()=>{
    document.getElementById('igcAutoLiveStatus').textContent=
      'Status: waiting · Verifying owner in Chrome; no action confirmed';
    document.getElementById('igcCountsRobotStatus').textContent=
      'Profile Counts: blocked by separate Chrome navigation';
    document.getElementById('igcAutoIssueTotal').textContent='6 unresolved issues';
    const batch=document.getElementById('igcAutoBatch');
    batch.value='10';
    batch.dispatchEvent(new Event('input',{bubbles:true}));
    window.igcAutomationCommandCenterRefresh();
   });
   assert.match(await page.locator('#igcAutomationActionStatus').innerText(),/Verifying owner/);
   assert.match(await page.locator('#igcAutomationAnalysisStatus').innerText(),/blocked by separate Chrome/);
   assert.match(await page.locator('#igcAutomationBatchSummary').innerText(),/Next batch preference: 10/);
   assert.match(await page.locator('#igcAutoReviewCaption').innerText(),/6 unresolved issues/);
   const drawer=page.locator('#igcAutoReviewDrawer');
   await drawer.locator('summary').click();
   assert(await drawer.evaluate(el=>el.open),'Issue Review summary should open with keyboard/mouse');
   assert(await page.locator('#igcAutoIssueTask').isVisible());
   assert(await page.locator('#igcAutoIssueFilter').isVisible());
   await drawer.locator('summary').press('Enter');
   assert(!await drawer.evaluate(el=>el.open),'Issue Review should close with keyboard');
   await center.screenshot({path:path.join(output,'command-center-'+width+'.png'),
     animations:'disabled'});
   await context.close();
  }
  console.log('GRANADA Windows Automation Center: rendered two lanes, live-status mirrors, saved-batch distinction, issue disclosure and 390/1280 layouts PASS');
 }finally{await browser.close()}
})().catch(err=>{console.error(err);process.exitCode=1});
