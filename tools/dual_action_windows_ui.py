"""Windows-only, integrated two-account robot-control surface.

The original 1+ MB HTML remains untouched: the native launcher inserts this
small auditable panel *only* for the standard Windows edition. No separate
frontend state/journal, no auto-click, no secret in visible DOM.
"""
DUAL_ACTION_PANEL = r"""
<style>
#igcDualActionWorkspacePanel{margin:16px 0;padding:18px;border:1px solid rgba(120,156,192,.28);
border-radius:16px;background:linear-gradient(145deg,#111f30,#131721);color:#e9f0f8;font:inherit}
#igcDualActionWorkspacePanel h3{margin:0 0 5px;font-size:16px;color:#f4f7ff}
#igcDualActionWorkspacePanel .igc-daw-sub{font-size:12px;color:#9cadbe;line-height:1.5}
#igcDualActionWorkspacePanel .igc-daw-header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:space-between}
#igcDualActionWorkspacePanel .igc-daw-actions{display:flex;gap:8px;flex-wrap:wrap}
#igcDualActionWorkspacePanel button{background:#1e3348;border:1px solid #38536a;border-radius:9px;
color:#f0f6ff;padding:9px 12px;font:inherit;font-size:12px;cursor:pointer}
#igcDualActionWorkspacePanel button:hover{background:#29465d}
#igcDualActionWorkspacePanel button:disabled{opacity:.48;cursor:not-allowed}
#igcDualActionWorkspacePanel button.igc-daw-stop{border-color:#9d6c55;color:#ffd8bd}
#igcDualActionWorkspacePanel .igc-daw-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
#igcDualActionWorkspacePanel .igc-daw-card{background:rgba(9,16,26,.56);
border:1px solid #33465a;border-radius:12px;padding:14px;min-width:0}
#igcDualActionWorkspacePanel .igc-daw-account{font-size:13px;font-weight:750;overflow-wrap:anywhere}
#igcDualActionWorkspacePanel .igc-daw-meta{font-size:12px;color:#9eb1c5;margin:6px 0 10px;overflow-wrap:anywhere}
#igcDualActionWorkspacePanel .igc-daw-status{font-size:12px;line-height:1.5;
padding:8px 10px;background:#111b28;border-radius:7px;min-height:24px;overflow-wrap:anywhere}
#igcDualActionWorkspacePanel .igc-daw-controls{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px;align-items:center}
#igcDualActionWorkspacePanel select{max-width:100%;min-height:34px;background:#192b3c;border:1px solid #466077;
border-radius:8px;color:#f0f6ff;font:inherit;font-size:12px;padding:5px 7px}
#igcDualActionWorkspacePanel .igc-daw-new{margin-top:14px;border-top:1px solid #33465a;padding-top:12px}
#igcDualActionWorkspacePanel .igc-daw-new h4{font-size:13px;margin:0 0 5px;color:#e9f0f8}
#igcDualActionWorkspacePanel .igc-daw-new textarea{box-sizing:border-box;width:100%;min-height:74px;resize:vertical;background:#142638;
border:1px solid #466077;border-radius:8px;color:#f0f6ff;font:inherit;font-size:12px;padding:9px}
#igcDualActionWorkspacePanel .igc-daw-pace{display:flex;gap:9px;flex-wrap:wrap;margin:10px 0}
#igcDualActionWorkspacePanel .igc-daw-pace label{display:flex;align-items:center;gap:5px;font-size:12px;color:#a9bfd2}
#igcDualActionWorkspacePanel .igc-daw-pace input{background:#142638;border:1px solid #466077;color:#e9f0f8;
border-radius:7px;width:58px;font:inherit;font-size:12px;padding:6px}
#igcDualActionWorkspacePanel .igc-daw-new-note{font-size:12px;color:#a9bfd2;margin-top:8px}
#igcDualActionWorkspacePanel .igc-daw-mode{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
font-size:12px;color:#b5c8dc;padding:10px 12px;border:1px solid #41546c;border-radius:10px}
#igcDualActionWorkspacePanel .igc-daw-mode input{accent-color:#87b6eb;width:16px;height:16px}
#igcDualActionWorkspacePanel .igc-daw-mode small{display:block;flex-basis:100%;color:#9eb1c5;line-height:1.45}
#igcDawCompletionModal[hidden]{display:none}
#igcDawCompletionModal{position:fixed;inset:0;background:rgba(0,0,0,.76);
z-index:2147483635;display:flex;justify-content:center;align-items:center;padding:16px}
#igcDawCompletionModal .igc-daw-modal-card{width:min(570px,94vw);max-height:83vh;
overflow-y:auto;background:#142236;border:1px solid #4a6582;box-shadow:0 16px 55px #000b;
border-radius:15px;padding:20px;color:#ecf4ff}
#igcDawCompletionModal .igc-daw-modal-head{display:flex;justify-content:space-between;gap:12px;align-items:center}
#igcDawCompletionModal h3{font-size:16px;margin:0}
#igcDawCompletionModal .igc-daw-review-list{max-height:220px}
#igcDualActionWorkspacePanel .igc-daw-review-list{display:grid;gap:5px;margin-top:12px;max-height:260px;overflow:auto}
#igcDualActionWorkspacePanel .igc-daw-review-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:5px;
padding:7px 9px;border:1px solid #34445a;border-radius:7px;background:#142032;font-size:12px;overflow-wrap:anywhere}
#igcDualActionWorkspacePanel .igc-daw-review-row small{grid-column:1/-1;color:#98b0c7}
#igcDualActionWorkspacePanel .igc-daw-reviewed{border-left:3px solid #40ad75}
#igcDualActionWorkspacePanel .igc-daw-no-change{border-left:3px solid #6ea9d9}
#igcDualActionWorkspacePanel .igc-daw-uncertain{border-left:4px solid #e28a57;background:#2c231f}
#igcDualActionWorkspacePanel .igc-daw-unresolved{border-left:3px solid #d9a43c}
#igcDualActionWorkspacePanel .igc-daw-unavailable{border-left:3px solid #8797a9}
#igcDualActionWorkspacePanel .igc-daw-review-search{width:100%;box-sizing:border-box;min-height:34px;
background:#142638;border:1px solid #466077;border-radius:8px;color:#e9f0f8;
font:inherit;font-size:12px;padding:7px 9px;margin:8px 0 3px}
#igcDualActionWorkspacePanel .igc-daw-page-rows{display:grid;gap:5px}
#igcDualActionWorkspacePanel .igc-daw-pager{display:flex;flex-wrap:wrap;gap:8px;align-items:center;
justify-content:space-between;padding:9px 3px;color:#a9bed2;font-size:12px}
#igcDualActionWorkspacePanel .igc-daw-pager button{min-height:34px}
#igcDualActionWorkspacePanel .igc-daw-pager-count{font-variant-numeric:tabular-nums}
#igcDualActionWorkspacePanel .igc-daw-note{font-size:12px;margin:12px 0 0;color:#a9bed2;
overflow-wrap:anywhere;white-space:pre-line}
@media(max-width:650px){#igcDualActionWorkspacePanel .igc-daw-grid{grid-template-columns:minmax(0,1fr)}}
</style>
<script>
(function(){
'use strict';
if(window.__igcDualActionPanelLoaded)return;
window.__igcDualActionPanelLoaded=true;
const PREFIX='/api/actions/dual-action-workspaces/';
const PROFILE=/^(?:legacy|ig_[a-z0-9_-]{8,64})$/;
const OWNER=/^u_[a-z0-9]+_[0-9]{1,4}$/;
const HANDLE=/^[a-z0-9._]{1,30}$/i;
let linked=null, activeBusy=false, savedReviews={}, preparedNew={};
// A slow read-only/API request in lane A must not freeze lane B's controls.
let laneBusy=new Set(), laneGlobalControlState=null;
// Pausing a running account is independent from the other lane's busy UI.
let lanePauseBusy=new Set();
let laneSnapshots={}, completionAcknowledged={}, completionQueue=[], completionShowing=false;
let statusPolling=false,restoreInFlight=false,restoreDone=false,restoreOwner='';
const $=(id)=>document.getElementById(id);
function el(tag,className,text){
  const x=document.createElement(tag);if(className)x.className=className;
  if(text!==undefined)x.textContent=String(text);return x;
}
function cap(){
  const m=(location.hash||'').match(/(?:^|[&#])igc-robot=(\d{1,5})\.([A-Za-z0-9_-]{20,256})/);
  if(!m)return null;
  const port=Number(m[1]);return port>=1&&port<=65535?{port,token:m[2]}:null;
}
function pair(){
  const p=window.IGC_INSTAGRAM_PROFILES;
  if(!p||!OWNER.test(p.owner||''))throw Error('Inicia sesión en InstaCleaner para usar dos cuentas.');
  const owner=p.owner,select=$('igcDualSecondary');
  const first=p.active,second=select&&select.value;
  const reg=Array.isArray(p.accounts)?p.accounts:JSON.parse(
    localStorage.getItem('igc_multi_profile_registry_cache_'+owner)||'[]');
  function lookup(account){
    if(!PROFILE.test(account||''))throw Error('Selecciona dos perfiles de Instagram registrados.');
    const match=reg.find(x=>(x.account_key||x.account)===account);
    const handle=match&&(match.username||match.expected_handle);
    if(!handle||!HANDLE.test(handle))throw Error('Falta @usuario verificado para '+account+'.');
    return {account,expected_handle:handle.toLowerCase()};
  }
  const a=lookup(first),b=lookup(second);
  if(a.account===b.account||a.expected_handle===b.expected_handle)
    throw Error('Selecciona dos cuentas diferentes en el selector superior.');
  return {owner,primary:a,secondary:b};
}
function notice(message){const x=$('igcDualActionWorkspaceFeedback');if(x)x.textContent=message;}
async function api(path,body){
  const auth=cap();if(!auth)throw Error('Abre la app nativa de Windows para conectar los robots.');
  const opts={headers:{'X-IGC-Bridge-Token':auth.token,'Content-Type':'application/json'}};
  if(body!==undefined){opts.method='POST';opts.body=JSON.stringify(body)}
  const res=await fetch('http://127.0.0.1:'+auth.port+PREFIX+path,opts);
  const value=await res.json();
  if(!res.ok)throw Error(String(value.error||'Error de sesión del robot').slice(0,200));
  return value;
}
function parseTargets(text){
  const parts=String(text||'').split(/[\s,;]+/).filter(Boolean);
  if(!parts.length||parts.length>1000)throw Error('Escribe entre 1 y 1000 @usuarios exactos.');
  const names=parts.map(x=>x.replace(/^@/,'').toLowerCase());
  if(names.some(x=>!HANDLE.test(x)))throw Error('Hay un @usuario inválido; corrige la lista antes de revisar.');
  if(new Set(names).size!==names.length)
    throw Error('Hay usuarios duplicados; no se eliminarán silenciosamente. Corrige la lista.');
  return names;
}
function markStarted(account,task){
  if(!linked||!account)return;
  completionAcknowledged[account]=false;
  // A start-one acknowledgement proves only authorization, NOT that the
  // background worker actually ran. Never present an idle status as completion.
  laneSnapshots[account]={running:false,observedRunning:false,awaitingStart:true,
    startedAt:Date.now(),state:'starting',task};
}
function enqueueCompletion(item){
  if(completionAcknowledged[item.account])return;
  completionAcknowledged[item.account]=true;
  completionQueue.push(item);
  displayNextCompletion();
}
function dismissCompletion(){
  const modal=$('igcDawCompletionModal');if(modal)modal.hidden=true;
  completionShowing=false;
  displayNextCompletion();
}
function displayNextCompletion(){
  const modal=$('igcDawCompletionModal');
  if(!modal||completionShowing||!completionQueue.length)return;
  const done=completionQueue.shift();completionShowing=true;
  const content=el('div','igc-daw-modal-card');
  const head=el('div','igc-daw-modal-head');
  head.append(el('h3',null,(done.source==='saved'?
    'Revisión guardada · @':'Tanda detenida o finalizada · @')+done.handle));
  const close=el('button',null,'Cerrar');close.type='button';
  close.addEventListener('click',dismissCompletion);head.append(close);
  content.append(head);
  content.append(el('p','igc-daw-sub',done.source==='saved'?
    'Cuenta '+done.account+' · '+done.task+
    ' · resumen del historial original (sólo lectura). No se inició Chrome ni se aprobó ningún clic.':
    'Cuenta '+done.account+' · '+done.task+' · '+done.state.toUpperCase()+
    ' · '+done.processed+' procesados (no necesariamente OK) · '+done.pending+' pendientes · '+
    done.issues+' requieren atención. No se aprobó ni repitió ningún clic.'));
  const list=el('div','igc-daw-review-list');list.setAttribute('aria-label',
    'Resultados originales de la tanda de esta cuenta');
  list.append(el('div','igc-daw-note','Consultando el historial local, sin tocar Instagram…'));
  content.append(list);
  const actions=el('div','igc-daw-controls');
  const inspect=el('button',null,'Revisar lista completa');
  inspect.type='button';inspect.addEventListener('click',()=>{
    const index=done.i;dismissCompletion();
    const button=$('igcDawReview'+index);if(button)button.click();
  });
  actions.append(inspect);content.append(actions);modal.replaceChildren(content);modal.hidden=false;
  // Read-only saved WAL; never use a live relationship or mutation endpoint
  // to populate the modal. A missing original cohort remains unresolved.
  if(!['unfollow','cancel'].includes(done.task))return;
  const read=done.savedBatch?
    Promise.resolve({owner:done.owner,account:done.account,task:done.task,
      batch:done.savedBatch}):
    api('review-one',{owner:done.owner,account:done.account,task:done.task});
  read.then(value=>{
      if(!completionShowing||modal.hidden||!content.isConnected)return;
      if(value?.owner!==done.owner||value?.account!==done.account||
         value?.task!==done.task)throw Error('La revisión no corresponde a esta cuenta.');
      list.replaceChildren();
      const batch=value.batch;
      if(!batch){list.append(el('div','igc-daw-note',
        'No hay una tanda pendiente en el historial local. Revisa el registro de acciones.'));return}
      // Reuse the original Review-first presentation; never reorder batch.targets.
      const names=prioritizedSavedReviewTargets(batch);
      const results=batch.action_results||{};
      showSavedResultPages(list,names,username=>{
        const result=results[username]||{},state=String(result.status||'pending');
        const row=el('div','igc-daw-review-row '+savedActionClass(result));
        row.append(el('span',null,'@'+String(username)),
          el('span',null,savedActionLabel(result)));
        row.append(el('small',null,String(result.at||'sin fecha')+' · '+
          state+' · '+String(result.message||'Sin diagnóstico guardado').slice(0,200)));
        return row;
      });
    })
    .catch(()=>{if(content.isConnected){list.replaceChildren();
      list.append(el('div','igc-daw-note',
      'No se pudo leer el historial. Abre Revisar pendientes manualmente.'));}});
}
// Saved WAL distinguishes a CONFIRMED relationship action from a profile
// already in the requested state (where the robot did NOT click). A pending
// possible-click is never shown as green or auto-approved.
// Keep large original saved cohorts inspectable without rendering 1,000 DOM
// rows at once. This is READ ONLY: paging cannot start/approve/replay actions,
// does not sort or mutate WAL targets, and never fetches another account.
const SAVED_RESULTS_PER_PAGE=50;
function showSavedResultPages(container,names,renderRow,intro=''){
 let index=0,term='';
 const total=names.length;
 container.replaceChildren();
 if(intro)container.append(el('div','igc-daw-note',intro));
 // Search is read-only over this exact saved cohort. Keep the input outside
 // the dynamically replaced page so typing never loses keyboard focus.
 if(total>SAVED_RESULTS_PER_PAGE){
   const find=el('input','igc-daw-review-search');
   find.type='search';find.placeholder='Buscar @usuario en esta tanda';
   find.setAttribute('aria-label','Buscar usuario en resultados guardados');
   find.autocomplete='off';
   find.addEventListener('input',()=>{
     term=find.value.trim().replace(/^@/,'').toLowerCase();
     index=0;drawPage();
   });
   container.append(find);
 }
 const rows=el('div','igc-daw-page-rows');
 const pager=el('div','igc-daw-pager');
 container.append(rows,pager);
 function drawPage(){
   if(!container.isConnected)return;
   const visible=term?names.filter(username=>
     String(username).toLowerCase().includes(term)):names;
   const size=visible.length,pages=Math.max(1,Math.ceil(size/SAVED_RESULTS_PER_PAGE));
   index=Math.max(0,Math.min(index,pages-1));
   const start=index*SAVED_RESULTS_PER_PAGE;
   rows.replaceChildren();
   if(!size)rows.append(el('div','igc-daw-note',
     total?'Sin coincidencias en esta tanda.':'Sin objetivos guardados.'));
   else for(const username of visible.slice(start,start+SAVED_RESULTS_PER_PAGE))
     rows.append(renderRow(username));
   pager.replaceChildren();
   const counter=el('span','igc-daw-pager-count',size?
     'Resultados '+(start+1)+'–'+Math.min(start+SAVED_RESULTS_PER_PAGE,size)+
     ' de '+size+(term?' (de '+total+' originales)':'')+
     ' · página '+(index+1)+' de '+pages:
     '0 resultados'+(term?' (de '+total+' originales)':''));
   counter.setAttribute('aria-live','polite');
   if(pages>1){
     const prev=el('button','igc-daw-page-prev','Anteriores');
     prev.type='button';prev.disabled=index===0;
     prev.setAttribute('aria-label','Página anterior de resultados');
     prev.addEventListener('click',()=>{index--;drawPage();container.scrollTop=0});
     pager.append(prev);
   }
   pager.append(counter);
   if(pages>1){
     const jump=el('select','igc-daw-page-jump');
     jump.setAttribute('aria-label','Ir a página de resultados');
     for(let n=1;n<=pages;n++){
       const option=el('option',null,'Página '+n);option.value=String(n);
       jump.append(option);
     }
     jump.value=String(index+1);
     jump.addEventListener('change',()=>{
       index=Number(jump.value)-1;drawPage();container.scrollTop=0;
     });
     const next=el('button','igc-daw-page-next','Siguientes');
     next.type='button';next.disabled=index===pages-1;
     next.setAttribute('aria-label','Página siguiente de resultados');
     next.addEventListener('click',()=>{index++;drawPage();container.scrollTop=0});
     pager.append(jump,next);
   }
 }
 drawPage();
}
function savedActionLabel(result){
 const status=String(result?.status||'pending');
 if(result?.possible_click===true&&status!=='ok')
   return 'REVIEW · CLIC INCIERTO';
 if(status==='ok')return 'OK · ACCIÓN CONFIRMADA';
 if(status==='already_not_following')return 'SIN ACCIÓN · YA NO SIGUES';
 if(status==='already_not_requested')return 'SIN ACCIÓN · SIN SOLICITUD';
 if(status==='profile_unavailable')return 'PERFIL NO DISPONIBLE';
 if(status==='pending')return 'PENDIENTE · NO PROCESADO';
 if(result?.safe_no_click===true)return 'REVIEW · SIN CLIC';
 return 'REVIEW · '+status.toUpperCase();
}
function savedActionClass(result){
 const status=String(result?.status||'pending');
 if(result?.possible_click===true&&status!=='ok')return 'igc-daw-uncertain';
 if(status==='ok')return 'igc-daw-reviewed';
 if(['already_not_following','already_not_requested'].includes(status))
   return 'igc-daw-no-change';
 if(status==='profile_unavailable')return 'igc-daw-unavailable';
 return 'igc-daw-unresolved';
}
// Reorder the VIEW only; preserve owner-approved batch.targets and WAL.
// Uncertain post-click rows are the most urgent manual review; proven
// no-click anomalies follow; untouched rows precede the blue no-action and
// green confirmed outcomes. Within a class preserve original cohort order.
function prioritizedSavedReviewTargets(batch){
 const results=batch?.action_results||{};
 return (Array.isArray(batch?.targets)?batch.targets:[])
  .map((username,index)=>{
   const entry=results[username]||{},status=String(entry.status||'pending');
   const priority=entry.possible_click===true&&status!=='ok'?0:
     ['ok','already_not_following','already_not_requested'].includes(status)?
       (status==='ok'?5:4):
     status==='profile_unavailable'?3:status==='pending'?2:1;
   return {username,index,priority};
  }).sort((a,b)=>a.priority-b.priority||a.index-b.index)
  .map(x=>x.username);
}
function card(account,i){
  const outer=el('section','igc-daw-card');
  outer.dataset.lane=String(i);
  outer.append(el('div','igc-daw-account',account.expected_handle?'@'+account.expected_handle:'Cuenta '+(i+1)));
  outer.append(el('div','igc-daw-meta',account.account||'Sin vincular'));
  const status=el('div','igc-daw-status','Sin sesión de acciones vinculada');
  status.id='igcDawStatus'+i;outer.append(status);
  const controls=el('div','igc-daw-controls');
  const task=el('select');task.id='igcDawTask'+i;
  for(const [val,name] of [['unfollow','Unfollow'],['cancel','Cancel Pending']]){
    const o=el('option',null,name);o.value=val;task.append(o);
  }
  controls.append(task);
  task.addEventListener('change',()=>{
    savedReviews[i]=null;preparedNew[i]=null;
    const old=$('igcDawReviewList'+i),fresh=$('igcDawNewList'+i);
    if(old)old.replaceChildren();if(fresh)fresh.replaceChildren();
  });
  const review=el('button',null,'Revisar pendientes');review.type='button';
  review.id='igcDawReview'+i;review.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked)throw Error('Primero vincula las dos cuentas de Chrome.');
    const bound=linked,selectedTask=task.value,account=bound[i].account;
    const result=await api('review-one',{owner:bound.owner,account,
      task:selectedTask});
    if(linked!==bound||task.value!==selectedTask)return;
    if(result?.owner!==bound.owner||result?.account!==account||
       result?.task!==selectedTask)
      throw Error('El historial recibido pertenece a otra cuenta.');
    const batch=result.batch;savedReviews[i]={task:selectedTask,batch};
    const targets=batch&&batch.action_results||{};
    const select=$('igcDawTarget'+i),list=$('igcDawReviewList'+i);
    select.replaceChildren();list.replaceChildren();
    const ordered=prioritizedSavedReviewTargets(batch).filter(x=>HANDLE.test(x));
    for(const username of ordered){
      const outcome=targets[username]||{status:'pending'},
        status=String(outcome.status||'pending');
      const reviewed=['ok','already_not_following','already_not_requested'].includes(status);
      const unavailable=status==='profile_unavailable'&&outcome.possible_click!==true;
      // Populate ALL unresolved options, even those on later display pages.
      // Green and proven no-action outcomes are not action candidates.
      if(status!=='ok'&&(!reviewed||outcome.possible_click===true)&&!unavailable){
        const o=el('option',null,'@'+username+' · '+status);
        o.value=username;select.append(o);
      }
    }
    showSavedResultPages(list,ordered,username=>{
      const outcome=targets[username]||{status:'pending'};
      const row=el('div','igc-daw-review-row '+savedActionClass(outcome));
      row.append(el('span',null,'@'+username),el('span',null,savedActionLabel(outcome)));
      row.append(el('small',null,'Acción: '+String(outcome.at||'sin fecha registrada')+
        ' · '+String(outcome.message||'sin confirmación').slice(0,140)));
      return row;
    },'⚠ Clic incierto primero · ⚠ Sin clic · ○ Pendiente · ◌ No disponible · '+
      '◇ Sin acción · ✓ Acción confirmada al final');
    notice(batch?('Cuenta '+(i+1)+': '+Object.keys(targets).length+
      ' perfiles de la tanda '+String(batch.id||'').slice(0,30)+
      '. Inspección manual; no se repite ningún clic.'):
      'Esta cuenta no tiene ninguna tanda pendiente.');
  }));
  controls.append(review);
  // Completion polling sees only workers observed in this UI session. A reload
  // or late re-link can miss the terminal transition. Recover the original
  // saved review ON DEMAND, without assuming a worker ran or approving clicks.
  const savedSummary=el('button',null,'Ver resumen guardado');
  savedSummary.type='button';savedSummary.id='igcDawSavedSummary'+i;
  savedSummary.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked)throw Error('Vincula ambas cuentas antes de revisar su historial.');
    const bound=linked,selectedTask=task.value,account=bound[i].account;
    if(!['unfollow','cancel'].includes(selectedTask))
      throw Error('Selecciona Unfollow o Cancel Pending.');
    const answer=await api('review-one',{owner:bound.owner,account,
      task:selectedTask});
    if(linked!==bound||task.value!==selectedTask)return;
    if(answer?.owner!==bound.owner||answer?.account!==account||
       answer?.task!==selectedTask)
      throw Error('El historial recibido pertenece a otra cuenta.');
    if(!answer.batch){
      notice('No hay una tanda pendiente guardada de esta cuenta y tarea.');
      return;
    }
    completionQueue.push({owner:bound.owner,account,
      handle:bound[i].expected_handle,i,task:selectedTask,state:'saved',
      source:'saved',savedBatch:answer.batch});
    displayNextCompletion();
  }));
  controls.append(savedSummary);
  const continueSaved=el('button',null,'Continuar tanda guardada');
  continueSaved.id='igcDawContinue'+i;continueSaved.type='button';
  continueSaved.addEventListener('click',()=>performLane(i,async()=>{
    // No browser automation until the human has read the exact disk-backed
    // Pending batch and explicitly approved owner+task+original targets.
    if(!linked||!savedReviews[i]||savedReviews[i].task!==task.value
       ||!savedReviews[i].batch)
      throw Error('Primero carga la tanda guardada de esta cuenta.');
    const record=savedReviews[i].batch;
    const targets=record.targets;
    if(!Array.isArray(targets)||!targets.length||targets.length>1000
       ||targets.some(x=>typeof x!=='string'||!HANDLE.test(x))
       ||new Set(targets).size!==targets.length)
      throw Error('La tanda guardada tiene objetivos inválidos. Revisión manual obligatoria.');
    const account=linked[i].account,handle=linked[i].expected_handle;
    const done=record.action_results||{};
    const pending=targets.filter(x=>!Object.prototype.hasOwnProperty.call(done,x)
      ||done[x]?.status==='pending').length;
    if(!pending)throw Error('La tanda no tiene perfiles vírgenes; revisa los amarillos manualmente.');
    const input=(id,def,min,max)=>{
      const raw=$(id)?.value;
      if(raw===undefined||raw==='')return def;
      const n=Number(raw);
      // Invalid numbers must stop BEFORE asking the owner to approve the
      // frozen cohort. Silently falling back to 30 could run extra profiles.
      if(!Number.isInteger(n)||n<min||n>max)
        throw Error('Corrige el tamaño de tanda, espera y descanso; sólo enteros dentro del rango.');
      return n;
    };
    const batchSize=input('igcAutoBatch',Math.min(targets.length,30),1,1000);
    // batch_size controls pacing/rest, NOT the number of approved saved
    // targets. An old 40-target cohort must never be mistaken for a NEW 10.
    const sizeWarning=targets.length>batchSize?
      ' ATENCIÓN: el tamaño configurado '+batchSize+
      ' NO reduce los '+targets.length+' objetivos de la tanda guardada. '+
      'Para trabajar sólo con una lista nueva, usa Nueva tanda. ':'';
    if(!confirm('Cuenta @'+handle+' · '+task.value+' · '+targets.length+
      ' objetivos originales, de los cuales '+pending+' no tienen resultado. '+
      'Tamaño configurado de sublote: '+batchSize+'.'+sizeWarning+
      ' Modo '+(linked.parallel?'PARALELO':'serial')+
      '. Se conservarán los clics inciertos sin repetirlos. ¿Continuar ESTA tanda guardada?'))return;
    // This is an explicit owner attestation, not an independent live check.
    // Followback audit must have been completed before authorizing Unfollow.
    if(task.value==='unfollow'&&!confirm('¿Confirmas que ya verificaste la lista COMPLETA '+
      'de seguidores de @'+handle+'? Sin esa evidencia NO se iniciará Unfollow.'))return;
    const gapSeconds=input('igcAutoGap',10,1,600);
    const restMinutes=input('igcAutoRest',5,0,240);
    const action={owner:linked.owner,account,expected_handle:handle,
      task:task.value,targets:targets.slice(),batch_id:record.id,
      batch_size:batchSize,gap_seconds:gapSeconds,rest_minutes:restMinutes,
      protected:[],tab_flow:'sequential',followers_evidence:task.value==='unfollow',
      confirmation:task.value+':'+targets.length};
    const command={owner:linked.owner,account,action,
      confirmation:'action-workspace-start:'+linked.owner+':'+account+':'+task.value};
    if(linked.parallel)command.parallel_action_confirmation=
      'parallel-action-workspace-start:'+linked.owner+':'+account+':'+task.value;
    const result=await api('start-one',command);
    markStarted(account,task.value);
    notice('Tanda original autorizada para @'+handle+'. Estado: '+
      String(result.status||'starting')+'. Modo: '+(linked.parallel?'paralelo explícito':'serial')+'.');
    await statusUpdate();
  }));
  controls.append(continueSaved);
  const cancelBatch=el('button','igc-daw-stop','Cancelar tanda (conservar historial)');
  cancelBatch.type='button';cancelBatch.id='igcDawCancelBatch'+i;
  cancelBatch.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked||!savedReviews[i]||savedReviews[i].task!==task.value
       ||!savedReviews[i].batch)
      throw Error('Primero carga la tanda original de esta cuenta con Revisar pendientes.');
    const bound=linked,selectedTask=task.value,account=bound[i].account;
    const batch=savedReviews[i].batch;
    if(typeof batch.id!=='string'||!batch.id||batch.id.length>128
       ||!Array.isArray(batch.targets)||!batch.targets.length)
      throw Error('La tanda guardada no se puede identificar. No se canceló nada.');
    const unresolved=batch.targets.filter(name=>![
      'ok','already_not_following','already_not_requested'
    ].includes(batch.action_results?.[name]?.status)).length;
    if(!confirm('¿Cancelar SÓLO la tanda '+batch.id+' de @'+bound[i].expected_handle+
      ' ('+selectedTask+')? '+unresolved+' perfiles aún requieren atención. '+
      'Se detendrán futuras acciones de ESTA cuenta; los clics inciertos, '+
      'resultados originales y protecciones NO se borrarán. '+
      'La otra cuenta continuará por separado.'))return;
    const result=await api('cancel-batch-one',{
      owner:bound.owner,account,task:selectedTask,batch_id:batch.id,
      confirmation:'action-workspace-cancel:'+bound.owner+':'+account+':'+
        selectedTask+':'+batch.id
    });
    if(linked!==bound||task.value!==selectedTask)return;
    if(result?.owner!==bound.owner||result?.account!==account||
       result?.task!==selectedTask)
      throw Error('Confirmación de cancelación perteneciente a otra cuenta.');
    savedReviews[i]=null;preparedNew[i]=null;
    const original=$('igcDawReviewList'+i);
    if(original)original.replaceChildren();
    await statusUpdate();
    notice(result.status==='cancelling'?
      'Cancelación solicitada a @'+bound[i].expected_handle+
      '. El último perfil puede seguir en curso; consulta el estado hasta que termine.':
      'Tanda de @'+bound[i].expected_handle+
      ' cancelada y archivada. Resultados y clics inciertos conservados.');
  }));
  controls.append(cancelBatch);
  const approve=el('button',null,'Aprobar revisión');
  approve.id='igcDawApprove'+i;approve.type='button';
  approve.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked||!savedReviews[i]||savedReviews[i].task!==task.value
       ||!savedReviews[i].batch)
      throw Error('Carga la tanda exacta de esta cuenta antes de aprobar.');
    const batch=savedReviews[i].batch,results=batch.action_results||{},
      names=batch.targets||[];
    if(!Array.isArray(names)||!names.length||!batch.id
       ||names.some(x=>!results[x]||!results[x].status||results[x].status==='pending'))
      throw Error('La tanda tiene perfiles sin observación. Continúa o revisa antes de aprobar.');
    const account=linked[i].account,uncertain=names.filter(x=>![
      'ok','already_not_following','already_not_requested','profile_unavailable'
    ].includes(results[x].status)).length;
    if(!confirm('¿Marcar como revisada la tanda '+batch.id+' de @'+
      linked[i].expected_handle+'? '+uncertain+' resultados seguirán amarillos/pendientes '+
      'si no hay confirmación. Esto NO convierte acciones inciertas en OK.'))return;
    const result=await api('approve-one',{owner:linked.owner,account,task:task.value,
      batch_id:batch.id,confirmation:'action-workspace-approve:'+linked.owner+':'+
        account+':'+task.value+':'+batch.id});
    savedReviews[i]=null;
    await statusUpdate();
    notice('Revisión de @'+linked[i].expected_handle+' archivada. '+
      String((result.unresolved_usernames||[]).length)+
      ' perfiles permanecen sin confirmación; no serán reintentados.');
  }));
  controls.append(approve);
  const target=el('select');target.id='igcDawTarget'+i;controls.append(target);
  const open=el('button',null,'Abrir revisión');open.type='button';
  open.id='igcDawOpen'+i;open.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked||!savedReviews[i]||savedReviews[i].task!==task.value||!target.value)
      throw Error('Primero carga la tanda guardada en esta cuenta.');
    const account=linked[i].account,username=target.value;
    if(!confirm('Abrir @'+username+' únicamente en Chrome de '+linked[i].expected_handle+
      '? No se hará ningún unfollow.'))return;
    await api('open-review-one',{owner:linked.owner,account,task:task.value,
      username,confirmation:'action-workspace-review:'+linked.owner+':'+account+':'+username});
    notice('Revisión manual abierta para @'+username+'. Sin clic automatizado.');
  }));
  controls.append(open);
  const stop=el('button','igc-daw-stop','Pausar esta cuenta');stop.type='button';
  stop.id='igcDawStop'+i;stop.addEventListener('click',()=>performPause(i,async()=>{
    if(!linked)throw Error('Primero vincula las dos cuentas.');
    const bound=linked,account=bound[i].account;
    await api('pause-one',{owner:bound.owner,account,
      confirmation:'action-workspace-pause:'+bound.owner+':'+account});
    if(linked===bound)await statusUpdate();
  }));
  controls.append(stop);
  outer.append(controls);
  const history=el('div','igc-daw-review-list');history.id='igcDawReviewList'+i;
  history.setAttribute('aria-label','Resultados de la tanda de esta cuenta');
  outer.append(history);
  const newBox=el('section','igc-daw-new');
  newBox.append(el('h4',null,'Nueva tanda · sólo esta cuenta'));
  const caption=el('label','igc-daw-sub','@usuarios exactos, separados por saltos de línea, coma o espacio.');
  caption.setAttribute('for','igcDawNewTargets'+i);newBox.append(caption);
  const newInput=el('textarea');newInput.id='igcDawNewTargets'+i;
  newInput.rows=4;newInput.maxLength=42000;newInput.spellcheck=false;
  newInput.placeholder='@ejemplo.uno\n@ejemplo.dos';
  newInput.addEventListener('input',()=>{preparedNew[i]=null;
    const list=$('igcDawNewList'+i);if(list)list.replaceChildren();});
  newBox.append(newInput);
  const pace=el('div','igc-daw-pace');
  function setting(id,name,initial,min,max){
    const label=el('label',null,name);
    const field=el('input');field.id=id+i;field.type='number';
    field.min=String(min);field.max=String(max);field.step='1';
    field.value=String(initial);
    field.addEventListener('input',()=>{preparedNew[i]=null;});
    label.append(field);pace.append(label);
    return field;
  }
  const batchField=setting('igcDawNewBatch','Por tanda',20,1,1000);
  const gapField=setting('igcDawNewGap','Segundos entre perfiles',15,1,600);
  const restField=setting('igcDawNewRest','Descanso (min)',10,0,240);
  newBox.append(pace);
  const newControls=el('div','igc-daw-controls');
  const verify=el('button',null,'Verificar lista sin clics');
  verify.type='button';verify.id='igcDawNewVerify'+i;
  verify.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked)throw Error('Vincula primero ambas cuentas.');
    const targets=parseTargets(newInput.value),account=linked[i].account,
      handle=linked[i].expected_handle;
    const p=await api('preflight-new-one',{owner:linked.owner,account,
      expected_handle:handle,task:task.value,targets,
      confirmation:'action-workspace-preflight:'+linked.owner+':'+account+':'+task.value});
    const list=$('igcDawNewList'+i);list.replaceChildren();
    for(const result of p.targets||[]){
      const good=result.offline_evidence==='untouched';
      const row=el('div','igc-daw-review-row '+(good?'igc-daw-reviewed':'igc-daw-unresolved'));
      row.append(el('span',null,'@'+result.username),
        el('span',null,good?'NUEVO':'BLOQUEADO · '+result.offline_evidence));
      list.append(row);
    }
    const counts=p.evidence_counts||{};
    if(!p.read_only||p.actions_enabled!==false)
      throw Error('La verificación no es de sólo lectura. Se canceló la preparación.');
    preparedNew[i]={
      owner:linked.owner,account,handle,task:task.value,targets:targets.slice(),
      allowed:p.offline_untouched_only===true&&!p.unresolved_saved_cohort,
    };
    notice('Revisión guardada para @'+handle+': '+targets.length+' objetivos, '+
      (counts.untouched||0)+' nuevos, '+(targets.length-(counts.untouched||0))+
      ' bloqueados. Esta revisión NO hizo clics en Instagram.');
  }));
  newControls.append(verify);
  const start=el('button',null,'Iniciar tanda nueva');
  start.type='button';start.id='igcDawNewStart'+i;
  start.addEventListener('click',()=>performLane(i,async()=>{
    if(!linked)throw Error('Vincula primero ambas cuentas.');
    const exact=parseTargets(newInput.value),p=preparedNew[i];
    if(!p||!p.allowed||p.owner!==linked.owner||p.account!==linked[i].account
       ||p.handle!==linked[i].expected_handle||p.task!==task.value
       ||JSON.stringify(p.targets)!==JSON.stringify(exact))
      throw Error('La lista cambió, contiene bloqueados o no fue verificada. Repite la comprobación.');
    function number(field,min,max){
      const v=Number(field.value);
      if(!Number.isInteger(v)||v<min||v>max)
        throw Error('Corrige los valores de tanda, segundos y descanso antes de iniciar.');
      return v;
    }
    const batchSize=number(batchField,1,1000),
      gapSeconds=number(gapField,1,600),restMinutes=number(restField,0,240);
    const account=p.account,handle=p.handle;
    // The disk snapshot may have changed. Recheck the ORIGINAL exact list
    // before user confirmation, then ActionRobot.start rechecks under WAL.
    const fresh=await api('preflight-new-one',{owner:p.owner,account,
      expected_handle:handle,task:p.task,targets:exact,
      confirmation:'action-workspace-preflight:'+p.owner+':'+account+':'+p.task});
    if(!fresh.read_only||fresh.actions_enabled!==false||!fresh.offline_untouched_only
       ||fresh.unresolved_saved_cohort)
      throw Error('La lista ya no está intacta. Hay historial o una tanda pendiente.');
    if(!confirm('NUEVA tanda · @'+handle+' · '+p.task+' · '+exact.length+
       ' perfiles NUEVOS, de '+batchSize+' por tanda. Modo '+
       (linked.parallel?'PARALELO con la otra cuenta':'serial')+
       '. ¿Autorizar ESTA cuenta?'))return;
    if(p.task==='unfollow'&&!confirm('¿Verificaste la lista COMPLETA y actual '+
       'de seguidores de @'+handle+'? La prevalidación local no lo demuestra.'))return;
    preparedNew[i]=null;
    const action={owner:p.owner,account,expected_handle:handle,
      task:p.task,targets:exact,batch_size:batchSize,gap_seconds:gapSeconds,
      rest_minutes:restMinutes,protected:[],tab_flow:'sequential',
      followers_evidence:p.task==='unfollow',
      confirmation:p.task+':'+exact.length};
    const command={owner:p.owner,account,action,
      confirmation:'action-workspace-start:'+p.owner+':'+account+':'+p.task};
    if(linked.parallel)command.parallel_action_confirmation=
      'parallel-action-workspace-start:'+p.owner+':'+account+':'+p.task;
    const result=await api('start-one',command);
    markStarted(account,p.task);
    notice('Tanda nueva de @'+handle+' enviada a su Chrome exclusivo. Estado: '+
      String(result.status||'starting')+'. Modo: '+(linked.parallel?'paralelo explícito':'serial')+'.');
  }));
  newControls.append(start);newBox.append(newControls);
  const newList=el('div','igc-daw-review-list');newList.id='igcDawNewList'+i;
  newList.setAttribute('aria-label','Prevalidación local de los objetivos de esta cuenta');
  newBox.append(newList);
  newBox.append(el('div','igc-daw-new-note',
    'Esta comprobación usa el historial local, NO verifica Follow en tiempo real. '+
    'El robot comprobará identidad, relación y protecciones antes de cualquier clic.'));
  outer.append(newBox);
  return outer;
}
function draw(p){
  const target=$('igcDawGrid');if(!target)return;
  target.replaceChildren();
  if(p){linked={0:p.primary,1:p.secondary,owner:p.owner,
    parallel:p.parallel===true};savedReviews={};preparedNew={};
    laneSnapshots={};completionAcknowledged={};completionQueue=[];completionShowing=false;
    if($('igcDawCompletionModal'))$('igcDawCompletionModal').hidden=true;}
  for(let i=0;i<2;i++)target.append(card(linked?linked[i]:{},i));
}
function syncGlobalLaneControls(){
  const controls=['igcDawConfigure','igcDawRefresh','igcDawParallelOptIn']
    .map(id=>$(id)).filter(Boolean);
  if(laneBusy.size&&laneGlobalControlState===null){
    laneGlobalControlState=controls.map(node=>({node,disabled:node.disabled}));
    for(const item of laneGlobalControlState)item.node.disabled=true;
  }else if(!laneBusy.size&&laneGlobalControlState!==null){
    for(const item of laneGlobalControlState)
      if(item.node.isConnected)item.node.disabled=item.disabled;
    laneGlobalControlState=null;
  }
}
async function performLane(i,fn){
  if(activeBusy||laneBusy.has(i))return;
  laneBusy.add(i);
  syncGlobalLaneControls();
  const lane=$('igcDawGrid')?.querySelector('[data-lane="'+i+'"]');
  const buttons=Array.from(lane?.querySelectorAll('button')||[])
    .filter(x=>!x.classList.contains('igc-daw-stop'));
  const disabled=buttons.map(button=>button.disabled);
  for(const button of buttons)button.disabled=true;
  try{await fn()}catch(e){
    notice('No se pudo confirmar la operación de esta cuenta: '+
      String(e.message||e).slice(0,140)+
      '. Una tanda autorizada podría seguir activa; revisa estado e historial antes de repetir.');
  }finally{
    laneBusy.delete(i);
    buttons.forEach((button,j)=>{if(button.isConnected)button.disabled=disabled[j]});
    syncGlobalLaneControls();
  }
}
async function perform(fn){
  if(activeBusy||laneBusy.size)return;
  activeBusy=true;
  const buttons=$('igcDualActionWorkspacePanel')?.querySelectorAll('button')||[];
  // A slow inspection/start for account A must never disable the emergency
  // Pause button for account B. Pause itself is guarded by a per-lane latch.
  for(const b of buttons)if(!b.classList.contains('igc-daw-stop'))b.disabled=true;
  try{await fn()}catch(e){
    // An accepted start command may already have launched the worker when a
    // later status GET fails. Never falsely claim no action occurred.
    notice('No se pudo confirmar la operación: '+String(e.message||e).slice(0,140)+
      '. Una tanda autorizada podría seguir activa; consulta estado e historial antes de repetir.');
  }
  finally{
    activeBusy=false;
    for(const b of buttons)if(!b.classList.contains('igc-daw-stop'))b.disabled=false;
  }
}
async function performPause(i,fn){
  if(lanePauseBusy.has(i))return;
  lanePauseBusy.add(i);
  const control=$('igcDawStop'+i);
  if(control)control.disabled=true;
  try{await fn()}
  catch(e){notice('No se pudo confirmar la pausa de esta cuenta: '+
    String(e.message||e).slice(0,190)+'. Consulta el estado; no repitas acciones a ciegas.')}
  finally{
    lanePauseBusy.delete(i);
    if(control)control.disabled=false;
  }
}
async function statusUpdate(silent=false,knownSnapshot=null){
  if(!linked)throw Error('Primero vincula los dos workspaces.');
  const current=linked;
  let x;
  try{
    x=knownSnapshot||await api('status?owner='+encodeURIComponent(current.owner));
  }catch(_){
    // A lost bridge is NOT evidence that either Chrome robot stopped. Never
    // leave stale RUNNING/PAUSED badges looking like freshly verified state.
    // Retain laneSnapshots and the original WAL; polling must keep retrying
    // a previously observed running worker after reconnect.
    if(linked===current){
      for(let i=0;i<2;i++){
        const label=$('igcDawStatus'+i);
        if(label)label.textContent='ESTADO NO VERIFICABLE · conexión con Chrome perdida. '+
          'La tanda podría seguir activa. No reinicies ni repitas acciones hasta consultar el historial.';
      }
      notice('Conexión perdida con el robot. Estado de ambas cuentas desconocido; '+
        'no se iniciaron clics nuevos. Consulta el historial antes de repetir.');
    }
    throw Error('No se pudo consultar el estado de los dos robots de Chrome.');
  }
  // If the owner reconfigured accounts during the request, do not associate
  // a stale account's state with a new pair of Instagram sessions.
  if(linked!==current)return x;
  if(x.owner&&x.owner!==current.owner)throw Error('Estado de otra cuenta bloqueado.');
  for(let i=0;i<2;i++){
    const scope=linked[i],info=(x.lanes||[]).find(y=>y.account===scope.account);
    const label=$('igcDawStatus'+i);
    // A server that reports the same workspace key but a DIFFERENT Instagram
    // login must never feed this account's badge or completion/Review queue.
    if(info&&typeof info.expected_handle==='string'&&
       info.expected_handle.toLowerCase()!==scope.expected_handle){
      if(label)label.textContent='IDENTIDAD NO VERIFICADA · la cuenta Chrome ya no coincide con @'+
        scope.expected_handle+'. Detén los robots y revisa las sesiones antes de continuar.';
      notice('El robot devolvió otra identidad para la cuenta '+scope.account+
        '. No se mostró ningún resultado ni se inició una acción nueva.');
      continue;
    }
    const ownerVisits=info&&Number.isSafeInteger(info.owner_profile_visits)&&
      info.owner_profile_visits>=0?info.owner_profile_visits:null;
    const siblingProofs=info&&Number.isSafeInteger(info.owner_sibling_proofs)&&
      info.owner_sibling_proofs>=0?info.owner_sibling_proofs:null;
    const currentProfile=typeof info?.current_profile==='string'&&HANDLE.test(info.current_profile)
      ? info.current_profile:'';
    const diagnostic=typeof info?.message==='string'
      ? info.message.replace(/[\r\n\x00-\x1f]+/g,' ').slice(0,180):'';
    // After a Windows restart there is no in-memory task, but its actual
    // original approved batch still lives in the per-account action journal.
    // Read-only labels must show 40 original vs 10 currently selected, without
    // silently restarting either relationship action.
    const count=(value)=>Number.isSafeInteger(value)&&value>=0&&value<=1000?value:'?';
    const savedText=(Array.isArray(info?.saved_batches)?info.saved_batches:[])
      .slice(0,2).map(batch=>{
        const taskLabel=batch?.task==='unfollow'?'Unfollow':
          batch?.task==='cancel'?'Cancel Pending':'tarea no verificable';
        if(batch?.unverifiable===true)
          return ' · HISTORIAL GUARDADO NO VERIFICABLE ('+taskLabel+
            '). Revisar registros antes de reanudar; ningún clic nuevo.';
        if(!batch||typeof batch.batch_id!=='string')return '';
        const batchId=batch.batch_id.replace(/[\r\n\x00-\x1f]/g,'').slice(0,90);
        return ' · TANDA GUARDADA (no ejecutándose): '+taskLabel+
          ' · Lote '+batchId+
          ' · Original '+count(batch.original_total)+
          ' · Selección actual '+count(batch.current_total)+
          ' · Sin registro '+count(batch.untouched)+
          ' · Review/advertencias '+count(batch.warnings)+
          ' · Acciones confirmadas '+count(batch.confirmed_clicks)+
          ' · Ya resueltos (sin clic) '+count(batch.already_resolved_no_click);
      }).join('');
    if(label)label.textContent=info?
      (String(info.state||'idle').toUpperCase()+' · '+(info.running?'Robot activo':'Robot detenido')+
       ' · '+String(info.task||'sin tarea')+' · '+String(info.processed||0)+' procesados · '+
       String(info.issues||0)+' pendientes de revisión'+
       (currentProfile?' · '+(info.running?'Perfil actual':'Último perfil')+': @'+currentProfile:'')+
       (diagnostic?' · Diagnóstico: '+diagnostic:'')+
       (ownerVisits!==null?' · visitas a mi perfil: '+ownerVisits:'')+
       (siblingProofs!==null?' · identidad desde otra pestaña: '+siblingProofs:'')+
       savedText):
      'Sin estado para esta cuenta.';
    if(!info)continue;
    const state=String(info.state||'idle'),running=info.running===true;
    const prev=laneSnapshots[scope.account],terminal=['complete','partial','review',
      'blocked','error','paused'];
    const awaiting=prev?.awaitingStart===true&&
      Date.now()-Number(prev.startedAt||0)<30000;
    const reported=String(info.task||'');
    const task=['unfollow','cancel'].includes(reported)?reported:
      awaiting?prev.task:'';
    if(running&&(!prev||(!prev.running&&!prev.awaitingStart)))
      completionAcknowledged[scope.account]=false;
    const sameTask=prev&&task===prev.task&&['unfollow','cancel'].includes(task);
    const terminalNow=terminal.includes(state);
    // Only a previously observed worker, or an explicitly approved job which
    // already reached a terminal state, can trigger completion.
    if(sameTask&&!completionAcknowledged[scope.account]&&
       ((prev.observedRunning&&((prev.running&&!running)||
          (terminalNow&&!terminal.includes(prev.state))))||
        (awaiting&&terminalNow))){
      enqueueCompletion({owner:current.owner,account:scope.account,
        handle:scope.expected_handle,i,task,state,
        processed:Number(info.processed)||0,pending:Number(info.pending)||0,
        issues:Number(info.issues)||0});
    }
    laneSnapshots[scope.account]={running,task,state,
      observedRunning:running||!!prev?.observedRunning,
      awaitingStart:awaiting&&!running&&!terminalNow,
      startedAt:prev?.startedAt||Date.now()};
  }
  // Never infer the active server mode from a stale checkbox.
  linked.parallel=x.parallel_mutations_enabled===true;
  if(!silent)notice(linked.parallel?
    'MODO PARALELO ACTIVADO: cada cuenta tiene ventana Chrome, historial y pausa propios. '+
    'El bloqueo global sigue protegiendo frente a otras instalaciones. No evita límites de Instagram.':
    'Sesiones independientes. Las acciones siguen SERIALIZADAS; no hay dos unfollows paralelos.');
  return x;
}
async function restoreLinkedSessions(){
  // Controller status is READ ONLY. Never grant consent or start any robot.
  const p=window.IGC_INSTAGRAM_PROFILES,owner=p&&p.owner;
  if(!OWNER.test(owner||'')||linked||activeBusy||restoreInFlight)return;
  if(restoreOwner!==owner){restoreOwner=owner;restoreDone=false}
  if(restoreDone)return;
  restoreInFlight=true;
  try{
    const saved=await api('status?owner='+encodeURIComponent(owner));
    if(linked||activeBusy||window.IGC_INSTAGRAM_PROFILES?.owner!==owner)return;
    if(saved.owner!==owner)throw Error('Estado de otro propietario: recuperación bloqueada.');
    if(saved.two_workspaces!==true||!Array.isArray(saved.lanes)||saved.lanes.length!==2){
      restoreDone=true;return;
    }
    let registry=Array.isArray(p.accounts)?p.accounts:[];
    if(!registry.length){
      try{registry=JSON.parse(localStorage.getItem('igc_multi_profile_registry_cache_'+owner)||'[]')}
      catch(_){registry=[]}
    }
    if(!Array.isArray(registry))registry=[];
    const used=new Set();
    const mapped=saved.lanes.map(item=>{
      if(!item||!PROFILE.test(item.account||'')||!HANDLE.test(item.expected_handle||'')
          ||used.has(item.account))return null;
      used.add(item.account);
      const row=registry.find(x=>x&&(x.account_key||x.account)===item.account);
      const handle=row&&(row.username||row.expected_handle);
      if(!HANDLE.test(handle||'')||handle.toLowerCase()!==item.expected_handle.toLowerCase())return null;
      return {account:item.account,expected_handle:handle.toLowerCase()};
    });
    if(mapped.some(x=>!x)||mapped[0].expected_handle===mapped[1].expected_handle){
      restoreDone=true;
      notice('La sesión guardada no coincide con las cuentas registradas. Vincula las cuentas manualmente.');
      return;
    }
    const parallel=saved.parallel_mutations_enabled===true;
    draw({owner,primary:mapped[0],secondary:mapped[1],parallel});
    const checkbox=$('igcDawParallelOptIn');if(checkbox)checkbox.checked=parallel;
    restoreDone=true;
    await statusUpdate(true,saved);
    notice(saved.bindings_restored_from_disk===true?
      'Vínculos de las dos cuentas recuperados tras reiniciar Windows. Ambos robots detenidos; '+
      'Chrome NO se abrió automáticamente. Modo serial: el paralelo requiere nueva autorización.':
      'Sesiones y estado recuperados · '+(parallel?'paralelo autorizado':'serial')+
      '. Sin iniciar robots ni repetir acciones.');
  }catch(_){/* Local bridge unavailable: next visible poll can retry. */}
  finally{restoreInFlight=false}
}
async function pollStatus(){
  if(document.hidden)return;
  const activeOwner=window.IGC_INSTAGRAM_PROFILES?.owner||'';
  if(linked&&activeOwner!==linked.owner){
    linked=null;draw(null);restoreDone=false;restoreOwner='';
    notice('Cambió la cuenta de InstaCleaner; se ocultaron las sesiones anteriores.');
  }
  if(!linked){await restoreLinkedSessions();return;}
  if(activeBusy||statusPolling)return;
  // Poll only after an explicit start or when a worker was observed running.
  if(!Object.values(laneSnapshots).some(x=>x.running||x.awaitingStart))return;
  statusPolling=true;
  try{await statusUpdate(true)}catch(_){/* Keep saved WAL intact on bridge errors. */}
  finally{statusPolling=false}
}
function mount(){
  const center=$('igcAutomationCommandCenter');if(!center||$('igcDualActionWorkspacePanel'))return false;
  const panel=el('section');panel.id='igcDualActionWorkspacePanel';
  const header=el('div','igc-daw-header');
  const heading=el('div');heading.append(el('h3',null,'Dos cuentas · Sesiones de acciones'));
  heading.append(el('div','igc-daw-sub',
    'Chrome por cuenta · historial original · serial por defecto, paralelo con autorización'));
  header.append(heading);
  const actions=el('div','igc-daw-actions');
  const mode=el('label','igc-daw-mode');
  const opt=el('input');opt.type='checkbox';opt.id='igcDawParallelOptIn';
  mode.append(opt,el('span',null,'Activar dos robots de acciones simultáneos (opcional)'));
  mode.append(el('small',null,
    'Predeterminado: serial. En paralelo, cada @cuenta utiliza su propia ventana Chrome, '+
    'tanda, historial y pausa. Cada acción requiere aprobación; Instagram puede aplicar límites.'));
  actions.append(mode);
  const configure=el('button',null,'Vincular dos cuentas');
  configure.type='button';configure.id='igcDawConfigure';
  configure.addEventListener('click',()=>perform(async()=>{
    const p=pair(),parallel=opt.checked===true;
    if(!confirm('Vincular @'+p.primary.expected_handle+' y @'+p.secondary.expected_handle+
      ' a dos sesiones Chrome separadas. '+(parallel?
      'MODO PARALELO: ambos robots podrán ejecutar acciones de relación a la vez '+
      'en distintas cuentas, con confirmación por cada tanda. ¿Lo autorizas?':
      'Modo serial: solo un robot de acciones a la vez. ¿Continuar?')))return;
    const data={...p,read_only_consent:true,
      parallel_actions_consent:parallel,
      acknowledge_parallel_actions:parallel,
      acknowledge_serial_actions:!parallel,
      confirmation:(parallel?'dual-action-workspaces-parallel:':'dual-action-workspaces:')+
        p.primary.account+':'+p.secondary.account};
    const response=await api('configure',data);
    if(response.parallel_mutations_enabled!==parallel)
      throw Error('El modo confirmado no coincide con el servidor. No se inició ninguna tarea.');
    draw({...p,parallel:response.parallel_mutations_enabled});await statusUpdate();
  }));
  actions.append(configure);
  const refresh=el('button',null,'Actualizar estado');refresh.type='button';
  refresh.id='igcDawRefresh';refresh.addEventListener('click',()=>perform(statusUpdate));
  actions.append(refresh);header.append(actions);panel.append(header);
  const grid=el('div','igc-daw-grid');grid.id='igcDawGrid';panel.append(grid);
  const feedback=el('div','igc-daw-note',
    'Puedes preparar tandas nuevas por cada cuenta con revisión local obligatoria, continuar tandas guardadas, ver resultados y pausar individualmente. Ninguna lista se ejecuta sin confirmación.');
  feedback.id='igcDualActionWorkspaceFeedback';feedback.setAttribute('role','status');
  panel.append(feedback);
  const modal=el('section');modal.id='igcDawCompletionModal';modal.hidden=true;
  modal.setAttribute('role','dialog');modal.setAttribute('aria-modal','true');
  modal.setAttribute('aria-label','Revisión de tanda de Instagram');
  panel.append(modal);center.insertAdjacentElement('afterend',panel);
  draw(null);void restoreLinkedSessions();return true;
}
function setup(){
  if(mount())return;
  // Automation Center can appear long after Home loads; an expiring
  // startup timer would silently hide the dual-account controls.
  const watcher=new MutationObserver(()=>{
    if(mount())watcher.disconnect();
  });
  watcher.observe(document.documentElement,{childList:true,subtree:true});
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
// Only polls saved owner-scoped status; never launches or authorizes actions.
setInterval(pollStatus,4000);
})();
</script>
"""
