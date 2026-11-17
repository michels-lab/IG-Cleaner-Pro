"use strict";
/* GRANADA regression: a full backup must include per-account Pending Double
 * Check visit attempts, and restoring older data must never rewind the ledger.
 * No browser, account login, network or actual Instagram actions are used. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function section(from,to){
 const a=html.indexOf(from),b=html.indexOf(to,a+from.length);
 assert(a>=0&&b>a,"Missing source span "+from);return html.slice(a,b);
}
const rawStore=new Map(),notices=[];let savedBackup=null,renderedPending=0;
const ctx={
 console,Set,Map,Array,Object,Number,String,Date,Math,JSON,
 IGС_PENDING_DOUBLE_TEST_ONLY:true,
 IGC_INSTAGRAM_PROFILES:{active:"ig_account_a",accounts:[
   {account_key:"ig_account_a",username:"firstaccount"},
   {account_key:"ig_account_b",username:"secondaccount"}]},
 localStorage:{
   getItem(key){return rawStore.get(ctx.IGC_INSTAGRAM_PROFILES.active+"::"+key)||null},
   setItem(key,v){rawStore.set(ctx.IGC_INSTAGRAM_PROFILES.active+"::"+key,String(v))},
   removeItem(key){rawStore.delete(ctx.IGC_INSTAGRAM_PROFILES.active+"::"+key)}
 },
 cleanUsername:u=>/^[a-z0-9._]+$/.test(String(u||"").toLowerCase())?String(u).toLowerCase():"",
 protectedSet:new Set(["protected.one"]),doneSet:new Set(["reviewed.one"]),
 reviewedMeta:{"reviewed.one":{reviewedAt:101}},actionLog:[],snoozeMap:{},
 dailyGoal:30,pendingRequestsRaw:[],pendingOpenedSet:new Set(["pending.one"]),
 pendingReviewedMeta:{"pending.one":{reviewedAt:101,decision:"still_pending",
    previousReviews:[{reviewedAt:80,decision:"reviewed"}]}},
 pendingSnoozeMap:{},activeFocusBatch:null,profileHistory:{},
 guidedSession100:null,internalSnapshot:null,
 currentMode:"following",pageSize:100,
 document:{getElementById:()=>({value:"all",checked:false})},
 msg:(message,level)=>notices.push({message,level}),
 getMediumThreshold:()=>40,getHighThreshold:()=>75,
 downloadFile:(filename,bytes,kind)=>{savedBackup=JSON.parse(bytes)},
 saveActionLog:()=>{},saveSnoozeMap:()=>{},savePendingRequests:()=>{},
 savePendingOpened:()=>{},savePendingReviewedMeta:()=>{},
 savePendingSnoozeMap:()=>{},saveActiveFocusBatch:()=>{},
 saveProfileHistory:()=>{},saveGuidedSession100:()=>{},saveConfig:()=>{},
 saveSet:()=>{},buildRows:()=>{},applyFilters:()=>{},
 renderBackupStats:()=>{},renderActionLog:()=>{},
 renderPendingRequests:()=>{renderedPending++},
 logAction:()=>{},LS_DAILY_GOAL:"daily_goal",LS_INTERNAL_SNAPSHOT:"snapshot",
 LS_PROT:"prot",LS_DONE:"done",LS_REVIEW_META:"review_meta",
};
ctx.window=ctx;
ctx.FileReader=class{readAsText(file){this.result=file.text;this.onload()}};
vm.createContext(ctx);
vm.runInContext(section("const IGC_PENDING_DOUBLE_SEEN=","function igcPendingDoubleRenderStatus(){"),ctx);
vm.runInContext(section("function exportFullBackup(){","function renderBackupStats(){"),ctx);
const importObj=data=>ctx.importFullBackup({files:[{text:JSON.stringify(data)}],value:"file"});
// 45 imported Pending requests; two separate verification cohorts 30 + 15.
ctx.igcPendingDoubleSaveSeen(new Set(Array.from({length:30},(_,i)=>"pending."+i)));
ctx.exportFullBackup();
assert.equal(savedBackup.instagramAccountKey,"ig_account_a");
assert.equal(savedBackup.pendingDoubleCheckSeen.length,30);
assert.equal(savedBackup.pendingReviewedMeta["pending.one"].previousReviews.length,1,
 "Historical decisions must still be in the full backup");
const oldBackup=structuredClone(savedBackup);
const new15=Array.from({length:15},(_,i)=>"pending."+(i+30));
ctx.igcPendingDoubleSaveSeen(new Set(new15));
importObj(oldBackup);
assert.equal(ctx.igcPendingDoubleSeen().size,45,
 "Restoring previous backup must UNION with newer attempted visits, never rewind");
assert(ctx.igcPendingDoubleSeen().has("pending.44"));
assert(ctx.igcPendingDoubleSeen().has("pending.0"));
importObj(oldBackup);
assert.equal(ctx.igcPendingDoubleSeen().size,45,"Repeated imports must be idempotent");
assert(renderedPending>=2,"New cycle counters must refresh after import");
// Older backup has no Double Check key; retain current progress untouched.
const legacy={...oldBackup};delete legacy.pendingDoubleCheckSeen;
importObj(legacy);
assert.equal(ctx.igcPendingDoubleSeen().size,45);
// Malformed payloads may not overwrite the legitimate set.
const malformed={...oldBackup,pendingDoubleCheckSeen:"everything"};
importObj(malformed);
assert.equal(ctx.igcPendingDoubleSeen().size,45);
// Cross-account backup MUST be rejected, even when it includes valid mark names.
ctx.IGC_INSTAGRAM_PROFILES.active="ig_account_b";
ctx.igcPendingDoubleSaveSeen(new Set(["another.1"]));
const beforeB=[...ctx.igcPendingDoubleSeen()];
importObj(oldBackup);
assert.deepEqual([...ctx.igcPendingDoubleSeen()],beforeB);
assert(notices.some(x=>x.level==="e"&&x.message.includes("otro Instagram")));
ctx.IGC_INSTAGRAM_PROFILES.active="ig_account_a";
assert.equal(ctx.igcPendingDoubleSeen().size,45);
assert.equal(ctx.pendingReviewedMeta["pending.one"].decision,"still_pending");
assert.equal(ctx.pendingReviewedMeta["pending.one"].previousReviews.length,1);
assert.match(html,/localStorage\.removeItem\(IGC_PENDING_DOUBLE_SEEN\);\s*igcPendingDoubleSelected\.clear\(\);\s*applyFilters\(\)/,
 "Explicit user-confirmed clear-all must also clear the independent review cycle");
console.log("PASS: Pending Double Check full backup 45 marks, monotonic same-account restore, old/malformed backups and cross-account isolation");
