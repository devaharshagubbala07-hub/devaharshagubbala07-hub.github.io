(() => {
  'use strict';
  try { if (localStorage.getItem('dg-portfolio-motion') === 'off') document.documentElement.dataset.motion = 'off'; } catch (_) {}
  const disposition = document.querySelector('#disposition');
  const resource = document.querySelector('#resource-type');
  const body = document.querySelector('#ledger-body');
  const friendly = value => value.split('_').join(' ');
  function render(data) {
    const rows = data.ledger.filter(r => (disposition.value==='All' || r.status===disposition.value) && (resource.value==='All' || r.type===resource.value));
    body.replaceChildren();
    for (const row of rows) {
      const tr=document.createElement('tr');
      const entry=document.createElement('td');entry.textContent=row.entry;
      const key=document.createElement('td');key.textContent=row.key;
      const status=document.createElement('td');const badge=document.createElement('span');
      badge.className='status'+(row.status==='Quarantined'?' quarantined':'');badge.textContent=row.status;status.append(badge);
      const reason=document.createElement('td');
      for (const item of [...row.errors,...row.warnings]) {const span=document.createElement('span');span.className='reason';span.textContent=friendly(item);reason.append(span);}
      if (!reason.childNodes.length) reason.textContent='Passed the scoped demo checks';
      tr.append(entry,key,status,reason);body.append(tr);
    }
    if(!rows.length){const tr=document.createElement('tr');const td=document.createElement('td');td.colSpan=4;td.textContent='No entries match these filters.';tr.append(td);body.append(tr);}
    document.querySelector('#ledger-count').textContent=`${rows.length} of ${data.totals.input_entries} input entries`;
  }
  fetch('outputs/summary.json').then(r=>{if(!r.ok)throw new Error('Data unavailable');return r.json();}).then(data=>{
    disposition.disabled=false;resource.disabled=false;
    for(const control of [disposition,resource])control.addEventListener('change',()=>render(data));
    render(data);
  }).catch(()=>{document.querySelector('#load-note').textContent='The interactive data could not load. The default quarantine ledger and source files remain available.';});
})();
