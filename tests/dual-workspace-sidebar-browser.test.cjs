'use strict';
// Real Chromium v120.72 screenshot regression: nav stays reachable even with robots expanded.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
(async()=>{
 const src=path.resolve(process.argv[2]||path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'));
 assert(fs.existsSync(src));const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 try{for(const viewport of [{width:1544,height:960},{width:1180,height:720}]){
  const context=await browser.newContext({viewport});
  await context.route('**/*',r=>r.request().url().startsWith('file:')?r.continue():r.abort('blockedbyclient'));
  const page=await context.newPage();await page.goto(pathToFileURL(src).href,{waitUntil:'domcontentloaded'});
  const advanced=page.locator('#igcDualAdvanced'),rail=page.locator('.igc-rail');
  assert.equal(await advanced.evaluate(x=>x.open),false);
  const home=await page.locator('#tab-moduleDashboard').boundingBox();
  const health=await page.locator('#tab-diag').boundingBox();
  const secondary=await page.locator('.igc-dual-workspace').boundingBox();
  assert(home&&health&&secondary&&home.y<health.y&&health.y<secondary.y,'Main navigation must precede second-account controls');
  assert(home.y<viewport.height,'Home must be reachable without scrolling');
  assert((await rail.boundingBox()).width<300,'Secondary account must not widen rail');
  assert(await page.locator('#igcDualSecondary').isVisible());
  assert(await page.getByRole('button',{name:'Open as tab'}).isVisible());
  assert(await page.getByRole('button',{name:'Detach to window'}).isVisible());
  assert.equal(await page.locator('#igcDualRobotTarget').isVisible(),false);
  await advanced.locator('summary').click();assert.equal(await advanced.evaluate(x=>x.open),true);
  assert(await page.locator('#igcDualRobotTarget').isVisible());
  assert(await page.getByRole('button',{name:'Stop both robots'}).isVisible());
  await rail.evaluate(e=>{e.scrollTop=0}); // Ignore the scroll from opening controls below navigation.
  const after=await page.locator('#tab-moduleDashboard').boundingBox();
  assert(Math.abs(home.y-after.y)<2,'Expanding advanced robots must not shift navigation');
  await advanced.locator('summary').click();assert.equal(await advanced.evaluate(x=>x.open),false);
  await context.close();
 }}finally{await browser.close()}
 console.log('GRANADA Chromium sidebar compact and expandable controls PASS');
})().catch(e=>{console.error(e);process.exit(1)});
