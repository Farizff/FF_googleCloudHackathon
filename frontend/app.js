const API_BASE = window.BOUNCE_API_BASE || '';
const GOOGLE_MAPS_API_KEY = 'YOUR_API_KEY';

let bounceMap = null;
let bounceMarkers = [];
let bounceInfoWindow = null;

function initBounceMap() {
  if (bounceMap) return; // already initialized
  const mapCanvas = document.getElementById('map-canvas');
  if (!mapCanvas) return;

  // Check if the API key is still the placeholder
  if (GOOGLE_MAPS_API_KEY === 'YOUR_API_KEY' || !GOOGLE_MAPS_API_KEY) {
    showMapFallback(mapCanvas, 'Map: configure GOOGLE_MAPS_API_KEY');
    return;
  }

  try {
    bounceMap = new google.maps.Map(mapCanvas, {
      center: { lat: 35.6762, lng: 139.6503 }, // Tokyo
      zoom: 13,
      disableDefaultUI: false,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: true,
    });
    bounceInfoWindow = new google.maps.InfoWindow();
  } catch (err) {
    showMapFallback(mapCanvas, 'Map: Google Maps failed to load');
  }
}

function showMapFallback(container, message) {
  if (!container) return;
  container.style.cssText = 'width:100%;height:300px;background:#e8eef4;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#0D3B66;font-weight:600;';
  container.textContent = message;
}

function clearBounceMarkers() {
  bounceMarkers.forEach(m => m.setMap(null));
  bounceMarkers = [];
}

function addVenueMarker(lat, lng, label, color) {
  if (!bounceMap) return null;
  const colorMap = {
    budget: '#2196F3',    // blue
    recommended: '#4CAF50', // green
    premium: '#FFC107',   // gold
    default: '#0D3B66',   // navy
  };
  const markerColor = colorMap[color] || colorMap.default;

  const svgIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="36" viewBox="0 0 24 36">
      <path fill="${markerColor}" d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24C24 5.4 18.6 0 12 0z"/>
      <circle fill="#ffffff" cx="12" cy="12" r="6"/>
    </svg>
  `;

  const marker = new google.maps.Marker({
    position: { lat, lng },
    map: bounceMap,
    icon: {
      url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svgIcon),
      scaledSize: new google.maps.Size(24, 36),
      anchor: new google.maps.Point(12, 36),
    },
    title: label,
  });

  marker.addListener('click', () => {
    if (bounceInfoWindow) {
      bounceInfoWindow.setContent(`<strong>${label}</strong>`);
      bounceInfoWindow.open(bounceMap, marker);
    }
  });

  bounceMarkers.push(marker);
  return marker;
}

async function showItineraryView() {
  const tripId = window.currentTripId;
  const itineraryId = window.currentItineraryId || (tripId === 'trip_tokyo_reunion_2026' ? 'iti_tokyo_reunion_2026' : null);
  if (!tripId && !itineraryId) {
    showOutput('No currentTripId set — cannot load itinerary.');
    return;
  }
  setStatus('Loading itinerary…');
  try {
    const data = await requestJson(`/itineraries/${itineraryId || tripId}`);
    const itinerary = data.itinerary;
    window.currentItineraryId = itinerary.itinerary_id || itineraryId;
    const titleEl = document.querySelector('#itinerary-title');
    const timelineEl = document.getElementById('itinerary-timeline');
    if (titleEl && itinerary) {
      titleEl.textContent = `${itinerary.trip_id} — Itinerary`;
    }
    if (timelineEl && itinerary?.days?.length) {
      const day = itinerary.days[0];
      timelineEl.innerHTML = (day.activities || []).map(act => {
        const time = act.start_time || act.time || '';
        const title = act.title || act.name || act.description || '';
        return `<li><time>${time}</time><span>${title}</span></li>`;
      }).join('');
    }

    // Initialize Google Map with itinerary venue pins
    initBounceMap();
    clearBounceMarkers();

    if (itinerary?.days?.length) {
      const day = itinerary.days[0];
      (day.activities || []).forEach((act, idx) => {
        if (act.lat && act.lng) {
          addVenueMarker(act.lat, act.lng, act.title || act.name || `Stop ${idx + 1}`, 'default');
        }
      });

      // Fit map to show all markers
      if (bounceMarkers.length > 0) {
        const bounds = new google.maps.LatLngBounds();
        bounceMarkers.forEach(m => bounds.extend(m.getPosition()));
        bounceMap.fitBounds(bounds);
      }
    }

    setStatus('Itinerary loaded', 'ok');
    showOutput(itinerary);
  } catch (err) {
    setStatus('Itinerary unavailable', 'error');
    showOutput(err.message);
  }
}

function showDisruptionSheet(alternatives = []) {
  if (!bounceMap) {
    initBounceMap();
  }
  if (!bounceMap) return;

  const colorByTier = { budget: 'budget', recommended: 'recommended', premium: 'premium' };
  (alternatives || []).forEach((alt, idx) => {
    const color = colorByTier[alt.tier?.toLowerCase()] || 'default';
    const label = alt.name || alt.venue_name || `Option ${idx + 1}: ${alt.tier || ''}`;
    if (alt.lat && alt.lng) {
      addVenueMarker(alt.lat, alt.lng, `${idx + 1}. ${label}`, color);
    }
  });

  if (bounceMarkers.length > 0) {
    const bounds = new google.maps.LatLngBounds();
    bounceMarkers.forEach(m => bounds.extend(m.getPosition()));
    bounceMap.fitBounds(bounds);
  }
}

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
  groupDashboard: document.querySelector('#group-dashboard'),
  suggestionReview: document.querySelector('#suggestion-review'),
  flockActiveView: document.querySelector('#flock-active-view'),
  activeTripView: document.querySelector('#active-trip-view'),
  splitBill: document.querySelector('#split-bill'),
  splitIntoFlocksButton: document.querySelector('#split-into-flocks'),
  startFlockModeButton: document.querySelector('#start-flockmode'),
  logExpenseButton: document.querySelector('#log-expense'),
  bottomNav: document.querySelector('.bottom-nav'),
  inviteToken: document.querySelector('#invite-token'),
  joinTripButton: document.querySelector('#join-trip-button'),
  inviteError: document.querySelector('#invite-error'),
  loadItineraryButton: document.querySelector('#load-itinerary-button'),
  refreshSettlementButton: document.querySelector('#refresh-settlement-button'),
};

const state = {
  travellerName: 'Alex',
  planningCategories: new Set(),
  tripMode: 'International',
  preferences: new Set(['Halal-friendly']),
  selectedFlightTier: 'recommended',
  selectedFlightNumber: 'ANA NH106',
  selectedExpenseMode: 'Everyone',
  selectedExpenseCategory: 'Food',
  suggestionStatus: 'pending',
  suggestionCount: 3,
  activeFlockName: 'The Explorers',
  expenseCount: 1,
};

function setStatus(message, stateName = 'pending') {
  if (!els.apiStatus) return;
  els.apiStatus.textContent = message;
  els.apiStatus.dataset.state = stateName;
}

function showOutput(payload) {
  if (!els.apiOutput) return;
  els.apiOutput.textContent = typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2);
}

function setBounceMessage(message) {
  if (els.bounceResponse) els.bounceResponse.textContent = message;
}

function visibleList(values) {
  const arr = Array.from(values || []);
  return arr.length ? arr.join(', ') : 'none selected yet';
}

function scrollToElement(element) {
  element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const text = await response.text();
  let body = {};
  try {
    body = text ? JSON.parse(text) : {};
  } catch (error) {
    body = { raw: text };
  }
  if (!response.ok) {
    throw new Error(body?.detail?.message || body?.detail || body?.message || `HTTP ${response.status}`);
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
    setStatus('API unavailable — using local demo interactions', 'error');
    showOutput(error.message);
    throw error;
  }
}

function selectedPlanningDetails() {
  return {
    traveller: state.travellerName,
    categories: Array.from(state.planningCategories),
    mode: state.tripMode,
    preferences: Array.from(state.preferences),
    selected_flight: state.selectedFlightNumber,
  };
}

async function sendTripPrompt() {
  const prompt = els.tripPrompt?.value?.trim();
  if (!prompt) {
    els.tripPrompt?.focus();
    setStatus('Add a trip brief or tap a few chips first', 'error');
    return null;
  }

  setStatus('Bounce is planning…');
  setBounceMessage('Reading the group brief, preferences, and current demo state…');

  const fallback = demoPlanningSnapshot(prompt);
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: `${prompt}\n\nContext: ${JSON.stringify(selectedPlanningDetails())}`,
        user_id: 'u_alex',
        trip_id: 'trip_tokyo_reunion_2026',
      }),
    }).then((res) => res.json());
    if (response.trip_id) window.currentTripId = response.trip_id;
    renderPlanningSnapshot({ ...fallback, bounce_message: response.message || fallback.bounce_message });
    setStatus('Planning snapshot ready', 'ok');
    // Load live flight options once the planning context is set.
    showFlightSelectionView();
    return response;
  } catch (error) {
    renderPlanningSnapshot(fallback);
    setStatus('Showing local planning snapshot — chat API unavailable', 'error');
showFlightSelectionView();
    return fallback;
  }
}

function demoPlanningSnapshot(prompt) {
  const categories = visibleList(state.planningCategories);
  const preferences = visibleList(state.preferences);
  const dayOneIntensity = state.preferences.has('Low walking first day') ? 'low-walking reset' : 'light culture walk';
  return {
    bounce_message: `Got it — I’ll plan this as a ${categories} Tokyo group trip for ${state.travellerName}. I’ll respect ${preferences}, keep Day 1 as a ${dayOneIntensity}, and use the ${state.tripMode.toLowerCase()} arrival buffer. Brief: “${prompt.slice(0, 90)}${prompt.length > 90 ? '…' : ''}”`,
    budget: { used_percent: state.preferences.has('Shopping') ? 71 : 64, per_traveller_usd: state.planningCategories.has('Shopping') ? 2380 : 2240 },
    flights: [
      { tier: 'Budget', flight_number: 'ZIPAIR ZG25', risk: 72 },
      { tier: 'Recommended', flight_number: 'ANA NH106', risk: 84 },
      { tier: 'Premium', flight_number: 'JAL JL1', risk: 80 },
    ],
    map_pins: ['Hotel', 'Asakusa', state.planningCategories.has('Food') ? 'Ueno dinner' : 'teamLab Borderless'],
  };
}

function renderPlanningSnapshot(snapshot) {
  setBounceMessage(snapshot.bounce_message);
  renderBudgetTracker(snapshot.budget);
  renderFlightOptions(snapshot.flights);
  renderMapPins(snapshot.map_pins);
}

function renderBudgetTracker(budget) {
  const meter = document.querySelector('.budget-meter span');
  const label = document.querySelector('#budget-tracker .muted');
  if (meter && budget?.used_percent) meter.style.width = `${budget.used_percent}%`;
  if (label && budget?.per_traveller_usd) label.innerHTML = `<strong>$${budget.per_traveller_usd.toLocaleString()}</strong> estimated per traveller before flights. Preferences: ${visibleList(state.preferences)}.`;
}

function renderFlightOptions(flights = []) {
  if (!els.flightOptions || flights.length === 0) return;
  els.flightOptions.innerHTML = flights.map((flight) => {
    const tier = flight.tier.toLowerCase();
    const selected = tier === state.selectedFlightTier;
    const risk = flight.risk ?? flight.risk_score ?? 0;
    return `
    <article class="flight-option-card${flight.tier === 'Recommended' ? ' is-recommended' : ''}${selected ? ' is-selected' : ''}" data-tier="${tier}" data-flight-number="${flight.flight_number}" tabindex="0" role="button" aria-pressed="${selected}">
      <span>${flight.tier}${selected ? ' · selected' : ''}</span><strong>${flight.flight_number}</strong><small>Risk ${risk}/100</small>
      <div class="risk-bar"><span style="width: ${risk}%"></span></div>
    </article>`;
  }).join('');
}

async function showFlightSelectionView() {
  const origin = window.tripOrigin || 'SFO';
  const destination = window.tripDestination || 'TYO';
  const date = window.tripDepartureDate || '2026-10-15';

  setStatus('Loading flights…');
  try {
    const data = await requestJson(`/flights/search?origin=${origin}&destination=${destination}&date=${date}`);
    if (data.error) {
      // Fall back to demo data if API returns an error.
      renderFlightOptions(demoPlanningSnapshot('').flights);
      setStatus('Flight search unavailable — showing demo options', 'error');
      return;
    }
    const options = data.options || [];
    if (options.length === 0) {
      renderFlightOptions(demoPlanningSnapshot('').flights);
      setStatus('No flights found — showing demo options', 'error');
      return;
    }
    renderFlightOptions(options);
    setStatus(`${options.length} flight option${options.length !== 1 ? 's' : ''} loaded`, 'ok');
  } catch (err) {
    renderFlightOptions(demoPlanningSnapshot('').flights);
    setStatus('Flight API unavailable — showing demo options', 'error');
    showOutput(err.message);
  }
}

function renderMapPins(pins = []) {
  const canvas = document.querySelector('.map-canvas');
  if (!canvas || pins.length === 0) return;
  canvas.dataset.pins = pins.join(' → ');
  canvas.setAttribute('aria-label', `Static map preview route: ${pins.join(' to ')}. Selected flight ${state.selectedFlightNumber}.`);
  canvas.title = `Route: ${pins.join(' → ')} · Flight: ${state.selectedFlightNumber}`;
}

function demoActiveTripSnapshot() {
  return {
    group: { joined: 7, pending: 3, organiser: 'Alex', co_leader: 'Priya' },
    suggestion: { count: state.suggestionCount, text: 'Move teamLab Borderless earlier so delayed arrivals can still join dinner.' },
    flock: { name: state.activeFlockName, reconvene: 'Shinjuku Station East Exit', countdown: '3h 42m' },
    active_trip: { flight: `${state.selectedFlightNumber} SFO → NRT · On time · Lands 4:50pm`, now: state.suggestionStatus === 'accepted' ? 'teamLab Borderless moved earlier' : 'teamLab Borderless' },
    split_bill: { amount: 128.40, description: 'Ramen dinner', split_between: splitBetweenCopy() },
  };
}

function renderGroupDashboard(snapshot = demoActiveTripSnapshot()) {
  if (!els.groupDashboard) return;
  els.groupDashboard.dataset.joined = snapshot.group.joined;
  els.groupDashboard.dataset.pending = snapshot.group.pending;
}

function renderSuggestionReview(snapshot = demoActiveTripSnapshot()) {
  if (!els.suggestionReview) return;
  els.suggestionReview.dataset.suggestions = snapshot.suggestion.count;
  const badge = els.suggestionReview.querySelector('.suggestion-count-badge');
  const item = els.suggestionReview.querySelector('.suggestion-item');
  if (badge) badge.textContent = String(snapshot.suggestion.count);
  if (item) item.dataset.status = state.suggestionStatus;
}

function renderFlockMode(snapshot = demoActiveTripSnapshot()) {
  if (!els.flockActiveView) return;
  els.flockActiveView.dataset.flock = snapshot.flock.name;
  const title = els.flockActiveView.querySelector('h2');
  if (title) title.textContent = `🐦 ${snapshot.flock.name}`;
  const muted = els.flockActiveView.querySelector('.muted');
  if (muted) muted.textContent = snapshot.flock.name === 'Food Scouts' ? 'Marcus, Sofia, Liam' : 'Alex, Priya, Aditya, Emma';
  const reconvene = els.flockActiveView.querySelector('.reconvene-countdown strong');
  if (reconvene) reconvene.textContent = `Meet at ${snapshot.flock.reconvene}`;
}

function renderActiveTrip(snapshot = demoActiveTripSnapshot()) {
  if (els.bottomNav) els.bottomNav.dataset.phase = 'active';
  if (!els.activeTripView) return;
  els.activeTripView.dataset.currentActivity = snapshot.active_trip.now;
  const banner = els.activeTripView.querySelector('.flight-status-banner');
  if (banner) banner.textContent = snapshot.active_trip.flight;
  const activity = els.activeTripView.querySelector('.current-activity-card strong');
  if (activity) activity.textContent = snapshot.active_trip.now;
}

function renderSplitBill(snapshot = demoActiveTripSnapshot()) {
  if (!els.splitBill) return;
  els.splitBill.dataset.amount = String(snapshot.split_bill.amount);
  const splitCopy = els.splitBill.querySelector('.muted');
  if (splitCopy) splitCopy.textContent = `Split between: ${snapshot.split_bill.split_between}`;
}

function toggleButton(button, isSelected) {
  button.classList.toggle('is-selected', isSelected);
  button.setAttribute('aria-pressed', String(isSelected));
}

function applyChipToPrompt(text) {
  if (!els.tripPrompt) return;
  const phrase = text === 'International' ? 'international arrivals with buffer' : text.toLowerCase();
  if (!els.tripPrompt.value.toLowerCase().includes(phrase.toLowerCase())) {
    els.tripPrompt.value = `${els.tripPrompt.value.trim()} ${els.tripPrompt.value.trim() ? ' ' : ''}${phrase}`.trim();
  }
}

function handlePlanningChip(button) {
  const category = button.dataset.category;
  const mode = button.dataset.mode;
  if (category) {
    if (state.planningCategories.has(category)) state.planningCategories.delete(category);
    else state.planningCategories.add(category);
    toggleButton(button, state.planningCategories.has(category));
    applyChipToPrompt(category);
    setStatus(`Planning focus: ${visibleList(state.planningCategories)}`, 'ok');
  }
  if (mode) {
    state.tripMode = state.tripMode === mode ? 'Domestic' : mode;
    toggleButton(button, state.tripMode === mode);
    applyChipToPrompt(mode);
    setStatus(`${state.tripMode} planning mode selected`, 'ok');
  }
  setBounceMessage(`I’ll tune the plan around: ${visibleList(state.planningCategories)}. Mode: ${state.tripMode}.`);
}

function handleProfileChip(button) {
  const label = button.textContent.trim();
  if (state.preferences.has(label)) state.preferences.delete(label);
  else state.preferences.add(label);
  toggleButton(button, state.preferences.has(label));
  button.classList.add('bounce-updated');
  setTimeout(() => button.classList.remove('bounce-updated'), 320);
  setStatus(`Profile preferences updated: ${visibleList(state.preferences)}`, 'ok');
  setBounceMessage(`Saved for this demo session: ${visibleList(state.preferences)}.`);
}

function selectFlight(card) {
  state.selectedFlightTier = card.dataset.tier;
  state.selectedFlightNumber = card.dataset.flightNumber || card.querySelector('strong')?.textContent || 'selected flight';
  els.flightOptions?.querySelectorAll('.flight-option-card').forEach((option) => {
    const selected = option === card;
    option.classList.toggle('is-selected', selected);
    option.setAttribute('aria-pressed', String(selected));
  });
  setStatus(`${state.selectedFlightNumber} selected for the group`, 'ok');
  showOutput({ selected_flight: state.selectedFlightNumber, tier: state.selectedFlightTier, note: 'Selection saved in local demo state.' });
  renderActiveTrip();
  renderMapPins((document.querySelector('.map-canvas')?.dataset.pins || 'Hotel → Asakusa → Ueno dinner').split(' → '));
}

async function showSettlementView() {
  const tripId = window.currentTripId;
  if (!tripId) {
    showOutput('No currentTripId set — cannot load settlement.');
    return;
  }
  setStatus('Loading settlement…');
  try {
    const data = await requestJson(`/settlements/${tripId}`);
    const balances = data.balances || {};
    const transactions = data.transactions || [];

    // Update balance cards in the split-bill section
    const balanceGrid = document.querySelector('.balance-grid');
    if (balanceGrid) {
      balanceGrid.innerHTML = Object.entries(balances).map(([userId, balance]) => {
        const cls = balance > 0.01 ? 'is-owed' : balance < -0.01 ? 'owes' : 'balanced';
        const sign = balance > 0 ? '+' : '';
        return `<article class="balance-card ${cls}"><strong>${userId}</strong><span>${sign}$${balance.toFixed(2)}</span></article>`;
      }).join('');
    }

    // Show transactions summary
    const output = { balances, transactions };
    showOutput(output);
    setStatus('Settlement loaded', 'ok');
  } catch (err) {
    setStatus('Settlement unavailable', 'error');
    showOutput(err.message);
  }
}

function activateFlockMode() {
  const firstFlockInput = document.querySelector('.flock-name-input');
  state.activeFlockName = firstFlockInput?.value?.trim() || state.activeFlockName;
  renderFlockMode();
  renderActiveTrip();
  scrollToElement(els.flockActiveView);
  setStatus(`FlockMode active for ${state.activeFlockName}`, 'ok');
  showOutput({ flock_mode: 'active', active_flock: state.activeFlockName, reconvene: 'Shinjuku Station East Exit 18:30' });
}

function prepareFlockSplit() {
  setStatus('Default Flocks prepared — review names, then start FlockMode', 'ok');
  showOutput({ flocks: ['The Explorers', 'Food Scouts'], next_step: 'Edit names if needed, then tap Start FlockMode.' });
  scrollToElement(document.querySelector('#flockmode-creation'));
}

function handleSuggestion(action) {
  const suggestionText = document.querySelector('.suggestion-text')?.textContent?.trim() || 'member suggestion';
  if (action === 'accept') {
    state.suggestionStatus = 'accepted';
    state.suggestionCount = Math.max(0, state.suggestionCount - 1);
    const timelineItem = document.querySelector('#itinerary-timeline li:nth-child(2) span');
    if (timelineItem) timelineItem.textContent = 'teamLab Borderless moved earlier — accepted member suggestion';
    setStatus('Suggestion accepted and applied to Day 1 itinerary', 'ok');
    setBounceMessage(`Accepted: ${suggestionText}`);
  } else if (action === 'modify') {
    state.suggestionStatus = 'modifying';
    if (els.tripPrompt) {
      els.tripPrompt.value = `Modify suggestion: ${suggestionText}`;
      scrollToElement(document.querySelector('#entry-conversation'));
      els.tripPrompt.focus();
    }
    setStatus('Suggestion loaded into Bounce prompt for modification', 'ok');
  } else {
    state.suggestionStatus = 'declined';
    state.suggestionCount = Math.max(0, state.suggestionCount - 1);
    setStatus('Suggestion declined — itinerary unchanged', 'ok');
    setBounceMessage('Declined the member suggestion and kept the current itinerary unchanged.');
  }
  renderSuggestionReview();
  renderActiveTrip();
  showOutput({ suggestion_status: state.suggestionStatus, remaining_suggestions: state.suggestionCount });
}

async function askBounceAboutToday() {
  const question = 'What should we know about today in Tokyo?';
  setStatus('Asking Bounce about today…');
  setBounceMessage('Checking today’s schedule, flight status, FlockMode, and group context…');
  try {
    const response = await requestJson('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: `${question} Context: active activity is ${demoActiveTripSnapshot().active_trip.now}, selected flight is ${state.selectedFlightNumber}, active Flock is ${state.activeFlockName}.`,
        user_id: 'u_alex',
        trip_id: 'trip_tokyo_reunion_2026',
      }),
    });
    setBounceMessage(response.message || 'Today looks manageable — keep the group together for the next transit and reconvene on time.');
    setStatus('Active trip answer ready', 'ok');
    showOutput(response);
  } catch (error) {
    const fallback = `Today: ${demoActiveTripSnapshot().active_trip.now}. ${state.selectedFlightNumber} is on time, ${state.activeFlockName} reconvenes at Shinjuku Station East Exit, and the safest next step is to leave an 18-minute train buffer.`;
    setBounceMessage(fallback);
    setStatus('Showing local active-trip answer — chat API unavailable', 'error');
    showOutput({ fallback: true, answer: fallback, reason: error.message });
  }
  scrollToElement(document.querySelector('#entry-conversation'));
}

function splitBetweenCopy() {
  if (state.selectedExpenseMode === 'Specific people') return 'Alex, Priya, Carlos';
  if (state.selectedExpenseMode === 'My Flock') return `${state.activeFlockName} members`;
  if (state.selectedExpenseMode === 'Just me') return state.travellerName;
  return 'Alex, Priya, Carlos (+4 more)';
}

function selectExpenseMode(button) {
  state.selectedExpenseMode = button.textContent.trim();
  document.querySelectorAll('.expense-tabs button').forEach((tab) => tab.setAttribute('aria-selected', String(tab === button)));
  renderSplitBill();
  setStatus(`Expense split mode: ${state.selectedExpenseMode}`, 'ok');
}

function selectExpenseCategory(button) {
  state.selectedExpenseCategory = button.textContent.replace(/^[^A-Za-z]+/, '').trim() || button.textContent.trim();
  els.splitBill?.querySelectorAll('.chip-grid .quick-chip').forEach((chip) => toggleButton(chip, chip === button));
  setStatus(`Expense category: ${state.selectedExpenseCategory}`, 'ok');
}

function expenseLoggingMode() {
  const mode = state.selectedExpenseMode;
  if (mode === 'Specific people') return 'specific_people';
  if (mode === 'My Flock') return 'my_flock';
  if (mode === 'Just me') return 'just_me';
  return 'everyone';
}

async function logDemoExpense() {
  const amountInput = document.querySelector('.amount-input input');
  const descriptionInput = document.querySelector('.expense-description');
  const amount = Number.parseFloat(amountInput?.value || '0') || 0;
  const description = descriptionInput?.value?.trim() || 'Shared expense';
  const tripId = window.currentTripId || 'trip_tokyo_reunion_2026';
  state.expenseCount += 1;
  renderSplitBill({ split_bill: { amount, description, split_between: splitBetweenCopy() } });
  const balanceCards = els.splitBill?.querySelectorAll('.balance-card span');
  const share = state.selectedExpenseMode === 'Just me' ? 0 : amount / (state.selectedExpenseMode === 'Specific people' ? 3 : 7);
  if (balanceCards?.[0]) balanceCards[0].textContent = `+$${(share * 2).toFixed(2)}`;
  if (balanceCards?.[1]) balanceCards[1].textContent = `-$${share.toFixed(2)}`;
  if (balanceCards?.[2]) balanceCards[2].textContent = state.selectedExpenseMode === 'Just me' ? '$0.00' : `-$${(share / 2).toFixed(2)}`;
  setStatus('Logging expense…');
  try {
    const payload = {
      trip_id: tripId,
      logged_by_user_id: 'u_alex',
      amount,
      currency: 'USD',
      category: state.selectedExpenseCategory,
      description,
      logging_mode: expenseLoggingMode(),
      participants: state.selectedExpenseMode === 'Specific people' ? ['u_alex', 'u_priya', 'u_marcus'] : undefined,
      flock_id: state.selectedExpenseMode === 'My Flock' ? 'flock_explorers' : undefined,
    };
    const result = await requestJson('/expenses', { method: 'POST', body: JSON.stringify(payload) });
    setStatus('Expense logged — settlement refreshed', 'ok');
    showOutput(result);
    await showSettlementView();
  } catch (error) {
    setStatus('Demo expense logged locally — expense API unavailable', 'error');
    showOutput({ expense: description, amount, category: state.selectedExpenseCategory, split_mode: state.selectedExpenseMode, split_between: splitBetweenCopy(), local_demo_state: true, reason: error.message });
  }
}

async function seedDemoTrip() {
  setStatus('Seeding demo trip…');
  const result = await fetch(`${API_BASE}/judge/seed-demo-trip`, { method: 'POST' }).then((response) => response.json());
  window.currentTripId = result.trip_id;
  window.currentItineraryId = result.itinerary_id || window.currentItineraryId;
  if (els.inviteToken && result.invite_token) els.inviteToken.value = result.invite_token;
  setStatus(`Demo trip seeded: ${result.trip_name || result.trip_id}`, 'ok');
  setBounceMessage(`Demo trip is ready. Invite token ${result.invite_token || 'is available after backend seed'} is prefilled for Join Trip.`);
  showOutput(result);
  return result;
}

async function triggerDisruption() {
  setStatus('Triggering demo disruption…');
  try {
    const result = await fetch(`${API_BASE}/judge/trigger-disruption`, { method: 'POST' }).then((response) => response.json());
    setStatus('Disruption event created', 'ok');
    setBounceMessage('Heads up — the disruption is handled. I found alternatives and kept the group timeline intact.');
    const timelineItem = document.querySelector('#itinerary-timeline li:nth-child(3) span');
    if (timelineItem) timelineItem.textContent = 'Mori Art Museum alternative selected after disruption';
    renderMapPins(['Hotel', 'teamLab Borderless', 'Mori Art Museum']);
    showOutput(result);
    return result;
  } catch (error) {
    setStatus('Showing local disruption fallback — API unavailable', 'error');
    const fallback = { alternatives: ['Mori Art Museum', 'Tokyo City View', 'Nezu Museum'], local_demo_state: true, reason: error.message };
    setBounceMessage('Demo fallback: venue closure handled with 3 alternatives near the current route.');
    showOutput(fallback);
    return fallback;
  }
}

async function joinTrip() {
  const token = els.inviteToken?.value?.trim();
  const name = els.nameInput?.value?.trim();
  if (!token) {
    showInviteError('Please enter an invite token.');
    return;
  }
  if (!name) {
    showInviteError('Please enter your name first (above).');
    return;
  }
  setStatus('Joining trip…');
  if (els.inviteError) els.inviteError.hidden = true;
  try {
    const userId = `u_${name.toLowerCase().replace(/\s+/g, '_')}`;
    const result = await requestJson('/trips/join', {
      method: 'POST',
      body: JSON.stringify({ invite_token: token, user_id: userId, name }),
    });
    window.currentTripId = result.trip_id;
    setStatus(`Joined ${result.trip_name}! Loading itinerary…`, 'ok');
    showOutput(result);
    // Navigate to itinerary / profile gap-fill screen
    document.querySelector('#entry-conversation')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return result;
  } catch (err) {
    setStatus('Join failed', 'error');
    showInviteError(err.message || 'Could not join trip. Check your token and try again.');
    showOutput(err.message);
    throw err;
  }
}

function showInviteError(msg) {
  if (!els.inviteError) return;
  els.inviteError.textContent = msg;
  els.inviteError.hidden = false;
}

function personalizeShell() {
  const name = els.nameInput?.value?.trim();
  if (!name) {
    els.nameInput?.focus();
    setStatus('Enter your name to personalize the demo', 'error');
    return;
  }
  state.travellerName = name;
  showOutput(`Nice to meet you, ${name}. Backend checks are ready below, and the planning controls now react visibly.`);
  setBounceMessage(`Hi ${name} — tell me the trip vibe, or tap chips and I’ll build the planning snapshot.`);
  scrollToElement(document.querySelector('#entry-conversation'));
}

function wirePlanningChips() {
  document.querySelectorAll('#entry-conversation .quick-chip').forEach((button) => {
    button.addEventListener('click', () => handlePlanningChip(button));
  });
}

function wireProfileChips() {
  document.querySelectorAll('#profile-gap-fill .quick-chip').forEach((button) => {
    toggleButton(button, state.preferences.has(button.textContent.trim()));
    button.addEventListener('click', () => handleProfileChip(button));
  });
}

function wireFlightCards() {
  els.flightOptions?.addEventListener('click', (event) => {
    const card = event.target.closest('.flight-option-card');
    if (card) selectFlight(card);
  });
  els.flightOptions?.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const card = event.target.closest('.flight-option-card');
    if (card) {
      event.preventDefault();
      selectFlight(card);
    }
  });
}

function wireSuggestionButtons() {
  document.querySelector('.sug-accept')?.addEventListener('click', () => handleSuggestion('accept'));
  document.querySelector('.sug-modify')?.addEventListener('click', () => handleSuggestion('modify'));
  document.querySelector('.sug-decline')?.addEventListener('click', () => handleSuggestion('decline'));
}

function wireSplitBillControls() {
  document.querySelectorAll('.expense-tabs button').forEach((button) => {
    button.addEventListener('click', () => selectExpenseMode(button));
  });
  els.splitBill?.querySelectorAll('.chip-grid .quick-chip').forEach((button) => {
    button.addEventListener('click', () => selectExpenseCategory(button));
  });
}

function wireBottomNav() {
  document.querySelectorAll('.bottom-nav .nav-tab').forEach((link) => {
    link.addEventListener('click', () => {
      document.querySelectorAll('.bottom-nav .nav-tab').forEach((tab) => {
        tab.classList.toggle('active', tab === link);
        if (tab === link) tab.setAttribute('aria-current', 'page');
        else tab.removeAttribute('aria-current');
      });
    });
  });
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
els.joinTripButton?.addEventListener('click', () => joinTrip().catch((error) => {
  setStatus('Join failed', 'error');
}));
els.inviteToken?.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') joinTrip().catch(() => {});
});

els.splitIntoFlocksButton?.addEventListener('click', prepareFlockSplit);
els.startFlockModeButton?.addEventListener('click', activateFlockMode);
els.logExpenseButton?.addEventListener('click', () => logDemoExpense().catch((error) => {
  setStatus('Expense logging failed', 'error');
  showOutput(error.message);
}));
els.loadItineraryButton?.addEventListener('click', () => showItineraryView().catch((error) => {
  setStatus('Itinerary load failed', 'error');
  showOutput(error.message);
}));
els.refreshSettlementButton?.addEventListener('click', () => showSettlementView().catch((error) => {
  setStatus('Settlement refresh failed', 'error');
  showOutput(error.message);
}));
document.querySelector('.ask-bounce-button')?.addEventListener('click', askBounceAboutToday);

wirePlanningChips();
wireProfileChips();
wireFlightCards();
wireSuggestionButtons();
wireSplitBillControls();
wireBottomNav();
renderGroupDashboard();
renderSuggestionReview();
renderActiveTrip();
renderSplitBill();
renderMapPins(['Hotel', 'Asakusa', 'Ueno dinner']);

// ─── FlockMode drag-and-drop ───────────────────────────────────────────
let draggedChip = null;

function initFlockModeDragDrop() {
  // Set up drag events on all member chips (both in unassigned pool and in flock dropzones)
  document.querySelectorAll('.member-chip[draggable="true"]').forEach(chip => {
    chip.addEventListener('dragstart', onDragStart);
    chip.addEventListener('dragend', onDragEnd);
  });

  // Set up drop zones: unassigned pool
  const pool = document.getElementById('unassigned-pool');
  if (pool) {
    pool.addEventListener('dragover', onDragOver);
    pool.addEventListener('drop', onDropPool);
    pool.addEventListener('dragleave', onDragLeave);
  }

  // Set up drop zones: flock dropzones
  document.querySelectorAll('.flock-dropzone').forEach(zone => {
    zone.addEventListener('dragover', onDragOver);
    zone.addEventListener('drop', onDropFlock);
    zone.addEventListener('dragleave', onDragLeave);
  });

  // Add Flock button
  const addFlockBtn = document.getElementById('add-flock-btn');
  if (addFlockBtn) {
    addFlockBtn.addEventListener('click', addNewFlock);
  }

  // Save FlockMode button
  const saveBtn = document.getElementById('save-flockmode-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', saveFlockMode);
  }
}

function onDragStart(e) {
  draggedChip = e.target;
  e.target.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', e.target.dataset.userId || '');
}

function onDragEnd(e) {
  e.target.classList.remove('dragging');
  document.querySelectorAll('.flock-dropzone').forEach(z => z.classList.remove('drag-over'));
  const pool = document.getElementById('unassigned-pool');
  if (pool) pool.classList.remove('drag-over');
  draggedChip = null;
}

function onDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.classList.add('drag-over');
}

function onDragLeave(e) {
  // Only remove class if leaving the container itself
  if (!e.currentTarget.contains(e.relatedTarget)) {
    e.currentTarget.classList.remove('drag-over');
  }
}

function onDropPool(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');
  if (!draggedChip) return;

  // If dropped back on the unassigned pool, remove from any flock
  const userId = draggedChip.dataset.userId;
  if (userId) removeMemberFromAllFlocks(userId);

  // Move chip to unassigned pool
  const pool = document.getElementById('unassigned-pool');
  if (pool && !pool.contains(draggedChip)) {
    pool.appendChild(draggedChip);
    updateLeaderOptions();
  }
}

function onDropFlock(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('drag-over');
  if (!draggedChip) return;

  const dropzone = e.currentTarget;
  const chip = draggedChip;
  const userId = chip.dataset.userId;

  // Remove from any other flock first
  if (userId) removeMemberFromAllFlocks(userId);

  // Append to this dropzone
  dropzone.appendChild(chip);
  updateLeaderOptions();
}

function removeMemberFromAllFlocks(userId) {
  document.querySelectorAll('.flock-dropzone').forEach(zone => {
    Array.from(zone.children).forEach(child => {
      if (child.dataset.userId === userId) {
        // Move back to unassigned pool
        const pool = document.getElementById('unassigned-pool');
        if (pool) pool.appendChild(child);
      }
    });
  });
}

function updateLeaderOptions() {
  // Collect all members currently placed in flocks
  const placedUserIds = new Set();
  document.querySelectorAll('.flock-dropzone .member-chip').forEach(chip => {
    if (chip.dataset.userId) placedUserIds.add(chip.dataset.userId);
  });

  // Update each flock's leader dropdown: disable options already assigned to another flock
  document.querySelectorAll('.flock-box').forEach(box => {
    const select = box.querySelector('.flock-leader-select');
    const thisFlockMembers = Array.from(box.querySelectorAll('.flock-dropzone .member-chip'))
      .map(c => c.dataset.userId)
      .filter(Boolean);
    const currentLeader = select?.value;

    Array.from(select?.options || []).forEach(opt => {
      const userId = opt.value;
      if (!userId) return; // skip placeholder
      const isInThisFlock = thisFlockMembers.includes(userId);
      const isPlacedElsewhere = placedUserIds.has(userId) && !isInThisFlock;
      opt.disabled = isPlacedElsewhere;
    });
  });
}

let flockCounter = 2; // already have 2 flocks (0 and 1)

function addNewFlock() {
  const grid = document.getElementById('flock-grid');
  if (!grid) return;

  const id = flockCounter++;
  const allUserIds = ['u_alex','u_priya','u_marcus','u_sofia','u_jake','u_aditya'];
  const name = `Flock ${id + 1}`;

  const article = document.createElement('article');
  article.className = 'flock-box';
  article.dataset.flockId = id;
  article.innerHTML = `
    <input class="flock-name-input" value="${name}" aria-label="Flock name" />
    <select class="flock-leader-select" aria-label="Select leader for this flock">
      <option value="">Select leader…</option>
      ${allUserIds.map(uid => {
        const displayName = uid.replace('u_', '').charAt(0).toUpperCase() + uid.replace('u_', '').slice(1);
        return `<option value="${uid}">${displayName}</option>`;
      }).join('')}
    </select>
    <div class="flock-dropzone" data-flock-id="${id}"></div>
  `;

  grid.appendChild(article);

  // Re-init drag events on all chips (new chips added in existing flocks)
  document.querySelectorAll('.member-chip[draggable="true"]').forEach(chip => {
    chip.removeEventListener('dragstart', onDragStart);
    chip.removeEventListener('dragend', onDragEnd);
    chip.addEventListener('dragstart', onDragStart);
    chip.addEventListener('dragend', onDragEnd);
  });

  // Set up dropzone events for the new dropzone
  const dropzone = article.querySelector('.flock-dropzone');
  dropzone.addEventListener('dragover', onDragOver);
  dropzone.addEventListener('drop', onDropFlock);
  dropzone.addEventListener('dragleave', onDragLeave);

  updateLeaderOptions();
}

function showToast(message) {
  // Remove existing toast
  document.querySelectorAll('.toast').forEach(t => t.remove());
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

async function saveFlockMode() {
  const tripId = window.currentTripId || 'trip_tokyo_reunion_2026';

  // Collect all flocks
  const flocks = [];
  document.querySelectorAll('.flock-box').forEach(box => {
    const name = box.querySelector('.flock-name-input')?.value?.trim() || `Flock ${flocks.length + 1}`;
    const leaderSelect = box.querySelector('.flock-leader-select');
    const leaderUserId = leaderSelect?.value || null;
    const memberIds = Array.from(box.querySelectorAll('.flock-dropzone .member-chip'))
      .map(chip => chip.dataset.userId)
      .filter(Boolean);

    if (memberIds.length > 0) {
      flocks.push({ name, leader_user_id: leaderUserId, member_ids: memberIds });
    }
  });

  const reconveneTime = document.getElementById('reconvene-time')?.value || '';
  const reconveneLocation = document.getElementById('reconvene-location')?.value || '';

  if (flocks.length === 0) {
    showToast('Add at least one member to a flock before saving.');
    return;
  }

  setStatus('Saving FlockMode…');

  try {
    const savedFlocks = await Promise.all(flocks.map((flock) => {
      const payload = {
        flock_name: flock.name,
        leader_user_id: flock.leader_user_id || flock.member_ids[0],
        member_ids: flock.member_ids,
        trip_id: tripId,
        reconvene_time: reconveneTime || '18:30',
        reconvene_location: reconveneLocation || 'Shinjuku Station East Exit',
        day_number: 5,
        activity: 'Tokyo free-time FlockMode',
      };
      return requestJson('/flocks', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    }));

    state.activeFlockName = flocks[0]?.name || state.activeFlockName;
    renderFlockMode({ ...demoActiveTripSnapshot(), flock: { name: state.activeFlockName, reconvene: reconveneLocation || 'Shinjuku Station East Exit' } });
    renderActiveTrip();
    showOutput({ saved_flocks: savedFlocks, trip_id: tripId });

    showToast('FlockMode activated 🐦');
    setStatus('FlockMode saved', 'ok');

    // Transition to flock-active-view
    document.getElementById('flock-active-view')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    setStatus('FlockMode save failed', 'error');
    showOutput(err.message);
    showToast('FlockMode save failed — check console');
  }
}

// Initialize drag-and-drop on load
document.addEventListener('DOMContentLoaded', initFlockModeDragDrop);
checkHealth().catch(() => {});
