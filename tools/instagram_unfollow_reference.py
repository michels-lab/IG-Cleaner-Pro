#!/usr/bin/env python3
"""Owner-approved InstaCleaner Unfollow transport from supplied Webpack sample.

The user supplied Pasted text(3).txt (Instagram Unfollowers). That sample uses a
same-origin authenticated following lookup and usePolarisUnfollowMutation.
No Instagram cookies, tokens, DOM source or POST bodies leave Chrome.
The operation identifier is unofficial and can stop working: fail closed.
"""
from __future__ import annotations

from urllib.parse import urlparse

from profile_counts_robot import valid_username

# Read-only exact-user ID resolution from the owner's *following* list.
# Numeric IDs are public profile metadata, NOT Instagram session material.
_REFERENCE_EXACT_FOLLOWING = r"""
async ({username}) => {
  const bad = code => ({code});
  if (location.protocol !== 'https:' ||
      !['instagram.com', 'www.instagram.com'].includes(location.hostname) ||
      !/^[A-Za-z0-9._]{1,30}$/.test(username)) return bad('INVALID_TARGET');
  const cookie = name => {
    const c = document.cookie.split(';').map(x => x.trim()).find(x => x.startsWith(name+'='));
    return c ? decodeURIComponent(c.slice(name.length+1)) : '';
  };
  const ownerId = cookie('ds_user_id');
  if (!/^\d{1,24}$/.test(ownerId)) return bad('NO_SESSION');
  const url = new URL('/api/v1/friendships/'+ownerId+'/following/', location.origin);
  url.searchParams.set('count', '50');
  url.searchParams.set('query', username);
  url.searchParams.set('search_surface','follow_list_page');
  const h = {'X-IG-App-ID':'936619743392459','X-ASBD-ID':'129477',
             'X-Requested-With':'XMLHttpRequest','Accept':'application/json'};
  const csrf=cookie('csrftoken'); if(csrf) h['X-CSRFToken']=csrf;
  const abort=new AbortController(), timer=setTimeout(()=>abort.abort(),12000);
  try {
    const r=await fetch(url.toString(),{method:'GET',credentials:'same-origin',
      redirect:'error',headers:h,signal:abort.signal});
    if (r.status===403 || r.status===429) return bad('RATE_LIMITED');
    if (!r.ok) return bad('LOOKUP_UNAVAILABLE');
    const j=await r.json();
    if(!j || j.status==='fail' || !Array.isArray(j.users)) return bad('LOOKUP_UNAVAILABLE');
    const found=j.users.filter(u=>u&&typeof u.username==='string'&&
      u.username.toLowerCase()===username.toLowerCase());
    if(found.length!==1) return bad('NO_EXACT_FOLLOWING_ID');
    const ids=[found[0].pk_id,found[0].pk,found[0].id].filter(v=>v!==undefined&&v!==null)
      .map(v=>String(v).trim());
    if(!ids.length||ids.some(v=>!/^\d{1,24}$/.test(v))||
       ids.some(v=>v!==ids[0]))return bad('AMBIGUOUS_TARGET_ID');
    return {code:'EXACT_FOLLOWING_ID',id:ids[0]};
  } catch(_) {return bad('LOOKUP_UNAVAILABLE')}
  finally {clearTimeout(timer)}
}
"""

# A single GraphQL POST copied in structure from the user-supplied sample.
# It uses the exact numeric target ID obtained via the positive lookup above.
# Token extraction and network response are NEVER returned to native Python.
_REFERENCE_UNFOLLOW_MUTATION = r"""
async ({targetId, dryRun=false}) => {
  const bad = code => ({code});
  if(location.protocol!=='https:'||
     !['instagram.com','www.instagram.com'].includes(location.hostname)||
     !/^\d{1,24}$/.test(targetId)) return bad('INVALID_TARGET');
  const cookie = name => {
    const c=document.cookie.split(';').map(x=>x.trim()).find(x=>x.startsWith(name+'='));
    return c ? decodeURIComponent(c.slice(name.length+1)) : '';
  };
  const moduleToken = (name, key='token') => {
    try { return typeof window.require==='function' ?
      (window.require(name)||{})[key]||'' : '' } catch(_) {return ''}
  };
  const metaToken = name => document.querySelector('input[name="'+name+'"]')?.value||'';
  const decodeTokens = html => {
    const fbDtsg=(html.match(/"DTSGInitialData",\[\],\{"token":"([^"]+)"/)||[])[1]||
      (html.match(/"dtsg":\{"token":"([^"]+)"/)||[])[1]||'';
    const lsd=(html.match(/"LSD",\[\],\{"token":"([^"]+)"/)||[])[1]||'';
    const revision=(html.match(/"client_revision":(\d+)/)||[])[1]||'';
    return {fbDtsg,lsd,revision};
  };
  let fbDtsg=moduleToken('DTSGInitialData')||metaToken('fb_dtsg');
  let lsd=moduleToken('LSD')||metaToken('lsd');
  let revision=String(moduleToken('SiteData','client_revision')||'');
  if(!fbDtsg||!lsd){
    const found=decodeTokens(document.documentElement?.innerHTML||'');
    fbDtsg=fbDtsg||found.fbDtsg;
    lsd=lsd||found.lsd;
    revision=revision||found.revision;
  }
  if(!fbDtsg||!lsd){
    // User's source uses the authenticated Instagram Home HTML as its
    // final read-only fallback. Never report the HTML or secrets to Python.
    const preload=new AbortController(),timeout=setTimeout(()=>preload.abort(),10000);
    try{
      const r=await fetch('https://www.instagram.com/',{
        method:'GET',credentials:'same-origin',redirect:'error',signal:preload.signal});
      if(r.ok){
        const found=decodeTokens(await r.text());
        fbDtsg=fbDtsg||found.fbDtsg;
        lsd=lsd||found.lsd;
        revision=revision||found.revision;
      }
    }catch(_){}finally{clearTimeout(timeout)}
  }
  const csrf=cookie('csrftoken'),owner=cookie('ds_user_id');
  if(!fbDtsg||!lsd||!csrf||!/^\d{1,24}$/.test(owner))
    return bad('SESSION_TOKENS_UNAVAILABLE');
  if(dryRun) return bad('READY_TO_MUTATE'); // No POST, no WAL consumed.
  // Exact owner-supplied h(fbDtsg): prefix "2" + SUM of UTF-16 char codes.
  const jazoest='2'+[...fbDtsg].reduce((sum,c)=>sum+c.charCodeAt(0),0);
  const form=new URLSearchParams({
    av:owner,__d:'www',__user:'0',__a:'1',__comet_req:'7',
    fb_dtsg:fbDtsg,jazoest,lsd,fb_api_caller_class:'RelayModern',
    fb_api_req_friendly_name:'usePolarisUnfollowMutation',
    variables:JSON.stringify({target_user_id:targetId,container_module:'profile',
      nav_chain:'PolarisProfilePostsTabRoot:profilePage:1:via_cold_start'}),
    server_timestamps:'true',doc_id:'27789106940691111'
  });
  try {
    if(revision){form.set('__rev',String(revision));form.set('__spin_r',String(revision))}
  } catch(_) {}
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),15000);
  try {
    // SINGLE relationship-changing request. No retry or fallback mutation.
    const r=await fetch('https://www.instagram.com/api/graphql',{
      method:'POST',credentials:'same-origin',redirect:'error',signal:abort.signal,
      headers:{'content-type':'application/x-www-form-urlencoded',
        'x-csrftoken':csrf,'x-fb-friendly-name':'usePolarisUnfollowMutation',
        'x-fb-lsd':lsd,'x-ig-app-id':'936619743392459','x-asbd-id':'129477'},
      body:form.toString()
    });
    const body=await r.text();
    let j=null;
    try {j=JSON.parse(body.replace(/^for \(;;\);/,''))} catch(_) {}
    if(r.status===403||r.status===429||j?.spam===true ||
      /feedback_required|checkpoint|action_blocked|try again later|rate limit/i.test(
        JSON.stringify(j?.errors||j?.error||j?.message||''))) return bad('ACTION_BLOCKED');
    if(!r.ok||!j||j.errors||j.error||j.status==='fail'||!j.data)
      return bad('MUTATION_UNCERTAIN');
    const seen=new Set(),nodes=[j.data];let friendship=null;
    for(let k=0;k<120&&nodes.length;k++){
      const x=nodes.pop();
      if(!x||typeof x!=='object'||seen.has(x))continue;
      seen.add(x);
      if(x.friendship_status&&typeof x.friendship_status==='object'){
        friendship=x.friendship_status;break;
      }
      if(typeof x.following==='boolean'&&typeof x.outgoing_request==='boolean'){
        friendship=x;break;
      }
      for(const v of Object.values(x))if(v&&typeof v==='object')nodes.push(v);
    }
    if(friendship&&friendship.following===false&&
       friendship.outgoing_request===false) return bad('MUTATION_ACCEPTED');
    return bad('MUTATION_UNCERTAIN');
  } catch(_){return bad('MUTATION_UNCERTAIN')}
  finally{clearTimeout(timer)}
}
"""


def reference_unfollow(page, username, expected_handle, *,
                       can_act, on_pre_click, verify_owner,
                       verify_target, verify_after):
    """One owner-approved mutation, with caller's durable WAL before POST.

    Return explicit safe_no_click block/review or verified completion. A possibly
    sent POST is always treated as uncertain unless a fresh visible profile
    confirms no-follow. Never automatically retry after an unknown outcome.
    """
    if valid_username(username) != username or not expected_handle:
        return "blocked", "Reference Unfollow: invalid requested target; no action clicked."
    if not on_pre_click:
        return "blocked", "Reference Unfollow requires durable journal consent; no action clicked."
    if can_act and not can_act(username):
        return "skipped", "Reference Unfollow: target protected or skipped; no action clicked."
    target=urlparse(getattr(page,"url",""))
    if (target.scheme!="https" or target.hostname not in
            ("instagram.com","www.instagram.com") or
            target.path.strip("/").casefold()!=username.casefold() or
            not verify_target(page, username) or
            not verify_owner(page, expected_handle)):
        return "blocked", "Reference Unfollow: exact Instagram target or signed-in owner not verified; no action clicked."
    try:
        item=page.evaluate(_REFERENCE_EXACT_FOLLOWING, {"username": username})
    except Exception:
        item=None
    if not isinstance(item,dict) or item.get("code")!="EXACT_FOLLOWING_ID":
        code=item.get("code") if isinstance(item,dict) else "LOOKUP_UNAVAILABLE"
        return ("blocked" if code in ("RATE_LIMITED","NO_SESSION") else "review",
                "Reference Unfollow read-only lookup: "+str(code)[:50]+
                ". No GraphQL request sent. Examine issues, do not assume unfollow.")
    target_id=item.get("id")
    if not isinstance(target_id,str) or not target_id.isdecimal() or len(target_id)>24:
        return "blocked", "Reference Unfollow: ambiguous target ID; no action clicked."
    # Confirm owner-session tokens exist while still read-only, BEFORE arming
    # the one-shot journal. Never consume a target merely for missing tokens.
    try:
        readiness=page.evaluate(_REFERENCE_UNFOLLOW_MUTATION,
                                {"targetId":target_id, "dryRun": True})
    except Exception:
        readiness=None
    if not isinstance(readiness, dict) or readiness.get("code")!="READY_TO_MUTATE":
        return "review", ("Reference Unfollow session preparation unavailable. "
                          "No POST or write-ahead action intent; review Chrome sign-in.")
    if (can_act and not can_act(username)) or not verify_target(page,username) or not verify_owner(page,expected_handle):
        return "blocked", "Reference Unfollow: target or owner changed before mutation; no action clicked."
    # Atomic/fsynced persistent intent must exist BEFORE the very first POST.
    # If this raises (e.g. disk full), no network mutation is attempted.
    on_pre_click("relationship_control")
    try:
        out=page.evaluate(_REFERENCE_UNFOLLOW_MUTATION, {"targetId":target_id, "dryRun": False})
    except Exception:
        out=None
    code=out.get("code") if isinstance(out,dict) else "MUTATION_UNCERTAIN"
    if code=="ACTION_BLOCKED":
        return "blocked", ("Instagram rejected the user-reference GraphQL Unfollow "
                           "(action block/403/429); click status uncertain. "
                           "The saved intent must not be replayed.")
    if code=="SESSION_TOKENS_UNAVAILABLE":
        return "review", ("Instagram session tokens were unavailable; mutation was "
                          "not submitted, but the original durable click intent is "
                          "preserved conservatively. No automatic retry.")
    # A successful Unfollow may have committed even when GraphQL's response is
    # missing/unknown. Confirm the actual FOLLOW state with one *read-only*
    # refresh before declaring uncertainty. Never issue a second POST.
    # The same final independent proof is required for a nominal success.
    verified, note=verify_after(page,username,expected_handle)
    if verified=="ok":
        return "ok", note
    if verified=="blocked":
        return "blocked", note
    if code!="MUTATION_ACCEPTED":
        return "review", ("User-reference GraphQL Unfollow did not positively confirm "
                          "a response and read-only verification remained uncertain. "
                          "Never send it again automatically.")
    return verified, note
