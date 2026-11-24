"""Native Windows Automations History view; read-only canonical action journal.

No new storage, no Instagram requests and no relationship clicks. Source data comes
from the existing token-protected /api/actions/history endpoint for each named
owner / Instagram workspace / task.
"""

AUTOMATION_ACTIVITY_PANEL = r"""
<style>
#igcAutomationActivitySection{width:100%;box-sizing:border-box}
#igcAutomationActivityPanel{width:100%;box-sizing:border-box;min-width:0;padding:20px;border:1px solid #354b60;
 border-radius:16px;color:#e7edf5;background:linear-gradient(155deg,#142237,#101b2c);font:inherit}
#igcAutomationActivityPanel h3{font-size:18px;margin:0 0 8px;color:#f0f6ff}
#igcAutomationActivityPanel .igc-act-muted{font-size:12px;line-height:1.5;color:#a5b5c9;margin:7px 0 12px}
#igcAutomationActivityPanel label{font-size:12px;color:#b4c9db;display:block;margin:9px 0 5px}
#igcAutomationActivityPanel select,#igcAutomationActivityPanel button{max-width:100%;box-sizing:border-box;
 background:#1c3044;border:1px solid #466179;border-radius:9px;color:#f1f6fd;padding:9px;font:inherit;font-size:12px}
#igcAutomationActivityPanel button{cursor:pointer;margin:10px 0 4px}
#igcAutomationActivityPanel button:disabled{opacity:.5}
#igcAutomationActivityPanel .igc-act-windows{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
#igcAutomationActivityPanel .igc-act-window{background:#17283a;border:1px solid #334d63;border-radius:10px;padding:11px;min-width:0}
#igcAutomationActivityPanel .igc-act-window span{display:block;color:#b7c9da;font-size:11px}
#igcAutomationActivityPanel .igc-act-window strong{font-size:22px;color:#f6f9ff;line-height:1.6;font-variant-numeric:tabular-nums}
#igcAutomationActivityPanel .igc-act-window.igc-act-primary{background:rgba(66,114,172,.17);border-color:rgba(116,188,239,.33)}
#igcAutomationActivityPanel .igc-act-section{border-top:1px solid #34465a;padding-top:11px;margin-top:14px}
#igcAutomationActivityPanel .igc-act-row{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:12px;line-height:1.9}
#igcAutomationActivityPanel .igc-act-row b{font-variant-numeric:tabular-nums}
#igcAutomationActivityPanel .igc-act-ok{color:#70d9a0}
#igcAutomationActivityPanel .igc-act-warning{color:#eec470}
#igcAutomationActivityPanel .igc-act-status{font-size:11px;color:#b4c7d8;overflow-wrap:anywhere}
#igcAutomationActivityPanel .igc-act-history{display:grid;gap:6px;max-height:360px;overflow:auto;margin:7px 0 10px}
#igcAutomationActivityPanel .igc-act-history-row{padding:9px;background:rgba(0,0,0,.13);border:1px solid #33495f;border-radius:9px;font-size:11px;color:#dee8f4}
#igcAutomationActivityPanel .igc-act-history-row small{display:block;color:#95adc0;font-size:10px;margin-top:4px}
#igcAutomationActivityPanel .igc-act-history-head{font-size:12px;color:#f0f5fd;font-weight:700;margin:0 0 4px}
#igcAutomationActivityPanel .igc-act-last{background:rgba(80,125,181,.1);border:1px solid #36516a;border-radius:10px;padding:9px;margin:10px 0 12px;font-size:12px;color:#e9f1fa}
#igcAutomationActivityPanel .igc-act-last small{display:block;font-size:10px;margin-top:3px;color:#a2b6c9}
#igcAutomationActivityPanel .igc-act-batch{background:#131f30;border:1px solid #35516b;border-radius:10px;padding:10px;margin-top:12px;display:grid;gap:6px;font-size:11px;color:#a8bcd0}
#igcAutomationActivityPanel .igc-act-batch strong{font-size:13px;color:#edf5ff}
#igcAutomationActivityPanel #igcActMorePeriods{border-top:1px solid #33495f;margin-top:13px;padding-top:8px}
#igcAutomationActivityPanel #igcActMorePeriods>summary{cursor:pointer;padding:8px 0;font-size:12px;font-weight:700;color:#8bcaff}
#igcAutomationActivityPanel #igcActMorePeriods .igc-act-windows{margin-top:9px}
#igcAutomationActivityPanel #igcActOrigin,#igcAutomationActivityPanel #igcActTask{width:min(100%,340px)}
#igcAutomationActivityPanel #igcActAccount{display:none}
@media(max-width:600px){#igcAutomationActivityPanel{padding:12px}#igcAutomationActivityPanel .igc-act-windows{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
<script id="igc-automation-activity">
(function(){
'use strict';
if(window.__igcAutomationActivityLoaded)return;
window.__igcAutomationActivityLoaded=true;
const $=id=>document.getElementById(id);
const OWNER=/^u_[a-z0-9]+_[0-9]{1,4}$/;
const ACCOUNT=/^(?:legacy|ig_[a-z0-9_-]{8,64})$/;
const HANDLE=/^[a-z0-9._]{1,30}$/i;
const TOKEN=/^[A-Za-z0-9_-]{20,256}$/;
const BRIDGE_READ_TIMEOUT_MS=8000;
const sessionStart=Date.now(); // This native app page session; reset on reload.
// Primary periods mirror igcStandardActivityTop() in Manual Actions.
const PERIODS=[['session','Esta sesión'],['today','Hoy'],['d7','Últimos 7 días'],
 ['h1','Última hora'],['h2','Últimas 2 horas'],['h3','Últimas 3 horas'],
 ['h24','Últimas 24 horas'],['week','Esta semana'],['month','Este mes'],['all','Histórico']];
let owner='',registry=[],loading=false,refreshAgain=false,dataReady=false,latest=[],unavailableTasks=[],lastKey='',lastActive='',lastGeneration=null,batchSequence=0,scopeEpoch=0;
function node(tag,name,txt){
 const x=document.createElement(tag);if(name)x.className=name;
 if(txt!==undefined)x.textContent=String(txt);return x;
}
function auth(){
 const m=(location.hash||'').match(/(?:^|[&#])igc-robot=(\d{1,5})\.([A-Za-z0-9_-]{20,256})/);
 if(!m||+m[1]<1||+m[1]>65535||!TOKEN.test(m[2]))throw Error('La sesión local de Windows no está disponible.');
 return {port:+m[1],token:m[2]};
}
function context(){
 const p=window.IGC_INSTAGRAM_PROFILES;
 if(!p||!OWNER.test(p.owner||''))return {owner:'',accounts:[],active:''};
 let arr=Array.isArray(p.accounts)?p.accounts:[];
 // The canonical registry getter is authoritative, including an empty
 // result. Never resurrect a removed identity from a fallback cache.
 if(!Array.isArray(arr))arr=[];
 const seen=new Set(),accounts=[];
 for(const item of arr){
   const account=item&&(item.account_key||item.account);
   const handle=item&&(item.username||item.expected_handle);
   if(!ACCOUNT.test(account||'')||!HANDLE.test(handle||'')||seen.has(account))continue;
   seen.add(account);accounts.push({account,handle:handle.toLowerCase()});
 }
 const active=accounts.some(x=>x.account===p.active)?p.active:'';
 return {owner:p.owner,accounts,active,generation:p.generation??null};
}
function registrySignature(ctx){
 return ctx.owner+'|'+ctx.accounts.map(a=>a.account+':'+a.handle).join('|');
}
function isCurrentScope(ctx,account){
 const current=context();
 return !!account&&current.owner===ctx.owner&&current.active===account&&
   current.generation===ctx.generation&&registrySignature(current)===registrySignature(ctx);
}
function dateValue(value){
 if(typeof value!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(value))return NaN;
 return Date.parse(value);
}
function startOfDay(d){return new Date(d.getFullYear(),d.getMonth(),d.getDate()).getTime()}
function startOfWeek(d){
 const midnight=startOfDay(d),weekday=(d.getDay()+6)%7;
 return new Date(d.getFullYear(),d.getMonth(),d.getDate()-weekday).getTime();
}
function cutoff(id,now){
 if(id==='session')return sessionStart;
 if(id==='h1')return now.getTime()-3600000;
 if(id==='h2')return now.getTime()-2*3600000;
 if(id==='h3')return now.getTime()-3*3600000;
 if(id==='h24')return now.getTime()-24*3600000;
 if(id==='d7')return now.getTime()-7*86400000;
 if(id==='today')return startOfDay(now);
 if(id==='week')return startOfWeek(now);
 if(id==='month')return new Date(now.getFullYear(),now.getMonth(),1).getTime();
 return -Infinity;
}
function classify(record){
 const state=String(record.status||'');
 // Only a verified action is counted; preexisting Follow and read-only
 // confirmations cannot be advertised as new unfollows/cancellations.
 if(state==='ok')return record.origin==='robot'?'verified':'legacy_unknown';
 if(['review','error','blocked'].includes(state))return 'warning';
 if(['already_not_following','already_not_requested'].includes(state))return 'no_action';
 if(state==='profile_unavailable')return 'unavailable';
 return 'unconfirmed';
}
function reconciledOutcomes(records){
 // The same reconciliation powers headline totals AND the visible journal.
 // Never let a timestamp tie with contradictory status/origin appear as OK.
 const groups=new Map();
 for(const r of records){
   if(!r||!['unfollow','cancel'].includes(r.task)||!HANDLE.test(r.username||''))continue;
   const key=r.task+':'+r.username.toLowerCase(),at=dateValue(r.at);
   if(!Number.isFinite(at))continue;
   const saved=groups.get(key);
   if(!saved||at>saved.at){
     groups.set(key,{key,at,record:r,conflict:false});
   }else if(at===saved.at&&(saved.record.status!==r.status||
                             saved.record.origin!==r.origin)){
     saved.conflict=true;
   }
 }
 // Aggregation runs for every period tile: avoid a redundant O(n log n) sort.
 return [...groups.values()];
}
function summarize(records,id,now,originFilter='all'){
 const lower=cutoff(id,now),upper=now.getTime();
 const out={verified:0,unfollow:0,cancel:0,warning:0,no_action:0,unavailable:0,
   legacy_unknown:0};
 const warningEvents=new Set();
 function recordWarning(key,status,at,origin){
   if(originFilter!=='all'&&origin!==originFilter)return;
   if(!['review','error','blocked'].includes(status))return;
   const when=dateValue(at);
   if(!Number.isFinite(when)||when<lower||when>upper)return;
   const eventKey=key+':'+status+':'+at;
   if(warningEvents.has(eventKey))return;
   warningEvents.add(eventKey);
   out.warning++;
 }
 for(const r of records){
   if(!r||!['unfollow','cancel'].includes(r.task)||!HANDLE.test(r.username||''))continue;
   const key=r.task+':'+r.username.toLowerCase();
   recordWarning(key,r.status,r.at,r.origin);
   for(const past of (Array.isArray(r.warning_events)?r.warning_events:[])){
     if(past)recordWarning(key,past.status,past.at,past.origin);
   }
 }
 for(const group of reconciledOutcomes(records)){
   if(group.conflict||group.at<lower||group.at>upper)continue;
   // Filter AFTER canonical reconciliation: hiding a contradictory unknown
   // row must never turn its same-time robot twin into a false verified OK.
   if(originFilter!=='all'&&group.record.origin!==originFilter)continue;
   const category=classify(group.record);
   if(category==='warning')continue; // Already counted at its own event time.
   if(Object.prototype.hasOwnProperty.call(out,category)){
     out[category]++;
     if(category==='verified')out[group.record.task]++;
   }
 }
 return out;
}
// Bound the entire read, including response decoding. A failed local
// controller must not hold the History refresh lock or stale counters forever.
async function bridgeReadJson(url,options={}){
 const controller=new AbortController();
 let timer;
 try{
   return await Promise.race([
     (async()=>{
       const response=await fetch(url,{...options,signal:controller.signal});
       const data=await response.json();
       return {ok:response.ok,data};
     })(),
     new Promise((_,reject)=>{
       timer=setTimeout(()=>{
         reject(Error('Local controller read timed out.'));
         controller.abort();
       },BRIDGE_READ_TIMEOUT_MS);
     })
   ]);
 }finally{clearTimeout(timer)}
}
async function readHistory(account,task,expectedOwner){
 // Bind the request owner before async I/O; the global owner may switch.
 const a=auth(),request={owner:expectedOwner,account,task};
 const {ok,data}=await bridgeReadJson('http://127.0.0.1:'+a.port+'/api/actions/history',{
   method:'POST',headers:{'X-IGC-Bridge-Token':a.token,'Content-Type':'application/json'},
   body:JSON.stringify(request)
 });
 if(!ok||data.owner!==expectedOwner||data.account!==account||data.task!==task||
    !Array.isArray(data.history_rows))throw Error('Historial no verificable para la cuenta seleccionada.');
 return data.history_rows.map(x=>({
   task,username:x.username,status:x.status,at:x.at,
   origin:x.origin==='robot'?'robot':'unknown',
   warning_events:Array.isArray(x.warning_events)?x.warning_events.map(e=>({
     status:e&&e.status,at:e&&e.at,
     origin:e&&e.origin==='robot'?'robot':'unknown'
   })):[]
 }));
}
async function readBatchStatus(account,expectedOwner){
 const a=auth();
 const headers={'X-IGC-Bridge-Token':a.token};
 async function get(path){
  const {ok,data:x}=await bridgeReadJson('http://127.0.0.1:'+a.port+path,{headers});
  if(!ok)throw Error('No hay estado de tanda verificable.');
  return x;
 }
 // Both are READ-ONLY. Two-account workspaces and the standard robot have
 // distinct live job supervisors but a shared owner/account authorization.
 const [dual,single]=await Promise.allSettled([
  get('/api/actions/dual-action-workspaces/status?owner='+encodeURIComponent(expectedOwner)),
  get('/api/actions/status')
 ]);
 // Report the exact active account only, preferring actually running jobs.
 const dualLane=dual.status==='fulfilled'&&dual.value.owner===expectedOwner&&
    Array.isArray(dual.value.lanes)?
    dual.value.lanes.find(x=>x&&x.account===account):null;
 const exactSingle=single.status==='fulfilled'&&single.value.owner===expectedOwner&&
    single.value.account===account?single.value:null;
 const dualState=dualLane?{running:dualLane.running,task:dualLane.task,state:dualLane.state,
   processed:dualLane.processed,pending:dualLane.pending,issues:dualLane.issues,
   total:dualLane.total,successful:dualLane.successful,
   noFollow:dualLane.already_not_following,noRequest:dualLane.already_not_requested,
   batchSize:dualLane.batch_size,batchId:dualLane.batch_id,
   message:dualLane.message,currentProfile:dualLane.current_profile,
   ownerProfileVisits:dualLane.owner_profile_visits,
   ownerSiblingProofs:dualLane.owner_sibling_proofs,scope:'dos cuentas'}:null;
 const singleState=exactSingle?{running:exactSingle.running,task:exactSingle.task,
   state:exactSingle.status,processed:exactSingle.processed,pending:exactSingle.pending,
   issues:exactSingle.issue_count,total:exactSingle.total,
   successful:exactSingle.successful,noFollow:exactSingle.already_not_following,
   noRequest:exactSingle.already_not_requested,
   batchSize:exactSingle.batch_size,batchId:exactSingle.review_batch?.id,
   message:exactSingle.message,currentProfile:exactSingle.current_profile,
   ownerProfileVisits:exactSingle.owner_profile_visits,
   ownerSiblingProofs:exactSingle.owner_sibling_proofs,scope:'robot principal'}:null;
 if(dualState?.running===true)return dualState;
 if(singleState?.running===true)return singleState;
 // A stopped previous batch from one supervisor also cannot prove that
 // the other supervisor has stopped. Show a known running batch above;
 // otherwise an unavailable supervisor means the current state is unknown.
 if(dual.status==='rejected'||single.status==='rejected')
   throw new Error('Estado del controlador local no verificable.');
 if(dualState&&['unfollow','cancel'].includes(dualState.task))return dualState;
 if(singleState&&['unfollow','cancel'].includes(singleState.task))return singleState;
 return null;
}
function showBatch(state){
 const e=$('igcActBatch'),title=$('igcActBatchTitle');
 if(!e||!title)return;
 if(state&&state.unavailable===true){
   title.textContent='Estado del robot no verificable';
   e.textContent='El controlador local no respondió. La tanda podría seguir activa; no se confirmó que terminara. Verifica la sesión del robot antes de iniciar otra acción.';
   return;
 }
 if(!state||!['unfollow','cancel'].includes(state.task)){
   title.textContent='Sin tanda de acciones activa';
   e.textContent='No hay un proceso asociado a esta cuenta en las sesiones locales del robot.';
   return;
 }
 const n=value=>Number.isInteger(value)&&value>=0?String(value):'—';
 title.textContent=(state.task==='unfollow'?'Unfollow':'Cancel Pending')+
   ' · '+String(state.state||'sin estado').slice(0,32)+
   (state.running?' · en ejecución':' · detenido');
 const ownerVisits=Number.isSafeInteger(state.ownerProfileVisits)&&state.ownerProfileVisits>=0?
   state.ownerProfileVisits:null;
 const siblingProofs=Number.isSafeInteger(state.ownerSiblingProofs)&&state.ownerSiblingProofs>=0?
   state.ownerSiblingProofs:null;
 const batchId=typeof state.batchId==='string'&&state.batchId.length<=128
   ? state.batchId:'';
 const description=typeof state.message==='string'
   ? state.message.replace(/[\r\n]+/g,' ').slice(0,220):'';
 // User-visible only, scoped to the selected Instagram account. Reject URLs,
 // arbitrary bridge text and invalid handles before showing a target.
 const currentProfile=typeof state.currentProfile==='string'&&HANDLE.test(state.currentProfile)
   ? state.currentProfile:'';
 e.textContent='Tamaño real de tanda: '+n(state.total)+
   ' · Tamaño configurado: '+n(state.batchSize)+
   (batchId?' · Lote: '+batchId:'')+
   (currentProfile?' · '+(state.running?'Perfil actual':'Último perfil')+': @'+currentProfile:'')+
   ' · Procesados: '+n(state.processed)+' · Pendientes: '+n(state.pending)+
   ' · Acciones confirmadas: '+n(state.successful)+
   ' · Ya no seguías (sin clic): '+n(state.noFollow)+
   ' · Sin solicitud activa (sin clic): '+n(state.noRequest)+
   ' · Review: '+n(state.issues)+' · '+state.scope+
   (ownerVisits===null?'':' · visitas a mi perfil: '+ownerVisits)+
   (siblingProofs===null?'':' · identidad desde otra pestaña: '+siblingProofs)+
   (description?' · Diagnóstico: '+description:'')+
   '. Procesados NO significa acciones confirmadas. Un estado desconocido se muestra como —, nunca como 0.';
}
function refreshBatch(account,expectedOwner){
 const request=++batchSequence,expectedEpoch=scopeEpoch,ctx=context();
 if(!isCurrentScope(ctx,account)||ctx.owner!==expectedOwner)return;
 readBatchStatus(account,expectedOwner).then(state=>{
  if(request!==batchSequence||scopeEpoch!==expectedEpoch||owner!==expectedOwner||
     $('igcActAccount')?.value!==account||!isCurrentScope(ctx,account))return;
  showBatch(state);
 }).catch(()=>{
  if(request!==batchSequence||scopeEpoch!==expectedEpoch||owner!==expectedOwner||
     $('igcActAccount')?.value!==account||!isCurrentScope(ctx,account))return;
  showBatch({unavailable:true});
 });
}
function setStatus(message){const e=$('igcActStatus');if(e)e.textContent=message}
function clearJournalValues(){
 const history=$('igcActHistory');if(history)history.replaceChildren();
 const last=$('igcActLast');if(last)last.textContent='—';
 for(const [key] of PERIODS){const el=$('igcActCount_'+key);if(el)el.textContent='—'}
 for(const key of ['verified','unfollow','cancel','warning','no_action','unavailable','legacy_unknown']){
   const el=$('igcActMetric_'+key);if(el)el.textContent='—';
 }
}
function clearValues(){
 batchSequence++;
 unavailableTasks=[];
 const bt=$('igcActBatchTitle');if(bt)bt.textContent='—';
 const b=$('igcActBatch');if(b)b.textContent='—';
 clearJournalValues();
}
function renderHistory(records,originFilter='all'){
 const list=$('igcActHistory'),last=$('igcActLast');
 if(!list||!last)return;
 // Use identical canonical reconciliation as the period counters.
 const entries=reconciledOutcomes(records)
   // Keep contradictory latest provenance visible as Review in either view.
   .filter(x=>originFilter==='all'||x.conflict||x.record.origin===originFilter)
   .sort((x,y)=>y.at-x.at).slice(0,15);
 list.replaceChildren();
 if(!entries.length){
   const partial=unavailableTasks.length>0&&$('igcActTask')?.value==='all';
   last.textContent=partial?
     'Sin registros en las tareas verificables; total desconocido.':
     'No hay acciones con fecha guardada.';
   list.append(node('p','igc-act-muted',partial?
     'Faltan registros de una tarea. No se puede concluir que hubo cero acciones.':
     'El historial está vacío o no tiene fechas verificables.'));
   return;
 }
 function name(entry){
   const r=entry.record;
   return (r.task==='unfollow'?'Unfollow':'Cancel Pending')+' · @'+r.username;
 }
 function desc(entry){
   if(entry.conflict)return 'REVIEW · historial contradictorio, sin OK verificable';
   const k=classify(entry.record);
   return k==='verified'?'OK confirmado':
     k==='warning'?'⚠ Review / advertencia':k==='legacy_unknown'?
     'OK histórico · origen sin registrar':k==='no_action'?'Ya resuelto · sin clic':
     k==='unavailable'?'No disponible':'No confirmado';
 }
 const newest=entries[0];last.replaceChildren();
 last.append(node('div',null,(unavailableTasks.length>0&&
   $('igcActTask')?.value==='all'?'Último registro verificable (parcial)':'Último registro')+
   ' · '+name(newest)),
   node('small',null,desc(newest)+' · '+new Date(newest.at).toLocaleString()));
 for(const entry of entries){
   const row=node('div','igc-act-history-row');
   row.append(node('div',null,name(entry)+' · '+desc(entry)),
     node('small',null,new Date(entry.at).toLocaleString()));
   list.append(row);
 }
}
function render(records){
 if(!dataReady)return;
 const selected=$('igcActTask')?.value||'all';
 const scoped=selected==='all'?records:records.filter(r=>r.task===selected);
 const originFilter=$('igcActOrigin')?.value||'all';
 // A damaged task WAL is unknown, not zero. Combined counters are LOWER
 // BOUNDS; task-specific numbers remain exact only for healthy sources.
 const incomplete=selected==='all'?unavailableTasks.length>0:
   unavailableTasks.includes(selected);
 const missingOnly=selected!=='all'&&incomplete;
 const panel=$('igcAutomationActivityPanel');
 if(panel)panel.setAttribute('data-history-partial',String(incomplete));
 const display=n=>missingOnly?'—':incomplete?'≥'+n:String(n);
 const now=new Date();
 for(const [key] of PERIODS){
   const out=summarize(scoped,key,now,originFilter);
   const el=$('igcActCount_'+key);
   if(el)el.textContent=display(out.verified);
 }
 if(missingOnly){
   const list=$('igcActHistory'),last=$('igcActLast');
   if(last)last.textContent='Historial no verificable de '+
     (selected==='cancel'?'Cancel Pending':'Unfollow')+'.';
   if(list)list.replaceChildren(node('p','igc-act-muted',
     'La lectura de esta tarea falló. No se presume cero ni se borran acciones de la otra tarea.'));
 }else renderHistory(scoped,originFilter);
 const period=$('igcActBreakdownPeriod')?.value||'today';
 const data=summarize(scoped,period,now,originFilter);
 for(const key of ['verified','unfollow','cancel','warning','no_action','unavailable','legacy_unknown']){
   const el=$('igcActMetric_'+key);if(el)el.textContent=display(data[key]);
 }
}
async function refresh(){
 const ctx=context(),selector=$('igcActAccount');
 if(!selector)return;
 if(!ctx.owner){scopeEpoch++;latest=[];owner='';lastKey='';lastActive='';lastGeneration=null;dataReady=false;clearValues();
   selector.replaceChildren();setStatus('Inicia sesión para consultar estadísticas guardadas.');return}
 const signature=registrySignature(ctx);
 if(signature!==lastKey){
   scopeEpoch++; // Owner, account registry, or handle identity changed.
   selector.replaceChildren();
   for(const account of ctx.accounts){
     const opt=node('option',null,'@'+account.handle);opt.value=account.account;selector.append(opt);
   }
   // The hidden selector is a projection of the active workspace, never
   // a fallback to the first account in a registry or a previous selection.
   selector.value=ctx.active;
   owner=ctx.owner;registry=ctx.accounts;lastKey=signature;lastActive=ctx.active;
   lastGeneration=ctx.generation;
   latest=[];dataReady=false;clearValues();
 }else if(ctx.active!==lastActive||ctx.generation!==lastGeneration){
   scopeEpoch++; // A -> B -> A must invalidate the first A response.
   // A real Instagram workspace switch invalidates the old account's numbers,
   // even if an earlier network request is still outstanding.
   selector.value=ctx.active;
   lastActive=ctx.active;lastGeneration=ctx.generation;
   latest=[];dataReady=false;clearValues();
 }
 // Even while an old request is loading, an unnamed or deleted active
 // workspace must show unknown, never another account's journal.
 selector.value=ctx.active;
 if(!ctx.active||!registry.length||!ACCOUNT.test(ctx.active)){
   latest=[];dataReady=false;clearValues();
   setStatus('Select a registered Instagram profile in this window to view its history.');return;
 }
 if(loading){refreshAgain=true;return;}
 loading=true;
 const button=$('igcActRefresh');if(button)button.disabled=true;
 const account=ctx.active,requestEpoch=scopeEpoch;
 // Live batch status is independent from the potentially slow journal.
 // On a new account, clearValues() already invalidated previous requests.
 refreshBatch(account,ctx.owner);
 setStatus('Refreshing saved history…');
 try{
   // A single corrupt Cancel Pending WAL must not erase valid Unfollow
   // counts (or vice versa). Require exact owner/account/task for every row.
   const tasks=['unfollow','cancel'];
   const responses=await Promise.allSettled(tasks.map(task=>readHistory(account,task,ctx.owner)));
   // Reject stale responses after an account selection or login switch.
   if(scopeEpoch!==requestEpoch||owner!==ctx.owner||selector.value!==account||
      !isCurrentScope(ctx,account))return;
   const failed=tasks.filter((task,i)=>responses[i].status!=='fulfilled');
   if(failed.length===tasks.length)
     throw Error('Unfollow y Cancel Pending: ambos historiales no son verificables.');
   unavailableTasks=failed;
   latest=responses.flatMap(r=>r.status==='fulfilled'?r.value:[]);
   dataReady=true;render(latest);
   const tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'hora local';
   const label=failed.map(t=>t==='cancel'?'Cancel Pending':'Unfollow').join(' y ');
   setStatus((failed.length?'Lectura PARCIAL: '+label+
     ' no verificable. Las cifras combinadas son mínimos (≥), no totales completos. · ':
     'Actualizado: ')+new Date().toLocaleTimeString()+' · '+tz+
     ' · origen robot confirmado cuando está registrado. Históricos sin origen: separados.');
 }catch(e){
   // Do not erase another account's metrics after a late failed request.
   if(scopeEpoch===requestEpoch&&owner===ctx.owner&&selector.value===account&&
      isCurrentScope(ctx,account)){
     latest=[];dataReady=false;clearJournalValues();
     setStatus('Sin historial verificable: '+String(e.message||e).slice(0,120));
   }
 }finally{
   loading=false;if(button)button.disabled=false;
   if(refreshAgain){refreshAgain=false;refresh()}
 }
}
function mount(){
 const page=$('page-automations');const flow=page?.querySelector('.igc-page-flow');
 if(!flow||!$('igcAutomationCommandCenter'))return false;
 if($('igcAutomationActivityPanel'))return true;
 // Replace the standalone HTML's explanatory History placeholder in the
 // installed Windows view. Never create a second History panel.
 let sectionRoot=$('igcAutomationActivitySection');
 if(!sectionRoot){
  sectionRoot=node('section');sectionRoot.id='igcAutomationActivitySection';
  sectionRoot.className='igc-robot-section';sectionRoot.hidden=true;
  flow.append(sectionRoot);
 }
 sectionRoot.replaceChildren();
 const panel=node('aside');panel.id='igcAutomationActivityPanel';
 panel.setAttribute('aria-label','Estadísticas de acciones automáticas');
 const head=node('div','igc-act-head');
 head.append(node('h3',null,'Activity & History · current account'));
 panel.append(head);
 panel.append(node('p','igc-act-muted','Actividad confirmada por cuenta · misma lógica de periodos diarios y móviles.'));
 // The page already has a primary Instagram account picker. Do not present
 // a second, conflicting account selector in the History workspace.
 const select=node('select');select.id='igcActAccount';select.hidden=true;
 select.addEventListener('change',()=>{scopeEpoch++;latest=[];dataReady=false;clearValues();refresh()});panel.append(select);
 const taskLabel=node('label',null,'Tipo de acción');taskLabel.htmlFor='igcActTask';panel.append(taskLabel);
 const task=node('select');task.id='igcActTask';
 for(const [value,label] of [['all','Todas las acciones'],['unfollow','Unfollow'],
    ['cancel','Cancel Pending']]){
   const opt=node('option',null,label);opt.value=value;task.append(opt);
 }
 task.addEventListener('change',()=>render(latest));panel.append(task);
 const originLabel=node('label',null,'Procedencia de las acciones');originLabel.htmlFor='igcActOrigin';panel.append(originLabel);
 const origin=node('select');origin.id='igcActOrigin';
 for(const [value,name] of [['all','Robot y registros históricos'],
    ['robot','Solo robot verificado'],['unknown','Origen histórico sin comprobar']]){
   const opt=node('option',null,name);opt.value=value;origin.append(opt);
 }
 origin.addEventListener('change',()=>render(latest));panel.append(origin);
 panel.append(node('p','igc-act-muted',
   'Esta vista consulta el diario local del robot. No atribuye acciones manuales a un robot ni adivina el origen de entradas antiguas.'));
 const grid=node('div','igc-act-windows');
 const extra=node('details');extra.id='igcActMorePeriods';
 extra.append(node('summary',null,'More periods · 1h / 2h / 3h / calendar'));
 const extraGrid=node('div','igc-act-windows');
 for(const [key,name] of PERIODS){
  const primary=['session','today','d7'].includes(key);
  const item=node('div','igc-act-window'+(primary?' igc-act-primary':'')),caption=node('span',null,name);
  const count=node('strong',null,'—');count.id='igcActCount_'+key;
  item.append(caption,count);(primary?grid:extraGrid).append(item);
 }
 panel.append(grid);extra.append(extraGrid);panel.append(extra);
 const batch=node('div','igc-act-batch');
 const batchTitle=node('strong',null,'—');batchTitle.id='igcActBatchTitle';
 const batchBody=node('div',null,'—');batchBody.id='igcActBatch';
 batch.append(batchTitle,batchBody);panel.append(batch);
 const last=node('div','igc-act-last','—');last.id='igcActLast';panel.append(last);
 const section=node('div','igc-act-section');
 const periodLabel=node('label',null,'Desglose del periodo');periodLabel.htmlFor='igcActBreakdownPeriod';section.append(periodLabel);
 const period=node('select');period.id='igcActBreakdownPeriod';
 for(const [key,name] of PERIODS){const opt=node('option',null,name);opt.value=key;period.append(opt)}
 period.value='today';period.addEventListener('change',()=>render(latest));section.append(period);
 for(const [key,name] of [['verified','Acciones confirmadas'],['unfollow','Unfollow realizados'],
  ['cancel','Solicitudes canceladas'],['warning','Review / advertencias (eventos)'],
  ['no_action','Ya estaban resueltas (sin clic)'],['unavailable','Perfiles no disponibles'],
  ['legacy_unknown','OK históricos sin procedencia registrada']]){
   const row=node('div','igc-act-row');
   row.append(node('span',key==='verified'||key==='unfollow'||key==='cancel'?'igc-act-ok':
     key==='warning'?'igc-act-warning':null,name));
   const number=node('b',null,'—');number.id='igcActMetric_'+key;row.append(number);section.append(row);
 }
 panel.append(section);
 const historySection=node('div','igc-act-section');
 historySection.append(node('div','igc-act-history-head','Historial de acciones · esta cuenta'));
 const history=node('div','igc-act-history');history.id='igcActHistory';
 history.setAttribute('aria-label','Últimos 15 resultados guardados del robot');
 historySection.append(history);panel.append(historySection);
 panel.append(node('p','igc-act-muted',
  'Diario de acciones del robot, no sumado al historial manual. Filtrar por procedencia no revalida entradas contradictorias. Cada OK de origen robot se cuenta una sola vez; advertencias anteriores conservan su fecha. Los OK antiguos sin origen identificado permanecen separados.'));
 const refreshButton=node('button',null,'Actualizar estadísticas');refreshButton.type='button';
 refreshButton.id='igcActRefresh';refreshButton.addEventListener('click',refresh);panel.append(refreshButton);
 const status=node('div','igc-act-status','Consulta de solo lectura; no inicia robots.');
 status.id='igcActStatus';status.setAttribute('role','status');panel.append(status);
 sectionRoot.append(panel);
 window.igcAutomationActivityRefresh=refresh;
 refresh();
 return true;
}
function setup(){
 if(!mount()){
   const watcher=new MutationObserver(()=>{if(mount())watcher.disconnect()});
   watcher.observe(document.documentElement,{childList:true,subtree:true});
 }
 window.setInterval(()=>{
   const panel=$('igcAutomationActivityPanel');
   if(panel&&panel.getClientRects().length)refresh();
 },15000);
 // Detect a changed pinned account promptly without polling the robot API.
 // Read-only DOM state check; journal requests occur only on a real change.
 window.setInterval(()=>{
   const panel=$('igcAutomationActivityPanel');
   if(!panel)return;
   const ctx=context();
   if(ctx.owner!==owner||ctx.active!==lastActive||ctx.generation!==lastGeneration||
      registrySignature(ctx)!==lastKey)refresh();
 },1000);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});
else setup();
})();
</script>
"""