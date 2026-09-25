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
  const x = v => 60 + (v - 20) / 80 * 630;
  const y = v => 295 - (v - 1) / 9 * 255;
  function render(g) {
    const layer = document.createDocumentFragment();
    for (let i = 1; i <= 10; i++) {
      layer.append(elem('line', {x1:60, y1:y(i), x2:690, y2:y(i), class:'grid'}));
      layer.append(elem('text', {x:44,y:y(i)+5,'text-anchor':'end','font-size':14}, i));
    }
    for (let i = 20; i <= 100; i += 20) layer.append(elem('text', {x:x(i),y:319,'text-anchor':'middle','font-size':14},i));
    layer.append(elem('text', {x:375,y:346,'text-anchor':'middle','font-size':14},'Physical activity level (dataset units)'));
    layer.append(elem('text', {x:60,y:20,'font-size':14},'Sleep quality · 1–10 score'));
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
    render(data.groups.all);
  }).catch(() => {document.querySelector('#load-note').textContent='The interactive data could not load. The default chart, findings and downloadable results remain available.';});
})();
