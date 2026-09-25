(() => {
  'use strict';
  try { if (localStorage.getItem('dg-portfolio-motion') === 'off') document.documentElement.dataset.motion = 'off'; } catch (_) {}
  const select = document.querySelector('#group');
  const chart = document.querySelector('#scatter');
  const ns = 'http://www.w3.org/2000/svg';
  const format = (x, n = 3) => Number(x).toFixed(n).replace('-', '−');
  const elem = (tag, attrs, text) => {
    const el = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, String(v)));
    if (text !== undefined) el.textContent = text;
    return el;
  };
  let lastWidth = 0;
  function render(g) {
    // Size the drawing coordinate system to the actual panel. Keeping 720 units
    // on a phone shrinks 14px axis labels to about 6px; this preserves legibility.
    const width = Math.max(280, Math.min(720, Math.round(chart.getBoundingClientRect().width)));
    lastWidth = width;
    const left = 40, right = width - 16;
    const x = v => left + (v - 20) / 80 * (right - left);
    const y = v => 295 - (v - 1) / 9 * 250;
    chart.setAttribute('viewBox', `0 0 ${width} 360`);
    const layer = document.createDocumentFragment();
    for (let i = 1; i <= 10; i++) {
      layer.append(elem('line', {x1:left, y1:y(i), x2:right, y2:y(i), class:'grid'}));
      layer.append(elem('text', {x:left-12,y:y(i)+5,'text-anchor':'end','font-size':14}, i));
    }
    for (let i = 20; i <= 100; i += 20) layer.append(elem('text', {x:x(i),y:319,'text-anchor':'middle','font-size':14},i));
    layer.append(elem('text', {x:(left+right)/2,y:346,'text-anchor':'middle','font-size':13},'Physical activity (dataset units)'));
    layer.append(elem('text', {x:left,y:20,'font-size':14},'Sleep quality · 1–10 score'));
    for (const p of g.points) {
      const dot = elem('circle', {cx:x(p.activity),cy:y(p.sleep),r:Math.sqrt(p.count)*2.1+2});
      dot.append(elem('title',{},`${p.count} record${p.count===1?'':'s'}: activity ${p.activity}, sleep score ${p.sleep}`));
      layer.append(dot);
    }
    layer.append(elem('line',{x1:x(g.activity_min),y1:y(g.intercept+g.slope*g.activity_min),x2:x(g.activity_max),y2:y(g.intercept+g.slope*g.activity_max),class:'fit'}));
    chart.replaceChildren(layer);
    chart.setAttribute('aria-label',`${g.label}: ${g.n} synthetic records. Activity–sleep Pearson correlation ${format(g.pearson_r)}. Bubble size shows record count.`);
    document.querySelector('#group-title').textContent = g.label;
    document.querySelector('#group-n').textContent = g.n;
    document.querySelector('#group-r').textContent = format(g.pearson_r);
    document.querySelector('#group-slope').textContent = (g.slope>=0?'+':'')+format(g.slope*10);
    document.querySelector('#group-note').textContent = g.n < 30
      ? `Only ${g.n} synthetic records in this group. A strong fitted relationship here is not a reliable basis for a population claim.`
      : 'This line describes the selected records without adjusting for age, stress or other differences. It does not estimate the effect of changing activity.';
  }
  fetch('outputs/summary.json').then(r => {if(!r.ok) throw new Error('Data unavailable');return r.json();}).then(data => {
    select.disabled = false;
    select.addEventListener('change', () => render(data.groups[select.value]));
    window.addEventListener('resize', () => {
      const width=Math.max(280,Math.min(720,Math.round(chart.getBoundingClientRect().width)));
      if(width!==lastWidth) render(data.groups[select.value]);
    });
    render(data.groups.all);
  }).catch(() => {document.querySelector('#load-note').textContent='The interactive data could not load. The default chart, findings and downloadable results remain available.';});
})();
