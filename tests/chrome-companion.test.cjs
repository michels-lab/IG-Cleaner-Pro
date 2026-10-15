"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const dir = path.join(__dirname, "../packaging/chrome-extension");
const C = require(path.join(dir,"collector.js"));
const manifest = JSON.parse(fs.readFileSync(path.join(dir,"manifest.json"),"utf8"));
const popup = fs.readFileSync(path.join(dir,"popup.js"),"utf8");
const html = fs.readFileSync(path.join(dir,"popup.html"),"utf8");
assert.equal(manifest.manifest_version,3);
assert.deepEqual(manifest.permissions,
 ["activeTab","scripting","storage","unlimitedStorage","downloads"]);
assert.equal(manifest.host_permissions,undefined,"No broad Instagram site permissions");
assert(!("content_scripts" in manifest),"No always-on background scraping");
assert(!("background" in manifest),"Do not run autonomous browser jobs");
assert(html.includes('id="capture"')&&html.includes('id="export"'));
assert(html.includes('id="reAudit"') && html.includes('id="historyExport"'));
assert(html.includes('id="roundRemaining"'));
const desktop=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
assert(desktop.includes('id="igcChromeCompanion"'),"Companion must be discoverable in Automations");
assert(desktop.includes('onclick="igcCountsExportQueue()"'),"Following queue export must be present");
assert(desktop.includes('onchange="igcCountsImportFile(this)"'),"CSV results must be importable");
const win=fs.readFileSync(path.join(__dirname,"../.github/workflows/profile-counts-windows-preview.yml"),"utf8");
const release=fs.readFileSync(path.join(__dirname,"../.github/workflows/release.yml"),"utf8");
for(const workflow of [win,release]){
 assert(workflow.includes("Copy-Item packaging/chrome-extension artifacts/profile-counts-preview/chrome-extension -Recurse -Force"),
  "The owner Windows ZIP must physically include the unpacked extension");
 assert(workflow.includes("node tests/chrome-companion.test.cjs"),
  "The Chrome extension must be tested before packaging");
}
for(const prohibited of [
 "chrome.cookies", "chrome.debugger", "chrome.webRequest",
 "fetch(", "XMLHttpRequest", "chrome.tabs.create("
]) assert(!popup.includes(prohibited),"Extension cannot access cookies/debugging/private network");

assert.equal(C.username("@Real.User"),"real.user");
assert.equal(C.profileFromUrl("https://www.instagram.com/hello.world/"),"hello.world");
for(const bad of ["accounts","reels","auth_platform","../wrong","https://evil.test/victim",""])
 assert.equal(C.username(bad),"","Rejected unsafe Instagram username "+bad);
assert.equal(C.profileFromUrl("https://www.instagram.com/accounts/login/"),"");
assert.equal(C.profileFromUrl("https://www.instagram.com/real.user/following/"),"");
assert.deepEqual(C.parseCount("1,234"),{count:"1234",approximate:false});
assert.deepEqual(C.parseCount("12.5K"),{count:"12500",approximate:true});
assert.deepEqual(C.parseCount("1,2 mil"),{count:"1200",approximate:true});
assert.deepEqual(C.parseCount("1.234.567"),{count:"1234567",approximate:false});
assert.equal(C.parseCount("text"),null);
assert.equal(C.parseCount("unknown"),null);
const oldRows={
  "two.user":{username:"two.user",followers:"22",following:"35",
    checked_at:"2026-04-01T00:00:00Z",status:"ok"},
  "one.user":{username:"one.user",followers:"11",following:"15",
    checked_at:"2025-01-01T00:00:00Z",status:"ok"},
  "incomplete":{username:"incomplete",status:"unavailable"}
};
assert.deepEqual(C.firstPassQueue(["two.user","missing","incomplete","one.user"],oldRows),
 ["missing","incomplete"],"Never measured before incomplete; complete records skipped");
assert.deepEqual(C.oldestFirst(["two.user","one.user","missing","incomplete"],oldRows),
 ["one.user","two.user"],"Second audit starts from the oldest last measurement");
const historyRows={};const latest={};
const a={...oldRows["one.user"]},newer={...a,followers:"17",following:"18",
 checked_at:"2026-10-15T09:00:00Z"};
C.appendMeasurement(latest,historyRows,a);
const changes=C.appendMeasurement(latest,historyRows,newer);
assert.equal(changes.followers_delta,6);
assert.equal(changes.following_delta,3);
assert.equal(latest["one.user"].followers,"17");
assert.equal(historyRows["one.user"].length,2);
assert.equal(C.historyCsv(historyRows,["one.user"]).split("\r\n").length,4,
 "Dated export must contain both original and subsequent count snapshots");
assert.deepEqual(C.importQueue('username,profile_url\r\n"a.user","https://instagram.com/a.user/"\r\n"b.user",\r\na.user,\r\n'),
 ["a.user","b.user"]);
assert.throws(()=>C.importQueue("profile_url\nhttps://instagram.com/x/"),/username/);
assert.throws(()=>C.importQueue('username\n"unclosed'),/Unclosed/);
const mkNode=(text,href)=>{
 const node={textContent:text,innerText:text,
   getAttribute:k=>k==="href"?href:k==="aria-label"?"":null,
   querySelectorAll:s=>s==="[title]"?[]:[]};
 return node;
};
const doc=(followers,following)=>({
 querySelector:sel=>sel==="header"?{
   querySelectorAll:q=>q==="a[href], a[role=\"link\"]"?[
     mkNode(followers,"/real.user/followers/"),
     mkNode(following,"/real.user/following/")
   ]:[]
 }:null
});
const extracted=C.extractVisibleProfile(doc("1,256 followers","1.2K following"),
 "https://www.instagram.com/real.user/");
assert.equal(extracted.username,"real.user");
assert.equal(extracted.followers,"1256");
assert.equal(extracted.following,"1200");
assert.equal(extracted.approximate,"true");
assert.equal(extracted.status,"ok");
assert.equal(C.extractVisibleProfile(doc("Loading","? following"),
 "https://www.instagram.com/real.user/").status,undefined,
 "Never invent a missing Instagram counter");
assert.match(C.extractVisibleProfile(doc("100 followers","50 following"),
 "https://www.instagram.com/accounts/login/").error,/profile page/);
assert.match(C.exportCsv({"real.user":extracted},["real.user"]),
 /real\.user,1256,1200,.*instagram_visible_profile_extension,ok,true/);
assert.equal(C.exportCsv({"real.user":extracted},["other.user"]).split("\r\n").length,2,
 "Unknown usernames should not add rows");

(async () => {
 const elements={};
 for(const id of ["workspace","queueFile","next","capture","export","historyExport","reAudit","clear",
  "queueSize","savedSize","remainingSize","roundRemaining","mode","status","current"]) {
   elements[id]={value:"",textContent:"",disabled:false,className:"",files:[],
      handlers:{},addEventListener(kind,fn){this.handlers[kind]=fn;}};
 }
 elements.workspace.value="owner.one";
 const persistent=new Map([["igc_chrome_last_workspace_v1","owner.one"]]);
 const history={navigations:[],injections:[],downloads:[]};
 let activeTab={id:12,url:"https://www.instagram.com/real.user/"};
 let result={...extracted};
 const chrome={
  storage:{local:{
   async get(keys){const reply={};for(const k of keys)reply[k]=persistent.get(k);return reply;},
   async set(obj){for(const [k,v] of Object.entries(obj))persistent.set(k,v);}
  }},
  tabs:{async query(){return [activeTab];},async update(id,info){
    assert.equal(id,12);history.navigations.push(info.url);activeTab.url=info.url;return activeTab;
  }},
  scripting:{async executeScript(opts){history.injections.push(opts);
    return opts.files?[{result:null}]:[{result}];}},
  downloads:{async download(input){history.downloads.push(input);return 1;}}
 };
 const document={readyState:"loading",getElementById:id=>elements[id],
   addEventListener(event,fn){this.readyFn=fn;}};
 const browser={window:{confirm:()=>true},chrome,document,IGC_CAPTURE:C,
   URL:{createObjectURL:()=>"blob:local",revokeObjectURL(){}},
   Blob:class {constructor(contents){this.parts=contents}},
   setTimeout:()=>{},Date,Number,Math,JSON,Array,Set,Map,
   String,Error,encodeURIComponent,globalThis:null};
 browser.globalThis=browser;
 vm.createContext(browser);
 vm.runInContext(popup,browser);
 document.readyFn();
 // The Chrome popup restores its prior workspace asynchronously. Allow
 // storage.get, storage.set and render to settle before simulating a click.
 await new Promise(resolve => setImmediate(resolve));
 assert.equal(history.navigations.length,0,"No autonomous Chrome navigation after loading popup");
 elements.queueFile.files=[{text:async()=>"username\nreal.user\nsecond.user\nreal.user\n"}];
 await elements.queueFile.handlers.change();
 assert.equal(elements.queueSize.textContent,"2");
 await elements.next.handlers.click();
 assert.deepEqual(history.navigations,["https://www.instagram.com/real.user/"]);
 assert.equal(history.injections.length,0,"Opening profile must never scrape before human confirmation");
 activeTab.url="https://www.instagram.com/real.user/";
 await elements.capture.handlers.click();
 assert.equal(elements.savedSize.textContent,"1");
 assert.equal(elements.remainingSize.textContent,"1");
 assert.equal(elements.reAudit.disabled,true,
  "Second audit is unavailable until all missing profiles are measured");
 assert.equal(history.injections.length,2);
 assert.equal(history.injections[0].target.tabId,12);
 assert.equal(history.injections[0].files[0],"collector.js");
 const scoped="igc_chrome_counts_v1__owner.one";
 assert.equal(persistent.get(scoped).records["real.user"].followers,"1256");
 await elements.export.handlers.click();
 assert.equal(history.downloads.length,1);
 assert.match(history.downloads[0].filename,/owner.one/);
 // Completing the first pass unlocks one deliberately started oldest-first
 // cycle; re-audits retain every historical record.
 activeTab.url="https://www.instagram.com/second.user/";
 result={...extracted,username:"second.user",followers:"100",
  following:"70",checked_at:"2025-10-01T12:00:00.000Z"};
 await elements.capture.handlers.click();
 assert.equal(elements.savedSize.textContent,"2");
 assert.equal(elements.remainingSize.textContent,"0");
 assert.equal(elements.reAudit.disabled,false);
 await elements.reAudit.handlers.click();
 assert.match(elements.mode.textContent,/Re-audit/);
 assert.equal(elements.roundRemaining.textContent,"2");
 await elements.next.handlers.click();
 assert.equal(history.navigations.at(-1),"https://www.instagram.com/second.user/",
  "The second audit starts with the oldest measured profile");
 activeTab.url="https://www.instagram.com/second.user/";
 result={...result,followers:"104",following:"73",
  checked_at:"2026-10-15T12:00:00.000Z"};
 await elements.capture.handlers.click();
 assert.equal(elements.roundRemaining.textContent,"1");
 assert.equal(elements.reAudit.disabled,true);
 assert.match(elements.status.textContent,/followers \+4/);
 await elements.next.handlers.click();
 assert.equal(history.navigations.at(-1),"https://www.instagram.com/real.user/",
  "The same profile must not be revisited twice in one audit cycle");
 await elements.historyExport.handlers.click();
 assert.equal(history.downloads.length,2);
 assert.match(history.downloads[1].filename,/History-owner.one/);
 const savedHistory=persistent.get("igc_chrome_counts_v1__owner.one");
 assert.equal(savedHistory.history["second.user"].length,2);
 assert.equal(savedHistory.history["second.user"][0].followers,"100");
 assert.equal(savedHistory.history["second.user"][1].followers,"104");
 activeTab.url="https://www.instagram.com/accounts/login/";
 await elements.capture.handlers.click();
 assert.match(elements.status.textContent,/profile/);
 assert.equal(elements.savedSize.textContent,"2","Failed capture cannot replace records");
 // A different workspace must not inherit imported queues or results.
 elements.workspace.value="owner.two";
 await elements.workspace.handlers.change();
 assert.equal(elements.savedSize.textContent,"0");
 assert.equal(elements.queueSize.textContent,"0");
 elements.workspace.value="owner.one";
 await elements.workspace.handlers.change();
 assert.equal(elements.savedSize.textContent,"2");
 assert.equal(elements.roundRemaining.textContent,"1",
  "Re-audit cycle progress must survive popup reopening and workspace selection");
 await elements.clear.handlers.click();
 assert.equal(elements.savedSize.textContent,"0");
 assert.equal(persistent.get(scoped).records["real.user"],undefined);
 console.log("Chrome Companion: read-only collection, explicit navigation, CSV and workspace isolation PASS");
})().catch(e=>{console.error(e);process.exitCode=1});
