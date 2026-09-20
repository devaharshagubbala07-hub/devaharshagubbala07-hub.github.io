(() => {
  'use strict';
  try { if (localStorage.getItem('dg-portfolio-motion') === 'off') document.documentElement.dataset.motion = 'off'; } catch (_) {}
  const $ = id => document.getElementById(id);
  const integer = new Intl.NumberFormat('en-US');
  const pct = n => n == null ? '—' : `${n.toFixed(1)}%`;
  const minutes = n => n == null ? '—' : `${Number(n.toFixed(1))} min`;
  const monthName = m => m === 'All months' ? 'Jan–Jun 2025' : new Intl.DateTimeFormat('en-US',{month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(`${m}-01T12:00:00Z`));
  let data, current;
  function bar(label, value, width, detail, color) {
    const li=document.createElement('li');
    const top=document.createElement('div');top.className='bar-top';
    const name=document.createElement('strong');name.textContent=label;
    const number=document.createElement('span');number.textContent=value;top.append(name,number);
    const track=document.createElement('div');track.className='track';track.setAttribute('aria-hidden','true');
    const fill=document.createElement('span');fill.className='fill';fill.style.setProperty('--width',`${Math.max(0,Math.min(100,width||0))}%`);if(color)fill.style.background=color;track.append(fill);
    const note=document.createElement('small');note.className='bar-detail';note.textContent=detail;li.append(top,track,note);return li;
  }
  function render() {
    const clinic=$('team').value,month=$('month').value;
    current=data.summary.find(r=>r.clinic===clinic&&r.month===month);
    if(!current)throw new Error('Missing selected summary');
    $('scope').textContent=`${clinic} · ${monthName(month)} · ${integer.format(current.booked)} booked slots · Synthetic data`;
    $('no-show').textContent=pct(current.no_show_pct);
    $('no-show-note').textContent=`${integer.format(current.no_show)} / ${integer.format(current.eligible)} eligible slots`;
    $('completed').textContent=integer.format(current.completed);
    $('completion-note').textContent=`${pct(current.completion_pct)} of all booked slots`;
    $('cancel-rate').textContent=pct(current.cancellation_pct);
    $('cancel-note').textContent=`${integer.format(current.cancelled)} cancelled; ${integer.format(current.short_notice_cancellations)} with <24 hours’ notice`;
    $('wait').textContent=minutes(current.median_wait_minutes);
    $('wait-note').textContent=`P90: ${minutes(current.p90_wait_minutes)} · Completed visits only`;
    $('outcomes').replaceChildren(...[['Completed',current.completed,'#335d91'],['No-show',current.no_show,'#bd8a43'],['Cancelled',current.cancelled,'#8196af']].map(([label,n,color])=>bar(label,integer.format(n),current.booked?n/current.booked*100:0,`${current.booked?pct(n/current.booked*100):'—'} of all booked slots`,color)));
    $('lead-time').replaceChildren(...data.lead_time.filter(r=>r.clinic===clinic&&r.month===month).map(r=>bar(r.lead_band,pct(r.no_show_pct),r.no_show_pct,`${integer.format(r.no_show)} no-shows / ${integer.format(r.eligible)} eligible slots`)));
    $('monthly-caption').textContent=`All six months for ${clinic.toLowerCase()}. ${month==='All months'?'':`Selected month: ${monthName(month)}.`} Scroll the table on smaller screens.`;
    $('monthly-rows').replaceChildren(...data.summary.filter(r=>r.clinic===clinic&&r.month!=='All months').map(r=>{
      const tr=document.createElement('tr');if(r.month===month)tr.className='selected';
      [monthName(r.month)+(r.month===month?' (selected)':''),integer.format(r.booked),integer.format(r.eligible),integer.format(r.no_show),pct(r.no_show_pct),minutes(r.median_wait_minutes)].forEach((value,i)=>{const cell=document.createElement(i===0?'th':'td');if(i===0)cell.scope='row';cell.textContent=value;tr.append(cell);});return tr;
    }));
  }
  function download() {
    const values={data_kind:'synthetic',...current};
    const quote=x=>`"${String(x??'').replaceAll('"','""')}"`;
    const csv=Object.keys(values).map(quote).join(',')+'\r\n'+Object.values(values).map(quote).join(',')+'\r\n';
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=`synthetic-appointments-${current.clinic.replaceAll(' ','-')}-${current.month.replaceAll(' ','-')}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  fetch('data.json').then(response=>{if(!response.ok)throw new Error('Data unavailable');return response.json();}).then(payload=>{
    if(payload.data_kind!=='synthetic'||!Array.isArray(payload.summary))throw new Error('Unexpected data');
    data=payload;const q=data.quality;const passed=Object.values(q.checks).filter(Boolean).length;
    $('quality-title').textContent=`${passed} of ${Object.keys(q.checks).length} reconciliation checks passed`;
    $('quality-note').textContent=`${integer.format(q.source_rows)} source rows = ${integer.format(q.accepted_rows)} accepted + ${integer.format(q.excluded_rows)} excluded. ${Object.entries(q.reasons).map(([k,v])=>`${k.replaceAll('_',' ')}: ${v}`).join('; ')}.`;
    $('team').addEventListener('change',render);$('month').addEventListener('change',render);
    $('reset').addEventListener('click',()=>{$('team').value='All teams';$('month').value='All months';render();});
    $('download').addEventListener('click',download);$('explorer').hidden=false;render();
  }).catch(error=>{$('error').hidden=false;$('explorer').hidden=true;console.error('Appointment demonstration unavailable',error);});
})();
