"""Native Windows Automations statistics sidebar; read-only canonical action journal.

No new storage, no Instagram requests and no relationship clicks. Source data comes
from the existing token-protected /api/actions/history endpoint for each named
owner / Instagram workspace / task.
"""

AUTOMATION_ACTIVITY_PANEL = r"""
<style>
#igcAutomationActivityLayout{display:grid;grid-template-columns:minmax(0,1fr) minmax(260px,310px);
  grid-template-areas:"center activity" "dual activity";align-items:start;gap:14px;min-width:0}
#igcAutomationActivityLayout>#igcAutomationCommandCenter{grid-area:center;min-width:0}
#igcAutomationActivityLayout>#igcDualActionWorkspacePanel{grid-area:dual;min-width:0}
#igcAutomationActivityPanel{grid-area:activity;position:sticky;top:14px;max-height:calc(100vh - 28px);
  overflow:auto;box-sizing:border-box;min-width:0;padding:15px;border:1px solid #354b60;
  border-radius:15px;color:#e7edf5;background:linear-gradient(160deg,#142237,#111922);
  font:inherit;box-shadow:0 14px 30px #0003}
#igcAutomationActivityPanel h3{font-size:16px;margin:0;color:#f0f6ff}
#igcAutomationActivityPanel .igc-act-muted{font-size:11px;line-height:1.5;color:#a5b5c9;margin:5px 0 10px}
#igcAutomationActivityPanel label{font-size:12px;color:#b4c9db;display:block;margin:9px 0 5px}
#igcAutomationActivityPanel select,#igcAutomationActivityPanel button{width:100%;box-sizing:border-box;
  background:#1c3044;border:1px solid #466179;border-radius:9px;color:#f1f6fd;
  padding:8px;font:inherit;font-size:12px}
#igcAutomationActivityPanel button{cursor:pointer;margin:10px 0 4px}
#igcAutomationActivityPanel button:disabled{opacity:.5}
#igcAutomationActivityPanel .igc-act-windows{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}
#igcAutomationActivityPanel .igc-act-window{background:#17283a;border:1px solid #334d63;
  border-radius:10px;padding:10px;min-width:0}
#igcAutomationActivityPanel .igc-act-window span{display:block;color:#b7c9da;font-size:11px}
#igcAutomationActivityPanel .igc-act-window strong{font-size:21px;color:#f6f9ff;line-height:1.6;font-variant-numeric:tabular-nums}
#igcAutomationActivityPanel .igc-act-window small{font-size:10px;color:#9baec2}
#igcAutomationActivityPanel .igc-act-section{border-top:1px solid #34465a;padding-top:9px;margin-top:10px}
#igcAutomationActivityPanel .igc-act-row{display:flex;align-items:center;justify-content:space-between;gap:8px;
  font-size:12px;line-height:1.9}
#igcAutomationActivityPanel .igc-act-row b{font-variant-numeric:tabular-nums}
#igcAutomationActivityPanel .igc-act-ok{color:#70d9a0}
#igcAutomationActivityPanel .igc-act-warning{color:#eec470}
#igcAutomationActivityPanel .igc-act-status{font-size:11px;color:#b4c7d8;overflow-wrap:anywhere}
#igcAutomationActivityPanel .igc-act-head{display:flex;align-items:center;justify-content:space-between;gap:7px}
#igcAutomationActivityPanel .igc-act-head button{margin:0;width:auto;min-width:72px;padding:6px}
#igcAutomationActivityLayout.igc-act-collapsed{grid-template-columns:minmax(0,1fr) 155px}
#igcAutomationActivityLayout.igc-act-collapsed #igcAutomationActivityPanel{max-height:75px;padding:10px}
#igcAutomationActivityLayout.igc-act-collapsed #igcAutomationActivityPanel > :not(.igc-act-head){display:none}
@media(max-width:980px){
 #igcAutomationActivityLayout.igc-act-collapsed{grid-template-columns:minmax(0,1fr)}
 #igcAutomationActivityLayout.igc-act-collapsed #igcAutomationActivityPanel{max-height:75px}
}
#igcAutomationActivityPanel .igc-act-window.igc-act-primary{
 background:linear-gradient(140deg,rgba(66,114,172,.21),rgba(18,36,55,.78));
 border-color:rgba(116,188,239,.33)}
#igcAutomationActivityPanel .igc-act-history{display:grid;gap:6px;max-height:210px;overflow-y:auto;margin:7px 0 10px}
#igcAutomationActivityPanel .igc-act-history-row{padding:7px 9px;background:rgba(0,0,0,.13);
 border:1px solid #33495f;border-radius:9px;font-size:11px;color:#dee8f4}
#igcAutomationActivityPanel .igc-act-history-row small{display:block;color:#95adc0;font-size:10px;margin-top:4px}
#igcAutomationActivityPanel .igc-act-history-head{font-size:12px;color:#f0f5fd;font-weight:700;margin:0 0 4px}
#igcAutomationActivityPanel .igc-act-last{background:rgba(80,125,181,.1);border:1px solid #36516a;
 border-radius:10px;padding:9px;margin:8px 0 12px;font-size:12px;color:#e9f1fa}
#igcAutomationActivityPanel .igc-act-last small{display:block;font-size:10px;margin-top:3px;color:#a2b6c9}
@media(max-width:980px){
 #igcAutomationActivityLayout{grid-template-columns:minmax(0,1fr);
   grid-template-areas:"activity" "center" "dual"}
 #igcAutomationActivityPanel{position:static;max-height:none}
}
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
const sessionStart=Date.now(); // This native app page session; reset on reload.
// Primary periods mirror igcStandardActivityTop() in Manual Actions.
const PERIODS=[['session','Esta sesión'],['today','Hoy'],['d7','Últimos 7 días'],
 ['h1','Última hora'],['h2','Últimas 2 horas'],['h3','Últimas 3 horas'],
 ['h24','Últimas 24 horas'],['week','Esta semana'],['month','Este mes'],['all','Histórico']];
let owner='',registry=[],loading=false,refreshAgain=false,dataReady=false,latest=[],lastKey='';
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
 if(!p||!OWNER.test(p.owner||''))return {owner:'',accounts:[]};
 let arr=Array.isArray(p.accounts)?p.accounts:[];
 if(!arr.length){
   try{arr=JSON.parse(localStorage.getItem('igc_multi_profile_registry_cache_'+p.owner)||'[]')}
   catch(_){arr=[]}
 }
 if(!Array.isArray(arr))arr=[];
 const seen=new Set(),accounts=[];
 for(const item of arr){
   const account=item&&(item.account_key||item.account);
   const handle=item&&(item.username||item.expected_handle);
   if(!ACCOUNT.test(account||'')||!HANDLE.test(handle||'')||seen.has(account))continue;
   seen.add(account);accounts.push({account,handle:handle.toLowerCase()});
 }
 return {owner:p.owner,accounts};
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
 if(state==='ok')return 'verified';
 if(['review','error','blocked'].includes(state))return 'warning';
 if(['already_not_following','already_not_requested'].includes(state))return 'no_action';
 if(state==='profile_unavailable')return 'unavailable';
 return 'unconfirmed';
}
function summarize(records,id,now){
 const lower=cutoff(id,now), upper=now.getTime();
 const out={verified:0,unfollow:0,cancel:0,warning:0,no_action:0,unavailable:0};
 const unique=new Set();
 for(const r of records){
   if(!r||!['unfollow','cancel'].includes(r.task)||!HANDLE.test(r.username||''))continue;
   const key=r.task+':'+r.username.toLowerCase();
   const t=dateValue(r.at);
   if(!Number.isFinite(t)||t<lower||t>upper)continue;
   if(unique.has(key))continue;unique.add(key);
   const category=classify(r);
   if(!Object.prototype.hasOwnProperty.call(out,category))continue;
   out[category]++;
   if(category==='verified')out[r.task]++;
 }
 return out;
}
async function readHistory(account,task){
 const a=auth(),request={owner,account,task};
 const response=await fetch('http://127.0.0.1:'+a.port+'/api/actions/history',{
   method:'POST',headers:{'X-IGC-Bridge-Token':a.token,'Content-Type':'application/json'},
   body:JSON.stringify(request)
 });
 const data=await response.json();
 if(!response.ok||data.owner!==owner||data.account!==account||data.task!==task||
    !Array.isArray(data.history_rows))throw Error('Historial no verificable para la cuenta seleccionada.');
 return data.history_rows.map(x=>({
   task,username:x.username,status:x.status,at:x.at
 }));
}
function setStatus(message){const e=$('igcActStatus');if(e)e.textContent=message}
function clearValues(){
 const history=$('igcActHistory');if(history)history.replaceChildren();
 const last=$('igcActLast');if(last)last.textContent='—';
 for(const [key] of PERIODS){const el=$('igcActCount_'+key);if(el)el.textContent='—'}
 for(const key of ['verified','unfollow','cancel','warning','no_action','unavailable']){
   const el=$('igcActMetric_'+key);if(el)el.textContent='—';
 }
}
function renderHistory(records){
 const list=$('igcActHistory'),last=$('igcActLast');
 if(!list||!last)return;
 const ordered=records.filter(r=>r&&['unfollow','cancel'].includes(r.task)&&
   HANDLE.test(r.username||'')&&Number.isFinite(dateValue(r.at)))
   .sort((a,b)=>dateValue(b.at)-dateValue(a.at));
 const seen=new Set(),entries=[];
 for(const r of ordered){
   const key=r.task+':'+r.username.toLowerCase();
   if(seen.has(key))continue;
   seen.add(key);entries.push(r);
   if(entries.length===15)break;
 }
 list.replaceChildren();
 if(!entries.length){
   last.textContent='No hay acciones con fecha guardada.';
   list.append(node('p','igc-act-muted','El historial está vacío o no tiene fechas verificables.'));
   return;
 }
 function name(r){return (r.task==='unfollow'?'Unfollow':'Cancel Pending')+' · @'+r.username}
 function desc(r){const k=classify(r);return k==='verified'?'OK confirmado':
   k==='warning'?'⚠ Review / advertencia':k==='no_action'?'Ya resuelto · sin clic':
   k==='unavailable'?'No disponible':'No confirmado'}
 const newest=entries[0];last.replaceChildren();
 last.append(node('div',null,'Último registro · '+name(newest)),
   node('small',null,desc(newest)+' · '+new Date(dateValue(newest.at)).toLocaleString()));
 for(const entry of entries){
   const row=node('div','igc-act-history-row');
   row.append(node('div',null,name(entry)+' · '+desc(entry)),
     node('small',null,new Date(dateValue(entry.at)).toLocaleString()));
   list.append(row);
 }
}
function render(records){
 if(!dataReady)return;
 const selected=$('igcActTask')?.value||'all';
 const scoped=selected==='all'?records:records.filter(r=>r.task===selected);
 const now=new Date();
 for(const [key] of PERIODS){
   const out=summarize(scoped,key,now);
   const el=$('igcActCount_'+key);
   if(el)el.textContent=String(out.verified);
 }
 renderHistory(scoped);
 const period=$('igcActBreakdownPeriod')?.value||'today';
 const data=summarize(scoped,period,now);
 for(const key of ['verified','unfollow','cancel','warning','no_action','unavailable']){
   const el=$('igcActMetric_'+key);if(el)el.textContent=String(data[key]);
 }
}
async function refresh(){
 if(loading){refreshAgain=true;return;}
 const ctx=context(),selector=$('igcActAccount');
 if(!selector)return;
 if(!ctx.owner){latest=[];owner='';lastKey='';dataReady=false;clearValues();
   selector.replaceChildren();setStatus('Inicia sesión para consultar estadísticas guardadas.');return}
 const signature=ctx.owner+'|'+ctx.accounts.map(a=>a.account+':'+a.handle).join('|');
 if(signature!==lastKey){
   const selected=selector.value;
   selector.replaceChildren();
   for(const account of ctx.accounts){
     const opt=node('option',null,'@'+account.handle);opt.value=account.account;selector.append(opt);
   }
   if(ctx.accounts.some(x=>x.account===selected))selector.value=selected;
   else if(ctx.accounts.some(x=>x.account===window.IGC_INSTAGRAM_PROFILES.active))
     selector.value=window.IGC_INSTAGRAM_PROFILES.active;
   owner=ctx.owner;registry=ctx.accounts;lastKey=signature;
   latest=[];dataReady=false;clearValues()
 }
 if(!registry.length||!ACCOUNT.test(selector.value)){
   dataReady=false;clearValues();setStatus('No hay cuentas registradas para consultar.');return;
 }
 loading=true;
 const button=$('igcActRefresh');if(button)button.disabled=true;
 try{
   const account=selector.value;
   const data=await Promise.all(['unfollow','cancel'].map(task=>readHistory(account,task)));
   // Reject stale responses after an account selection or login switch.
   if(owner!==ctx.owner||selector.value!==account||context().owner!==ctx.owner)return;
   latest=data.flat();dataReady=true;render(latest);
   const tz=Intl.DateTimeFormat().resolvedOptions().timeZone||'hora local';
   setStatus('Actualizado: '+new Date().toLocaleTimeString()+' · '+tz+
     ' · datos del historial local verificado. No incluye lecturas sin clic.');
 }catch(e){
   latest=[];dataReady=false;clearValues();
   setStatus('Sin datos verificables: '+String(e.message||e).slice(0,120));
 }finally{
   loading=false;if(button)button.disabled=false;
   if(refreshAgain){refreshAgain=false;refresh()}
 }
}
function mount(){
 const center=$('igcAutomationCommandCenter');
 if(!center)return false;
 if($('igcAutomationActivityPanel'))return true;
 const layout=node('div');layout.id='igcAutomationActivityLayout';
 center.parentNode.insertBefore(layout,center);layout.append(center);
 const dual=$('igcDualActionWorkspacePanel');
 if(dual)layout.append(dual);
 const panel=node('aside');panel.id='igcAutomationActivityPanel';
 panel.setAttribute('aria-label','Estadísticas de acciones automáticas');
 const head=node('div','igc-act-head');
 head.append(node('h3',null,'Automation Activity'));
 const toggle=node('button',null,'Contraer');toggle.type='button';toggle.id='igcActToggle';
 toggle.setAttribute('aria-expanded','true');
 toggle.setAttribute('aria-label','Contraer o expandir estadísticas de Automations');
 toggle.addEventListener('click',()=>{
   const compact=layout.classList.toggle('igc-act-collapsed');
   toggle.textContent=compact?'Expandir':'Contraer';
   toggle.setAttribute('aria-expanded',String(!compact));
 });
 head.append(toggle);panel.append(head);
 panel.append(node('p','igc-act-muted','Actividad confirmada por cuenta · misma lógica de periodos diarios y móviles.'));
 const label=node('label',null,'Cuenta de Instagram');label.htmlFor='igcActAccount';panel.append(label);
 const select=node('select');select.id='igcActAccount';
 select.addEventListener('change',()=>{latest=[];dataReady=false;clearValues();refresh()});panel.append(select);
 const taskLabel=node('label',null,'Tipo de acción');taskLabel.htmlFor='igcActTask';panel.append(taskLabel);
 const task=node('select');task.id='igcActTask';
 for(const [value,label] of [['all','Todas las acciones'],['unfollow','Unfollow'],
    ['cancel','Cancel Pending']]){
   const opt=node('option',null,label);opt.value=value;task.append(opt);
 }
 task.addEventListener('change',()=>render(latest));panel.append(task);
 const grid=node('div','igc-act-windows');
 for(const [key,name] of PERIODS){
   const primary=['session','today','d7'].includes(key);
  const item=node('div','igc-act-window'+(primary?' igc-act-primary':'')),caption=node('span',null,name);
   const count=node('strong',null,'—');count.id='igcActCount_'+key;
   item.append(caption,count);grid.append(item);
 }
 panel.append(grid);
 const last=node('div','igc-act-last','—');last.id='igcActLast';panel.append(last);
 const section=node('div','igc-act-section');
 const periodLabel=node('label',null,'Desglose del periodo');periodLabel.htmlFor='igcActBreakdownPeriod';section.append(periodLabel);
 const period=node('select');period.id='igcActBreakdownPeriod';
 for(const [key,name] of PERIODS){const opt=node('option',null,name);opt.value=key;period.append(opt)}
 period.value='today';period.addEventListener('change',()=>render(latest));section.append(period);
 for(const [key,name] of [['verified','Acciones confirmadas'],['unfollow','Unfollow realizados'],
  ['cancel','Solicitudes canceladas'],['warning','Review / advertencias'],
  ['no_action','Ya estaban resueltas (sin clic)'],['unavailable','Perfiles no disponibles']]){
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
  'Actividad del robot (no sumada al historial manual). Solo OK con fecha cuenta como acción realizada; Review y perfiles ya resueltos se cuentan aparte.'));
 const refreshButton=node('button',null,'Actualizar estadísticas');refreshButton.type='button';
 refreshButton.id='igcActRefresh';refreshButton.addEventListener('click',refresh);panel.append(refreshButton);
 const status=node('div','igc-act-status','Consulta de solo lectura; no inicia robots.');
 status.id='igcActStatus';status.setAttribute('role','status');panel.append(status);
 layout.append(panel);
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
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup,{once:true});
else setup();
})();
</script>
"""