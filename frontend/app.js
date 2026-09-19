const API_BASE = window.location.origin.includes('localhost') && !window.location.pathname.startsWith('/static')
    ? ''
    : (window.location.origin);

let currentView = 'trips-list';
let currentTripId = null;
let editingTripId = null;

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function showView(viewName) {
    currentView = viewName;
    $$('.view').forEach(v => v.classList.add('hidden'));
    const target = $('#view-' + viewName);
    if (target) {
        target.classList.remove('hidden');
    }
}

function showToast(message, type = 'info') {
    const container = $('#toast-container');
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-green-600 border-green-700',
        error: 'bg-red-600 border-red-700',
        info: 'bg-slate-700 border-slate-800',
        warning: 'bg-amber-600 border-amber-700'
    };
    toast.className = `toast px-4 py-3 rounded-lg shadow-lg text-white text-sm flex items-center gap-2 border ${colors[type] || colors.info} min-w-[260px]`;
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '!'
    };
    toast.innerHTML = `<span class="font-bold">${icons[type] || icons.info}</span><span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(120%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    if (text == null) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

async function apiRequest(url, method = 'GET', body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body != null) {
        opts.body = JSON.stringify(body);
    }
    const res = await fetch(API_BASE + url, opts);
    let data = null;
    const text = await res.text();
    try { data = text ? JSON.parse(text) : null; } catch (e) { data = text; }
    if (!res.ok) {
        const msg = (data && data.detail) ? data.detail : `Request failed: ${res.status}`;
        throw new Error(msg);
    }
    return { ok: true, status: res.status, data };
}

function formatDate(d) {
    if (!d) return '';
    const dt = new Date(d);
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function daysBetween(start, end) {
    if (!start || !end) return 0;
    const a = new Date(start);
    const b = new Date(end);
    return Math.round((b - a) / (1000 * 60 * 60 * 24)) + 1;
}

function totalActivities(trip) {
    return (trip.days || []).reduce((sum, d) => sum + (d.activities || []).length, 0);
}

async function renderTripsList() {
    showView('trips-list');
    const container = $('#view-trips-list');
    container.innerHTML = `
        <div class="mb-8 flex items-center justify-between">
            <div>
                <h2 class="text-2xl font-bold text-slate-800">My Trips</h2>
                <p class="text-slate-500 mt-1" id="trips-subtitle">Loading...</p>
            </div>
            <button id="btn-create-trip" data-testid="create-trip-btn" class="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-medium shadow-sm transition-colors flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Create Trip
            </button>
        </div>
        <div id="trips-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"></div>
    `;

    $('#btn-create-trip').addEventListener('click', () => openTripForm());
    $('#brand-link').addEventListener('click', () => renderTripsList());

    try {
        const { data: trips } = await apiRequest('/api/trips');
        const grid = $('#trips-grid');
        $('#trips-subtitle').textContent = `${trips.length} trip${trips.length === 1 ? '' : 's'} planned`;

        if (trips.length === 0) {
            grid.innerHTML = `
                <div class="col-span-full bg-white rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
                    <div class="mx-auto w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <h3 class="text-lg font-semibold text-slate-700 mb-1">No trips yet</h3>
                    <p class="text-slate-500 mb-5">Create your first trip to get started planning adventures.</p>
                </div>
            `;
        } else {
            grid.innerHTML = trips.map(trip => renderTripCard(trip)).join('');
            $$('[data-action]', grid).forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const action = btn.dataset.action;
                    const tripId = btn.dataset.tripId;
                    if (action === 'view') renderTripDetails(tripId);
                    else if (action === 'edit') openTripForm(tripId);
                    else if (action === 'delete') confirmDeleteTrip(tripId);
                });
            });
        }
    } catch (err) {
        showToast('Failed to load trips: ' + err.message, 'error');
        $('#trips-grid').innerHTML = `<div class="col-span-full p-8 bg-red-50 border border-red-200 rounded-xl text-red-700">Error: ${escapeHtml(err.message)}</div>`;
    }
}

function renderTripCard(trip) {
    const numDays = daysBetween(trip.start_date, trip.end_date);
    const numActs = totalActivities(trip);
    return `
        <div class="trip-card bg-white rounded-xl border border-slate-200 hover:border-indigo-300 hover:shadow-md transition-all overflow-hidden" data-testid="trip-card" data-trip-id="${trip.id}">
            <div class="h-24 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center relative">
                <span class="absolute inset-0 bg-black/10"></span>
                <div class="relative text-white text-center px-4">
                    <div class="text-xs font-medium uppercase tracking-wide opacity-90">${escapeHtml(trip.destination)}</div>
                </div>
            </div>
            <div class="p-5">
                <h3 class="font-semibold text-lg text-slate-800 mb-2" data-testid="trip-name">${escapeHtml(trip.name)}</h3>
                <div class="flex items-center gap-2 text-sm text-slate-500 mb-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    <span>${formatDate(trip.start_date)} — ${formatDate(trip.end_date)}</span>
                </div>
                <div class="flex items-center gap-4 text-sm text-slate-500 mb-4">
                    <span class="flex items-center gap-1"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>${numDays} day${numDays === 1 ? '' : 's'}</span>
                    <span class="flex items-center gap-1"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>${numActs} activit${numActs === 1 ? 'y' : 'ies'}</span>
                </div>
                <div class="flex items-center gap-2 pt-3 border-t border-slate-100">
                    <button class="flex-1 bg-slate-50 hover:bg-slate-100 text-slate-700 py-2 rounded-lg text-sm font-medium transition-colors" data-action="view" data-trip-id="${trip.id}" data-testid="view-trip-btn">
                        View Details
                    </button>
                    <button class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="Edit" data-action="edit" data-trip-id="${trip.id}" data-testid="edit-trip-btn">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button class="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Delete" data-action="delete" data-trip-id="${trip.id}" data-testid="delete-trip-btn">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </div>
        </div>
    `;
}

async function confirmDeleteTrip(tripId) {
    const confirm = await showConfirmModal(
        'Delete Trip',
        'Are you sure you want to delete this trip? This action cannot be undone.',
        'Delete',
        'bg-red-600 hover:bg-red-700'
    );
    if (!confirm) return;
    try {
        await apiRequest(`/api/trips/${tripId}`, 'DELETE');
        showToast('Trip deleted successfully', 'success');
        renderTripsList();
    } catch (err) {
        showToast('Failed to delete trip: ' + err.message, 'error');
    }
}

function showConfirmModal(title, message, confirmText = 'Confirm', confirmClass = 'bg-indigo-600 hover:bg-indigo-700') {
    return new Promise((resolve) => {
        const root = $('#modal-root');
        root.innerHTML = `
            <div id="confirm-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 fade-in">
                <div class="bg-white rounded-xl shadow-2xl max-w-md w-full">
                    <div class="p-6 border-b border-slate-100">
                        <h3 class="text-lg font-semibold text-slate-800">${escapeHtml(title)}</h3>
                    </div>
                    <div class="p-6">
                        <p class="text-slate-600">${escapeHtml(message)}</p>
                    </div>
                    <div class="p-6 pt-0 flex justify-end gap-3">
                        <button id="modal-cancel" class="px-4 py-2 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors">Cancel</button>
                        <button id="modal-confirm" class="px-4 py-2 text-white rounded-lg font-medium transition-colors ${confirmClass}">${escapeHtml(confirmText)}</button>
                    </div>
                </div>
            </div>
        `;
        const cleanup = (result) => {
            $('#confirm-modal').remove();
            resolve(result);
        };
        $('#modal-cancel').addEventListener('click', () => cleanup(false));
        $('#modal-confirm').addEventListener('click', () => cleanup(true));
    });
}

function openTripForm(tripId = null) {
    editingTripId = tripId;
    showView('trip-form');
    const container = $('#view-trip-form');
    const isEdit = !!tripId;
    container.innerHTML = `
        <div class="mb-6">
            <button id="btn-back-to-list" class="text-sm text-slate-600 hover:text-indigo-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                Back to Trips
            </button>
        </div>
        <div class="bg-white rounded-xl border border-slate-200 p-8 max-w-2xl shadow-sm">
            <h2 class="text-2xl font-bold text-slate-800 mb-6">${isEdit ? 'Edit Trip' : 'Create New Trip'}</h2>
            <form id="trip-form" data-testid="${isEdit ? 'edit-trip-form' : 'create-trip-form'}" novalidate>
                <div class="space-y-5">
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1.5">Trip Name <span class="text-red-500">*</span></label>
                        <input type="text" id="field-name" name="name" data-testid="trip-name-input" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" required placeholder="e.g. Summer Europe Tour">
                        <div class="text-red-600 text-sm mt-1 hidden" id="err-name"></div>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1.5">Destination <span class="text-red-500">*</span></label>
                        <input type="text" id="field-destination" name="destination" data-testid="trip-destination-input" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" required placeholder="e.g. France, Italy, Spain">
                        <div class="text-red-600 text-sm mt-1 hidden" id="err-destination"></div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1.5">Start Date <span class="text-red-500">*</span></label>
                            <input type="date" id="field-start-date" name="start_date" data-testid="trip-start-date-input" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" required>
                            <div class="text-red-600 text-sm mt-1 hidden" id="err-start_date"></div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-slate-700 mb-1.5">End Date <span class="text-red-500">*</span></label>
                            <input type="date" id="field-end-date" name="end_date" data-testid="trip-end-date-input" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" required>
                            <div class="text-red-600 text-sm mt-1 hidden" id="err-end_date"></div>
                        </div>
                    </div>
                </div>
                <div class="text-sm text-slate-500 mt-2" id="form-error-general"></div>
                <div class="mt-8 flex gap-3 justify-end">
                    <button type="button" id="btn-cancel-form" class="px-5 py-2.5 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium shadow-sm transition-colors" data-testid="trip-submit-btn">${isEdit ? 'Save Changes' : 'Create Trip'}</button>
                </div>
            </form>
        </div>
    `;

    $('#btn-back-to-list', container).addEventListener('click', () => {
        editingTripId = null;
        renderTripsList();
    });
    $('#btn-cancel-form', container).addEventListener('click', () => {
        editingTripId = null;
        renderTripsList();
    });
    const tripForm = $('#trip-form', container);

    if (isEdit) {
        (async () => {
            try {
                const { data: trip } = await apiRequest(`/api/trips/${tripId}`);
                $('#field-name').value = trip.name;
                $('#field-destination').value = trip.destination;
                $('#field-start-date').value = trip.start_date;
                $('#field-end-date').value = trip.end_date;
            } catch (err) {
                showToast('Failed to load trip: ' + err.message, 'error');
                editingTripId = null;
                renderTripsList();
            }
        })();
    }

    tripForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        $$('[id^="err-"]', container).forEach(el => { el.classList.add('hidden'); el.textContent = ''; });
        $('#form-error-general', container).textContent = '';

        const name = $('#field-name', container).value.trim();
        const destination = $('#field-destination', container).value.trim();
        const start_date = $('#field-start-date', container).value;
        const end_date = $('#field-end-date', container).value;

        let hasError = false;
        if (!name) { $('#err-name', container).textContent = 'Trip name is required'; $('#err-name', container).classList.remove('hidden'); hasError = true; }
        if (!destination) { $('#err-destination', container).textContent = 'Destination is required'; $('#err-destination', container).classList.remove('hidden'); hasError = true; }
        if (!start_date) { $('#err-start_date', container).textContent = 'Start date is required'; $('#err-start_date', container).classList.remove('hidden'); hasError = true; }
        if (!end_date) { $('#err-end_date', container).textContent = 'End date is required'; $('#err-end_date', container).classList.remove('hidden'); hasError = true; }
        if (start_date && end_date && new Date(end_date) < new Date(start_date)) {
            $('#err-end_date', container).textContent = 'End date cannot be earlier than start date';
            $('#err-end_date', container).classList.remove('hidden');
            hasError = true;
        }
        if (hasError) return;

        const payload = { name, destination, start_date, end_date };
        try {
            if (isEdit) {
                await apiRequest(`/api/trips/${tripId}`, 'PUT', payload);
                showToast('Trip updated successfully', 'success');
            } else {
                const { data: newTrip } = await apiRequest('/api/trips', 'POST', payload);
                showToast('Trip created successfully', 'success');
                editingTripId = null;
                renderTripDetails(newTrip.id);
                return;
            }
            editingTripId = null;
            renderTripsList();
        } catch (err) {
            $('#form-error-general', container).textContent = err.message;
            showToast(err.message, 'error');
        }
    });
}

async function renderTripDetails(tripId) {
    currentTripId = tripId;
    showView('trip-details');
    const container = $('#view-trip-details');
    container.innerHTML = `
        <div class="mb-6">
            <button id="btn-back-to-list" class="text-sm text-slate-600 hover:text-indigo-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                Back to Trips
            </button>
        </div>
        <div id="trip-details-content">Loading...</div>
    `;

    $('#btn-back-to-list', container).addEventListener('click', () => {
        currentTripId = null;
        renderTripsList();
    });

    try {
        const { data: trip } = await apiRequest(`/api/trips/${tripId}`);
        renderTripDetailsContent(trip);
    } catch (err) {
        container.innerHTML = `<div class="p-8 bg-red-50 border border-red-200 rounded-xl text-red-700">Error: ${escapeHtml(err.message)}</div>`;
        showToast('Failed to load trip: ' + err.message, 'error');
    }
}

function renderTripDetailsContent(trip) {
    const numDays = daysBetween(trip.start_date, trip.end_date);
    const numActs = totalActivities(trip);
    const sortedDays = [...(trip.days || [])].sort((a, b) => new Date(a.date) - new Date(b.date));
    const container = $('#trip-details-content');

    container.innerHTML = `
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-8">
            <div class="h-32 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-end">
                <div class="p-6 w-full bg-gradient-to-t from-black/40 to-transparent">
                    <div class="text-white/80 text-sm font-medium uppercase tracking-wide mb-1">${escapeHtml(trip.destination)}</div>
                    <h2 class="text-3xl font-bold text-white" data-testid="trip-details-name">${escapeHtml(trip.name)}</h2>
                </div>
            </div>
            <div class="p-6 flex flex-wrap gap-6 items-center justify-between border-b border-slate-100">
                <div class="flex flex-wrap gap-6">
                    <div>
                        <div class="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Dates</div>
                        <div class="font-medium text-slate-800">${formatDate(trip.start_date)} — ${formatDate(trip.end_date)}</div>
                    </div>
                    <div>
                        <div class="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Duration</div>
                        <div class="font-medium text-slate-800">${numDays} day${numDays === 1 ? '' : 's'}</div>
                    </div>
                    <div>
                        <div class="text-xs text-slate-500 uppercase tracking-wide mb-0.5">Itinerary</div>
                        <div class="font-medium text-slate-800">${sortedDays.length} day${sortedDays.length === 1 ? '' : 's'} · ${numActs} activit${numActs === 1 ? 'y' : 'ies'}</div>
                    </div>
                </div>
                <div class="flex gap-2">
                    <button id="btn-edit-trip" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors flex items-center gap-2" data-testid="details-edit-btn">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                        Edit Trip
                    </button>
                    <button id="btn-delete-trip" class="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg font-medium transition-colors flex items-center gap-2" data-testid="details-delete-btn">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        Delete
                    </button>
                </div>
            </div>
        </div>

        <div class="mb-6 flex items-center justify-between">
            <h3 class="text-xl font-bold text-slate-800">Itinerary</h3>
            <button id="btn-add-day" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium shadow-sm transition-colors flex items-center gap-2" data-testid="add-day-btn">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Add Day
            </button>
        </div>

        <div id="days-container" class="space-y-5">
            ${sortedDays.length === 0 ? `
                <div class="bg-white rounded-xl border-2 border-dashed border-slate-200 p-12 text-center">
                    <div class="mx-auto w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-4">
                        <svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    <h4 class="text-lg font-semibold text-slate-700 mb-1">No days added</h4>
                    <p class="text-slate-500 mb-5">Start building your itinerary by adding your first day.</p>
                </div>
            ` : sortedDays.map((day, idx) => renderDayCard(day, idx + 1)).join('')}
        </div>
    `;

    $('#btn-edit-trip', container).addEventListener('click', () => openTripForm(trip.id));
    $('#btn-delete-trip', container).addEventListener('click', async () => {
        const confirm = await showConfirmModal(
            'Delete Trip',
            'Are you sure you want to delete this trip? This action cannot be undone.',
            'Delete',
            'bg-red-600 hover:bg-red-700'
        );
        if (!confirm) return;
        try {
            await apiRequest(`/api/trips/${trip.id}`, 'DELETE');
            showToast('Trip deleted successfully', 'success');
            currentTripId = null;
            renderTripsList();
        } catch (err) {
            showToast('Failed to delete trip: ' + err.message, 'error');
        }
    });

    $('#btn-add-day', container).addEventListener('click', () => openDayForm());

    $$('[data-day-action]', container).forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.dayAction;
            const dayId = btn.dataset.dayId;
            if (action === 'edit-day') openDayForm(dayId);
            else if (action === 'delete-day') confirmDeleteDay(dayId);
            else if (action === 'add-activity') openActivityForm(dayId);
        });
    });

    $$('[data-activity-action]', container).forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.activityAction;
            const dayId = btn.dataset.dayId;
            const activityId = btn.dataset.activityId;
            if (action === 'edit') openActivityForm(dayId, activityId);
            else if (action === 'delete') confirmDeleteActivity(dayId, activityId);
        });
    });
}

function renderDayCard(day, dayNumber) {
    const activities = day.activities || [];
    return `
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden fade-in" data-day-id="${day.id}" data-testid="day-card">
            <div class="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-indigo-600 text-white rounded-lg flex items-center justify-center font-bold">
                        D${dayNumber}
                    </div>
                    <div>
                        <div class="font-semibold text-slate-800 text-lg">
                            ${escapeHtml(day.title || `Day ${dayNumber}`)}
                        </div>
                        <div class="text-sm text-slate-500">${formatDate(day.date)}</div>
                    </div>
                </div>
                <div class="flex gap-1">
                    <button class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-white rounded-md transition-colors" title="Edit day" data-day-action="edit-day" data-day-id="${day.id}" data-testid="edit-day-btn">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button class="p-2 text-slate-500 hover:text-red-600 hover:bg-white rounded-md transition-colors" title="Delete day" data-day-action="delete-day" data-day-id="${day.id}" data-testid="delete-day-btn">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </div>
            <div class="p-5">
                <div class="space-y-3 mb-4">
                    ${activities.length === 0 ? `
                        <div class="text-sm text-slate-400 italic py-4 text-center bg-slate-50 rounded-lg">No activities planned for this day yet.</div>
                    ` : activities.map(act => `
                        <div class="flex items-start gap-3 p-4 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors" data-activity-id="${act.id}" data-testid="activity-card">
                            <div class="mt-0.5">
                                <div class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center flex-shrink-0">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                                </div>
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="font-medium text-slate-800" data-testid="activity-name">${escapeHtml(act.name)}</div>
                                ${act.location ? `<div class="text-sm text-slate-500 mt-0.5 flex items-center gap-1"><svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>${escapeHtml(act.location)}</div>` : ''}
                                ${act.description ? `<div class="text-sm text-slate-600 mt-1">${escapeHtml(act.description)}</div>` : ''}
                            </div>
                            <div class="flex gap-1 flex-shrink-0">
                                <button class="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-colors" title="Edit activity" data-activity-action="edit" data-day-id="${day.id}" data-activity-id="${act.id}" data-testid="edit-activity-btn">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                                </button>
                                <button class="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors" title="Delete activity" data-activity-action="delete" data-day-id="${day.id}" data-activity-id="${act.id}" data-testid="delete-activity-btn">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <button class="w-full py-2.5 border-2 border-dashed border-slate-300 rounded-lg text-slate-500 hover:text-indigo-600 hover:border-indigo-400 hover:bg-indigo-50/50 transition-colors text-sm font-medium flex items-center justify-center gap-2" data-day-action="add-activity" data-day-id="${day.id}" data-testid="add-activity-btn">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                    Add Activity
                </button>
            </div>
        </div>
    `;
}

function openDayForm(dayId = null) {
    showModalForm({
        title: dayId ? 'Edit Day' : 'Add Day',
        submitText: dayId ? 'Save Changes' : 'Add Day',
        fields: [
            { id: 'date', label: 'Date', type: 'date', required: true },
            { id: 'title', label: 'Title (optional)', type: 'text', placeholder: 'e.g. Arrival in Paris' }
        ],
        onLoad: async () => {
            if (dayId) {
                try {
                    const { data: day } = await apiRequest(`/api/trips/${currentTripId}/days/${dayId}`);
                    $('#modal-field-date').value = day.date;
                    $('#modal-field-title').value = day.title || '';
                } catch (err) {
                    showToast('Failed to load day: ' + err.message, 'error');
                }
            }
        },
        onSubmit: async (values) => {
            if (!values.date) throw new Error('Date is required');
            const payload = { date: values.date };
            if (values.title !== undefined) payload.title = values.title || null;
            if (dayId) {
                await apiRequest(`/api/trips/${currentTripId}/days/${dayId}`, 'PUT', payload);
                showToast('Day updated successfully', 'success');
            } else {
                await apiRequest(`/api/trips/${currentTripId}/days`, 'POST', payload);
                showToast('Day added successfully', 'success');
            }
            renderTripDetails(currentTripId);
        }
    });
}

async function confirmDeleteDay(dayId) {
    const confirm = await showConfirmModal(
        'Delete Day',
        'Are you sure you want to delete this day and all its activities? This cannot be undone.',
        'Delete Day',
        'bg-red-600 hover:bg-red-700'
    );
    if (!confirm) return;
    try {
        await apiRequest(`/api/trips/${currentTripId}/days/${dayId}`, 'DELETE');
        showToast('Day deleted successfully', 'success');
        renderTripDetails(currentTripId);
    } catch (err) {
        showToast('Failed to delete day: ' + err.message, 'error');
    }
}

function openActivityForm(dayId, activityId = null) {
    showModalForm({
        title: activityId ? 'Edit Activity' : 'Add Activity',
        submitText: activityId ? 'Save Changes' : 'Add Activity',
        fields: [
            { id: 'name', label: 'Activity Name', type: 'text', required: true, placeholder: 'e.g. Visit Eiffel Tower' },
            { id: 'location', label: 'Location (optional)', type: 'text', placeholder: 'e.g. Champ de Mars, Paris' },
            { id: 'description', label: 'Description (optional)', type: 'textarea', placeholder: 'Add any notes or details about this activity...' }
        ],
        onLoad: async () => {
            if (activityId) {
                try {
                    const { data: act } = await apiRequest(`/api/trips/${currentTripId}/days/${dayId}/activities/${activityId}`);
                    $('#modal-field-name').value = act.name;
                    $('#modal-field-location').value = act.location || '';
                    $('#modal-field-description').value = act.description || '';
                } catch (err) {
                    showToast('Failed to load activity: ' + err.message, 'error');
                }
            }
        },
        onSubmit: async (values) => {
            if (!values.name || !values.name.trim()) throw new Error('Activity name is required');
            const payload = { name: values.name.trim() };
            if (values.location !== undefined) payload.location = values.location || null;
            if (values.description !== undefined) payload.description = values.description || null;
            if (activityId) {
                await apiRequest(`/api/trips/${currentTripId}/days/${dayId}/activities/${activityId}`, 'PUT', payload);
                showToast('Activity updated successfully', 'success');
            } else {
                await apiRequest(`/api/trips/${currentTripId}/days/${dayId}/activities`, 'POST', payload);
                showToast('Activity added successfully', 'success');
            }
            renderTripDetails(currentTripId);
        }
    });
}

async function confirmDeleteActivity(dayId, activityId) {
    const confirm = await showConfirmModal(
        'Delete Activity',
        'Are you sure you want to delete this activity? This cannot be undone.',
        'Delete',
        'bg-red-600 hover:bg-red-700'
    );
    if (!confirm) return;
    try {
        await apiRequest(`/api/trips/${currentTripId}/days/${dayId}/activities/${activityId}`, 'DELETE');
        showToast('Activity deleted successfully', 'success');
        renderTripDetails(currentTripId);
    } catch (err) {
        showToast('Failed to delete activity: ' + err.message, 'error');
    }
}

function showModalForm({ title, submitText, fields, onLoad, onSubmit }) {
    const root = $('#modal-root');
    root.innerHTML = `
        <div id="form-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 fade-in">
            <div class="bg-white rounded-xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
                <div class="p-6 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white z-10">
                    <h3 class="text-lg font-semibold text-slate-800">${escapeHtml(title)}</h3>
                    <button id="modal-close" class="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-md transition-colors">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
                <form id="modal-form" class="p-6 space-y-4" novalidate>
                    ${fields.map(f => {
                        const inputEl = f.type === 'textarea'
                            ? `<textarea id="modal-field-${f.id}" name="${f.id}" rows="3" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" ${f.required ? 'required' : ''} ${f.placeholder ? `placeholder="${escapeHtml(f.placeholder)}"` : ''}></textarea>`
                            : `<input type="${f.type}" id="modal-field-${f.id}" name="${f.id}" class="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition" ${f.required ? 'required' : ''} ${f.placeholder ? `placeholder="${escapeHtml(f.placeholder)}"` : ''}>`;
                        return `
                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-1.5">
                                    ${escapeHtml(f.label)} ${f.required ? '<span class="text-red-500">*</span>' : ''}
                                </label>
                                ${inputEl}
                                <div class="text-red-600 text-sm mt-1 hidden" id="modal-err-${f.id}"></div>
                            </div>
                        `;
                    }).join('')}
                    <div class="text-sm text-red-600 hidden" id="modal-form-error"></div>
                </form>
                <div class="p-6 pt-0 flex justify-end gap-3">
                    <button type="button" id="modal-cancel" class="px-5 py-2.5 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors">Cancel</button>
                    <button type="submit" form="modal-form" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium shadow-sm transition-colors">${escapeHtml(submitText)}</button>
                </div>
            </div>
        </div>
    `;

    const cleanup = () => { $('#form-modal').remove(); };

    $('#modal-close').addEventListener('click', cleanup);
    $('#modal-cancel').addEventListener('click', cleanup);

    if (onLoad) {
        Promise.resolve(onLoad()).catch(err => showToast(err.message, 'error'));
    }

    $('#modal-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        fields.forEach(f => {
            const errEl = $(`#modal-err-${f.id}`);
            if (errEl) { errEl.classList.add('hidden'); errEl.textContent = ''; }
        });
        $('#modal-form-error').classList.add('hidden');
        $('#modal-form-error').textContent = '';

        const values = {};
        let hasError = false;
        fields.forEach(f => {
            const el = $(`#modal-field-${f.id}`);
            values[f.id] = el ? el.value : '';
            if (f.required && (!values[f.id] || (typeof values[f.id] === 'string' && !values[f.id].trim()))) {
                const errEl = $(`#modal-err-${f.id}`);
                if (errEl) { errEl.textContent = `${f.label.replace(' (optional)', '')} is required`; errEl.classList.remove('hidden'); }
                hasError = true;
            }
        });
        if (hasError) return;

        try {
            await onSubmit(values);
            cleanup();
        } catch (err) {
            $('#modal-form-error').textContent = err.message;
            $('#modal-form-error').classList.remove('hidden');
            showToast(err.message, 'error');
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    $('#btn-reset-data').addEventListener('click', async () => {
        const confirm = await showConfirmModal(
            'Reset All Data',
            'This will delete all trips and restore the default sample data. Are you sure?',
            'Reset Data',
            'bg-amber-600 hover:bg-amber-700'
        );
        if (!confirm) return;
        try {
            await apiRequest('/api/system/reset', 'POST');
            showToast('Data reset to seed state', 'success');
            currentTripId = null;
            editingTripId = null;
            renderTripsList();
        } catch (err) {
            showToast('Failed to reset data: ' + err.message, 'error');
        }
    });

    $('#brand-link').addEventListener('click', () => {
        currentTripId = null;
        editingTripId = null;
        renderTripsList();
    });

    renderTripsList();
});
