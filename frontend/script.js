// script.js - enhanced UI behaviors
const analyzeBtn = document.getElementById('analyzeBtn');
const suggestBtn = document.getElementById('suggestBtn');
const resultsEl = document.getElementById('results');
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');

analyzeBtn.addEventListener('click', () => runAnalyze(false));
suggestBtn.addEventListener('click', () => runAnalyze(true));

function setLoading(on){
  loadingEl.hidden = !on;
  analyzeBtn.disabled = on;
  suggestBtn.disabled = on;
  if(on) { resultsEl.innerHTML = ''; errorEl.textContent = ''; }
}

async function runAnalyze(suggestOnly=false){
  const raw = document.getElementById('taskInput').value.trim();
  let tasks;
  try {
    tasks = JSON.parse(raw || document.getElementById('sampleJson').textContent);
    if(!Array.isArray(tasks)) throw new Error('Please provide a JSON array of tasks');
  } catch(e){
    errorEl.textContent = 'Invalid JSON: ' + e.message;
    return;
  }

  const strat = document.getElementById('strategy').value;
  let weights = null;
  if(strat === 'fast') weights = {"urgency":0.1,"importance":0.2,"effort":0.6,"dependencies":0.1};
  else if(strat === 'impact') weights = {"urgency":0.1,"importance":0.7,"effort":0.1,"dependencies":0.1};
  else if(strat === 'deadline') weights = {"urgency":0.8,"importance":0.1,"effort":0.05,"dependencies":0.05};

  setLoading(true);

  try {
    const url = suggestOnly ? '/api/tasks/suggest/' : '/api/tasks/analyze/';
    const resp = await fetch(url, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({tasks, weights})
    });

    const body = await resp.json();

    if(!resp.ok){
      errorEl.textContent = body.error || JSON.stringify(body);
      setLoading(false);
      return;
    }

    // For suggest endpoint the shape is different
    const items = suggestOnly ? (body.suggestions || []) : (body.tasks || []);
    if(items.length === 0){
      resultsEl.innerHTML = '<p class="muted">No tasks returned</p>';
      setLoading(false);
      return;
    }

    renderResults(items, suggestOnly);
  } catch(err){
    errorEl.textContent = 'Network or server error: ' + (err.message || err);
  } finally {
    setLoading(false);
  }
}

function renderResults(items, suggestMode){
  resultsEl.innerHTML = '';
  // If suggestions, each item is { task, reason_summary }
  items.forEach((it, idx) => {
    const task = suggestMode ? it.task : it;
    const score = (task._score ?? 0);
    const scorePct = Math.round(Math.min(1, Math.max(0, score)) * 100);

    const card = document.createElement('article');
    card.className = 'task-card';

    // left meta
    const meta = document.createElement('div');
    meta.className = 'task-meta';

    const title = document.createElement('h3');
    title.className = 'task-title';
    title.innerHTML = escapeHtml(task.title || `Task ${idx+1}`);

    const sub = document.createElement('div');
    sub.className = 'task-sub muted';
    sub.textContent = `Due: ${task.due_date || 'N/A'} • Hours: ${task.estimated_hours ?? 'N/A'} • Importance: ${task.importance ?? 'N/A'}`;

    const barWrap = document.createElement('div');
    barWrap.className = 'scorebar';
    const barInner = document.createElement('i');
    barInner.style.width = (scorePct) + '%';
    // color by score
    if(score >= 0.7) barInner.style.background = 'linear-gradient(90deg, #ef4444, #c53030)';
    else if(score >= 0.4) barInner.style.background = 'linear-gradient(90deg, #f59e0b, #e89b1a)';
    else barInner.style.background = 'linear-gradient(90deg, #16a34a, #0f9b45)';
    barWrap.appendChild(barInner);

    const explanation = document.createElement('pre');
    explanation.className = 'explain';
    explanation.textContent = task._explanation || '';

    meta.appendChild(title);
    meta.appendChild(sub);
    meta.appendChild(barWrap);
    meta.appendChild(explanation);

    // right badge
    const badge = document.createElement('div');
    badge.className = 'score-badge';
    if(score >= 0.7) badge.classList.add('score-high');
    else if(score >= 0.4) badge.classList.add('score-mid');
    else badge.classList.add('score-low');

    badge.innerHTML = `<div style="font-size:14px">${(scorePct)}%</div><div style="font-size:11px;opacity:.9">priority</div>`;

    card.appendChild(meta);
    card.appendChild(badge);

    // if suggest mode, show reason summary
    if(suggestMode && it.reason_summary){
      const reason = document.createElement('div');
      reason.className = 'muted';
      reason.style.marginTop = '8px';
      reason.textContent = 'Why: ' + it.reason_summary;
      meta.appendChild(reason);
    }

    resultsEl.appendChild(card);
  });
}

function escapeHtml(s){
  return String(s || '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}
