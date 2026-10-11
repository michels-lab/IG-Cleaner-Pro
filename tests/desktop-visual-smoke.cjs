"use strict";
/* Real running Chromium screenshot acceptance of the distributable Desktop HTML. */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");
const {pathToFileURL} = require("node:url");
const {chromium} = require("playwright");

(async () => {
  const root = path.resolve(__dirname, "..");
  const entry = path.join(root, "desktop/ig_cleaner_pro_v120_27_synced_companion.html");
  const destination = path.join(root, "artifacts/desktop-visual");
  fs.mkdirSync(destination, {recursive:true});
  const sha = process.env.GITHUB_SHA || process.env.IGC_SOURCE_SHA;
  assert.match(sha || "", /^[0-9a-f]{40}$/i, "Full candidate source SHA required");
  const digest = v => crypto.createHash("sha256").update(v).digest("hex");
  const browser = await chromium.launch({headless:true, args:["--no-sandbox"]});
  const shots = [];
  try {
    for(const viewport of [
      {name:"compact",width:390,height:844},
      {name:"wide",width:1360,height:900}
    ]) {
      const context = await browser.newContext({viewport:{width:viewport.width,height:viewport.height}});
      const page = await context.newPage();
      const fileUrl=pathToFileURL(entry).href;
      await page.goto(fileUrl,{waitUntil:"domcontentloaded",timeout:60000});
      await page.locator("#igcAppShell").waitFor({state:"visible"});
      // Real Chromium parses stray backslash-n outside <style> as visible
      // text nodes and lifts them above the shell. Source/PNG checks alone
      // previously missed this exact regression.
      const unexpectedText = await page.evaluate(() => {
        const shell = document.querySelector('#igcAppShell');
        const beforeShell = [];
        for (let node = document.body.firstChild; node && node !== shell; node = node.nextSibling) {
          if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
            beforeShell.push(node.textContent.trim());
          }
        }
        return {beforeShell, shellTop: shell.getBoundingClientRect().top};
      });
      assert.equal(unexpectedText.beforeShell.length, 0,
        'Unexpected raw text above the sidebar: ' + JSON.stringify(unexpectedText.beforeShell));
      assert(unexpectedText.shellTop >= -2 && unexpectedText.shellTop <= 2,
        'App shell displaced by stray HTML text: ' + JSON.stringify(unexpectedText));

      const headerAbout=page.locator(".igc-commandbar > #aboutDeveloperBtn");
      assert(await headerAbout.isVisible(), "About must be visible in the permanent top header");
      const initialBounds=await headerAbout.boundingBox();
      assert(initialBounds && initialBounds.x>=0 && initialBounds.x+initialBounds.width<=viewport.width,
        "Header About is clipped outside the viewport: "+JSON.stringify(initialBounds));
      await page.locator(".igc-workspace").evaluate(el=>el.scrollTop=el.scrollHeight);
      assert(await headerAbout.isVisible(), "About disappeared after scrolling workspace");
      async function capture(surface, section) {
        const name=`${surface}-${viewport.name}-${section}.png`;
        const file=path.join(destination,name);
        await page.screenshot({path:file, animations:"disabled", fullPage:false});
        const data=fs.readFileSync(file);
        assert(data.length>3000, "Screenshot unexpectedly empty");
        assert(data.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])), "Invalid PNG");
        assert.equal(data.readUInt32BE(16), viewport.width, "Screenshot width mismatch");
        assert.equal(data.readUInt32BE(20), viewport.height, "Screenshot height mismatch");
        shots.push({platform:"desktop",surface,section,viewport:viewport.name,
          width:viewport.width,height:viewport.height,path:name,sha256:digest(data),
          capture_method:"running-browser"});
      }
      await capture("home","initial");
      await page.locator("#aboutDeveloperBtn").click();
      const modal=page.locator("#aboutDeveloperOverlay");
      await modal.waitFor({state:"visible"});
      assert(await page.locator(".aboutDeveloperCard").isVisible(), "Developer panel absent");
      assert.equal(await page.locator(".aboutBrandRow > div").count(), 2, "Brand logos must be adjacent");
      const brandLogos=await page.locator(".aboutBrandRow img").evaluateAll(ims=>ims.map(img=>{
        const r=img.getBoundingClientRect(); return {top:r.top,left:r.left,width:r.width,height:r.height};
      }));
      assert.equal(brandLogos.length,2);
      assert(Math.abs(brandLogos[0].top-brandLogos[1].top)<25,
        "App and Michel's Lab logos are not aligned horizontally");
      const face=await page.locator(".aboutPortraitImg").boundingBox();
      assert(face&&face.height>=180,"Developer portrait must be large and readable");
      const socialsBox=await page.locator(".aboutSocials").boundingBox();
      assert(socialsBox && socialsBox.x>face.x+face.width-5,
        "Social links must form a list alongside the portrait");
      assert(await page.locator(".aboutBrandMini").isVisible(), "Michel's Lab card absent");
      assert(await page.locator(".aboutBrandTag").innerText() === "TOOLS WITH IDENTITY.", "Brand slogan mismatch");
      assert.equal(await page.locator(".aboutSocial").count(),5,"All five socials must be present");
      const imgs=await page.locator("#aboutDeveloperOverlay img").evaluateAll(imgs =>
        imgs.map(im=>({alt:im.alt,loaded:im.complete && im.naturalWidth>0})));
      assert(imgs.length>=3 && imgs.every(im=>im.loaded), "Author/product/studio images must load in real browser");
      if (viewport.name === "compact") {
        const firstView = await page.evaluate(() => {
          const selectors=[
            ".aboutProductMark",".aboutAvatar",".aboutBrandMini",".aboutBrandTag",
            ...Array.from({length:5},(_,i)=>`.aboutSocial:nth-child(${i+1})`)
          ];
          return selectors.map(selector=>{
            const el=document.querySelector(selector);
            const r=el?.getBoundingClientRect();
            return {selector,visible:!!r&&r.width>0&&r.height>0
                &&r.top>=0&&r.bottom<=window.innerHeight-4,
                top:r?.top,bottom:r?.bottom};
          });
        });
        assert(firstView.every(v=>v.visible),
          "P0: compact About must show author, Lab/slogan and all five social links without scrolling: "+
          JSON.stringify(firstView.filter(v=>!v.visible)));
      }
      if (viewport.name === "compact") {
        const geometry=await page.evaluate(()=>{
          const mark=document.querySelector(".aboutProductMark")?.getBoundingClientRect();
          const image=document.querySelector(".aboutOfficialLockup")?.getBoundingClientRect();
          const close=document.querySelector("#aboutDeveloperClose")?.getBoundingClientRect();
          const shell=document.querySelector(".aboutShell")?.getBoundingClientRect();
          if(!mark||!image||!close||!shell)return {valid:false,reason:"missing geometry"};
          const contained=image.left>=mark.left && image.right<=mark.right &&
              image.top>=mark.top && image.bottom<=mark.bottom;
          const overlap=image.left < close.right && image.right > close.left &&
              image.top < close.bottom && image.bottom > close.top;
          const withinShell=mark.left>=shell.left && mark.right<=shell.right;
          return {valid:contained&&!overlap&&withinShell,contained,overlap,withinShell,
              mark:{x:mark.x,width:mark.width},image:{x:image.x,width:image.width}};
        });
        assert(geometry.valid, "P0: compact product logo spills/overlaps close action: "+JSON.stringify(geometry));
      }
      await capture("about","initial");
      const links=page.locator(".aboutSocial");
      const boxes=await links.evaluateAll(xs=>xs.map(e=>e.getBoundingClientRect().top));
      assert(boxes.every((y,i)=>i===0||y>boxes[i-1]),
        "Social links should be one vertical list, never a tile grid");
      await links.last().scrollIntoViewIfNeeded();
      for(let k=0;k<5;k++){
        const url=await links.nth(k).getAttribute("href");
        assert(/^https?:\/\/|^mailto:/.test(url||""), "Broken social link target");
        assert((await links.nth(k).innerText()).trim().length>4,"Social link missing readable label");
      }
      await capture("about","socials");
      await page.locator("#aboutDeveloperClose").click();
      assert(!(await modal.isVisible()),"About close action must work");
      await context.close();
    }
  } finally {await browser.close();}
  const manifest={
    schema:"igc-desktop-runtime-visual-v1",
    source_commit:sha,
    html_sha256:digest(fs.readFileSync(entry)),
    screenshots:shots,
    reviewed_in:"automated real Chromium run",
    physical_device_acceptance:"not_claimed"
  };
  fs.writeFileSync(path.join(destination,"manifest.json"),JSON.stringify(manifest,null,2)+"\n");
  assert.equal(shots.length,6);
  console.log("SUCCESS: Desktop Home+About six runtime screenshots and loaded studio/socials verified");
})().catch(err=>{console.error(err);process.exitCode=1});
