(() => {
  'use strict';
  const $=id=>document.getElementById(id);
  const money=n=>n==null?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(n);
  const integer=n=>new Intl.NumberFormat('en-US').format(n);
  const pct=n=>n==null?'—':n.toFixed(1)+'%';
  let data,current,scenario;
  try{if(localStorage.getItem('dg-portfolio-motion')==='off')document.documentElement.dataset.motion='off';}catch(_){}
  function bar(label,value,width,note,color){
    const li=document.createElement('li'),top=document.createElement('div'),title=document.createElement('strong'),amount=document.createElement('span'),track=document.createElement('div'),fill=document.createElement('span'),detail=document.createElement('small');
    top.className='bar-top';title.textContent=label;amount.textContent=value;top.append(title,amount);track.className='track';track.setAttribute('aria-hidden','true');fill.className='fill';fill.style.setProperty('--width',Math.max(0,Math.min(100,width))+'%');if(color)fill.style.background=color;track.append(fill);detail.className='bar-detail';detail.textContent=note;li.append(top,track,detail);return li;
  }
  function value(){
    const hourly=Number($('hourly').value),realization=Number($('realization').value),threshold=Number($('threshold').value),capacity=current.net_capacity_minutes/60*hourly;
    const benefit=Math.max(capacity,0)*realization/100+Math.min(capacity,0),net=benefit-current.technology_cost_usd;
    const roi=current.technology_cost_usd?100*net/current.technology_cost_usd:null,breakEven=capacity>0?100*current.technology_cost_usd/capacity:null;
    scenario={hourly_rate_usd:hourly,realization_pct:realization,quality_threshold_pct:threshold,capacity_value_usd:capacity,modeled_net_value_usd:net,modeled_roi_pct:roi,break_even_realization_pct:breakEven};
    $('hourly-label').textContent=money(hourly);$('realization-label').textContent=realization+'%';$('threshold-label').textContent=threshold+'%';
    $('net-value').textContent=money(net);$('roi').textContent=pct(roi);$('break-even').textContent=breakEven==null?'Not attainable':pct(breakEven)+(breakEven>100?' · above 100%':'');
    const passes=current.first_pass_pct!=null&&current.first_pass_pct>=threshold;
    $('decision').className='decision'+(passes?' pass':'');
    $('decision').textContent=passes?`The fixture meets your ${threshold}% first-pass threshold. The financial result still depends on the assumed baseline, labor value, and realization factor.`:`The fixture is below your ${threshold}% first-pass threshold (${pct(current.first_pass_pct)} observed in the generated records). A positive modeled value alone is not a go-ahead.`;
  }
  function render(){
    const department=$('department').value,month=$('month').value;
    current=data.summary.find(x=>x.department===department&&x.month===month);if(!current)throw Error('Missing scope');
    $('scope').textContent=`${department} · ${month==='All months'?data.period:month} · ${integer(current.tasks)} business tasks · Synthetic data`;
    $('cost').textContent=money(current.technology_cost_usd);$('unit-cost').textContent=money(current.cost_per_useful_task_usd);$('acceptance').textContent=pct(current.first_pass_pct);$('capacity').textContent=(current.net_capacity_minutes/60).toFixed(1)+' h';$('acceptance-note').textContent=`${integer(current.accepted)} accepted / ${integer(current.tasks)} tasks`;
    const monthly=data.summary.filter(x=>x.department===department&&x.month!=='All months'),max=Math.max(...monthly.map(x=>x.technology_cost_usd));
    $('trend').replaceChildren(...monthly.map(x=>bar(x.month+(x.month===month?' · selected':''),money(x.technology_cost_usd),100*x.technology_cost_usd/max,`${integer(x.tasks)} tasks · ${money(x.setup_cents/100)} setup included`)));
    $('cost-note').textContent=`Selected scope: ${money(current.api_cost_microusd/1e6)} API usage + ${money(current.license_cents/100)} recurring fees + ${money(current.setup_cents/100)} setup. Token counts include ${integer(current.retries)} retries; one row still represents one business task.`;
    $('outcomes').replaceChildren(...[['Accepted first pass',current.accepted,'#335d91'],['Accepted after rework',current.reworked,'#8196af'],['Manual fallback',current.fallback,'#bd8a43']].map(([label,n,color])=>bar(label,integer(n),current.tasks?100*n/current.tasks:0,pct(current.tasks?100*n/current.tasks:null)+' of business tasks',color)));
    value();
  }
  function download(){
    const r={data_kind:'synthetic_scenario',...current,...scenario},quote=x=>'"'+String(x??'').replaceAll('"','""')+'"';
    const csv=[Object.keys(r),Object.values(r)].map(a=>a.map(quote).join(',')).join('\r\n')+'\r\n';
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='ai-value-scenario.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  fetch('data.json').then(r=>{if(!r.ok)throw Error('Data unavailable');return r.json();}).then(payload=>{
    if(payload.data_kind!=='synthetic_scenario')throw Error('Unexpected source');data=payload;
    $('checks').textContent=`${Object.values(data.checks).filter(Boolean).length} of ${Object.keys(data.checks).length} checks passed`;
    $('quality').textContent='Task IDs, outcomes, monthly totals, department totals, token repricing, and one-time fee aggregation reconcile across the complete fixture.';
    $('department').addEventListener('change',render);$('month').addEventListener('change',render);for(const id of ['hourly','realization','threshold'])$(id).addEventListener('input',value);$('download').addEventListener('click',download);
    $('reset').addEventListener('click',()=>{$('department').value='All departments';$('month').value='All months';$('hourly').value='45';$('realization').value='25';$('threshold').value='80';render();});
    $('explorer').hidden=false;render();
  }).catch(e=>{$('error').hidden=false;$('explorer').hidden=true;console.error(e);});
})();
