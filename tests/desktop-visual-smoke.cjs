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
      assert(await page.locator("#aboutDeveloperBtn").isVisible(), "About navigation must be accessible");
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
      assert(await page.locator(".aboutDeveloperCard").isVisible(), "Author card absent");
      assert(await page.locator(".aboutBrandMini").isVisible(), "Michel's Lab card absent");
      assert(await page.locator(".aboutBrandTag").innerText() === "TOOLS WITH IDENTITY.", "Brand slogan mismatch");
      assert.equal(await page.locator(".aboutSocial").count(),5,"All five socials must be present");
      const imgs=await page.locator("#aboutDeveloperOverlay img").evaluateAll(imgs =>
        imgs.map(im=>({alt:im.alt,loaded:im.complete && im.naturalWidth>0})));
      assert(imgs.length>=3 && imgs.every(im=>im.loaded), "Author/product/studio images must load in real browser");
      await capture("about","initial");
      const links=page.locator(".aboutSocial");
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
