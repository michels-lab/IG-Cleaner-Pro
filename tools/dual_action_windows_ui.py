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
#igcDualActionWorkspacePanel .igc-daw-review-list{display:grid;gap:5px;margin-top:12px;max-height:260px;overflow:auto}
#igcDualActionWorkspacePanel .igc-daw-review-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:5px;
padding:7px 9px;border:1px solid #34445a;border-radius:7px;background:#142032;font-size:12px;overflow-wrap:anywhere}
#igcDualActionWorkspacePanel .igc-daw-review-row small{grid-column:1/-1;color:#98b0c7}
#igcDualActionWorkspacePanel .igc-daw-reviewed{border-left:3px solid #40ad75}
#igcDualActionWorkspacePanel .igc-daw-unresolved{border-left:3px solid #d9a43c}
#igcDualActionWorkspacePanel .igc-daw-unavailable{border-left:3px solid #8797a9}
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
  review.id='igcDawReview'+i;review.addEventListener('click',()=>perform(async()=>{
    if(!linked)throw Error('Primero vincula las dos cuentas de Chrome.');
    const result=await api('review-one',{owner:linked.owner,account:linked[i].account,task:task.value});
    const batch=result.batch;savedReviews[i]={task:task.value,batch};
    const targets=batch&&batch.action_results||{};
    const select=$('igcDawTarget'+i),list=$('igcDawReviewList'+i);
    select.replaceChildren();list.replaceChildren();
    for(const username of (batch&&Array.isArray(batch.targets)?batch.targets:[])){
      if(!HANDLE.test(username))continue;
      const outcome=targets[username]||{status:'pending'},status=String(outcome.status||'pending');
      const reviewed=['ok','already_not_following','already_not_requested'].includes(status);
      const unavailable=status==='profile_unavailable';
      const row=el('div','igc-daw-review-row '+(reviewed?'igc-daw-reviewed':
        unavailable?'igc-daw-unavailable':'igc-daw-unresolved'));
      row.append(el('span',null,'@'+username),el('span',null,
        reviewed?'OK':unavailable?'NO DISPONIBLE':'REVIEW · '+status.toUpperCase()));
      row.append(el('small',null,'Acción: '+String(outcome.at||'sin fecha registrada')+
        ' · '+String(outcome.message||'sin confirmación').slice(0,140)));
      list.append(row);
      // Completed green rows are historical evidence, NOT replay candidates.
      if(!reviewed&&!unavailable){
        const o=el('option',null,'@'+username+' · '+status);
        o.value=username;select.append(o);
      }
    }
    notice(batch?('Cuenta '+(i+1)+': '+Object.keys(targets).length+
      ' perfiles de la tanda '+String(batch.id||'').slice(0,30)+
      '. Inspección manual; no se repite ningún clic.'):
      'Esta cuenta no tiene ninguna tanda pendiente.');
  }));
  controls.append(review);
  const continueSaved=el('button',null,'Continuar tanda guardada');
  continueSaved.id='igcDawContinue'+i;continueSaved.type='button';
  continueSaved.addEventListener('click',()=>perform(async()=>{
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
    if(!confirm('Cuenta @'+handle+' · '+task.value+' · '+targets.length+
      ' objetivos originales, de los cuales '+pending+' no tienen resultado. '+
      'Se conservarán los clics inciertos sin repetirlos. ¿Continuar ESTA tanda guardada?'))return;
    // This is an explicit owner attestation, not an independent live check.
    // Followback audit must have been completed before authorizing Unfollow.
    if(task.value==='unfollow'&&!confirm('¿Confirmas que ya verificaste la lista COMPLETA '+
      'de seguidores de @'+handle+'? Sin esa evidencia NO se iniciará Unfollow.'))return;
    const input=(id,def,min,max)=>{
      const n=Number($(id)?.value);
      return Number.isFinite(n)&&n>=min&&n<=max?n:def;
    };
    const batchSize=input('igcAutoBatch',Math.min(targets.length,30),1,1000);
    const gapSeconds=input('igcAutoGap',10,1,600);
    const restMinutes=input('igcAutoRest',5,0,240);
    const action={owner:linked.owner,account,expected_handle:handle,
      task:task.value,targets:targets.slice(),batch_id:record.id,
      batch_size:batchSize,gap_seconds:gapSeconds,rest_minutes:restMinutes,
      protected:[],tab_flow:'sequential',followers_evidence:task.value==='unfollow',
      confirmation:task.value+':'+targets.length};
    const result=await api('start-one',{owner:linked.owner,account,action,
      confirmation:'action-workspace-start:'+linked.owner+':'+account+':'+task.value});
    notice('Tanda original autorizada para @'+handle+'. Estado: '+
      String(result.status||'starting')+'. No hay dos robots de acciones simultáneos.');
    await statusUpdate();
  }));
  controls.append(continueSaved);
  const approve=el('button',null,'Aprobar revisión');
  approve.id='igcDawApprove'+i;approve.type='button';
  approve.addEventListener('click',()=>perform(async()=>{
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
  open.id='igcDawOpen'+i;open.addEventListener('click',()=>perform(async()=>{
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
  stop.id='igcDawStop'+i;stop.addEventListener('click',()=>perform(async()=>{
    if(!linked)throw Error('Primero vincula las dos cuentas.');
    const account=linked[i].account;
    await api('pause-one',{owner:linked.owner,account,
      confirmation:'action-workspace-pause:'+linked.owner+':'+account});
    await statusUpdate();
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
  verify.addEventListener('click',()=>perform(async()=>{
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
  start.addEventListener('click',()=>perform(async()=>{
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
       ' perfiles NUEVOS, de '+batchSize+' por tanda. ¿Autorizar esta cuenta?'))return;
    if(p.task==='unfollow'&&!confirm('¿Verificaste la lista COMPLETA y actual '+
       'de seguidores de @'+handle+'? La prevalidación local no lo demuestra.'))return;
    preparedNew[i]=null;
    const action={owner:p.owner,account,expected_handle:handle,
      task:p.task,targets:exact,batch_size:batchSize,gap_seconds:gapSeconds,
      rest_minutes:restMinutes,protected:[],tab_flow:'sequential',
      followers_evidence:p.task==='unfollow',
      confirmation:p.task+':'+exact.length};
    const result=await api('start-one',{owner:p.owner,account,action,
      confirmation:'action-workspace-start:'+p.owner+':'+account+':'+p.task});
    notice('Tanda nueva de @'+handle+' enviada a su Chrome exclusivo. Estado: '+
      String(result.status||'starting')+'. No hay mutaciones paralelas.');
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
  if(p){linked={0:p.primary,1:p.secondary,owner:p.owner};savedReviews={};preparedNew={}}
  for(let i=0;i<2;i++)target.append(card(linked?linked[i]:{},i));
}
async function perform(fn){
  if(activeBusy)return;
  activeBusy=true;
  const buttons=$('igcDualActionWorkspacePanel')?.querySelectorAll('button')||[];
  for(const b of buttons)b.disabled=true;
  try{await fn()}catch(e){notice('No se ejecutó ninguna nueva acción: '+String(e.message||e).slice(0,190))}
  finally{activeBusy=false;for(const b of buttons)b.disabled=false}
}
async function statusUpdate(){
  if(!linked)throw Error('Primero vincula los dos workspaces.');
  const x=await api('status?owner='+encodeURIComponent(linked.owner));
  for(let i=0;i<2;i++){
    const info=(x.lanes||[]).find(y=>y.account===linked[i].account);
    const label=$('igcDawStatus'+i);
    if(label)label.textContent=info?
      (String(info.state||'idle').toUpperCase()+' · '+(info.running?'Robot activo':'Robot detenido')+
       ' · '+String(info.task||'sin tarea')+' · '+String(info.processed||0)+' revisados · '+
       String(info.issues||0)+' pendientes de revisión'):'Sin estado para esta cuenta.';
  }
  notice('Sesiones independientes. Las acciones siguen SERIALIZADAS; no hay dos unfollows paralelos.');
}
function mount(){
  const center=$('igcAutomationCommandCenter');if(!center||$('igcDualActionWorkspacePanel'))return false;
  const panel=el('section');panel.id='igcDualActionWorkspacePanel';
  const header=el('div','igc-daw-header');
  const heading=el('div');heading.append(el('h3',null,'Dos cuentas · Sesiones de acciones'));
  heading.append(el('div','igc-daw-sub',
    'Chrome separado por cuenta · historial original · sin acciones simultáneas'));
  header.append(heading);
  const actions=el('div','igc-daw-actions');
  const configure=el('button',null,'Vincular dos cuentas');
  configure.type='button';configure.id='igcDawConfigure';
  configure.addEventListener('click',()=>perform(async()=>{
    const p=pair();
    if(!confirm('Vincular @'+p.primary.expected_handle+' y @'+p.secondary.expected_handle+
      ' a dos sesiones Chrome separadas. Los unfollows permanecerán uno por uno.'))return;
    await api('configure',{...p,read_only_consent:true,acknowledge_serial_actions:true,
      confirmation:'dual-action-workspaces:'+p.primary.account+':'+p.secondary.account});
    draw(p);await statusUpdate();
  }));
  actions.append(configure);
  const refresh=el('button',null,'Actualizar estado');refresh.type='button';
  refresh.id='igcDawRefresh';refresh.addEventListener('click',()=>perform(statusUpdate));
  actions.append(refresh);header.append(actions);panel.append(header);
  const grid=el('div','igc-daw-grid');grid.id='igcDawGrid';panel.append(grid);
  const feedback=el('div','igc-daw-note',
    'Puedes preparar tandas nuevas por cada cuenta con revisión local obligatoria, continuar tandas guardadas, ver resultados y pausar individualmente. Ninguna lista se ejecuta sin confirmación.');
  feedback.id='igcDualActionWorkspaceFeedback';feedback.setAttribute('role','status');
  panel.append(feedback);center.insertAdjacentElement('afterend',panel);
  draw(null);return true;
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
})();
</script>
"""
