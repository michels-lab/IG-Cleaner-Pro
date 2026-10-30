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
let linked=null, activeBusy=false, savedReviews={};
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
  const review=el('button',null,'Revisar pendientes');review.type='button';
  review.id='igcDawReview'+i;review.addEventListener('click',()=>perform(async()=>{
    if(!linked)throw Error('Primero vincula las dos cuentas de Chrome.');
    const result=await api('review-one',{owner:linked.owner,account:linked[i].account,task:task.value});
    const batch=result.batch;savedReviews[i]={task:task.value,batch};
    const targets=batch&&batch.action_results||{};
    const select=$('igcDawTarget'+i);select.replaceChildren();
    for(const [username,outcome] of Object.entries(targets)){
      if(!HANDLE.test(username))continue;
      const o=el('option',null,'@'+username+' · '+String(outcome.status||'pending'));
      o.value=username;select.append(o);
    }
    notice(batch?('Cuenta '+(i+1)+': '+Object.keys(targets).length+
      ' perfiles de la tanda '+String(batch.id||'').slice(0,30)+
      '. Inspección manual; no se repite ningún clic.'):
      'Esta cuenta no tiene ninguna tanda pendiente.');
  }));
  controls.append(review);
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
  return outer;
}
function draw(p){
  const target=$('igcDawGrid');if(!target)return;
  target.replaceChildren();
  if(p){linked={0:p.primary,1:p.secondary,owner:p.owner};savedReviews={}}
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
    'Las tandas se autorizan desde los controles de automatización existentes. Aquí se separan cuentas, se inspeccionan las revisiones y se puede pausar cada sesión.');
  feedback.id='igcDualActionWorkspaceFeedback';feedback.setAttribute('role','status');
  panel.append(feedback);center.insertAdjacentElement('afterend',panel);
  draw(null);return true;
}
function setup(){
  if(!mount()){let tries=0;const check=setInterval(()=>{if(mount()||++tries>25)clearInterval(check)},300)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});else setup();
})();
</script>
"""
