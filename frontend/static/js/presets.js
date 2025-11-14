/**
 * Preset Frequencies Management
 */

import { api } from './api.js';

let allPresets = [];
let currentModeFilter = '';

// DOM Elements
const elements = {
    presetList: document.getElementById('preset-list'),
    presetModeFilter: document.getElementById('preset-mode-filter'),
    managePresetsBtn: document.getElementById('manage-presets-btn'),

    // Preset Manager Modal
    presetManagerModal: document.getElementById('preset-manager-modal'),
    closePresetManagerBtn: document.getElementById('close-preset-manager-btn'),
    customPresetsList: document.getElementById('custom-presets-list'),
    addPresetBtn: document.getElementById('add-preset-btn'),

    // Add Preset Modal
    addPresetModal: document.getElementById('add-preset-modal'),
    closeAddPresetBtn: document.getElementById('close-add-preset-btn'),
    presetNameInput: document.getElementById('preset-name-input'),
    presetModeInput: document.getElementById('preset-mode-input'),
    presetRigFreqInput: document.getElementById('preset-rig-freq-input'),
    presetCarrierFreqInput: document.getElementById('preset-carrier-freq-input'),
    presetBandInput: document.getElementById('preset-band-input'),
    savePresetBtn: document.getElementById('save-preset-btn'),
    cancelAddPresetBtn: document.getElementById('cancel-add-preset-btn')
};

/**
 * Initialize preset functionality
 */
export async function initPresets() {
    console.log('Initializing presets...');

    setupEventListeners();
    await loadPresets();
    await populateModeFilters();
}

/**
 * Setup event listeners for preset UI
 */
function setupEventListeners() {
    // Mode filter
    elements.presetModeFilter.addEventListener('change', handleModeFilterChange);

    // Manage presets button
    elements.managePresetsBtn.addEventListener('click', openPresetManager);

    // Modal controls
    elements.closePresetManagerBtn.addEventListener('click', closePresetManager);
    elements.addPresetBtn.addEventListener('click', openAddPresetModal);
    elements.closeAddPresetBtn.addEventListener('click', closeAddPresetModal);
    elements.cancelAddPresetBtn.addEventListener('click', closeAddPresetModal);
    elements.savePresetBtn.addEventListener('click', handleSavePreset);

    // Close modal when clicking outside
    elements.presetManagerModal.addEventListener('click', (e) => {
        if (e.target === elements.presetManagerModal) closePresetManager();
    });
    elements.addPresetModal.addEventListener('click', (e) => {
        if (e.target === elements.addPresetModal) closeAddPresetModal();
    });
}

/**
 * Load all presets from API
 */
export async function loadPresets() {
    try {
        allPresets = await api.getPresets();
        console.log('Loaded presets:', allPresets);
        renderPresetList();
    } catch (error) {
        console.error('Failed to load presets:', error);
        showError('Failed to load presets');
    }
}

/**
 * Populate mode filter dropdown with unique modes from presets
 */
async function populateModeFilters() {
    try {
        const modes = [...new Set(allPresets.map(p => p.modem))].sort();

        // Update filter dropdown
        elements.presetModeFilter.innerHTML = '<option value="">All Modes</option>';
        modes.forEach(mode => {
            const option = document.createElement('option');
            option.value = mode;
            option.textContent = mode;
            elements.presetModeFilter.appendChild(option);
        });

        // Update add preset modal dropdown
        elements.presetModeInput.innerHTML = '<option value="">Select a mode...</option>';
        modes.forEach(mode => {
            const option = document.createElement('option');
            option.value = mode;
            option.textContent = mode;
            elements.presetModeInput.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to populate mode filters:', error);
    }
}

/**
 * Handle mode filter change
 */
function handleModeFilterChange(e) {
    currentModeFilter = e.target.value;
    renderPresetList();
}

/**
 * Render preset list in sidebar
 */
function renderPresetList() {
    const filteredPresets = currentModeFilter
        ? allPresets.filter(p => p.modem === currentModeFilter)
        : allPresets;

    if (filteredPresets.length === 0) {
        elements.presetList.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.875rem; text-align: center;">No presets available for this filter.</p>';
        return;
    }

    elements.presetList.innerHTML = '';

    filteredPresets.forEach(preset => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-secondary';
        btn.style.cssText = 'width: 100%; text-align: left; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.25rem;';

        const nameRow = document.createElement('div');
        nameRow.style.cssText = 'display: flex; justify-content: space-between; align-items: center;';

        const name = document.createElement('strong');
        name.textContent = preset.name;
        name.style.fontSize = '0.875rem';

        const badge = document.createElement('span');
        badge.textContent = preset.modem;
        badge.style.cssText = 'font-size: 0.7rem; background: var(--accent); color: white; padding: 0.125rem 0.5rem; border-radius: 10px;';

        nameRow.appendChild(name);
        nameRow.appendChild(badge);

        const freq = document.createElement('div');
        freq.style.cssText = 'font-size: 0.75rem; color: var(--text-secondary);';
        freq.textContent = `${formatFrequency(preset.rig_frequency)} • Carrier: ${preset.carrier_frequency} Hz`;

        btn.appendChild(nameRow);
        btn.appendChild(freq);

        btn.addEventListener('click', () => applyPreset(preset.id));

        elements.presetList.appendChild(btn);
    });
}

/**
 * Format frequency in Hz to MHz
 */
function formatFrequency(freqHz) {
    const freqMhz = freqHz / 1000000;
    return freqMhz.toFixed(4) + ' MHz';
}

/**
 * Apply a preset
 */
async function applyPreset(presetId) {
    try {
        const response = await api.applyPreset(presetId);
        const preset = response.data;

        console.log('Applying preset:', preset);

        // Set modem mode
        await api.setModem(preset.modem);

        // Set rig frequency
        await api.setRigFrequency(preset.rig_frequency);

        // Set carrier frequency
        await api.setCarrier(preset.carrier_frequency);

        // Update UI elements directly
        updateUIAfterPresetApplied(preset);

        showSuccess(`Applied preset: ${preset.name}`);
    } catch (error) {
        console.error('Failed to apply preset:', error);
        showError('Failed to apply preset: ' + error.message);
    }
}

/**
 * Update UI elements after preset is applied
 */
function updateUIAfterPresetApplied(preset) {
    // Update modem display
    const modemDisplay = document.getElementById('current-modem');
    if (modemDisplay) {
        modemDisplay.textContent = preset.modem;
    }

    // Update carrier frequency display and slider
    const carrierValue = document.getElementById('carrier-value');
    const carrierFreq = document.getElementById('carrier-freq');
    const carrierInput = document.getElementById('carrier-input');
    if (carrierValue) {
        carrierValue.textContent = preset.carrier_frequency;
    }
    if (carrierFreq) {
        carrierFreq.value = preset.carrier_frequency;
    }
    if (carrierInput) {
        carrierInput.value = preset.carrier_frequency;
    }

    // Update rig frequency display
    const rigFrequency = document.getElementById('rig-frequency');
    const rigFreqDisplay = document.getElementById('rig-freq-display');

    if (rigFrequency) {
        const freqText = preset.rig_frequency.toLocaleString() + ' Hz';
        rigFrequency.textContent = freqText;
    }

    if (rigFreqDisplay) {
        const mhz = (preset.rig_frequency / 1000000).toFixed(4);
        rigFreqDisplay.textContent = `${mhz} MHz`;
    }
}

/**
 * Open preset manager modal
 */
async function openPresetManager() {
    elements.presetManagerModal.style.display = 'flex';
    await loadCustomPresets();
}

/**
 * Close preset manager modal
 */
function closePresetManager() {
    elements.presetManagerModal.style.display = 'none';
}

/**
 * Load and render custom presets in manager
 */
async function loadCustomPresets() {
    try {
        const customPresets = await api.getCustomPresets();

        if (customPresets.length === 0) {
            elements.customPresetsList.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.875rem; text-align: center; padding: 2rem;">No custom presets yet. Click "Add Preset" to create one.</p>';
            return;
        }

        elements.customPresetsList.innerHTML = '';

        customPresets.forEach(preset => {
            const item = document.createElement('div');
            item.style.cssText = 'background: var(--bg-secondary); border: 1px solid var(--border-medium); border-radius: var(--radius-md); padding: 1rem; display: flex; justify-content: space-between; align-items: center;';

            const info = document.createElement('div');
            info.innerHTML = `
                <strong style="font-size: 0.9375rem; display: block; margin-bottom: 0.25rem;">${preset.name}</strong>
                <div style="font-size: 0.8125rem; color: var(--text-secondary);">
                    <span style="background: var(--accent); color: white; padding: 0.125rem 0.5rem; border-radius: 10px; font-size: 0.7rem; margin-right: 0.5rem;">${preset.modem}</span>
                    ${formatFrequency(preset.rig_frequency)} • Carrier: ${preset.carrier_frequency} Hz
                    ${preset.band ? ` • ${preset.band}` : ''}
                </div>
            `;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'btn btn-secondary';
            deleteBtn.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.8125rem;';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.title = 'Delete preset';
            deleteBtn.addEventListener('click', () => handleDeletePreset(preset.id, preset.name));

            item.appendChild(info);
            item.appendChild(deleteBtn);
            elements.customPresetsList.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load custom presets:', error);
        showError('Failed to load custom presets');
    }
}

/**
 * Open add preset modal
 */
function openAddPresetModal() {
    // Reset form
    elements.presetNameInput.value = '';
    elements.presetModeInput.value = '';
    elements.presetRigFreqInput.value = '';
    elements.presetCarrierFreqInput.value = '1500';
    elements.presetBandInput.value = '';

    elements.addPresetModal.style.display = 'flex';
}

/**
 * Close add preset modal
 */
function closeAddPresetModal() {
    elements.addPresetModal.style.display = 'none';
}

/**
 * Handle save preset
 */
async function handleSavePreset() {
    const name = elements.presetNameInput.value.trim();
    const modem = elements.presetModeInput.value;
    const rigFreq = parseFloat(elements.presetRigFreqInput.value);
    const carrierFreq = parseInt(elements.presetCarrierFreqInput.value);
    const band = elements.presetBandInput.value.trim();

    // Validation
    if (!name) {
        showError('Please enter a preset name');
        return;
    }

    if (!modem) {
        showError('Please select a mode');
        return;
    }

    if (!rigFreq || rigFreq <= 0) {
        showError('Please enter a valid rig frequency');
        return;
    }

    if (!carrierFreq || carrierFreq < 500 || carrierFreq > 3000) {
        showError('Carrier frequency must be between 500 and 3000 Hz');
        return;
    }

    try {
        const presetData = {
            name,
            modem,
            rig_frequency: rigFreq,
            carrier_frequency: carrierFreq,
            band: band || null
        };

        await api.createPreset(presetData);
        showSuccess('Preset saved successfully!');

        closeAddPresetModal();
        await loadPresets();
        await loadCustomPresets();
        await populateModeFilters();
    } catch (error) {
        console.error('Failed to save preset:', error);
        showError('Failed to save preset: ' + error.message);
    }
}

/**
 * Handle delete preset
 */
async function handleDeletePreset(presetId, presetName) {
    if (!confirm(`Are you sure you want to delete "${presetName}"?`)) {
        return;
    }

    try {
        await api.deletePreset(presetId);
        showSuccess('Preset deleted successfully!');

        await loadPresets();
        await loadCustomPresets();
        await populateModeFilters();
    } catch (error) {
        console.error('Failed to delete preset:', error);
        showError('Failed to delete preset: ' + error.message);
    }
}

/**
 * Show success message (using toast if available)
 */
function showSuccess(message) {
    console.log('SUCCESS:', message);
    if (window.showToast) {
        window.showToast(message, 'success');
    } else {
        alert(message);
    }
}

/**
 * Show error message (using toast if available)
 */
function showError(message) {
    console.error('ERROR:', message);
    if (window.showToast) {
        window.showToast(message, 'error');
    } else {
        alert(message);
    }
}
