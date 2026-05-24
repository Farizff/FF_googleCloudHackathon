const API_BASE = window.BOUNCE_API_BASE || '';

const els = {
  nameInput: document.querySelector('#traveller-name'),
  startButton: document.querySelector('#start-button'),
  healthButton: document.querySelector('#health-button'),
  seedButton: document.querySelector('#seed-button'),
  disruptionButton: document.querySelector('#disruption-button'),
  apiStatus: document.querySelector('#api-status'),
  apiOutput: document.querySelector('#api-output'),
  tripPrompt: document.querySelector('#trip-prompt'),
  sendTripPromptButton: document.querySelector('#send-trip-prompt'),
  bounceResponse: document.querySelector('#bounce-response'),
  flightOptions: document.querySelector('#flight-options'),
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

async function sendTripPrompt() {
  const prompt = els.tripPrompt?.value?.trim();
  if (!prompt) {
    els.tripPrompt?.focus();
    return null;
  }

  setStatus('Bounce is planning…');
  if (els.bounceResponse) els.bounceResponse.textContent = 'Reading the group brief and building a planning snapshot…';

  const fallback = demoPlanningSnapshot(prompt);
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: prompt, user_id: 'u_alex', trip_id: 'trip_tokyo_reunion_2026' }),
    }).then((res) => res.json());
    renderPlanningSnapshot({ ...fallback, bounce_message: response.message || fallback.bounce_message });
    setStatus('Planning snapshot ready', 'ok');
    return response;
  } catch (error) {
    renderPlanningSnapshot(fallback);
    setStatus('Showing local planning snapshot — chat API unavailable', 'error');
    return fallback;
  }
}

function demoPlanningSnapshot(prompt) {
  return {
    bounce_message: `Got it — I’ll plan this as a culture-heavy Tokyo group trip. Brief: “${prompt.slice(0, 90)}${prompt.length > 90 ? '…' : ''}”`,
    budget: { used_percent: 64, per_traveller_usd: 2240 },
    flights: [
      { tier: 'Budget', flight_number: 'ZIPAIR ZG25', risk: 72 },
      { tier: 'Recommended', flight_number: 'ANA NH106', risk: 84 },
      { tier: 'Premium', flight_number: 'JAL JL1', risk: 80 },
    ],
    map_pins: ['Hotel', 'Asakusa', 'Ueno dinner'],
  };
}

function renderPlanningSnapshot(snapshot) {
  if (els.bounceResponse) els.bounceResponse.textContent = snapshot.bounce_message;
  renderBudgetTracker(snapshot.budget);
  renderFlightOptions(snapshot.flights);
  renderMapPins(snapshot.map_pins);
}

function renderBudgetTracker(budget) {
  const meter = document.querySelector('.budget-meter span');
  const label = document.querySelector('#budget-tracker .muted');
  if (meter && budget?.used_percent) meter.style.width = `${budget.used_percent}%`;
  if (label && budget?.per_traveller_usd) label.innerHTML = `<strong>$${budget.per_traveller_usd.toLocaleString()}</strong> estimated per traveller before flights.`;
}

function renderFlightOptions(flights = []) {
  if (!els.flightOptions || flights.length === 0) return;
  els.flightOptions.innerHTML = flights.map((flight) => `
    <article class="flight-option-card${flight.tier === 'Recommended' ? ' is-recommended' : ''}" data-tier="${flight.tier.toLowerCase()}">
      <span>${flight.tier}</span><strong>${flight.flight_number}</strong><small>Risk ${flight.risk}/100</small>
      <div class="risk-bar"><span style="width: ${flight.risk}%"></span></div>
    </article>
  `).join('');
}

function renderMapPins(pins = []) {
  const canvas = document.querySelector('.map-canvas');
  if (!canvas || pins.length === 0) return;
  canvas.dataset.pins = pins.join(' → ');
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
els.sendTripPromptButton?.addEventListener('click', () => sendTripPrompt().catch((error) => {
  setStatus('Chat planning failed', 'error');
  showOutput(error.message);
}));
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
