"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=html.match(/<script id="igc-v12024-frozen-focus-preview-js">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Missing frozen Focus preview logic");new vm.Script(script);
const store=new Map(),nodes=new Map(),opens=[],messages=[];
function node(id){if(!nodes.has(id))nodes.set(id,{
 textContent:"",innerHTML:"",disabled:false,value:"",
 className:"",style:{},classList:{add(){},remove(){}},setAttribute(){}
});return nodes.get(id)}
const row=user=>({username:user,href:"https://www.instagram.com/"+user+"/",timestamp:Date.now()});
const ctx={
  console,Math,Number,String,Date,Object,Set,Map,JSON,Error,
  pendingRequestsRaw:[row("old.one"),row("old.two")],
  followersRaw:[],followingRaw:[],
  pendingCandidateRows:()=>ctx.pendingRequestsRaw,
  pendingAnyFocusCandidates:()=>ctx.pendingRequestsRaw,
  allMainFocusOpenableRows:()=>[],
  igcBatchQuality:rows=>({total:rows.length,confirmed:rows.length,
    changes:0,historical:0,unverifiable:0,stable:0}),
  igcWhyOpened:()=>"",igcProfileHistoryText:()=>"",focusContextHtml:()=>"",
  esc:String,
  openConfirmedFocusRows:(rows)=>{opens.push(rows.map(r=>r.username));return true},
  msg:(message)=>messages.push(message),
  localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,String(v)),
    removeItem:k=>store.delete(k)},
  document:{querySelectorAll:()=>[],getElementById:node,
    addEventListener(){}},
  setTimeout:()=>{}
};ctx.window=ctx;
vm.createContext(ctx);vm.runInContext(script,ctx,{timeout:1500});
ctx.igcPreviewNextFocus("pending",2);
assert.equal(node("igcFocusPreviewOpen").disabled,false);
assert.match(node("igcFocusPreviewList").innerHTML,/old.one/);
ctx.pendingRequestsRaw=[row("new.one"),row("new.two"),row("fresh.three")];
assert.equal(ctx.igcTryOpenPreparedFocus("pending",2),"stale");
assert.equal(opens.length,0,"Stale batch must not silently open or substitute old profiles");
assert.equal(node("igcFocusPreviewOpen").disabled,false,
  "After importing new files the regenerated Focus preview must be actionable");
assert.match(node("igcFocusPreviewList").innerHTML,/new.one/);
assert.doesNotMatch(node("igcFocusPreviewList").innerHTML,/old.one/);
assert.match(messages.at(-1),/Updated the preview/);
assert.equal(ctx.igcTryOpenPreparedFocus("pending",2),"opened");
assert.deepEqual(opens[0],["new.one","new.two"]);
ctx.pendingRequestsRaw=[row("third.batch.one"),row("third.batch.two")];
ctx.igcPreviewNextFocus("pending",2);
assert.equal(ctx.igcTryOpenPreparedFocus("pending",2),"opened");
assert.deepEqual(opens[1],["third.batch.one","third.batch.two"]);
console.log("PASS: old frozen preview automatically becomes fresh/visible after import; explicit click opens correct second and third batches");
