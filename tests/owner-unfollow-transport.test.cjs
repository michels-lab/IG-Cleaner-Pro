'use strict';
const assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm'), path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../tools/instagram_unfollow_reference.py'),'utf8');
function pick(symbol){
  const rx=new RegExp(symbol+' = r"""([\\s\\S]*?)"""');
  const match=source.match(rx);assert(match,'Missing '+symbol);
  new vm.Script('('+match[1]+')');
  return match[1];
}
const lookup=pick('_REFERENCE_EXACT_FOLLOWING');
const mutation=pick('_REFERENCE_UNFOLLOW_MUTATION');
function session(response){
  const requested=[];
  const doc={cookie:'ds_user_id=999; csrftoken=csrf',
    documentElement:{innerHTML:''},
    querySelector(q){return q==='input[name="fb_dtsg"]'?{value:'dtsg'}:
                           q==='input[name="lsd"]'?{value:'lsd'}:null;}};
  const fetch=async (url,opts)=>{
    requested.push({url:String(url),opts});
    return opts.method==='GET'?{status:200,ok:true,json:async()=>response?.get||
        {users:[{username:'target.user',pk:'123'}]}}:
      {status:response?.status||200,ok:response?.ok!==false,
       text:async()=>JSON.stringify(response?.post||{data:{
         unfollow:{friendship_status:{following:false,outgoing_request:false}}}})};
  };
  class AbortController {constructor(){this.signal={}}abort(){}}
  const ctx={window:{require:()=>({token:'',client_revision:'1'})},
    location:{protocol:'https:',hostname:'www.instagram.com',
       origin:'https://www.instagram.com'},
    document:doc, fetch, AbortController,URL,URLSearchParams,setTimeout,clearTimeout};
  vm.createContext(ctx);
  const get=vm.runInContext('('+lookup+')',ctx);
  const post=vm.runInContext('('+mutation+')',ctx);
  return {get,post,requested,doc};
}
(async()=>{
  let s=session();
  const found=await s.get({username:'target.user'});
  assert.equal(found.code,'EXACT_FOLLOWING_ID');
  assert.equal(found.id,'123');
  assert.equal(s.requested.length,1);
  const dry=await s.post({targetId:found.id,dryRun:true});
  assert.equal(dry.code,'READY_TO_MUTATE');
  assert.equal(s.requested.length,1,'Preflight is read-only; no click and no POST');
  const changed=await s.post({targetId:found.id,dryRun:false});
  assert.equal(changed.code,'MUTATION_ACCEPTED');
  assert.equal(s.requested.length,2);
  assert.equal(s.requested[1].opts.method,'POST');
  const form=new URLSearchParams(s.requested[1].opts.body);
  assert.equal(form.get('fb_api_req_friendly_name'),'usePolarisUnfollowMutation');
  assert.equal(form.get('doc_id'),'27789106940691111');
  assert.equal(JSON.parse(form.get('variables')).target_user_id,'123');
  assert.deepEqual(Object.keys(changed),['code'],'No token leak into Python');
  s=session({get:{users:[{username:'other.account',pk:'123'}]}});
  assert.equal((await s.get({username:'target.user'})).code,'NO_EXACT_FOLLOWING_ID');
  assert.equal(s.requested.length,1);
  s=session({post:{errors:[{message:'feedback_required'}]}});
  assert.equal((await s.post({targetId:'123'})).code,'ACTION_BLOCKED');
  assert.equal(s.requested.filter(x=>x.opts.method==='POST').length,1);
  s=session({post:{data:{unfollow:{friendship_status:{
    following:true,outgoing_request:false}}}}});
  assert.equal((await s.post({targetId:'123'})).code,'MUTATION_UNCERTAIN');
  s=session();s.doc.cookie='ds_user_id=999; csrftoken=';
  assert.equal((await s.post({targetId:'123',dryRun:true})).code,'SESSION_TOKENS_UNAVAILABLE');
  assert.equal(s.requested.length,0);
  console.log('Owner-supplied Unfollow browser transport: positive, block, uncertain and preflight PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
