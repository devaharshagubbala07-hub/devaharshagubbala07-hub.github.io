'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const count = n => n.toLocaleString('en-US');
  const percent = n => n === null ? 'Not available' : `${(n * 100).toFixed(1)}%`;
  const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let data;
  let page = 0;
  const pageSize = 12;
  const status = (r, minimum) => r.err === null ? 'missing_ratio' : minimum > 0 && r.discharges === null ? 'missing_volume' : minimum > 0 && r.discharges < minimum ? 'below_volume' : 'eligible';
  const explanation = {missing_ratio:'No published ratio',missing_volume:'Discharge count unavailable',below_volume:'Below selected volume minimum'};
  const titleCase = name => name.toLowerCase().replace(/\b\w/g, c => c.toUpperCase());
  function renderTable() {
    const minimum = Number($('minimum').value);
    const query = $('hospital-search').value.trim().toLowerCase();
    const scope = $('table-scope').value;
    const rows = data.indiana_rows.filter(r => {
      if (r.measure_id !== $('condition').value) return false;
      const disposition = status(r, minimum);
      if (scope === 'eligible' && disposition !== 'eligible') return false;
      if (scope === 'above' && (disposition !== 'eligible' || r.err <= 1)) return false;
      if (scope === 'excluded' && disposition === 'eligible') return false;
      return !query || r.facility_name.toLowerCase().includes(query) || r.facility_id.includes(query);
    });
    const pages = Math.max(1, Math.ceil(rows.length / pageSize));
    page = Math.min(page, pages - 1);
    const subset = rows.slice(page * pageSize, (page + 1) * pageSize);
    $('hospital-body').innerHTML = subset.length ? subset.map(r => {
      const disposition = status(r, minimum);
      let note = disposition === 'eligible' ? (r.err > 1 ? 'Above 1' : r.err === 1 ? 'Exactly 1' : 'Below 1') : explanation[disposition];
      if (r.footnote) note += ` · CMS footnote ${r.footnote}`;
      return `<tr><th scope="row">${escape(titleCase(r.facility_name))}<small>CMS ${escape(r.facility_id)}</small></th><td class="numeric">${r.err === null ? 'Unavailable' : r.err.toFixed(4)}</td><td class="numeric">${r.discharges === null ? 'Unavailable' : count(r.discharges)}</td><td>${escape(note)}</td></tr>`;
    }).join('') : '<tr><td colspan="4" class="empty-row">No hospitals match these table filters. Change the search or record status.</td></tr>';
    $('table-count').textContent = rows.length ? `Showing ${page * pageSize + 1}–${Math.min((page + 1) * pageSize, rows.length)} of ${rows.length} matching hospitals · alphabetical order` : '0 matching hospitals';
    $('page-number').textContent = `Page ${page + 1} of ${pages}`;
    $('previous').disabled = page === 0;
    $('next').disabled = page + 1 >= pages;
  }
  function renderChart() {
    const cohorts = data.summaries[$('minimum').value];
    $('comparison-chart').innerHTML = Object.entries(data.measures).map(([measure, label]) => {
      const pair = [['IN','Indiana'],['US','National']].map(([region, name]) => {
        const share = cohorts[measure][region].above_share;
        return `<div class="bar-line"><span>${name}</span><div class="bar-track"><i class="bar-fill ${region.toLowerCase()}" style="width:${share === null ? 0 : share * 100}%"></i></div><strong>${share === null ? 'N/A' : percent(share)}</strong></div>`;
      }).join('');
      return `<div class="condition-bars"><h4>${escape(label)}</h4>${pair}<p>Eligible hospitals: ${count(cohorts[measure].IN.eligible)} Indiana · ${count(cohorts[measure].US.eligible)} national</p></div>`;
    }).join('');
    $('chart-filter-label').textContent = `All six conditions · ${$('minimum').selectedOptions[0].textContent}`;
  }
  function render() {
    const minimum = $('minimum').value;
    const label = data.measures[$('condition').value];
    const {IN: local, US: national} = data.summaries[minimum][$('condition').value];
    $('selection-label').textContent = `${label} · ${$('minimum').selectedOptions[0].textContent}`;
    $('eligible').textContent = `${local.eligible} / ${local.source_hospitals}`;
    $('eligible-note').textContent = minimum === '0' ? 'Hospitals with a published ratio' : 'Published ratio and selected volume minimum';
    $('indiana-share').textContent = percent(local.above_share);
    $('national-share').textContent = percent(national.above_share);
    $('indiana-count').textContent = `${count(local.above_one)} of ${count(local.eligible)} eligible hospitals`;
    $('national-count').textContent = `${count(national.above_one)} of ${count(national.eligible)} eligible hospitals`;
    $('median').textContent = local.median_err === null ? 'N/A' : local.median_err.toFixed(4);
    $('denominator-note').textContent = `Indiana: ${local.source_hospitals} source hospitals = ${local.eligible} eligible + ${local.missing_ratio} without a published ratio + ${local.missing_volume} with unavailable volume + ${local.below_volume} below the volume threshold.`;
    if (local.above_share === null || national.above_share === null) {
      $('comparison-note').textContent = 'No comparison is available for this selection. Missing results are not zero.';
    } else {
      const difference = (local.above_share - national.above_share) * 100;
      $('comparison-note').textContent = `Indiana is ${Math.abs(difference).toFixed(1)} percentage points ${difference < 0 ? 'below' : 'above'} national on this descriptive hospital-share measure.${local.eligible < 30 ? ' Fewer than 30 Indiana hospitals remain; inspect the small denominator.' : ''}`;
    }
    renderChart(); renderTable();
  }
  fetch('outputs/summary.json').then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then(result => {
    data = result;
    for (const id of ['condition','minimum','reset','hospital-search','table-scope']) $(id).disabled = false;
    for (const id of ['condition','minimum']) $(id).addEventListener('change', () => {page = 0; render();});
    $('hospital-search').addEventListener('input', () => {page = 0; renderTable();});
    $('table-scope').addEventListener('change', () => {page = 0; renderTable();});
    $('previous').addEventListener('click', () => {page--; renderTable();});
    $('next').addEventListener('click', () => {page++; renderTable();});
    $('reset').addEventListener('click', () => {
      $('condition').value = 'READM-30-COPD-HRRP'; $('minimum').value = '0';
      $('hospital-search').value = ''; $('table-scope').value = 'eligible'; page = 0; render();
    });
    render();
  }).catch(() => {
    $('load-note').textContent = 'Interactive data could not load. Baseline findings and CSV downloads remain available; reload to retry.';
  });
})();
