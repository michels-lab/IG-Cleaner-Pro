'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const start=html.indexOf('function igcMutualRatioInfo(');
const end=html.indexOf('function followersMutualSmartCandidates(',start);
assert(start>0&&end>start,'Mutuals ratio helper must exist');
const records={
 underfollowed:{status:'ok',followers:'12',following:'2400',approximate:false},
 popular:{status:'ok',followers:'200000',following:'100',approximate:false},
 rounded:{status:'ok',followers:'100',following:'400',approximate:true},
 invalid:{status:'unavailable',followers:'',following:''}
};
const ctx={window:{igcCountsGetRecord:u=>records[u]||null},
 historyFocusScore:()=>0,followerOldestFirstSort:(a,b)=>a.username.localeCompare(b.username),
 Number,Math};
vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
assert(ctx.igcMutualRatioBonus({username:'underfollowed'})>ctx.igcMutualRatioBonus({username:'popular'}),
 'High Following/Followers ratio should raise human Focus ranking');
assert(ctx.igcMutualFocusSort({username:'underfollowed'},{username:'popular'})<0);
assert.equal(ctx.igcMutualRatioInfo({username:'invalid'}),null,
 'Unavailable counts must not be interpreted as zero');
assert.equal(ctx.igcMutualRatioInfo({username:'missing'}),null,
 'Missing visible counts should not affect Focus ranking');
assert(ctx.igcMutualRatioBonus({username:'rounded'})>0);
assert(html.includes("if(kind==='mutual')return dedupe("),
 'Prepared Focus must reuse mutual candidate function');
assert(html.includes(".sort(igcMutualFocusSort)"),
 'Mutual Focus candidates must use ratio sorting');
assert(!/window\.igcAutoChoose\('mutual'\)/.test(html),'Mutuals must not run action automations');
console.log('Mutuals Focus-only visible ratio priority and missing-data safety: PASS');
