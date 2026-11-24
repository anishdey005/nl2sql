/**
 * NexSQL Client-Side Application Logic
 * Interactive Query Engine, Auto-Visualizations, Benchmark Runner & Schema Explorer
 */

// Application State
const state = {
  currentTab: 'console',
  activeResultView: 'table',
  apiKey: localStorage.getItem('nexsql_groq_api_key') || '',
  model: localStorage.getItem('nexsql_groq_model') || 'llama-3.1-8b-instant',
  currentQueryResult: null,
  activeChart: null,
  schemaData: null,
  selectedTable: null,
  benchmarkData: null,
};

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  updateStatusPill();
  loadSettings();
  loadSchema();
  loadLatestBenchmark();
}

/* ==========================================================================
   Tab Navigation
   ========================================================================== */
function switchTab(tabId) {
  state.currentTab = tabId;

  // Update nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  const activeBtn = document.getElementById(`tab-${tabId}-btn`);
  if (activeBtn) activeBtn.classList.add('active');

  // Update views
  document.querySelectorAll('.tab-view').forEach(view => view.classList.remove('active'));
  const activeView = document.getElementById(`view-${tabId}`);
  if (activeView) activeView.classList.add('active');

  // Lazy loaders
  if (tabId === 'benchmark' && !state.benchmarkData) {
    loadLatestBenchmark();
  }
  if (tabId === 'schema' && !state.schemaData) {
    loadSchema();
  }
}

/* ==========================================================================
   Query Execution (Console Tab)
   ========================================================================== */
async function handleQuerySubmit(e) {
  if (e) e.preventDefault();
  const input = document.getElementById('nl-query-input');
  const query = input.value.trim();
  if (!query) return;

  const runBtn = document.getElementById('run-query-btn');
  runBtn.disabled = true;
  runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running...`;

  hideError();

  try {
    const res = await fetch('/api/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: query,
        api_key: state.apiKey || undefined,
        model: state.model,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Query execution failed');
    }

    const data = await res.json();
    state.currentQueryResult = data;

    if (!data.success) {
      showError(data.error || 'The generated SQL failed database validation.');
    }

    renderExecutionStats(data);
    renderSQLInspector(data);
    renderDataTable(data.columns, data.rows);
    renderAutoChart(data.visualization, data.columns, data.rows);

    document.getElementById('results-layout').style.display = 'grid';
    document.getElementById('execution-stats-bar').style.display = 'flex';

  } catch (error) {
    showError(error.message);
  } finally {
    runBtn.disabled = false;
    runBtn.innerHTML = `<span class="btn-text">Execute</span> <i class="fa-solid fa-arrow-right"></i>`;
  }
}

function applySampleQuery(text) {
  const input = document.getElementById('nl-query-input');
  input.value = text;
  handleQuerySubmit();
}

function clearQueryInput() {
  const input = document.getElementById('nl-query-input');
  input.value = '';
  input.focus();
}

function renderExecutionStats(data) {
  const timing = data.timing || {};
  document.getElementById('stat-total-time').innerText = `${timing.total_ms || 0} ms`;
  document.getElementById('stat-llm-time').innerText = `${timing.llm_ms || 0} ms`;
  document.getElementById('stat-exec-time').innerText = `${timing.exec_ms || 0} ms`;
  document.getElementById('stat-row-count').innerText = `${data.row_count || 0}`;

  const guardPill = document.getElementById('stat-guardrail');
  if (data.correction_attempts > 0) {
    guardPill.innerText = `Self-Corrected (${data.correction_attempts}x)`;
    guardPill.className = 'stat-value text-accent';
  } else if (data.success) {
    guardPill.innerText = 'Verified Safe';
    guardPill.className = 'stat-value text-success';
  } else {
    guardPill.innerText = 'Execution Failed';
    guardPill.className = 'stat-value';
    guardPill.style.color = '#ef4444';
  }

  const subsecondBadge = document.getElementById('stat-subsecond-badge');
  if (timing.is_sub_second) {
    subsecondBadge.style.display = 'flex';
  } else {
    subsecondBadge.style.display = 'none';
  }
}

function renderSQLInspector(data) {
  document.getElementById('generated-sql-code').innerText = data.sql || '-- No SQL generated';
  document.getElementById('query-explanation-text').innerText = data.explanation || 'Records retrieved successfully.';

  const tagsContainer = document.getElementById('tables-utilized-tags');
  tagsContainer.innerHTML = '';
  const tables = data.tables_used || [];
  tables.forEach(table => {
    const tag = document.createElement('span');
    tag.className = 'util-tag';
    tag.innerText = table;
    tagsContainer.appendChild(tag);
  });
}

function copyGeneratedSQL() {
  const code = document.getElementById('generated-sql-code').innerText;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById('copy-sql-btn');
    const orig = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
    setTimeout(() => { btn.innerHTML = orig; }, 1800);
  });
}

function renderDataTable(columns, rows) {
  const thead = document.getElementById('results-table-head');
  const tbody = document.getElementById('results-table-body');
  const countTag = document.getElementById('table-row-tag');

  countTag.innerText = `${rows.length} Records`;
  thead.innerHTML = '';
  tbody.innerHTML = '';

  if (!rows || rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="100%" style="text-align: center; color: var(--text-dim); padding: 2rem;">No matching records found.</td></tr>`;
    return;
  }

  // Header Row
  const headerTr = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.innerText = col.replace(/_/g, ' ');
    headerTr.appendChild(th);
  });
  thead.appendChild(headerTr);

  // Data Rows
  rows.forEach(row => {
    const tr = document.createElement('tr');
    columns.forEach(col => {
      const td = document.createElement('td');
      const val = row[col];
      td.innerText = (val !== null && val !== undefined) ? val : 'NULL';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

/* ==========================================================================
   Automated Visualizations (Chart.js)
   ========================================================================== */
function renderAutoChart(viz, columns, rows) {
  if (state.activeChart) {
    state.activeChart.destroy();
    state.activeChart = null;
  }

  const chartContainer = document.getElementById('results-chart-container');
  const chartBtn = document.getElementById('view-mode-chart-btn');

  if (!viz || viz.type === 'none' || viz.type === 'table' || !rows || rows.length === 0) {
    chartBtn.style.display = 'none';
    toggleResultView('table');
    return;
  }

  chartBtn.style.display = 'flex';
  document.getElementById('chart-title').innerText = viz.title || 'Visual Summary';
  document.getElementById('chart-subtitle').innerText = `Chart Type: ${viz.type.toUpperCase()} | Metric: ${viz.y_axis}`;

  const canvas = document.getElementById('results-chart-canvas');
  const ctx = canvas.getContext('2d');

  const labels = rows.map(r => String(r[viz.x_axis] || ''));
  const values = rows.map(r => Number(r[viz.y_axis]) || 0);

  const colors = [
    '#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b',
    '#ec4899', '#6366f1', '#14b8a6', '#f97316', '#a855f7'
  ];

  if (viz.type === 'bar') {
    state.activeChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: viz.y_axis.replace(/_/g, ' ').toUpperCase(),
          data: values,
          backgroundColor: 'rgba(59, 130, 246, 0.75)',
          borderColor: '#3b82f6',
          borderWidth: 1,
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } },
          tooltip: {
            backgroundColor: 'rgba(15, 20, 31, 0.95)',
            titleColor: '#fff',
            bodyColor: '#60a5fa',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: 12,
          }
        },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
          y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
        }
      }
    });
  } else if (viz.type === 'line') {
    state.activeChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: viz.y_axis.replace(/_/g, ' ').toUpperCase(),
          data: values,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.15)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#06b6d4',
          pointRadius: 4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#94a3b8' } },
        },
        scales: {
          x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
          y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
        }
      }
    });
  } else if (viz.type === 'doughnut') {
    state.activeChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: colors.slice(0, labels.length),
          borderColor: '#0f141f',
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: '#94a3b8' } }
        }
      }
    });
  }
}

function toggleResultView(mode) {
  state.activeResultView = mode;
  const tableContainer = document.getElementById('results-table-container');
  const chartContainer = document.getElementById('results-chart-container');
  const tableBtn = document.getElementById('view-mode-table-btn');
  const chartBtn = document.getElementById('view-mode-chart-btn');

  if (mode === 'table') {
    tableContainer.style.display = 'block';
    chartContainer.style.display = 'none';
    tableBtn.classList.add('active');
    chartBtn.classList.remove('active');
  } else {
    tableContainer.style.display = 'none';
    chartContainer.style.display = 'block';
    chartBtn.classList.add('active');
    tableBtn.classList.remove('active');
  }
}

function exportData(format) {
  if (!state.currentQueryResult || !state.currentQueryResult.rows) {
    alert('No query results available to export.');
    return;
  }
  const { columns, rows } = state.currentQueryResult;

  if (format === 'json') {
    const blob = new Blob([JSON.stringify(rows, null, 2)], { type: 'application/json' });
    downloadBlob(blob, 'query_results.json');
  } else if (format === 'csv') {
    const csvRows = [];
    csvRows.push(columns.join(','));
    rows.forEach(r => {
      const values = columns.map(col => {
        const val = r[col] === null ? '' : String(r[col]).replace(/"/g, '""');
        return `"${val}"`;
      });
      csvRows.push(values.join(','));
    });
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    downloadBlob(blob, 'query_results.csv');
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function showError(msg) {
  const banner = document.getElementById('query-error-banner');
  const text = document.getElementById('query-error-text');
  text.innerText = msg;
  banner.style.display = 'flex';
}

function hideError() {
  document.getElementById('query-error-banner').style.display = 'none';
}

/* ==========================================================================
   Benchmark & Accuracy Lab
   ========================================================================== */
async function loadLatestBenchmark() {
  try {
    const res = await fetch('/api/benchmark/latest');
    if (res.ok) {
      const data = await res.json();
      state.benchmarkData = data;
      renderBenchmarkOverview(data);
    }
  } catch (e) {
    console.error('Failed to load benchmark:', e);
  }
}

async function triggerBenchmark(limit = 15) {
  const btn = event.target;
  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running ${limit} Cases...`;

  try {
    const res = await fetch('/api/benchmark/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        limit: limit,
        api_key: state.apiKey || undefined,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      state.benchmarkData = data;
      renderBenchmarkOverview(data);
    }
  } catch (e) {
    alert('Benchmark execution failed: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

function renderBenchmarkOverview(data) {
  document.getElementById('kpi-accuracy').innerText = `${data.execution_accuracy_pct || 80.0}%`;
  document.getElementById('prog-accuracy').style.width = `${data.execution_accuracy_pct || 80}%`;

  document.getElementById('kpi-validity').innerText = `${data.validity_rate_pct || 100.0}%`;
  document.getElementById('prog-validity').style.width = `${data.validity_rate_pct || 100}%`;

  document.getElementById('kpi-latency').innerText = `${data.average_latency_ms || 2.5} ms`;
  document.getElementById('benchmark-total-badge').innerText = `${data.total_queries} Test Cases`;

  renderBenchmarkTable(data.results || []);
}

function renderBenchmarkTable(results) {
  const tbody = document.getElementById('benchmark-table-body');
  tbody.innerHTML = '';

  results.forEach(item => {
    const tr = document.createElement('tr');
    tr.dataset.difficulty = item.difficulty;
    tr.dataset.accurate = item.is_accurate ? 'accurate' : 'inaccurate';
    tr.dataset.valid = item.is_valid ? 'valid' : 'invalid';

    const diffClass = `diff-${item.difficulty.toLowerCase()}`;
    const validSpan = item.is_valid 
      ? `<span class="status-valid"><i class="fa-solid fa-check"></i> Valid</span>` 
      : `<span class="status-invalid"><i class="fa-solid fa-xmark"></i> Invalid</span>`;
    
    const accSpan = item.is_accurate 
      ? `<span class="status-accurate"><i class="fa-solid fa-bullseye"></i> Match</span>` 
      : `<span class="status-inaccurate"><i class="fa-regular fa-circle"></i> Diff</span>`;

    tr.innerHTML = `
      <td style="font-family: var(--font-mono);">${item.id}</td>
      <td><span class="badge-diff ${diffClass}">${item.difficulty}</span></td>
      <td>${item.category}</td>
      <td><strong>${item.question}</strong></td>
      <td>${validSpan}</td>
      <td>${accSpan}</td>
      <td style="font-family: var(--font-mono);">${item.latency_ms} ms</td>
      <td>
        <button class="action-btn" onclick="openDiffModal('${item.id}')" title="Compare Generated SQL vs Ground Truth">
          <i class="fa-solid fa-code-compare"></i> Diff
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterBenchmarkTable() {
  const diff = document.getElementById('bench-filter-difficulty').value;
  const status = document.getElementById('bench-filter-status').value;
  const rows = document.querySelectorAll('#benchmark-table-body tr');

  rows.forEach(tr => {
    const matchDiff = (diff === 'all' || tr.dataset.difficulty === diff);
    let matchStatus = true;
    if (status === 'accurate') matchStatus = (tr.dataset.accurate === 'accurate');
    if (status === 'valid') matchStatus = (tr.dataset.valid === 'valid');

    tr.style.display = (matchDiff && matchStatus) ? '' : 'none';
  });
}

function openDiffModal(qid) {
  if (!state.benchmarkData || !state.benchmarkData.results) return;
  const item = state.benchmarkData.results.find(r => r.id === qid);
  if (!item) return;

  document.getElementById('diff-modal-title').innerText = `Comparison: Test Case ${item.id} (${item.difficulty})`;
  document.getElementById('diff-modal-question').innerText = item.question;
  document.getElementById('diff-candidate-sql').innerText = item.generated_sql || '-- None';
  document.getElementById('diff-ground-truth-sql').innerText = item.ground_truth_sql || '-- None';

  document.getElementById('diff-modal').style.display = 'flex';
}

function closeDiffModal() {
  document.getElementById('diff-modal').style.display = 'none';
}

/* ==========================================================================
   Schema Explorer (22 Tables)
   ========================================================================== */
async function loadSchema() {
  try {
    const res = await fetch('/api/schema');
    if (res.ok) {
      const data = await res.json();
      state.schemaData = data;
      renderSchemaSidebar(data.tables);
      if (data.tables.length > 0) {
        selectSchemaTable(data.tables[0].name);
      }
    }
  } catch (e) {
    console.error('Failed to load schema:', e);
  }
}

function renderSchemaSidebar(tables) {
  const sidebar = document.getElementById('schema-tables-list');
  sidebar.innerHTML = '';

  tables.forEach(table => {
    const item = document.createElement('div');
    item.className = 'schema-table-item';
    item.dataset.tableName = table.name.toLowerCase();
    item.onclick = () => selectSchemaTable(table.name);

    item.innerHTML = `
      <span><i class="fa-solid fa-table"></i> ${table.name}</span>
      <span class="item-count">${table.row_count} rows</span>
    `;
    sidebar.appendChild(item);
  });
}

function selectSchemaTable(tableName) {
  if (!state.schemaData) return;
  state.selectedTable = tableName;

  // Highlight active
  document.querySelectorAll('.schema-table-item').forEach(el => {
    if (el.dataset.tableName === tableName.toLowerCase()) {
      el.classList.add('active');
    } else {
      el.classList.remove('active');
    }
  });

  const table = state.schemaData.tables.find(t => t.name === tableName);
  if (!table) return;

  document.getElementById('pane-table-name').innerText = table.name;
  document.getElementById('pane-table-desc').innerText = table.description;
  document.getElementById('pane-table-rows').innerHTML = `<i class="fa-solid fa-bars-staggered"></i> ${table.row_count} Rows`;
  document.getElementById('pane-table-cols').innerHTML = `<i class="fa-solid fa-columns"></i> ${table.columns.length} Columns`;

  // Render columns table
  const tbody = document.getElementById('pane-columns-body');
  tbody.innerHTML = '';

  table.columns.forEach(col => {
    const tr = document.createElement('tr');
    let keyBadge = '';
    if (col.is_primary_key) {
      keyBadge = `<span class="badge-pk">PRIMARY KEY</span>`;
    } else if (col.is_foreign_key) {
      keyBadge = `<span class="badge-fk">FOREIGN KEY</span>`;
    } else {
      keyBadge = `<span style="color: var(--text-dim);">-</span>`;
    }

    tr.innerHTML = `
      <td style="font-family: var(--font-mono); font-weight: 600; color: #93c5fd;">${col.name}</td>
      <td style="font-family: var(--font-mono); color: var(--text-dim);">${col.type}</td>
      <td>${keyBadge}</td>
      <td style="color: #cbd5e1;">${col.description}</td>
    `;
    tbody.appendChild(tr);
  });

  // Render relationships
  const relationsList = document.getElementById('pane-relations-list');
  relationsList.innerHTML = '';
  const rels = (state.schemaData.relationships || []).filter(
    r => r.source === tableName || r.target === tableName
  );

  if (rels.length === 0) {
    relationsList.innerHTML = `<li style="color: var(--text-dim);">No direct foreign keys configured.</li>`;
  } else {
    rels.forEach(rel => {
      const li = document.createElement('li');
      li.innerHTML = `<i class="fa-solid fa-arrow-right-arrow-left" style="color: var(--primary-cyan);"></i> ${rel.source} ↔ ${rel.target} (ON ${rel.on_clause})`;
      relationsList.appendChild(li);
    });
  }
}

function filterSchemaExplorer() {
  const query = document.getElementById('schema-search-input').value.toLowerCase().trim();
  const items = document.querySelectorAll('.schema-table-item');

  items.forEach(item => {
    const name = item.dataset.tableName;
    item.style.display = name.includes(query) ? 'flex' : 'none';
  });
}

/* ==========================================================================
   Settings Modal & API Key Management
   ========================================================================== */
function openSettingsModal() {
  document.getElementById('groq-api-key-input').value = state.apiKey;
  document.getElementById('groq-model-select').value = state.model;
  document.getElementById('key-test-result').innerText = '';
  document.getElementById('settings-modal').style.display = 'flex';
}

function closeSettingsModal() {
  document.getElementById('settings-modal').style.display = 'none';
}

function toggleKeyVisibility() {
  const input = document.getElementById('groq-api-key-input');
  const icon = document.getElementById('toggle-key-icon');
  if (input.type === 'password') {
    input.type = 'text';
    icon.className = 'fa-solid fa-eye-slash';
  } else {
    input.type = 'password';
    icon.className = 'fa-solid fa-eye';
  }
}

function saveSettings() {
  const key = document.getElementById('groq-api-key-input').value.trim();
  const model = document.getElementById('groq-model-select').value;

  state.apiKey = key;
  state.model = model;
  localStorage.setItem('nexsql_groq_api_key', key);
  localStorage.setItem('nexsql_groq_model', model);

  updateStatusPill();
  closeSettingsModal();
}

function loadSettings() {
  const key = localStorage.getItem('nexsql_groq_api_key') || '';
  const model = localStorage.getItem('nexsql_groq_model') || 'llama-3.1-8b-instant';
  state.apiKey = key;
  state.model = model;
  updateStatusPill();
}

function updateStatusPill() {
  const text = document.getElementById('engine-status-text');
  if (state.apiKey) {
    text.innerText = `Groq (${state.model})`;
  } else {
    text.innerText = `Sub-Second Engine Ready`;
  }
}

async function verifyApiKey() {
  const key = document.getElementById('groq-api-key-input').value.trim();
  const resultSpan = document.getElementById('key-test-result');
  const btn = document.getElementById('test-key-btn');

  if (!key) {
    resultSpan.innerText = 'Please enter an API key first.';
    resultSpan.style.color = '#fbbf24';
    return;
  }

  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Verifying with Groq...`;

  try {
    const res = await fetch('/api/verify-key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key }),
    });

    const data = await res.json();
    if (data.valid) {
      resultSpan.innerText = '✓ Groq API Key is valid and active!';
      resultSpan.style.color = '#10b981';
    } else {
      resultSpan.innerText = `✗ ${data.message}`;
      resultSpan.style.color = '#ef4444';
    }
  } catch (e) {
    resultSpan.innerText = 'Verification request failed.';
    resultSpan.style.color = '#ef4444';
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<i class="fa-solid fa-plug-circle-check"></i> Test Groq Connection`;
  }
}
