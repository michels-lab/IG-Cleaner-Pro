"use strict";
// Production Focus eligibility + real scoped localStorage, using a 918/484
// fixture and A -> B -> A switching (no real Instagram user data).
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const source=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const script=source.match(/<script id="igc-instagram-profile-isolation">([\s\S]*?)<\/script>/)?.[1];
assert(script,"Real per-Instagram namespace script required");
function part(from,to){
 const a=source.indexOf(from),b=source.indexOf(to,a+from.length);
 assert(a>=0&&b>a,"Missing production function: "+from);return source.slice(a,b);
}
const rawMap=new Map([["igc_v12027_supabase_config",JSON.stringify({email:"fixture@example.test"})]]);
const raw={getItem:k=>rawMap.has(k)?rawMap.get(k):null,
 setItem:(k,v)=>rawMap.set(String(k),String(v)),
 removeItem:k=>rawMap.delete(k),key:i=>[...rawMap.keys()][i]||null,
 get length(){return rawMap.size}};
let reloads=0;
const node={addEventListener(){},getElementById:()=>null};
const ctx={window:{localStorage:raw,indexedDB:{open:n=>({name:n})}},document:node,
 location:{hash:"",reload:()=>reloads++},
 console,Date,Math,JSON,Set,Map,Array,String,Number,Boolean,Error,Proxy,Reflect,
 URLSearchParams,encodeURIComponent,decodeURIComponent};
vm.createContext(ctx);
vm.runInContext(script,ctx);
assert.notEqual(ctx.IGC_INSTAGRAM_OWNER,"signed_out");
const A="ig_first_123",B="ig_second_456";
const identity=ctx.window.IGC_INSTAGRAM_PROFILES;
identity.setAccounts([{account_key:A,username:"fixture.a"},{account_key:B,username:"fixture.b"}]);
identity._verified=true;
ctx.V113={cache:null,cacheAt:0,cacheMs:2000};
ctx.calcRisk=()=>({score:0,level:"bajo",reasons:[],codes:[]});
ctx.getMediumThreshold=()=>30;ctx.getHighThreshold=()=>60;
ctx.cleanUsername=x=>String(x).toLowerCase();ctx.currentMode="following";
ctx.isSnoozed=()=>false;ctx.isInActiveFocus=()=>false;
ctx.profileHistoryOf=()=>null;ctx.pendingRows=()=>[];
ctx.followersMutualRows=()=>[];ctx.protectedSet=new Set();
ctx.pendingRequestsRaw=[];ctx.pendingReviewedMeta={};ctx.pendingOpenedSet=new Set();
ctx.safe=(fn,fallback)=>{try{return fn()}catch{return fallback}};
vm.runInContext(part("function isDoneValidForMode(row,mode){","function reviewedAtTsForMode("),ctx);
vm.runInContext(part("function isPreviouslyHandledForNormalFocus(","function mainFocusNoOpenReason("),ctx);
vm.runInContext(part("function buildRowsForMode(mode){","function pctDecimal(part,total){"),ctx);
vm.runInContext(part("function uniq(rows){","function tag(label,value"),ctx);
vm.runInContext(part("function rowsFor(kind){","function stateFor(kind){"),ctx);
function profiles(n){return Array.from({length:n},(_,i)=>{
 const username="profile_"+String(i).padStart(4,"0");
 return {username,href:"https://www.instagram.com/"+username+"/",timestamp:1700000000};
});}
function reviewMeta(){return {mode:"following",relation:"No me sigue",relationGood:false,
 followsBack:false,isFollower:false,iFollow:true,reviewedAt:Date.now(),reviewReason:"reviewed"};}
function load(key,rows){
 vm.runInContext("igcActiveInstagramProfile="+JSON.stringify(key),ctx);
 ctx.followingRaw=rows;
 ctx.followingMap=new Map(rows.map(r=>[r.username,r]));
 ctx.followersRaw=[];ctx.followersMap=new Map();
 ctx.doneSet=new Set(JSON.parse(vm.runInContext("localStorage.getItem('ig_v13_done')",ctx)||"[]"));
 ctx.reviewedMeta=JSON.parse(vm.runInContext("localStorage.getItem('ig_v15_review_meta')",ctx)||"{}");
}
function confirm(n){
 const rows=ctx.followingRaw.filter(r=>!ctx.doneSet.has(r.username)).slice(0,n);
 for(const row of rows){ctx.doneSet.add(row.username);ctx.reviewedMeta[row.username]=reviewMeta();}
 vm.runInContext("localStorage.setItem('ig_v13_done',JSON.stringify([...doneSet]));localStorage.setItem('ig_v15_review_meta',JSON.stringify(reviewedMeta))",ctx);
}
function totals(){
 return {main:ctx.rowsFor("main").length,recheck:ctx.rowsFor("recheck").length,
   doubleCheck:ctx.rowsFor("double").length,
   reviewed:ctx.cache(true).noMeSigue.filter(r=>ctx.isDoneValidForMode(r,"following")).length};
}
const aRows=profiles(918);
load(A,aRows);confirm(484);
assert.deepEqual(totals(),{main:434,recheck:918,doubleCheck:918,reviewed:484});
identity.switch(B);
assert.equal(reloads,1);
const bRows=profiles(120);
load(B,bRows);confirm(60);
assert.deepEqual(totals(),{main:60,recheck:120,doubleCheck:120,reviewed:60});
identity.switch(A);assert.equal(reloads,2);
load(A,aRows);
assert.deepEqual(totals(),{main:434,recheck:918,doubleCheck:918,reviewed:484},
 "Returning to A must not restore B counts or reopen the 484 reviewed profiles");
confirm(30);
assert.deepEqual(totals(),{main:404,recheck:918,doubleCheck:918,reviewed:514},
 "A confirmed batch must immediately reduce Focus but not Recheck");
identity.switch(B);load(B,bRows);
assert.deepEqual(totals(),{main:60,recheck:120,doubleCheck:120,reviewed:60},
 "A's newest thirty confirmations must not contaminate B");
identity.switch(A);load(A,aRows);
assert.deepEqual(totals(),{main:404,recheck:918,doubleCheck:918,reviewed:514});
assert.equal(reloads,4);
const aKey="igc_profile__"+ctx.IGC_INSTAGRAM_OWNER+"__"+A+"__ig_v13_done";
const bKey="igc_profile__"+ctx.IGC_INSTAGRAM_OWNER+"__"+B+"__ig_v13_done";
assert.equal(JSON.parse(rawMap.get(aKey)).length,514);
assert.equal(JSON.parse(rawMap.get(bKey)).length,60);
console.log("PASS: real scoped state A-B-A 918 total / 484 reviewed / 434 available; 30 confirmations persist without rebound");
