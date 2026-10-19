"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12024-frozen-focus-preview-js">([\\s\\S]*?)<\\/script>/)?.[1];
assert(script,"Frozen Focus preview must be present");
new vm.Script(script);
assert.match(html,/return window\\.igcPrioritizedMainFocusPool\\?\\.\\(\\)/,
  "Editable Focus refills must reuse the same complete prioritization pool");

const store=new Map(),nodes=new Map(),opens=[];
const sample=(username,score=10,level="baja",riskLevel="bajo")=>({
  username,href:"https://www.instagram.com/"+username+"/",timestamp:1,score,
  priority:level,riskLevel,riskScore:score,dateMain:1000
});
const changed=sample("changed.one",90),critical=sample("critical.one",80,"alta");
const risk=sample("risk.one",70,"baja","alto"),normal=sample("normal.one",50),
  last=sample("normal.two",40),prohibited=sample("protected.one",99,"critica");
const eligible=[changed,changed,critical,risk,normal,last];
let current=eligible;
const node=id=>{
  if(!nodes.has(id))nodes.set(id,{
    textContent:"",innerHTML:"",disabled:false,className:"",style:{},
    classList:{add(){},remove(){}},setAttribute(){}
  });
  return nodes.get(id);
};
const ctx={
  console,Math,Number,String,Date,Object,Set,Map,JSON,Error,
  localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,String(v)),removeItem:k=>store.delete(k)},
  document:{getElementById:node,querySelectorAll:()=>[],addEventListener(){}},
  setTimeout:()=>{},
  followingRaw:[changed,critical,risk,normal,last,prohibited],
  followersRaw:[],pendingRequestsRaw:[sample("pending.one"),sample("pending.two")],
  doneSet:new Set(["changed.one"]),isDoneValidForMode:()=>false,
  calcPriority:r=>({score:r.score,level:r.priority}),
  allMainFocusOpenableRows:()=>current,
  pendingCandidateRows:()=>ctx.pendingRequestsRaw,pendingAnyFocusCandidates:()=>ctx.pendingRequestsRaw,
  followersFocusCandidates:()=>[],followersMutualCandidates:()=>[],
  followersMutualAnyFocusCandidates:()=>[],
  igcBatchQuality:rows=>({total:rows.length,confirmed:rows.length,
    changes:0,historical:0,unverifiable:0,stable:0}),
  igcWhyOpened:()=>"",igcProfileHistoryText:()=>"",
  focusContextHtml:()=>"",focusContextText:()=>"",esc:String,
  profileUrl:u=>"https://www.instagram.com/"+u+"/",
  openConfirmedFocusRows:(rows,label,kind,n,opts)=>{opens.push({users:rows.map(r=>r.username),kind,n,opts});return true},
  msg:()=>{}
};ctx.window=ctx;vm.createContext(ctx);
vm.runInContext(script,ctx,{timeout:1500});

const expected=["changed.one","critical.one","risk.one","normal.one","normal.two"];
assert.deepEqual(Array.from(ctx.igcPrioritizedMainFocusPool().map(r=>r.username)),expected,
  "The first small priority tier must not suppress other eligible profiles");
assert(!ctx.igcPrioritizedMainFocusPool().some(r=>r.username===prohibited.username),
  "Prioritization may only draw from the existing eligible pool");

ctx.igcPreviewNextFocus("main",5);
const saved=()=>JSON.parse(store.get("ig_v12024_prepared_focus_batches")||"{}");
assert.deepEqual(Array.from(saved()["main:5"].usernames),expected);
assert.equal(node("igcFocusPreviewOpen").disabled,false);
assert.match(node("igcFocusPreviewList").innerHTML,/normal.two/);
assert.equal(ctx.igcTryOpenPreparedFocus("main",5),"opened");
assert.equal(opens.length,1);
assert.deepEqual(Array.from(opens[0].users),expected);
assert.equal(opens[0].opts.exact,true,"Frozen selection cannot silently replace profiles");

ctx.igcPreviewNextFocus("main",10);
assert.equal(saved()["main:10"].usernames.length,5,
  "A partial batch must tell the truth when fewer than ten eligible profiles exist");
assert.match(node("igcFocusPreviewOpen").textContent,/Abrir estos 5/);

ctx.igcPreviewNextFocus("pending",2);
assert.deepEqual(Array.from(saved()["pending:2"].usernames),["pending.one","pending.two"],
  "Pending Focus uses its own already eligible pool and must not be changed by main priority tiers");

// A new ZIP/import changes source signature. Never open a stale frozen set or
// silently substitute a profile without showing the new list to the owner.
ctx.followingRaw=[...ctx.followingRaw,sample("new.following")];
current=[...current,sample("new.following")];
const before=opens.length;
assert.equal(ctx.igcTryOpenPreparedFocus("main",10),"stale");
assert.equal(opens.length,before);
assert.equal(node("igcFocusPreviewOpen").disabled,false);
assert.equal(saved()["main:10"].usernames.length,6,
  "The replacement batch must appear as a new visible preview");
assert.equal(ctx.igcTryOpenPreparedFocus("main",10),"opened");
assert.equal(opens.length,before+1);
assert.equal(opens.at(-1).users.length,6);
console.log("PASS: GRANADA Focus priority tiers fill eligible batches, share editor pool, retain frozen confirmation and stale import safety");
