"use strict";
// Owner regression: 9,896 cloud review records do NOT mean 9,896 currently
// reviewed Following users. Historical records span modules and ZIP vintages.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const first=html.indexOf("function renderReviewRealtimePanel(){");
const last=html.indexOf("function renderPendingRealtimePanel(){",first);
assert(first>=0&&last>first,"Missing actual Review dashboard renderer");
const renderer=html.slice(first,last);
const row=(username,followsBack=false)=>({username,followsBack,relationGood:followsBack});
const rows=[row("confirmed"),row("fresh"),row("confirmedmutual",true),row("freshmutual",true),row("protected"),row("paused")];
const done=new Set(["confirmed","confirmedmutual"]),protectedSet=new Set(["protected"]);
const host={innerHTML:""};
const ctx={
 console,Set,protectedSet,activeFocusBatch:null,
 ensureReviewStandardSidebar:()=>host,
 withTempMode:(_mode,fn)=>fn(),
 buildRowsForMode:()=>rows,
 isDoneValidForMode:r=>done.has(r.username),
 isSnoozed:r=>r.username==="paused",
 allMainFocusOpenableRows:()=>rows.filter(r=>!r.followsBack&&!done.has(r.username)&&!protectedSet.has(r.username)&&r.username!=="paused"),
 igcStandardActivityTop:()=>"",
 igcSidebarStats:values=>values.map(v=>v.label+":"+v.value).join(" | "),
 igcSidebarActiveBatch:()=>""
};
vm.createContext(ctx);vm.runInContext(renderer,ctx);
ctx.renderReviewRealtimePanel();
for(const expected of [
  "revisados vigentes:2","por revisar en Following:2",
  "protegidos:1","abribles:1","no me siguen:4"
])assert(host.innerHTML.includes(expected),"Missing authoritative current-count label "+expected);
assert(!host.innerHTML.includes("9896"),"Current Review may never invent a historical cloud count");
assert(html.includes("Historial de revisiones (todas las secciones)"),"Cloud summary must explicitly be historical");
assert(html.includes("Historial de nube:"),"Sync completion must explain history separately");
assert(html.includes("revisiones vigentes en Following"),"Actual current Following review total must be visible");
assert(html.includes("espacio(s) de Instagram registrados"),"The count of workspaces must not look like follower profiles");
console.log("PASS: current Review, cloud history and workspace counts have separate truthful meanings");
