const API_BASE = window.BOUNCE_API_BASE || '';

const els = {
  nameInput: document.querySelector('#traveller-name'),
  startButton: document.querySelector('#start-button'),
  healthButton: document.querySelector('#health-button'),
  seedButton: document.querySelector('#seed-button'),
  disruptionButton: document.querySelector('#disruption-button'),
  apiStatus: document.querySelector('#api-status'),
  apiOutput: document.querySelector('#api-output'),
};

function setStatus(message, state = 'pending') {
  if (!els.apiStatus) return;
  els.apiStatus.textContent = message;
  els.apiStatus.dataset.state = state;
}

function showOutput(payload) {
  if (!els.apiOutput) return;
  els.apiOutput.textContent = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new Error(body?.detail?.message || body?.detail || `HTTP ${response.status}`);
  }
  return body;
}

async function checkHealth() {
  setStatus('Checking API…');
  try {
    const health = await fetch(`${API_BASE}/health`).then((response) => response.json());
    setStatus(`API online: ${health.app || 'Bounce'} ${health.version || ''}`.trim(), 'ok');
    showOutput(health);
    return health;
  } catch (error) {
    setStatus('API unavailable — start FastAPI or set BOUNCE_API_BASE', 'error');
    showOutput(error.message);
    throw error;
  }
}

async function seedDemoTrip() {
  setStatus('Seeding demo trip…');
  const result = await fetch(`${API_BASE}/judge/seed-demo-trip`, { method: 'POST' }).then((response) => response.json());
  setStatus('Demo trip seeded', 'ok');
  showOutput(result);
  return result;
}

async function triggerDisruption() {
  setStatus('Triggering demo disruption…');
  const result = await fetch(`${API_BASE}/judge/trigger-disruption`, { method: 'POST' }).then((response) => response.json());
  setStatus('Disruption event created', 'ok');
  showOutput(result);
  return result;
}

function personalizeShell() {
  const name = els.nameInput?.value?.trim();
  if (!name) {
    els.nameInput?.focus();
    return;
  }
  showOutput(`Nice to meet you, ${name}. Backend checks are ready below.`);
  document.querySelector('#demo-title')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

els.startButton?.addEventListener('click', personalizeShell);
els.nameInput?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') personalizeShell();
});
els.healthButton?.addEventListener('click', () => checkHealth().catch(() => {}));
els.seedButton?.addEventListener('click', () => seedDemoTrip().catch((error) => {
  setStatus('Seed failed', 'error');
  showOutput(error.message);
}));
els.disruptionButton?.addEventListener('click', () => triggerDisruption().catch((error) => {
  setStatus('Disruption trigger failed', 'error');
  showOutput(error.message);
}));

checkHealth().catch(() => {});
