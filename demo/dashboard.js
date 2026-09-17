(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const currency = value => new Intl.NumberFormat('en-US', {style:'currency',currency:'USD',maximumFractionDigits:2}).format(value);
  const compactCurrency = value => new Intl.NumberFormat('en-US', {style:'currency',currency:'USD',notation:'compact',maximumFractionDigits:2}).format(value);
  const whole = value => new Intl.NumberFormat('en-US').format(value);
  const text = (id, value) => { $(id).textContent = value; };
  try {
    const data = JSON.parse($('analytics-data').textContent);
    if (data.schema_version !== 1 || data.data_kind !== 'synthetic') throw new Error('Unexpected dataset');
    const selectRow = (year, plan) => data.annual.find(row => row.year === year && row.plan === plan);
    function render() {
      const year = $('year').value, plan = $('plan').value;
      const row = selectRow(year, plan), previous = selectRow(String(Number(year)-1), plan);
      if (!row) throw new Error('No data for selected scope');
      text('scope', `${year} · ${plan} · Incurred calendar-year view · Synthetic data`);
      text('pmpm', currency(row.pmpm));
      text('allowed', compactCurrency(row.allowed_cents / 100));
      $('allowed').title = currency(row.allowed_cents / 100);
      text('members', whole(row.members));
      text('months', whole(row.member_months));
      text('zero', `${whole(row.zero_claim_members)} members had no accepted claims`);
      text('change', previous && previous.pmpm ? `${((row.pmpm/previous.pmpm-1)*100).toFixed(1)}% change from ${previous.year}` : 'First reporting year in this example');
      text('share', `${row.high_cost_share.toFixed(1)}%`);
      $('concentration').value = row.high_cost_share;
      text('concentration-note', `${row.high_cost_members} of ${row.members} enrolled members reached $50,000 in observed allowed cost within this selection.`);
      text('sensitivity', row.continuous_pmpm === null ? 'No members meet the 12-month rule in this selection.' : `${row.continuous_members} members were enrolled for all 12 months. Their PMPM was ${currency(row.continuous_pmpm)}, compared with ${currency(row.pmpm)} for all enrolled members.`);
      $('services').replaceChildren();
      data.services.filter(s => s.year === year && s.plan === plan).forEach(service => {
        const share = row.allowed_cents ? service.allowed_cents / row.allowed_cents * 100 : 0;
        const item=document.createElement('li'), label=document.createElement('div');
        label.className='bar-label';
        const name=document.createElement('strong'), value=document.createElement('span');
        name.textContent=service.service_category; value.textContent=currency(service.allowed_cents/100);
        label.append(name,value);
        const track=document.createElement('div'), fill=document.createElement('span'), percent=document.createElement('span');
        track.className='track'; track.setAttribute('aria-hidden','true'); fill.className='fill';
        fill.style.setProperty('--width', `${share}%`); track.append(fill);
        percent.className='bar-share'; percent.textContent=`${share.toFixed(1)}% of allowed cost`;
        item.append(label,track,percent); $('services').append(item);
      });
      text('comparison-label', `${plan} · The same metric definitions are applied to each year.`);
      const metrics=[['Allowed cost PMPM','pmpm',currency],['Total allowed cost','allowed_cents',v=>currency(v/100)],['Enrolled members','members',whole],['Member-months','member_months',whole],['High-cost members','high_cost_members',whole],['High-cost share of cost','high_cost_share',v=>`${v.toFixed(1)}%`]];
      $('comparison').replaceChildren();
      metrics.forEach(([name,key,format]) => {
        const tr=document.createElement('tr'), th=document.createElement('th'); th.scope='row'; th.textContent=name; tr.append(th);
        ['2024','2025'].forEach(y=>{const td=document.createElement('td');td.textContent=format(selectRow(y,plan)[key]);tr.append(td);});
        $('comparison').append(tr);
      });
    }
    const quality=data.quality;
    text('quality-heading',`${Object.values(quality.checks).filter(Boolean).length} of ${Object.keys(quality.checks).length} reconciliation checks passed`);
    text('quality-counts',`${whole(quality.raw_rows)} source rows = ${whole(quality.accepted_rows)} accepted + ${quality.excluded_rows} excluded.`);
    const reasons={exact_duplicate:'Exact duplicate',unknown_member:'Unknown member',outside_enrollment:'Outside enrollment',cost_components_do_not_balance:'Cost components do not balance'};
    Object.entries(quality.exclusions).forEach(([reason,count])=>{const li=document.createElement('li');li.textContent=`${reasons[reason] || reason}: ${count}`;$('exclusions').append(li);});
    $('year').addEventListener('change',render); $('plan').addEventListener('change',render);
    $('reset').addEventListener('click',()=>{$('year').value='2025';$('plan').value='All plans';render();});
    $('download').addEventListener('click',()=>{
      const row=selectRow($('year').value,$('plan').value);
      const entries=Object.entries({data_kind:'synthetic',...row});
      const quote=v=>`"${String(v ?? '').replaceAll('"','""')}"`;
      const content=entries.map(([k])=>quote(k)).join(',')+'\r\n'+entries.map(([,v])=>quote(v)).join(',')+'\r\n';
      const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));
      const link=document.createElement('a');link.href=url;link.download=`synthetic-claims-${row.year}-${row.plan.toLowerCase().replaceAll(' ','-')}.csv`;
      document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
    render(); $('explorer').hidden=false;
  } catch (error) {
    $('error').hidden=false; $('explorer').hidden=true;
    console.error('Claims demonstration failed to initialize',error);
  }
})();
