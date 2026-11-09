'use strict';
/* GRANADA: use the actual distributable parser / ZIP routing; synthetic only. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,
 '../desktop/ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
function section(start,end){
 const i=html.indexOf(start),j=html.indexOf(end,i+start.length);
 assert(i>=0&&j>i, 'Missing production logic: '+start);
 return html.slice(i,j);
}
// A later compatibility script previously overwrote the transactional importer.
// It could publish an empty Pending list on corrupt JSON or wrong category.
assert.equal((html.match(/async function processPendingFiles\(\)\{/g)||[]).length,1,
 'There must be one canonical manually imported Pending file handler.');
assert.equal((html.match(/window\.processPendingFiles\s*=\s*async function/g)||[]).length,0,
 'Never replace safe Pending manual importer with the old destructive override.');

const nodes=new Map(),saved=[];
function node(id){if(!nodes.has(id))nodes.set(id,{
 textContent:'',dataset:{},title:'',value:'',style:{},innerHTML:''
});return nodes.get(id)}
const ctx={
 console,Math,JSON,URL,Date,Map,Set,Number,String,Array,Object,
 window:null,document:{getElementById:node},decodeText:String,
 basename:p=>String(p).replace(/\\/g,'/').split('/').pop(),
 CATEGORY_ORDER:['following','followers','pending_follow_requests',
                 'recent_follow_requests','recently_unfollowed_profiles','blocked_profiles'],
 pendingRequestsRaw:[{username:'saved.before',timestamp:1}],
 pendingTableLimit:300,diagData:[],
 q:node,savePendingRequests:()=>saved.push(ctx.pendingRequestsRaw.map(x=>x.username)),
 renderPendingRequests:()=>{},
};
ctx.window=ctx;
vm.createContext(ctx);
vm.runInContext(section('function cleanUsername(value){','function extractFromJSON(data,source)'),ctx);
vm.runInContext(section('function pendingLabelMap(item){','async function processPendingFiles()'),ctx);
vm.runInContext(section('function zipCategoryFor(item){','function renderZipSummary('),ctx);
vm.runInContext(section('async function parseZipPending(items,zipName=', 'async function parseZipExtras('),ctx);
ctx.igcParseDetected=(payload,txt,source)=>ctx.extractPendingRequestsFromJSON(payload.data,source);
ctx.igcDiagEntry=()=>({file:'synthetic'});
const users=Array.from({length:725},(_,i)=>({
 string_list_data:[{value:'request'+String(i).padStart(4,'0'),
 timestamp:1700000000+i,href:'https://www.instagram.com/_u/request'+
 String(i).padStart(4,'0')}]
}));
const shard=(name,data,category='pending_follow_requests')=>({
 entry:{name:'connections/followers_and_following/'+name},
 file:{name,size:12000},
 text:JSON.stringify(data),payload:{format:'json',category,data}
});
const a=shard('pending_follow_requests_1.json',users.slice(0,350));
const b=shard('pending_follow_requests_2.json',users.slice(350));
const c=shard('recent_follow_requests_1.json',users.slice(0,5),'recent_follow_requests');
const d=shard('followers_1.json',users.slice(0,5),'followers');
const e=shard('following_2.json',users.slice(0,5),'following');
const f=shard('blocked_profiles_1.json',users.slice(0,5),'blocked_profiles');
const official=shard('pending_follow_requests.json',
 {relationships_follow_requests_sent:users.slice(0,2)});
assert.equal(ctx.zipCategoryFor(a),'pending_follow_requests');
assert.equal(ctx.zipCategoryFor(b),'pending_follow_requests');
assert.equal(ctx.zipCategoryFor(official),'pending_follow_requests');
assert.equal(ctx.zipCategoryFor(c),'recent_follow_requests',
 'Outgoing Pending must never mix with incoming recent requests');
assert.equal(ctx.zipCategoryFor(d),'followers');
assert.equal(ctx.zipCategoryFor(e),'following');
assert.equal(ctx.zipCategoryFor(f),'blocked_profiles');
assert.equal(ctx.zipCategoryFor(shard('custom-export.json',users.slice(0,2))),
 'pending_follow_requests',
 'Known detected category must outrank generic string_list_data=>Followers fallback.');
const groups=Object.fromEntries(ctx.CATEGORY_ORDER.map(x=>[x,[]]));
for(const item of [a,b,c,d,e,f])groups[ctx.zipCategoryFor(item)].push(item);
assert.equal(groups.pending_follow_requests.length,2);
assert.equal(groups.followers.length,1);
assert.equal(groups.recent_follow_requests.length,1);
(async()=>{
 const count=await ctx.parseZipPending(groups.pending_follow_requests,'two-shards.zip');
 assert.equal(count,725,'All distinct requests from both shards must be imported');
 assert.equal(ctx.pendingRequestsRaw.length,725);
 assert(ctx.pendingRequestsRaw.some(x=>x.username==='request0000'));
 assert(ctx.pendingRequestsRaw.some(x=>x.username==='request0724'));
 assert(!ctx.pendingRequestsRaw.some(x=>x.username==='saved.before'));
 assert.equal(saved.length,1,'One completed ZIP snapshot, not one per shard');
 assert.match(node('pendingFilesLabel').textContent,/725 usuarios únicos/);
 // A second VALID JSON shard that declares requests but whose usernames
 // cannot be extracted must reject the WHOLE ZIP. The old code imported only
 // the good first shard and silently abandoned every request in the second.
 const beforeIncomplete=saved.length;
 const firstSnapshot=ctx.pendingRequestsRaw.map(x=>x.username);
 const unreadableShard=shard('pending_follow_requests_3.json',{
   relationships_follow_requests_sent:[{
     title:'unparseable!',string_list_data:[{value:'not/a/handle'}]
   }]
 });
 await assert.rejects(
   ()=>ctx.parseZipPending([a,unreadableShard],'truncated-shard.zip'),
   /pending_follow_requests_3\.json.*Se conservaron los Pending anteriores/i,
   'Unusable nonempty shard cannot cause partial replacement when A was valid.');
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),firstSnapshot);
 assert.equal(saved.length,beforeIncomplete,
   'No snapshot write is allowed when any nonempty Pending shard is unreadable.');
 // Even if a single shard has hundreds of valid requests, ONE unreadable
 // source entry means the native Pending export is incomplete and must not
 // replace the old snapshot. A zero-rows-only guard misses this case.
 const mixed=shard('pending_follow_requests_4.json',{
   relationships_follow_requests_sent:[
     users[700],
     {title:'unparseable!',string_list_data:[{value:'bad/name'}]}
   ]
 });
 const beforePartialCount=saved.length;
 const beforePartialNames=ctx.pendingRequestsRaw.map(x=>x.username);
 await assert.rejects(
   ()=>ctx.parseZipPending([a,mixed],'mixed-valid-invalid-shard.zip'),
   /pending_follow_requests_4\.json.*1 solicitud\(es\).*Se conservaron los Pending anteriores/,
   'Readable rows must not mask one bad sent-request row in the same shard.');
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),beforePartialNames);
 assert.equal(saved.length,beforePartialCount);
 // Mixed children in ONE native request are also corrupt; valid first
 // identity must not hide an invalid second identity in source data.
 const mixedChildren=shard('pending_follow_requests_5.json',{
   relationships_follow_requests_sent:[{
     string_list_data:[{value:'valid.inner'},{value:'not/a/handle'}]
   }]
 });
 await assert.rejects(()=>ctx.parseZipPending([a,mixedChildren],'bad-child.zip'),
  /pending_follow_requests_5\.json.*Se conservaron los Pending anteriores/);
 assert.equal(saved.length,beforePartialCount);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),beforePartialNames);
 // A genuinely empty *declared* sent-request shard is valid and must not
 // invalidate other nonempty shards; only the final union is persisted.
 const verifiedEmptyShard=shard('pending_follow_requests_3.json',{
   relationships_follow_requests_sent:[]
 });
 assert.equal(await ctx.parseZipPending([a,b,verifiedEmptyShard],
    'empty-plus-valid-shards.zip'),725);
 assert.equal(ctx.pendingRequestsRaw.length,725);
 // Empty or malformed shard aborts before replacement and must retain WAL.
 const original=saved.length;
 const oldNames=ctx.pendingRequestsRaw.map(x=>x.username);
 const broken=shard('pending_follow_requests_3.json',
 {relationships_follow_requests_sent:[{string_list_data:[{value:'not/a/handle'}]}]});
 broken.payload.format='invalid-json';
 await assert.rejects(()=>ctx.parseZipPending([a,broken],'bad-shard.zip'),
  /Se conservaron los Pending anteriores/);
 assert.deepEqual(ctx.pendingRequestsRaw.map(x=>x.username),oldNames);
 assert.equal(saved.length,original);
 console.log('GRANADA Pending ZIP: 725 requests in two numbered shards; strict category isolation, atomic failure, one runtime manual importer PASS');
})().catch(err=>{console.error(err);process.exitCode=1});
