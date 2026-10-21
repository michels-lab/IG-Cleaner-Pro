'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const match=html.match(/<script id="igc-automations-plan">([\s\S]*?)<\/script>/);
assert(match,'Autonomous issue summary script must be available');
const elements={};const storage=new Map(),calls=[];
function element(tag="div"){return {tag,children:[],textContent:"",value:"",style:{},disabled:false,
 appendChild(x){this.children.push(x)},replaceChildren(){this.children=[]},
 addEventListener(name,fn){if(name==="click")this.click=fn}}}
for(const id of ["igcAutoRows","igcAutoMetrics","igcAutoExecutionMetrics",
 "igcAutoIssueRows","igcAutoIssueTotal","igcAutoIssueStatus","igcAutoLiveStatus","igcAutoStatus",
 "igcAutoPause","igcAutoResume","igcAutoProgress","igcAutoIssueTask",
 "igcAutoIssueFilter","igcAutoIssueSearch","igcAutoSearch","igcAutoBatch","igcAutoRest","igcAutoGap"]){
 elements[id]=element(id);
}
elements.igcAutoIssueTask.value="unfollow";
elements.igcAutoIssueFilter.value="pending";
elements.igcAutoBatch.value="30";elements.igcAutoRest.value="5";elements.igcAutoGap.value="10";
const profile={owner:"owner-A",active:"ig-A",accounts:[{account_key:"ig-A",username:"my.profile"}]};
const issues=[{username:"mutual.after",status:"ok",issue:"unexpected_followback",message:"Follow Back visible",at:"2026-10-12"},
 {username:"no.info",status:"review",issue:"missing_profile_info",message:"No se encontró botón",at:"2026-10-12"}];
const reply={owner:"owner-A",account:"ig-A",task:"unfollow",status:"partial",total:3,
 successful:2,remaining:1,errors:1,protected:0,skipped:0,issue_count:2,issues,
 rows:issues,running:false,message:"Tanda revisada"};
const localStorage={getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)};
const ctx={window:{IGC_INSTAGRAM_PROFILES:profile,
 location:{hash:"#igc-robot=33333.0123456789abcdefghijabcdefgh"},
 showPage(){},confirm:()=>true},
 document:{hidden:false,getElementById:id=>elements[id]||null,createElement:element},
 localStorage,followingRaw:[],followersRaw:[],followersMap:new Map(),pendingRequestsRaw:[],
 protectedSet:new Set(),saveSet(){},LS_PROT:"test-protected",Set,Map,JSON,Math,Number,String,Date,encodeURIComponent,
 fetch:async(url,options)=>{
   calls.push(url);
   assert.equal(options.headers["X-IGC-Bridge-Token"],"0123456789abcdefghijabcdefgh");
   return {ok:true,json:async()=>reply}
 },setInterval(){}};
vm.createContext(ctx);vm.runInContext(match[1],ctx);
(async()=>{
 await ctx.window.igcAutoPoll();
 assert.equal(elements.igcAutoIssueRows.children.length,2);
 const first=elements.igcAutoIssueRows.children[0];
 assert.equal(first.children[0].children[0].href,"https://www.instagram.com/mutual.after/");
 assert.equal(first.children[2].children[0].textContent,"↗ Open profile");
 assert.notEqual(first.children[2].children[0].target,"_blank",
  "Integrated app must not open a separate logged-out browser");
 await first.children[2].children[0].click();
 assert(calls.some(url=>url.endsWith("/api/actions/open-profile")),
  "Open profile must use token-authenticated robot Chrome");
 assert.match(first.children[1].children[0].textContent,/Follow Back/);
 first.children[2].children[2].click(); // mark reviewed
 assert.equal(elements.igcAutoIssueRows.children.length,1,"Reviewed item is hidden from pending filter");
 elements.igcAutoIssueFilter.value="reviewed";ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,1);
 elements.igcAutoIssueFilter.value="all";ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,2);
 elements.igcAutoIssueFilter.value="unexpected_followback";ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,1);
 elements.igcAutoIssueFilter.value="all";ctx.window.igcAutoRenderIssues();
 // Another Instagram does not inherit saved exceptions or review decisions.
 profile.active="ig-B";
 ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,1,"Other account should show empty-state only");
 assert.match(elements.igcAutoIssueStatus.textContent,/No results yet/);
 profile.active="ig-A";
 ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,2,"Return to account restores saved result cache");
 assert.match(elements.igcAutoIssueTotal.textContent,/1 need manual review/);
 issues.push({username:"interrupted.after.crash",status:"review",
  issue:"interrupted_action_uncertain",safe_no_click:false,
  message:"Result unknown after a durable pre-click intent",
  click_phase:"unfollow_menu",at:"2026-10-21"});
 await ctx.window.igcAutoPoll();
 elements.igcAutoIssueFilter.value="interrupted_action_uncertain";
 ctx.window.igcAutoRenderIssues();
 assert.equal(elements.igcAutoIssueRows.children.length,1,
  "Interrupted click must have a dedicated filter, not be confused with harmless no-click failures");
 const interrupted=elements.igcAutoIssueRows.children[0];
 assert.match(interrupted.children[1].children[0].textContent,/never auto-retry/);
 assert.match(interrupted.children[1].children[1].textContent,/Last armed click phase: unfollow menu/);
 assert.match(interrupted.children[1].children[2].textContent,/No automatic retry/);
 console.log("Automations issue summaries, filters, profile navigation, reviewed state, interrupted-click diagnosis and account isolation: PASS");
})().catch(e=>{console.error(e);process.exitCode=1});
