/**
 * Main application logic for FLDIGI Web Wrapper
 */

import { wsClient } from './websocket.js';
import { api } from './api.js';
import { initPresets } from './presets.js';

const MODE_SPEEDS = {
    'BPSK31': 65,
    'QPSK31': 130,
    'BPSK63': 100,
    'QPSK63': 160,
    'BPSK125': 200,
    'QPSK125': 320
};

const state = {
    connected: false,
    modem: '',
    carrier: 1500,
    bandwidth: 31,
    txStatus: 'RX',
    signalQuality: 0,
    liveTxMode: true,
    liveTxActive: false,
    liveTxBuffer: '',
    lastTxText: '',
    liveTxStartTime: 0,
    liveTxStarting: false,
    liveTxDebounceTimer: null,
    liveTxDebounceDelay: 30,
    liveTxInFlight: false,
    showTxProgress: false,
    txOverlay: {
        charQueue: [],
        transmittedCount: 0,
        animationFrame: null,
        startTime: 0
    }
};

const elements = {
    // Status
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    connectBtn: document.getElementById('connect-btn'),

    // Modem
    currentModem: document.getElementById('current-modem'),
    modemSelect: document.getElementById('modem-select'),
    setModemBtn: document.getElementById('set-modem-btn'),
    carrierFreq: document.getElementById('carrier-freq'),
    carrierValue: document.getElementById('carrier-value'),
    txidToggle: document.getElementById('txid-toggle'),

    // TX/RX
    trxStatus: document.getElementById('trx-status'),
    rxBtn: document.getElementById('rx-btn'),
    tuneBtn: document.getElementById('tune-btn'),
    abortBtn: document.getElementById('abort-btn'),

    // Text
    rxText: document.getElementById('rx-text'),
    txText: document.getElementById('tx-text'),
    txOverlay: null,
    txProgressToggle: document.getElementById('tx-progress-toggle'),
    clearRxBtn: document.getElementById('clear-rx-btn'),
    clearTxBtn: document.getElementById('clear-tx-btn'),
    sendTxBtn: document.getElementById('send-tx-btn'),

    // Rig
    rigName: document.getElementById('rig-name'),
    rigFrequency: document.getElementById('rig-frequency'),
    rigFreqDisplay: document.getElementById('rig-freq-display'),
    rigMode: document.getElementById('rig-mode')
};

/**
 * Initialize application
 */
async function init() {
    console.log('Initializing FLDIGI Web Wrapper...');

    setupEventListeners();

    setupWebSocketHandlers();

    initTxOverlay();

    loadTxProgressSetting();

    await initPresets();

    wsClient.connect();

    await checkConnectionStatus();

    console.log('Application initialized');
}

function loadTxProgressSetting() {
    const saved = localStorage.getItem('showTxProgress');
    state.showTxProgress = saved === 'true';
    elements.txProgressToggle.checked = state.showTxProgress;
}

function initTxOverlay() {
    const txContainer = elements.txText.parentElement;
    const overlay = document.createElement('div');
    overlay.id = 'tx-overlay';
    overlay.style.cssText = `
        position: absolute;
        top: calc(1.125rem + 1px);
        left: calc(1.125rem + 1px);
        right: calc(1.125rem + 1px);
        bottom: calc(1.125rem + 1px);
        pointer-events: none;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        padding: 0.875rem;
        overflow: hidden;
        color: transparent;
        box-sizing: border-box;
        letter-spacing: 0.02em;
    `;
    txContainer.style.position = 'relative';
    txContainer.appendChild(overlay);
    elements.txOverlay = overlay;
}

function getTransmitSpeed() {
    const modemUpper = state.modem.toUpperCase();
    for (const [mode, wpm] of Object.entries(MODE_SPEEDS)) {
        if (modemUpper.includes(mode)) {
            return (wpm * 5) / 60;
        }
    }
    return null;
}

function isModeSupported() {
    const modemUpper = state.modem.toUpperCase();
    for (const mode of Object.keys(MODE_SPEEDS)) {
        if (modemUpper.includes(mode)) {
            return true;
        }
    }
    return false;
}

function startTxOverlay() {
    if (!state.showTxProgress || !isModeSupported()) {
        return;
    }

    state.txOverlay.charQueue = [];
    state.txOverlay.transmittedCount = 0;
    state.txOverlay.startTime = Date.now();

    elements.txText.classList.add('tx-transmitting');

    if (state.txOverlay.animationFrame) {
        cancelAnimationFrame(state.txOverlay.animationFrame);
    }

    updateTxOverlay();
}

function updateTxOverlay() {
    if (!state.liveTxActive) {
        elements.txOverlay.innerHTML = '';
        return;
    }

    const charsPerSec = getTransmitSpeed();
    if (charsPerSec === null) {
        stopTxOverlay();
        return;
    }

    const currentTime = Date.now();
    const elapsed = (currentTime - state.txOverlay.startTime) / 1000;
    const expectedChars = Math.floor(elapsed * charsPerSec);
    const currentText = elements.txText.value;
    const transmittedChars = Math.min(expectedChars, currentText.length);

    if (transmittedChars > 0) {
        const transmitted = currentText.substring(0, transmittedChars);
        const untransmitted = currentText.substring(transmittedChars);

        elements.txOverlay.innerHTML =
            `<span style="color: rgb(239, 68, 68);">${escapeHtml(transmitted)}</span>` +
            `<span style="color: #10b981;">${escapeHtml(untransmitted)}</span>`;
    } else {
        elements.txOverlay.innerHTML = `<span style="color: #10b981;">${escapeHtml(currentText)}</span>`;
    }

    state.txOverlay.transmittedCount = transmittedChars;
    state.txOverlay.animationFrame = requestAnimationFrame(updateTxOverlay);
}

function stopTxOverlay() {
    if (state.txOverlay.animationFrame) {
        cancelAnimationFrame(state.txOverlay.animationFrame);
        state.txOverlay.animationFrame = null;
    }
    elements.txOverlay.innerHTML = '';
    elements.txText.classList.remove('tx-transmitting');
    state.txOverlay.charQueue = [];
    state.txOverlay.transmittedCount = 0;
    state.txOverlay.startTime = 0;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    elements.connectBtn.addEventListener('click', handleConnectClick);

    elements.setModemBtn.addEventListener('click', handleSetModem);
    elements.carrierFreq.addEventListener('input', handleCarrierChange);
    elements.carrierFreq.addEventListener('change', handleCarrierSet);
    elements.txidToggle.addEventListener('change', handleTxidToggle);

    // TX/RX control (with null checks)
    if (elements.rxBtn) elements.rxBtn.addEventListener('click', () => handleTxRxControl('rx'));
    if (elements.tuneBtn) elements.tuneBtn.addEventListener('click', () => handleTxRxControl('tune'));
    if (elements.abortBtn) elements.abortBtn.addEventListener('click', () => handleTxRxControl('abort'));

    elements.clearRxBtn.addEventListener('click', handleClearRx);
    elements.clearTxBtn.addEventListener('click', handleClearTx);
    elements.sendTxBtn.addEventListener('click', handleSendTx);

    // Live TX editing - monitor textarea changes
    elements.txText.addEventListener('input', handleLiveTxInput);

    elements.txProgressToggle.addEventListener('change', handleTxProgressToggle);

    document.addEventListener('keydown', handleKeyboardShortcuts);
}

/**
 * Setup WebSocket message handlers
 */
function setupWebSocketHandlers() {
    wsClient.on('status_update', (data) => {
        console.log('Status update:', data);

        if (data.modem) {
            updateModem(data.modem);
        }
        if (data.carrier !== undefined) {
            updateCarrier(data.carrier);
        }
        if (data.tx_status) {
            updateTxRxStatus(data.tx_status);
        }
        // Update rig information if present
        if (data.rig_frequency !== undefined || data.rig_mode !== undefined || data.rig_name !== undefined) {
            const rigInfo = {
                frequency: data.rig_frequency,
                mode: data.rig_mode,
                name: data.rig_name
            };
            updateRigInfo(rigInfo);
        }
    });

    wsClient.on('connection_status', (data) => {
        console.log('Connection status:', data);
        updateConnectionStatus(data.connected, data);
    });

    wsClient.on('text_update', (data) => {
        if (data.text_type === 'rx') {
            appendRxText(data.text, 'rx');
        } else if (data.text_type === 'tx') {
            appendRxText(data.text, 'tx');
        }
    });

    wsClient.on('error', (data) => {
        console.error('WebSocket error:', data);
        showNotification(data.error, 'error');
    });
}

/**
 * Check FLDIGI connection status
 */
async function checkConnectionStatus() {
    try {
        const status = await api.getConnectionStatus();
        updateConnectionStatus(status.connected, status);
    } catch (error) {
        console.error('Failed to check connection status:', error);
    }
}

/**
 * Handle connect button click
 */
async function handleConnectClick() {
    if (state.connected) {
        try {
            await api.disconnect();
            updateConnectionStatus(false);
            showNotification('Disconnected from FLDIGI', 'info');
        } catch (error) {
            showNotification('Failed to disconnect: ' + error.message, 'error');
        }
    } else {
        try {
            const result = await api.connect();
            if (result.success) {
                await checkConnectionStatus();
                showNotification('Connected to FLDIGI', 'success');
            } else {
                showNotification('Failed to connect: ' + result.message, 'error');
            }
        } catch (error) {
            showNotification('Failed to connect: ' + error.message, 'error');
        }
    }
}

/**
 * Update connection status UI
 */
function updateConnectionStatus(connected, details = {}) {
    state.connected = connected;

    if (connected) {
        elements.statusIndicator.classList.add('connected');
        elements.statusText.textContent = 'Connected';
        elements.connectBtn.innerHTML = '<i class="fas fa-plug-circle-xmark"></i><span>Disconnect</span>';
        // Change to danger button style when connected (to disconnect)
        elements.connectBtn.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        elements.connectBtn.style.boxShadow = '0 4px 12px rgba(239, 68, 68, 0.25)';

        loadInitialData();
    } else {
        elements.statusIndicator.classList.remove('connected');
        elements.statusText.textContent = 'Disconnected';
        elements.connectBtn.innerHTML = '<i class="fas fa-plug"></i><span>Connect</span>';
        // Reset to primary button style when disconnected (to connect)
        elements.connectBtn.style.background = 'linear-gradient(135deg, var(--accent), var(--accent-hover))';
        elements.connectBtn.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.25)';
    }
}

/**
 * Load initial data from FLDIGI
 */
async function loadInitialData() {
    try {
        const modemInfo = await api.getModemInfo();
        updateModem(modemInfo.name);
        updateCarrier(modemInfo.carrier);

        const txrxStatus = await api.getTxRxStatus();
        updateTxRxStatus(txrxStatus.status);

        const rigInfo = await api.getRigInfo();
        updateRigInfo(rigInfo);

        const txidData = await api.getTxid();
        elements.txidToggle.checked = txidData.txid || false;

    } catch (error) {
        console.error('Failed to load initial data:', error);
    }
}

/**
 * Handle modem selection
 */
async function handleSetModem() {
    const modemName = elements.modemSelect.value;

    console.log('Setting modem to:', modemName);

    if (!modemName || modemName.trim() === '') {
        showNotification('Please select a modem', 'warning');
        return;
    }

    try {
        const result = await api.setModem(modemName);
        console.log('Modem set result:', result);
        updateModem(modemName);
        showNotification(`Modem set to ${modemName}`, 'success');
    } catch (error) {
        console.error('Failed to set modem:', error);
        showNotification('Failed to set modem: ' + error.message, 'error');
    }
}

/**
 * Handle carrier frequency slider change
 */
function handleCarrierChange(event) {
    const frequency = parseInt(event.target.value);
    elements.carrierValue.textContent = frequency;
}

function handleTxProgressToggle(event) {
    state.showTxProgress = event.target.checked;
    localStorage.setItem('showTxProgress', state.showTxProgress);
    console.log('[TX Progress] Toggled:', state.showTxProgress);

    if (!state.showTxProgress && state.txOverlay.animationFrame) {
        stopTxOverlay();
    }
}

/**
 * Handle carrier frequency set (on release)
 */
async function handleCarrierSet(event) {
    const frequency = parseInt(event.target.value);

    try {
        await api.setCarrier(frequency);
        updateCarrier(frequency);
        showNotification(`Carrier set to ${frequency} Hz`, 'success');
    } catch (error) {
        showNotification('Failed to set carrier: ' + error.message, 'error');
    }
}

/**
 * Handle TXID toggle
 */
async function handleTxidToggle(event) {
    const enabled = event.target.checked;

    try {
        await api.setTxid(enabled);
        showNotification(`TXID ${enabled ? 'enabled' : 'disabled'}`, 'success');
    } catch (error) {
        showNotification('Failed to set TXID: ' + error.message, 'error');
        // Revert toggle on error
        event.target.checked = !enabled;
    }
}

/**
 * Handle TX/RX control buttons
 */
async function handleTxRxControl(action) {
    try {
        let result;
        switch (action) {
            case 'rx':
                result = await api.startRx();
                break;
            case 'tx':
                result = await api.startTx();
                break;
            case 'tune':
                result = await api.startTune();
                break;
            case 'abort':
                result = await api.abort();
                break;
        }

        if (result.success) {
            showNotification(result.message, 'success');
        }
    } catch (error) {
        showNotification('Failed: ' + error.message, 'error');
    }
}

async function handleLiveTxInput(event) {
    if (!state.liveTxMode || !state.connected || !state.liveTxActive || state.liveTxStarting) {
        return;
    }

    if (state.liveTxDebounceTimer) {
        clearTimeout(state.liveTxDebounceTimer);
    }

    state.liveTxDebounceTimer = setTimeout(async () => {
        if (state.liveTxInFlight) {
            return;
        }

        const currentText = elements.txText.value;
        const sentLength = state.liveTxBuffer.length;
        const transmittedCount = state.txOverlay.transmittedCount;

        if (currentText.length > sentLength) {
            if (currentText.startsWith(state.liveTxBuffer)) {
                const newChars = currentText.substring(sentLength);
                const previousBuffer = state.liveTxBuffer;

                state.liveTxBuffer = currentText;
                state.liveTxInFlight = true;

                try {
                    await api.addTxCharsLive(newChars, false);
                    console.log('[TX LIVE] Added chars:', JSON.stringify(newChars));
                } catch (error) {
                    state.liveTxBuffer = previousBuffer;
                    elements.txText.value = previousBuffer;
                    console.error('[TX LIVE] Error adding chars:', error);
                    showNotification('Failed to send characters', 'error');
                } finally {
                    state.liveTxInFlight = false;
                }
            } else {
                console.warn('[TX LIVE] Cannot edit middle of text, reverting');
                elements.txText.value = state.liveTxBuffer;
                const cursorPos = elements.txText.selectionStart;
                if (cursorPos < transmittedCount) {
                    showNotification('⚠️ Cannot insert into transmitted text (shown in red). Type at the end only.', 'warning');
                } else {
                    showNotification('⚠️ Cannot edit queued text. Place cursor at end to continue typing.', 'warning');
                }
                state.lastTxText = state.liveTxBuffer;
                setTimeout(() => {
                    elements.txText.selectionStart = elements.txText.selectionEnd = state.liveTxBuffer.length;
                }, 10);
                return;
            }
        } else if (currentText.length < sentLength) {
            const numDeleted = sentLength - currentText.length;
            const expectedAfterDelete = state.liveTxBuffer.substring(0, sentLength - numDeleted);

            if (currentText === expectedAfterDelete) {
                if (sentLength - numDeleted < transmittedCount) {
                    console.warn('[TX LIVE] Cannot delete transmitted text, reverting');
                    elements.txText.value = state.liveTxBuffer;
                    showNotification('⚠️ Cannot delete transmitted text (shown in red). Wait for transmission to complete or press End TX.', 'warning');
                    state.lastTxText = state.liveTxBuffer;
                    setTimeout(() => {
                        elements.txText.selectionStart = elements.txText.selectionEnd = state.liveTxBuffer.length;
                    }, 10);
                    return;
                }

                const previousBuffer = state.liveTxBuffer;

                state.liveTxBuffer = currentText;
                state.liveTxInFlight = true;

                console.log('[TX LIVE] Backspacing', numDeleted, 'characters from end');
                try {
                    await api.sendBackspaceLive(numDeleted);
                    console.log('[TX LIVE] Sent', numDeleted, 'backspaces');
                } catch (error) {
                    state.liveTxBuffer = previousBuffer;
                    elements.txText.value = previousBuffer;
                    console.error('[TX LIVE] Error sending backspace:', error);
                    showNotification('Failed to send backspace', 'error');
                } finally {
                    state.liveTxInFlight = false;
                }
            } else {
                console.warn('[TX LIVE] Cannot edit middle of text, reverting');
                elements.txText.value = state.liveTxBuffer;
                const cursorPos = elements.txText.selectionStart;
                if (cursorPos < transmittedCount) {
                    showNotification('⚠️ Cannot delete from transmitted text (shown in red). Backspace from end only.', 'warning');
                } else {
                    showNotification('⚠️ Cannot delete from middle of queued text. Backspace from end only.', 'warning');
                }
                state.lastTxText = state.liveTxBuffer;
                setTimeout(() => {
                    elements.txText.selectionStart = elements.txText.selectionEnd = state.liveTxBuffer.length;
                }, 10);
                return;
            }
        }

        state.lastTxText = elements.txText.value;
    }, state.liveTxDebounceDelay);
}

/**
 * Handle send TX text (behavior depends on mode and current TX state)
 */
async function handleSendTx() {
    const text = elements.txText.value;

    try {
        if (state.liveTxMode) {
            // LIVE MODE: Send button toggles TX on/off
            if (!state.liveTxActive) {
                // NOT transmitting → START TX
                if (!text.trim()) {
                    showNotification('Please enter text to transmit', 'warning');
                    return;
                }

                console.log('[TX LIVE] Starting transmission with buffer');

                state.liveTxActive = true;
                state.liveTxStarting = true;
                state.liveTxStartTime = Date.now();

                console.log('[TX LIVE] Calling atomic startLiveTx endpoint with', text.length, 'chars');
                await api.startLiveTx(text);
                console.log('[TX LIVE] Text added to buffer and TX started atomically');

                state.liveTxBuffer = text;
                state.lastTxText = elements.txText.value;
                state.liveTxStarting = false;
                console.log('[TX LIVE] Startup complete, sent:', text.length, 'chars, current textarea:', elements.txText.value.length, 'chars');

                startTxOverlay();

                elements.sendTxBtn.innerHTML = '<i class="fas fa-stop"></i> End TX';
                elements.sendTxBtn.classList.add('btn-danger');
                elements.sendTxBtn.classList.remove('btn-primary');

                showNotification('Live TX started - type to continue', 'success');
            } else {
                console.log('[TX LIVE] Ending transmission');

                if (state.liveTxDebounceTimer) {
                    clearTimeout(state.liveTxDebounceTimer);
                    state.liveTxDebounceTimer = null;
                }

                state.liveTxInFlight = false;

                stopTxOverlay();

                await api.endTxLive();

                elements.sendTxBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
                elements.sendTxBtn.classList.remove('btn-danger');
                elements.sendTxBtn.classList.add('btn-primary');

                showNotification('Ending transmission...', 'info');
            }
        } else {
            // BATCH MODE: Send entire message at once (old behavior)
            if (!text.trim()) {
                showNotification('Please enter text to transmit', 'warning');
                return;
            }

            console.log('[TX] Sending text:', text);
            await api.sendTxText(text);
            console.log('[TX] API call successful, displaying in RX buffer');
            // Display sent text in RX buffer (in red to indicate TX)
            appendRxText(text, 'tx');
            console.log('[TX] Text appended to RX buffer');
            elements.txText.value = '';
            showNotification('Text added to transmit queue', 'success');
        }
    } catch (error) {
        console.error('[TX] Error:', error);
        showNotification('Failed to send text: ' + error.message, 'error');
    }
}

/**
 * Handle clear RX
 */
async function handleClearRx() {
    try {
        await api.clearRx();
        elements.rxText.innerHTML = '';  // Clear all child elements
        showNotification('RX buffer cleared', 'success');
    } catch (error) {
        showNotification('Failed to clear RX: ' + error.message, 'error');
    }
}

/**
 * Handle clear TX
 */
async function handleClearTx() {
    try {
        await api.clearTx();
        elements.txText.value = '';
        showNotification('TX buffer cleared', 'success');
    } catch (error) {
        showNotification('Failed to clear TX: ' + error.message, 'error');
    }
}

/**
 * Update modem display
 */
function updateModem(modemName) {
    state.modem = modemName;
    elements.currentModem.textContent = modemName;

    // Only update dropdown if user is not actively selecting
    // (avoid overwriting their selection while they're choosing)
    if (document.activeElement !== elements.modemSelect) {
        elements.modemSelect.value = modemName;
    }
}

/**
 * Update carrier frequency display
 */
function updateCarrier(frequency) {
    state.carrier = frequency;
    elements.carrierValue.textContent = frequency;
    elements.carrierFreq.value = frequency;
}

/**
 * Update TX/RX status display
 */
function updateTxRxStatus(status) {
    const previousStatus = state.txStatus;
    state.txStatus = status;
    elements.trxStatus.textContent = status;

    elements.trxStatus.className = 'stat-value';
    if (status === 'RX') {
        elements.trxStatus.className += ' status-rx';
    } else if (status === 'TX') {
        elements.trxStatus.className += ' status-tx';
    } else if (status === 'TUNE') {
        elements.trxStatus.className += ' status-tune';
    }

    if (state.liveTxMode && previousStatus === 'TX' && status === 'RX') {
        const timeSinceStart = Date.now() - state.liveTxStartTime;
        if (state.liveTxActive && timeSinceStart < 2000) {
            console.log('[TX LIVE] Ignoring TX→RX transition - new TX session started', timeSinceStart, 'ms ago');
            return;
        }

        if (state.liveTxDebounceTimer) {
            clearTimeout(state.liveTxDebounceTimer);
            state.liveTxDebounceTimer = null;
        }

        const text = elements.txText.value;

        if (text.trim()) {
            appendRxText(text, 'tx');
        }

        elements.txText.value = '';
        state.liveTxBuffer = '';
        state.lastTxText = '';
        state.liveTxActive = false;

        stopTxOverlay();

        if (elements.sendTxBtn.textContent.includes('End')) {
            elements.sendTxBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            elements.sendTxBtn.classList.remove('btn-danger');
            elements.sendTxBtn.classList.add('btn-primary');
        }

        console.log('[TX LIVE] Transmission complete - buffer will be cleared by next startLiveTx()');

        showNotification('Transmission complete', 'success');
    }
}


/**
 * Update rig information
 */
function updateRigInfo(rigInfo) {
    if (rigInfo.name !== undefined) {
        elements.rigName.textContent = rigInfo.name || 'Not configured';
    }

    if (rigInfo.frequency !== undefined) {
        // Format frequency for display
        const freqText = rigInfo.frequency ? rigInfo.frequency.toLocaleString() + ' Hz' : '-';
        elements.rigFrequency.textContent = freqText;

        // Also update the stat card display (show in MHz for cleaner display)
        if (rigInfo.frequency) {
            const mhz = (rigInfo.frequency / 1000000).toFixed(4);
            elements.rigFreqDisplay.textContent = `${mhz} MHz`;
        } else {
            elements.rigFreqDisplay.textContent = '-';
        }
    }

    if (rigInfo.mode !== undefined) {
        elements.rigMode.textContent = rigInfo.mode || '-';
    }
}

/**
 * Handle keyboard shortcuts (using custom keybinds from window)
 */
function handleKeyboardShortcuts(event) {
    // Don't intercept shortcuts when typing in input fields (except Ctrl+Enter)
    const isInInput = event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA' || event.target.tagName === 'SELECT';

    const parts = [];
    if (event.ctrlKey) parts.push('Ctrl');
    if (event.altKey) parts.push('Alt');
    if (event.shiftKey) parts.push('Shift');

    let key = event.key;
    if (key === ' ') key = 'Space';
    else if (key.length === 1) key = key.toUpperCase();
    else if (key.startsWith('Arrow')) key = key.substring(5);

    if (key !== 'Control' && key !== 'Alt' && key !== 'Shift' && key !== 'Meta') {
        parts.push(key);
    }

    const keyString = parts.join('+');

    // Check if we're capturing a keybind (from keybind modal)
    if (window.capturingElement) {
        return; // Let the keybind modal handle it
    }

    // Get custom keybinds from window (set by index.html)
    const customKeybinds = window.currentKeybinds || {};
    const macroKeybinds = window.macroKeybinds || {};

    if (macroKeybinds[keyString]) {
        event.preventDefault();
        const macroKey = macroKeybinds[keyString];
        const macroBtn = document.querySelector(`#macro-buttons button[title*="Macro ${macroKey}"]`) ||
                        Array.from(document.querySelectorAll('#macro-buttons button')).find(btn =>
                            btn.textContent.includes(`Macro ${macroKey}`)
                        );
        if (macroBtn) {
            macroBtn.click();
        }
        return;
    }

    // Don't handle other shortcuts when in input fields (except allowed ones)
    if (isInInput && !(event.ctrlKey || event.altKey || event.metaKey)) {
        return;
    }

    for (const [id, bind] of Object.entries(customKeybinds)) {
        if (bind.keys === keyString) {
            event.preventDefault();

            switch(bind.action) {
                case 'sendTx':
                    handleSendTx();
                    break;
                case 'clearRx':
                    handleClearRx();
                    break;
                case 'abort':
                    handleTxRxControl('abort');
                    break;
                case 'toggleConnection':
                    elements.connectBtn.click();
                    break;
                case 'startRx':
                    handleTxRxControl('rx');
                    break;
                case 'startTx':
                    handleTxRxControl('tx');
                    break;
            }
            return;
        }
    }

    // Legacy Alt+1-5: Send macro (if not overridden)
    if (event.altKey && !event.ctrlKey && !event.shiftKey) {
        const num = parseInt(event.key);
        if (num >= 1 && num <= 5) {
            event.preventDefault();
            const macroBtn = document.querySelector(`#macro-buttons button:nth-child(${num})`);
            if (macroBtn) {
                macroBtn.click();
            }
            return;
        }
    }
}

/**
 * Append text to RX display
 * @param {string} text - The text to append
 * @param {string} type - Either 'rx' or 'tx' (tx will be displayed in red)
 */
function appendRxText(text, type = 'rx') {
    console.log(`[appendRxText] Called with type=${type}, text length=${text.length}`);
    console.log(`[appendRxText] RX element exists:`, !!elements.rxText);

    const span = document.createElement('span');

    // Only add newline for TX messages (which are complete messages)
    // RX text streams character-by-character, so we preserve the original formatting
    if (type === 'tx' && !text.endsWith('\n')) {
        text += '\n';
    }

    span.textContent = text;

    // TX text is shown in red (like FLDIGI does)
    if (type === 'tx') {
        span.className = 'text-red-500 font-bold';
        console.log('[appendRxText] TX text, applying red/bold styling');
    }

    elements.rxText.appendChild(span);
    console.log(`[appendRxText] Span appended, total children: ${elements.rxText.children.length}`);

    elements.rxText.parentElement.scrollTop = elements.rxText.parentElement.scrollHeight;
}

/**
 * Show notification using toast system
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // Use global toast function from index.html
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
