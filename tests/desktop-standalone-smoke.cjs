"use strict";
/** Opens the actual generated single-file Desktop artifact in Chromium offline. */
const fs=require("node:fs");
const path=require("node:path");
const {pathToFileURL}=require("node:url");
const assert=require("node:assert/strict");
const {chromium}=require("playwright");

(async()=>{
 const file=path.resolve(process.argv[2]||"");
 assert(file.endsWith(".html") && fs.existsSync(file),"Provide the generated standalone Desktop HTML");
 const html=fs.readFileSync(file,"utf8");
 assert(html.includes("data:image/png;base64,"),"No embedded PNG app/studio asset");
 assert(html.includes("data:image/jpeg;base64,"),"No embedded JPG author image");
 assert(!/\b(?:src|href)=["']assets\//i.test(html),"Unresolved relative Desktop asset");
 const browser=await chromium.launch({headless:true,args:["--no-sandbox"]});
 try{
  for(const viewport of [{width:390,height:844},{width:1360,height:900}]){
   const context=await browser.newContext({viewport});
   const page=await context.newPage();
   await page.goto(pathToFileURL(file).href,{waitUntil:"domcontentloaded",timeout:60000});
   await page.locator("#igcAppShell").waitFor({state:"visible",timeout:15000});
   await page.locator("#aboutDeveloperBtn").click();
   await page.locator("#aboutDeveloperOverlay").waitFor({state:"visible"});
   assert(await page.locator(".aboutDeveloperCard").isVisible());
   assert(await page.locator(".aboutBrandMini").isVisible());
   assert.equal((await page.locator(".aboutBrandTag").innerText()).trim(),"TOOLS WITH IDENTITY.");
   assert.equal(await page.locator(".aboutSocial").count(),5);
   const imgs=await page.locator("#aboutDeveloperOverlay img").evaluateAll(xs=>xs.map(x=>({
     alt:x.alt,loaded:x.complete&&x.naturalWidth>0,uri:x.currentSrc.startsWith("data:")
   })));
   assert(imgs.length>=3 && imgs.every(x=>x.loaded&&x.uri),
    "Standalone offline About failed to display embedded branding images: "+JSON.stringify(imgs));
   await page.locator("#aboutDeveloperClose").click();
   assert(!(await page.locator("#aboutDeveloperOverlay").isVisible()));
   await context.close();
  }
  console.log("PASS: standalone Desktop HTML opened from file:// at compact/wide sizes, embedded images loaded, About opens/closes.");
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
