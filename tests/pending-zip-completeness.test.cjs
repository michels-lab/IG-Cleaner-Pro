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
 section("async function processPendingFiles(){","function pendingAgeDays(row){")+
 section("function zipImportScope(){","async function applyZipCore(")+
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
// Extraction may identify valid rows even from a partially corrupted source;
// import must reject that source rather than publish the incomplete subset.
const completePayload={relationships_follow_requests_sent:requests.slice(0,-1)};
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
// Mixed relationship JSON MUST NOT promote recent/blocked/following into outgoing
// requests, even when those sections contain perfectly valid usernames.
const mixed={relationships_follow_requests_sent:[requests[0]],
 recent_follow_requests:[{string_list_data:[{value:"not.pending.user"}]}],
 blocked_profiles:[{string_list_data:[{value:"also.not.pending"}]}],
 relationships_following:[{string_list_data:[{value:"already.accepted"}]}]};
assert.deepEqual(Array.from(ctx.extractPendingRequestsFromJSON(mixed,"pending_follow_requests.json"),
 x=>x.username),["request0000"],"Only sent requests count as Pending");

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
  file:{name:"pending_follow_requests.json",size:180000},payload:{format:"json",category:"pending_follow_requests",data:completePayload},
  text:JSON.stringify(completePayload)
 }],"export.zip");
 assert.equal(imported,725);
 assert.equal(ctx.pendingRequestsRaw.length,725,"ZIP import must use all native string_list_data rows");
 assert(!ctx.pendingRequestsRaw.some(x=>x.username==="old.saved"),"New verified ZIP replaces old imported snapshot");
 assert.match(element("pendingFilesLabel").textContent,/725 usuarios únicos de 726 registros fuente/);
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
 // Invalid native Pending structure used to fall back to a generic
 // parser and promote arbitrary profile metadata as outgoing requests.
 const beforeMalformedSaves=saved.length;
 const corruptSent=value=>({
   entry:{name:"connections/followers_and_following/pending_follow_requests.json"},
   file:{name:"pending_follow_requests.json",size:60},
   payload:{format:"json",category:"pending_follow_requests",
     data:{relationships_follow_requests_sent:value,
       recent_follow_requests:[{string_list_data:[{value:"not.sent"}]}]}},
   text:"{}"
 });
 for(const malformed of [null,{string_list_data:[{value:"fake.profile"}]},
                          "fake.profile",42]){
   await assert.rejects(()=>ctx.parseZipPending(
     [corruptSent(malformed)],"corrupt-canonical.zip"),
     /relationships_follow_requests_sent inválido.*Se conservaron los Pending anteriores/);
   assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
   assert.equal(saved.length,beforeMalformedSaves,
     "A fake Pending identity must never overwrite saved owner data");
 }
 // A file named pending_follow_requests can contain unrelated categories.
 // Recent, following and blocked are NOT evidence of outgoing requests.
 for(const wrongSection of [
   {recent_follow_requests:[{string_list_data:[{value:"recent.only"}]}]},
   {relationships_following:[{string_list_data:[{value:"already.followed"}]}]},
   {blocked_profiles:[{string_list_data:[{value:"blocked.only"}]}]}
 ]){
   await assert.rejects(()=>ctx.parseZipPending([{
     entry:{name:"pending_follow_requests_2.json"},
     file:{name:"pending_follow_requests_2.json",size:120},
     payload:{format:"json",category:"pending_follow_requests",data:wrongSection},
     text:JSON.stringify(wrongSection)
   }],"wrong-section.zip"),
   /otra sección de Instagram.*Se conservaron los Pending anteriores/);
   assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
   assert.equal(saved.length,beforeMalformedSaves);
 }
 // Generic profile extractors accept titles/names without sent-request
 // proof. The ZIP Pending importer must never call them as a fallback.
 let genericCalls=0;
 ctx.extractFromJSON=()=>{genericCalls++;return [{username:"metadata.only"}]};
 await assert.rejects(()=>ctx.parseZipPending([{
   entry:{name:"pending_follow_requests.json"},
   file:{name:"pending_follow_requests.json",size:70},
   payload:{format:"json",category:"pending_follow_requests",
     data:{name:"metadata.only"}},
   text:'{"name":"metadata.only"}'
 }],"metadata.zip"),/Se conservaron los Pending anteriores/);
 assert.equal(genericCalls,0);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),original);
 assert.equal(saved.length,beforeMalformedSaves);
 // Legitimate legacy root string_list_data remains supported.
 assert.equal(await ctx.parseZipPending([{
   entry:{name:"pending_follow_requests_legacy.json"},
   file:{name:"pending_follow_requests_legacy.json",size:110},
   payload:{format:"json",category:"pending_follow_requests",
     data:[{string_list_data:[{value:"legacy.sent",timestamp:1700000910}]}]},
   text:"[]"
 }],"legacy-sent.zip"),1);
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),["legacy.sent"],
   "Legacy row survives across the isolated parser's JS array realm");
 // Restore 725 verified source rows for subsequent snapshot-preservation tests.
 assert.equal(await ctx.parseZipPending([{
   entry:{name:"pending_follow_requests.json"},
   file:{name:"pending_follow_requests.json",size:180000},
   payload:{format:"json",category:"pending_follow_requests",data:completePayload},
   text:JSON.stringify(completePayload)
 }],"valid-again.zip"),725);
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
 // Manual Pending import historically erased the saved snapshot when JSON
 // was corrupt, of the wrong category, or partly missing. All file inputs
 // must validate before publishing a new list or touching existing history.
 const manualFile=(name,data)=>({name,raw:typeof data==="string"?data:JSON.stringify(data)});
 ctx.readFile=async file=>file.raw;
 ctx.document.getElementById=element;
 ctx.pendingRequestsRaw=[{username:"old.saved",timestamp:1234}];
 element("pendingInput").files=[manualFile("pending_follow_requests.json","{invalid")];
 const savedBaseline=saved.length;
 assert.equal(await ctx.processPendingFiles(),false);
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),["old.saved"]);
 assert.equal(saved.length,savedBaseline,"Corrupt file must never write empty Pending storage");
 assert.match(messages.at(-1),/Se conservaron 1 Pending anteriores/);

 element("pendingInput").files=[manualFile("recent_follow_requests.json",{
  relationships_follow_requests_received:[{title:"recent.not.pending"}]})];
 assert.equal(await ctx.processPendingFiles(),false,
  "Incoming/recent requests are not outgoing Pending");
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),["old.saved"]);

 element("pendingInput").files=[
  manualFile("pending_follow_requests.json",completePayload),
  manualFile("pending_follow_requests_2.json","{broken")
 ];
 assert.equal(await ctx.processPendingFiles(),false,
  "One corrupt chunk must reject the WHOLE multi-file Pending import");
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),["old.saved"]);
 assert.equal(saved.length,savedBaseline);

 element("pendingInternalFilter").value="reviewed";
 element("pendingRiskFilter").value="alto";
 element("pendingAgeFilter").value="90";
 element("pendingSearchBox").value="old.saved";
 element("pendingInput").files=[manualFile("pending_follow_requests.json",{
  ...completePayload,recent_follow_requests:[{string_list_data:[{value:"not.pending"}]}]})];
 assert.equal(await ctx.processPendingFiles(),true);
 assert.equal(ctx.pendingRequestsRaw.length,725);
 assert(!ctx.pendingRequestsRaw.some(r=>r.username==="not.pending"));
 assert.match(messages.at(-1),/725 usuarios únicos de 726 registros fuente/);
 assert.doesNotMatch(messages.at(-1),/sin @usuario verificable/);
 assert.equal(element("pendingInternalFilter").value,"all");
 assert.equal(element("pendingRiskFilter").value,"all");
 assert.equal(element("pendingAgeFilter").value,"0");
 assert.equal(element("pendingSearchBox").value,"");
 assert.equal(saved.at(-1).length,725);

 // One malformed record among 726 valid/duplicate entries MUST reject the
 // entire manual JSON, even though 725 handles can still be extracted. A
 // warning on a successful import would silently lose pending invitations.
 const lastComplete=ctx.pendingRequestsRaw.map(x=>x.username),beforePartial=saved.length;
 element("pendingInput").files=[manualFile("pending_follow_requests.json",payload)];
 assert.equal(await ctx.processPendingFiles(),false,
   "Partially readable native JSON must not replace a complete Pending snapshot.");
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),lastComplete);
 assert.equal(saved.length,beforePartial,"No partial Pending snapshot may be stored.");
 assert.match(messages.at(-1),/1 solicitud\(es\) enviadas sin @usuario verificable/);
 // Two valid source shards are still rejected when one has a hidden bad row.
 element("pendingInput").files=[
  manualFile("pending_follow_requests_1.json",completePayload),
  manualFile("pending_follow_requests_2.json",payload)
 ];
 assert.equal(await ctx.processPendingFiles(),false);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),lastComplete);
 assert.equal(saved.length,beforePartial);

 // An individual native record with two child identities cannot hide its
 // malformed second child merely because its first child was readable.
 const mixedNested={relationships_follow_requests_sent:[{
  string_list_data:[
   {value:"valid.inner",href:"https://www.instagram.com/valid.inner/"},
   {value:"not/a/handle",href:"https://invalid.example/not-a-profile"}
  ]
 }]};
 element("pendingInput").files=[manualFile("pending_follow_requests.json",mixedNested)];
 assert.equal(await ctx.processPendingFiles(),false);
 assert.equal(saved.length,beforePartial);

 // Explicitly empty native JSON is the ONLY verified manual zero.
 element("pendingInput").files=[manualFile("pending_follow_requests.json",{
  relationships_follow_requests_sent:[]})];
 assert.equal(await ctx.processPendingFiles(),true);
 assert.equal(ctx.pendingRequestsRaw.length,0);

 // Legacy label_values exports still import, and a filename alone cannot
 // turn an unrelated valid JSON into Pending.
 element("pendingInput").files=[manualFile("pending_follow_requests.json",labelPayload)];
 assert.equal(await ctx.processPendingFiles(),true);
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),["label.one"]);
 // The full ZIP already pins account identity. Manual Pending imports must
 // enforce the same binding after asynchronous File reads before ANY writes.
 // A user can switch Instagram accounts while a large .json/.html is loading.
 const importOwner={owner:"u_owner_42",active:"ig_first_1234567",verified:true};
 ctx.IGC_INSTAGRAM_PROFILES=importOwner;
 ctx.pendingRequestsRaw=[{username:"original.owner.pending",timestamp:15}];
 const beforeCrossAccount=saved.length;
 const correctFiles=[
  manualFile("pending_follow_requests_1.json",completePayload),
  manualFile("pending_follow_requests_2.json",completePayload)
 ];
 element("pendingInput").files=correctFiles;
 let fileReads=0;
 ctx.readFile=async file=>{
   fileReads++;
   if(fileReads===2)importOwner.active="ig_second_123456";
   return file.raw;
 };
 assert.equal(await ctx.processPendingFiles(),false,
   "Switching to B while importing the second Pending shard must abort.");
 assert.equal(fileReads,2);
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),
   ["original.owner.pending"],"A's import cannot be published to B");
 assert.equal(saved.length,beforeCrossAccount,
   "A mid-import account switch must never write storage or review history");
 assert.match(messages.at(-1),/Cambió la cuenta o el perfil de Instagram/);

 // Exact same-account manual multi-file import still succeeds and keeps
 // proper unique count. No switch, no new Chrome or Instagram action.
 importOwner.active="ig_first_1234567";
 fileReads=0;
 ctx.readFile=async file=>{fileReads++;return file.raw};
 assert.equal(await ctx.processPendingFiles(),true);
 assert.equal(fileReads,2);
 assert.equal(ctx.pendingRequestsRaw.length,725);
 assert.equal(saved.length,beforeCrossAccount+1);

 // Signed-in account identity becoming unverified must also fail closed.
 ctx.pendingRequestsRaw=[{username:"original.owner.pending",timestamp:15}];
 const safeCount=saved.length;
 ctx.readFile=async file=>{importOwner.verified=false;return file.raw};
 element("pendingInput").files=[correctFiles[0]];
 assert.equal(await ctx.processPendingFiles(),false);
 assert.equal(saved.length,safeCount);
 assert.deepEqual(Array.from(ctx.pendingRequestsRaw,x=>x.username),
   ["original.owner.pending"]);
 importOwner.verified=true;
 console.log("PASS: native Pending 725 + category isolation + atomic manual import on corrupt/mixed/empty files; ZIP retains original WAL");
})().catch(e=>{console.error(e);process.exitCode=1});
