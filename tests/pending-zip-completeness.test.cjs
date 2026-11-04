"use strict";
/* GRANADA: reproduce real Pending ZIP omissions and repeated Focus cohorts.
 * Synthetic Instagram exports only. No live account, network or mutation. */
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
function section(start,end){
 const a=html.indexOf(start),b=html.indexOf(end,a+start.length);
 assert(a>=0&&b>a,start+" must remain executable in the distributable HTML");
 return html.slice(a,b);
}
const nodes=new Map(),messages=[],saved=[];
function element(id){if(!nodes.has(id))nodes.set(id,{innerHTML:"",textContent:"",value:"",dataset:{},title:"",style:{}});return nodes.get(id)}
const ctx={console,URL,Date,Math,JSON,Map,Set,Array,Object,String,Number,
 window:null,document:{getElementById:element},
 pendingRequestsRaw:[],pendingOpenedSet:new Set(),pendingReviewedMeta:{},pendingSnoozeMap:{},
 diagData:[],q:element,basename:p=>String(p).split("/").pop(),
 msg:m=>messages.push(m),logAction:()=>{},savePendingRequests:()=>saved.push(ctx.pendingRequestsRaw.map(x=>x.username)),
 renderPendingSessionPanel:()=>{},renderPendingRealtimePanel:()=>{},renderActiveBatchDock:()=>{},
 pendingCrossStatus:()=>({inFollowing:false}),pendingCrossBadge:()=>"—",
 formatDateFromTs:()=>"—",pendingAgeDays:()=>10,esc:s=>String(s),
 isInActiveFocus:row=>row.username==="request0003",
 pendingOldestFirstSort:(a,b)=>(a.timestamp||0)-(b.timestamp||0),
 activeBatchRowResolved:()=>false,
 pendingNoOpenReason:()=>"",renderPendingRequests:()=>{}, 
};
ctx.window=ctx;
ctx.decodeText=v=>String(v||"");
ctx.pendingRows=()=>ctx.pendingRequestsRaw.map(x=>({...x,reviewed:!!x.reviewed,
 opened:!!x.opened||ctx.pendingOpenedSet.has(x.username),
 snoozed:!!x.snoozed,riskLevel:"bajo",riskScore:0,riskReasons:[]}));
ctx.pendingFilteredRows=()=>ctx.pendingRows();
ctx.igcDiagEntry=()=>({type:"pending"});
vm.createContext(ctx);
vm.runInContext(
 section("function cleanUsername(value){","function extractFromJSON(data,source)")+
 section("function pendingLabelMap(item){","async function processPendingFiles()")+
 section("function parseHTMLUsers(payload,source){","function parseJSONUsers(payload,source){")+
 section("function isPendingOpenableForFocus(row){","function isMutualOpenableForFocus(row){")+
 section("function pendingCandidateRows(){","function openFocusRows(rows,label")+
 section("function focusBatchFill(primaryRows, fallbackRows, n, kind){","function followersMutualAnyFocusCandidates(){")+
 section("let pendingTableLimit=300;","function pendingOldestFirstSort(a,b){")+
 section("async function parseZipPending(items,zipName=''){","async function parseZipExtras(groups){")+
 section("function openConfirmedFocusRows(rows,label,kind,requestedCount=null,opts={}){","</script>"),ctx,{timeout:4000});

// Official fixture is string_list_data, NOT label_values.
const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,
 "fixtures/instagram-export-sample/connections/followers_and_following/pending_follow_requests.json"),"utf8"));
const small=ctx.extractPendingRequestsFromJSON(fixture,"pending_follow_requests.json");
assert.deepEqual(Array.from(small,x=>x.username),["pending_two","pending_one"]);
assert.equal(small[0].timestamp,1700000202);
assert.equal(small[1].href,"https://www.instagram.com/pending_one/");
// Stress: >300 distinct requests, duplicate casing, no accidental title/metadata.
const requests=Array.from({length:725},(_,i)=>({
 title:"request"+String(i).padStart(4,"0"),string_list_data:[{
 value:"request"+String(i).padStart(4,"0"),
 href:"https://www.instagram.com/_u/request"+String(i).padStart(4,"0"),
 timestamp:1700000000+i
 }]
}));
requests.push({title:"REQUEST0000",string_list_data:[{value:"REQUEST0000",timestamp:1700000900}]});
requests.push({title:"My Requests",string_list_data:[{value:"invalid/username",href:"https://not-instagram.example/u/invalid"}]});
const payload={relationships_follow_requests_sent:requests};
const parsed=ctx.extractPendingRequestsFromJSON(payload,"pending_follow_requests.json");
assert.equal(parsed.length,725,"Every valid unique sent request must survive; duplicate not counted twice");
assert.equal(parsed.find(x=>x.username==="request0000").timestamp,1700000900);
assert(!parsed.some(x=>x.username==="my requests"));
const labelPayload={relationships_follow_requests_sent:[{
 label_values:[{label:"Username",value:"label.one"},{label:"URL",value:"https://www.instagram.com/label.one/"}],
 timestamp:1700000888
}]};
assert.equal(ctx.extractPendingRequestsFromJSON(labelPayload,"pending_follow_requests.json")[0].username,"label.one",
 "Legacy label_values remains backward compatible");

// HTML exports can have plain profile anchors, rather than <td> Username.
// Preserve strict category isolation: recent requests are NOT Pending requests.
ctx.directCards=doc=>doc.cards||[];
ctx.profileAnchor=card=>card.anchor||null;
ctx.tableFields=card=>card.fields||{};
ctx.dateTextFromCard=()=>"";ctx.dedupe=list=>Array.from(new Map(list.map(x=>[x.username,x])).values());
const anchor=url=>({getAttribute:()=>url,parentElement:null});
const htmlDoc={cards:[],main:{querySelectorAll:()=>[
 anchor("https://www.instagram.com/_u/html.pending.one"),
 anchor("https://evil.example/instagram.com/not_a_pending")
]},querySelector:selector=>selector==="main"?htmlDoc.main:null};
assert.deepEqual(Array.from(ctx.parseHTMLUsers(
 {category:"pending_follow_requests",doc:htmlDoc},"pending_follow_requests.html"),
 x=>x.username),["html.pending.one"]);
assert.equal(ctx.parseHTMLUsers(
 {category:"recent_follow_requests",doc:htmlDoc},"recent_follow_requests.html").length,0);
const htmlTable={cards:[{fields:{username:"html.table",name:"Pending"}}],
 querySelector:()=>null,body:{querySelectorAll:()=>[]}};
assert.equal(ctx.parseHTMLUsers(
 {category:"pending_follow_requests",doc:htmlTable},"pending_follow_requests.html")[0].username,"html.table");

// This is the real ZIP-to-Pending function with the parser directly connected.
ctx.igcParseDetected=(detected,text,source)=>ctx.extractPendingRequestsFromJSON(detected.data,source);
ctx.pendingRequestsRaw=[{username:"old.saved",timestamp:1}];
(async()=>{
 const imported=await ctx.parseZipPending([{
  entry:{name:"connections/followers_and_following/pending_follow_requests.json"},
  file:{name:"pending_follow_requests.json",size:180000},payload:{format:"json",category:"pending_follow_requests",data:payload},
  text:JSON.stringify(payload)
 }],"export.zip");
 assert.equal(imported,725);
 assert.equal(ctx.pendingRequestsRaw.length,725,"ZIP import must use all native string_list_data rows");
 assert(!ctx.pendingRequestsRaw.some(x=>x.username==="old.saved"),"New verified ZIP replaces old imported snapshot");
 assert.match(element("pendingFilesLabel").textContent,/725 usuarios únicos de 727 registros fuente/);
 assert.equal(saved.at(-1).length,725);

 // Unreviewed opened rows remain visible but are excluded from fresh Focus.
 ctx.pendingRequestsRaw[0].opened=true;
 ctx.pendingRequestsRaw[1].reviewed=true;
 ctx.pendingRequestsRaw[2].snoozed=true;
 assert.equal(ctx.isPendingOpenableForFocus(ctx.pendingRows()[0]),false);
 const eligible=ctx.pendingCandidateRows();
 assert.equal(eligible.length,721);
 const excluded=new Set([...ctx.pendingRequestsRaw.slice(0,3).map(x=>x.username),"request0003"]);
 assert(!eligible.some(x=>excluded.has(x.username)),
   "Focus must exclude exactly those marked opened, reviewed, snoozed or active, regardless of timestamp sorting");
 const fallback=ctx.focusBatchFill([],ctx.pendingRows(),20,"pending");
 assert.equal(fallback.length,20,"Existing untouched requests refill Focus 20");
 assert(!fallback.some(x=>x.opened||x.reviewed||x.snoozed||x.username==="request0003"),
   "Fallback never reintroduces opened, reviewed or active Pending profiles");

 // Opening a Pending Focus saves an open ATTEMPT before Chrome without
 // inventing a completed review, cancellation or window.open success.
 const beforeReview=Object.keys(ctx.pendingReviewedMeta).length;
 const selected=eligible.slice(0,2).map(x=>x.username);
 const recorded=[];
 ctx.igcConfirmBatchQuality=()=>true;
 ctx.setActiveFocusBatch=(kind,rows)=>{ctx.activeFocusBatch={kind,rows}};
 ctx.savePendingOpened=()=>recorded.push([...ctx.pendingOpenedSet]);
 ctx.showSafeFocusPopup=()=>{};
 ctx.forceLiveRefresh=()=>{};
 ctx.open=()=>null; // Chrome blocked popup, no confirmed browser opening.
 assert.equal(ctx.openConfirmedFocusRows(eligible.slice(0,2),"Pending · Foco 2","pending",2,{exact:true}),true);
 assert(selected.every(u=>ctx.pendingOpenedSet.has(u)));
 assert.equal(Object.keys(ctx.pendingReviewedMeta).length,beforeReview,
   "Opening a tab must NEVER invent a reviewed or cancelled request");
 assert.equal(recorded.length,1,"Open attempts must persist even when Chrome blocks popups");
 assert(selected.every(u=>!ctx.pendingCandidateRows().some(r=>r.username===u)),
   "A blocked popup must not recycle a previously attempted Pending profile");

 // All rows are stored. Display starts at 300 and gives access to 301..725.
 ctx.pendingRequestsRaw.forEach(x=>{x.opened=false;x.reviewed=false;x.snoozed=false});
 ctx.renderPendingRequests();
 assert.equal((element("pendingTableBody").innerHTML.match(/<tr\b/g)||[]).length,300);
 assert.match(element("pendingTablePager").innerHTML,/300 de 725/);
 ctx.pendingShowMore();
 assert.equal((element("pendingTableBody").innerHTML.match(/<tr\b/g)||[]).length,600);
 ctx.pendingShowMore();
 assert.equal((element("pendingTableBody").innerHTML.match(/<tr\b/g)||[]).length,725);
 assert.match(element("pendingTablePager").innerHTML,/725 de 725/);
 assert.match(element("pendingStats").innerHTML,/725<\/b><span>visibles de 725 filtrados/);

 // Nonempty sent requests with zero extractable identities must NOT wipe history.
 const original=ctx.pendingRequestsRaw.map(x=>x.username);
 await assert.rejects(
  ()=>ctx.parseZipPending([{entry:{name:"pending_follow_requests.json"},
    file:{size:100},payload:{format:"json",data:{relationships_follow_requests_sent:[
     {title:"unparseable!",string_list_data:[{value:"bad/name"}]}
    ]}},text:"{}"}],"bad.zip"),/Se conservaron los Pending anteriores/);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
 // A partial export without pending_follow_requests must retain saved prior ZIP
 // rather than silently rendering 0 or claiming an empty outgoing request list.
 const savedBefore=saved.length;
 assert.equal(await ctx.parseZipPending([],"following-only.zip"),0);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
 assert.equal(saved.length,savedBefore,"No Pending source must not overwrite storage");
 assert.match(element("pendingFilesLabel").textContent,/no incluye solicitudes enviadas/);
 assert.match(element("pendingFilesLabel").textContent,/725 Pending anteriores conservados/);
 // Malformed canonical source is NOT a verified empty list.
 await assert.rejects(()=>ctx.parseZipPending([{
  entry:{name:"pending_follow_requests.json"},file:{size:50},
  payload:{format:"invalid-json",error:"bad syntax"},text:"{broken"
 }],"bad-json.zip"),/Se conservaron los Pending anteriores/);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
 // A well-formed native JSON declaring an explicitly EMPTY array is the
 // only evidence that replacing a prior Pending snapshot with zero is valid.
 assert.equal(await ctx.parseZipPending([{
  entry:{name:"pending_follow_requests.json"},file:{size:51},
  payload:{format:"json",category:"pending_follow_requests",
    data:{relationships_follow_requests_sent:[]}},text:'{"relationships_follow_requests_sent":[]}'
 }],"verified-empty.zip"),0);
 assert.equal(ctx.pendingRequestsRaw.length,0);
 assert.match(element("pendingFilesLabel").textContent,/explícitamente vacía/);
 console.log("PASS: native Pending JSON (725 rows), ZIP import, legacy labels, no-repeat Focus, 300+ pagination, non-destructive malformed ZIP");
})().catch(e=>{console.error(e);process.exitCode=1});
