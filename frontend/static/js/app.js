window.showToast = function(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toast-container');

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 300);
    }, duration);
};

window.webConfig = {
    theme: 'dark',
    hasSeenWelcome: false,
    custom_keybinds: null,
    betaFeatures: false
};

async function loadWebConfig() {
    try {
        const response = await fetch('/api/settings/web-config');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.config) {
                window.webConfig = data.config;
                return window.webConfig;
            }
        }
    } catch (e) {
    }
    return window.webConfig;
}

async function saveWebConfig() {
    try {
        const response = await fetch('/api/settings/web-config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(window.webConfig)
        });
        if (response.ok) {
            const data = await response.json();
            return data.success;
        }
    } catch (e) {
    }
    return false;
}

window.saveWebConfig = saveWebConfig;

function applyBetaFeatures(enabled) {
    const modemTab = document.getElementById('tab-modem');
    const txProgressContainer = document.getElementById('tx-progress-container');
    const txProgressToggle = document.getElementById('tx-progress-toggle');

    if (enabled) {
        modemTab.style.display = '';
        txProgressContainer.style.display = 'flex';
    } else {
        modemTab.style.display = 'none';
        txProgressContainer.style.display = 'none';

        // Turn off TX progress when beta features are disabled
        if (txProgressToggle && txProgressToggle.checked) {
            txProgressToggle.checked = false;
            localStorage.setItem('showTxProgress', 'false');
            // Trigger change event to update state
            txProgressToggle.dispatchEvent(new Event('change'));
        }
    }
}

const themeToggle = document.getElementById('theme-toggle');
const themeIcon = themeToggle.querySelector('i');
const html = document.documentElement;

async function initTheme() {
    await loadWebConfig();

    // Apply beta features setting on load
    if (typeof applyBetaFeatures === 'function') {
        applyBetaFeatures(window.webConfig.betaFeatures || false);
    }

    // Initialize theme manager after config is loaded
    if (window.themeManager) {
        await window.themeManager.init();
        return;
    }

    // Fallback to old theme system for backward compatibility
    const savedTheme = window.webConfig.theme ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    if (savedTheme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    } else {
        html.setAttribute('data-theme', 'light');
    }
}

themeToggle.addEventListener('click', async () => {
    // If theme manager is available, use it for smarter toggling
    if (window.themeManager) {
        const currentTheme = window.themeManager.getTheme(window.themeManager.currentTheme);
        const currentBase = currentTheme ? currentTheme.base : 'dark';
        const newBase = currentBase === 'dark' ? 'light' : 'dark';

        // Find a default theme with the opposite base
        const themes = window.themeManager.getAllThemes();
        const newThemeId = Object.keys(themes).find(id =>
            !id.startsWith('custom-') && themes[id].base === newBase
        ) || newBase;

        await window.themeManager.applyTheme(newThemeId, false);
        return;
    }

    // Fallback to old theme toggle
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-theme', newTheme);
    window.webConfig.theme = newTheme;
    await saveWebConfig();

    if (newTheme === 'dark') {
        themeIcon.classList.replace('fa-moon', 'fa-sun');
    } else {
        themeIcon.classList.replace('fa-sun', 'fa-moon');
    }
});

initTheme();

const carrierInput = document.getElementById('carrier-input');
const carrierSlider = document.getElementById('carrier-freq');
const carrierValue = document.getElementById('carrier-value');

carrierInput.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    if (value >= 500 && value <= 3000) {
        carrierSlider.value = value;
        carrierValue.textContent = value;
    }
});

carrierSlider.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    carrierInput.value = value;
    carrierValue.textContent = value;
});

const modemSearch = document.getElementById('modem-search');
const modemSelect = document.getElementById('modem-select');
const allOptions = Array.from(modemSelect.querySelectorAll('option'));
const allOptgroups = Array.from(modemSelect.querySelectorAll('optgroup'));

modemSearch.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    if (!searchTerm) {
        allOptgroups.forEach(g => g.style.display = '');
        allOptions.forEach(o => o.style.display = '');
        return;
    }
    allOptgroups.forEach(g => g.style.display = 'none');
    allOptions.forEach(o => o.style.display = 'none');
    allOptions.forEach(o => {
        if (o.value.toLowerCase().includes(searchTerm)) {
            o.style.display = '';
            if (o.parentElement.tagName === 'OPTGROUP') {
                o.parentElement.style.display = '';
            }
        }
    });
});

let currentConfig = null;
let lastCall = '';

async function loadConfig() {
    try {
        const config = await fetch('/api/macros/config').then(r => r.json());
        currentConfig = config;
        document.getElementById('station-call').textContent = config.callsign;
        document.getElementById('station-name').textContent = config.name;
        document.getElementById('station-qth').textContent = config.qth;
        document.getElementById('config-callsign').value = config.callsign;
        document.getElementById('config-name').value = config.name;
        document.getElementById('config-qth').value = config.qth;
        loadMacros(config.macros);
    } catch (e) {
    }
}

function loadMacros(macros) {
    const container = document.getElementById('macro-buttons');
    container.innerHTML = '';
    Object.keys(macros).sort().forEach(key => {
        const btn = document.createElement('button');
        btn.className = 'macro-btn';
        btn.innerHTML = `<i class="fas fa-bolt"></i> Macro ${key}`;
        btn.title = macros[key];
        btn.onclick = () => sendMacro(macros[key]);
        container.appendChild(btn);
    });
}

async function loadModems() {
    try {
        const response = await fetch('/api/modem/list');
        const data = await response.json();
        const modems = data.modems || [];

        const groups = {};
        modems.forEach(modem => {
            let groupName = 'Other';

            if (modem.startsWith('BPSK') || modem.startsWith('QPSK') || modem.startsWith('PSK')) {
                groupName = 'PSK';
            } else if (modem.startsWith('RTTY')) {
                groupName = 'RTTY';
            } else if (modem.startsWith('OLIVIA') || modem.includes('OLIVIA')) {
                groupName = 'Olivia';
            } else if (modem.startsWith('CONTESTIA')) {
                groupName = 'Contestia';
            } else if (modem.startsWith('MT63')) {
                groupName = 'MT63';
            } else if (modem.startsWith('THOR')) {
                groupName = 'Thor';
            } else if (modem.startsWith('DOMINO') || modem.includes('DOMINO')) {
                groupName = 'DominoEX';
            } else if (modem.startsWith('MFSK')) {
                groupName = 'MFSK';
            } else if (modem.startsWith('CW')) {
                groupName = 'CW';
            } else if (modem.startsWith('HELL')) {
                groupName = 'Hellschreiber';
            } else if (modem.startsWith('THROB')) {
                groupName = 'Throb';
            } else if (modem.startsWith('PACKET')) {
                groupName = 'Packet';
            }

            if (!groups[groupName]) groups[groupName] = [];
            groups[groupName].push(modem);
        });

        const modemSelect = document.getElementById('modem-select');
        modemSelect.innerHTML = '';

        const preferredOrder = ['PSK', 'RTTY', 'Olivia', 'Contestia', 'MT63', 'Thor', 'DominoEX', 'MFSK', 'CW', 'Hellschreiber', 'Throb', 'Packet', 'Other'];

        preferredOrder.forEach(groupName => {
            if (groups[groupName]) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = groupName;
                groups[groupName].sort().forEach(modem => {
                    const option = document.createElement('option');
                    option.value = modem;
                    option.textContent = modem;
                    optgroup.appendChild(option);
                });
                modemSelect.appendChild(optgroup);
            }
        });

        allOptions.length = 0;
        allOptgroups.length = 0;
        allOptions.push(...Array.from(modemSelect.querySelectorAll('option')));
        allOptgroups.push(...Array.from(modemSelect.querySelectorAll('optgroup')));

    } catch (e) {
    }
}

async function sendMacro(text) {
    try {
        const exp = await fetch('/api/macros/expand', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, last_call: lastCall || null})
        }).then(r => r.json());

        await fetch('/api/txrx/text/tx', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: exp.expanded_text})
        });

        const rx = document.getElementById('rx-text');
        const span = document.createElement('span');
        span.textContent = exp.expanded_text.endsWith('\n') ? exp.expanded_text : exp.expanded_text + '\n';
        span.className = 'text-red-500';
        rx.appendChild(span);
        rx.parentElement.scrollTop = rx.parentElement.scrollHeight;
    } catch (e) {
    }
}

document.getElementById('set-call-btn').onclick = () => {
    lastCall = document.getElementById('last-call-input').value.toUpperCase().trim();
};

document.getElementById('config-btn').onclick = () => document.getElementById('config-modal').classList.add('active');
document.getElementById('close-config-btn').onclick = () => document.getElementById('config-modal').classList.remove('active');
document.getElementById('shortcuts-help-btn').onclick = async () => {
    document.getElementById('keybinds-modal').classList.add('active');
    await loadKeybinds();
};
document.getElementById('close-keybinds-btn').onclick = () => document.getElementById('keybinds-modal').classList.remove('active');
document.getElementById('tutorial-btn').onclick = () => {
    startTutorial();
};

document.getElementById('settings-btn').onclick = () => {
    document.getElementById('settings-modal').classList.add('active');
    // Load and apply beta features setting
    document.getElementById('beta-features-toggle').checked = window.webConfig.betaFeatures || false;
    applyBetaFeatures(window.webConfig.betaFeatures || false);
    // Load theme grids if theme UI is available
    if (window.loadThemeGrids) {
        window.loadThemeGrids();
    }
};
document.getElementById('close-settings-btn').onclick = () => document.getElementById('settings-modal').classList.remove('active');

document.getElementById('beta-features-toggle').onchange = async function() {
    const enabled = this.checked;
    window.webConfig.betaFeatures = enabled;
    applyBetaFeatures(enabled);

    // Save to backend
    try {
        await fetch('/api/settings/web-config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(window.webConfig)
        });
        showToast(`Beta features ${enabled ? 'enabled' : 'disabled'}`, 'success');
    } catch (e) {
        showToast('Failed to save setting', 'error');
    }
};

document.getElementById('save-config-btn').onclick = async () => {
    try {
        await fetch('/api/macros/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                callsign: document.getElementById('config-callsign').value,
                name: document.getElementById('config-name').value,
                qth: document.getElementById('config-qth').value
            })
        });
        await loadConfig();
        document.getElementById('config-modal').classList.remove('active');
    } catch (e) {
    }
};

document.getElementById('save-rx-btn').onclick = () => {
    const rxText = document.getElementById('rx-text');
    const text = rxText.textContent || rxText.innerText;

    if (!text.trim()) {
        showToast('RX buffer is empty', 'warning');
        return;
    }

    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `fldigi-rx-${timestamp}.txt`;

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast(`Saved as ${filename}`, 'success');
};

document.getElementById('settings-bandwidth').oninput = (e) => {
    document.getElementById('settings-bandwidth-value').value = e.target.value;
};
document.getElementById('settings-bandwidth-value').oninput = (e) => {
    document.getElementById('settings-bandwidth').value = e.target.value;
};

async function loadModemSettings() {
    try {
        const modem = await fetch('/api/modem/info').then(r => r.json());
        if (modem.bandwidth) {
            document.getElementById('settings-bandwidth').value = modem.bandwidth;
            document.getElementById('settings-bandwidth-value').value = modem.bandwidth;
        }
        document.getElementById('settings-afc').checked = (await fetch('/api/settings/afc').then(r => r.json())).enabled;
        document.getElementById('settings-squelch').checked = (await fetch('/api/settings/squelch').then(r => r.json())).enabled;
        document.getElementById('settings-reverse').checked = (await fetch('/api/settings/reverse').then(r => r.json())).enabled;
    } catch (e) {
        console.error('Failed to load modem settings:', e);
    }
}

// Make it globally accessible
window.loadModemSettings = loadModemSettings;

document.getElementById('save-settings-btn').onclick = async () => {
    try {
        const bandwidth = parseInt(document.getElementById('settings-bandwidth-value').value);
        const afc = document.getElementById('settings-afc').checked;
        const squelch = document.getElementById('settings-squelch').checked;
        const reverse = document.getElementById('settings-reverse').checked;

        await Promise.all([
            fetch('/api/modem/bandwidth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({bandwidth})
            }),
            fetch('/api/settings/afc', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: afc})
            }),
            fetch('/api/settings/squelch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: squelch})
            }),
            fetch('/api/settings/reverse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: reverse})
            })
        ]);

        document.getElementById('settings-modal').classList.remove('active');
        showToast('Settings applied successfully!', 'success');
    } catch (e) {
        showToast('Failed to apply some settings. Check console.', 'error');
    }
};

let currentEditingMacroKey = null;

document.getElementById('edit-macros-btn').onclick = () => {
    document.getElementById('macro-editor-modal').classList.add('active');
    loadMacroEditor();
};

document.getElementById('close-macro-editor-btn').onclick = () => {
    document.getElementById('macro-editor-modal').classList.remove('active');
};

document.getElementById('close-macro-edit-dialog-btn').onclick = () => {
    document.getElementById('macro-edit-dialog').classList.remove('active');
};

document.getElementById('cancel-macro-edit-btn').onclick = () => {
    document.getElementById('macro-edit-dialog').classList.remove('active');
};

async function loadMacroEditor() {
    try {
        const response = await fetch('/api/macros/macros');
        const data = await response.json();
        const macros = data.macros;

        const container = document.getElementById('macro-list');
        container.innerHTML = '';

        const sortedKeys = Object.keys(macros).sort();
        sortedKeys.forEach(key => {
            const macroItem = document.createElement('div');
            macroItem.style.cssText = 'display: flex; justify-content: space-between; align-items: flex-start; padding: 1rem; background: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 0.75rem; transition: var(--transition);';
            macroItem.onmouseover = () => macroItem.style.background = 'var(--bg-tertiary)';
            macroItem.onmouseout = () => macroItem.style.background = 'var(--bg-secondary)';

            macroItem.innerHTML = `
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: var(--accent); margin-bottom: 0.25rem;">Macro: ${key}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace; white-space: pre-wrap; word-break: break-word;">${macros[key]}</div>
                </div>
                <div style="display: flex; gap: 0.5rem; margin-left: 1rem;">
                    <button class="btn btn-secondary" style="padding: 0.5rem 0.75rem;" onclick="editMacro('${key}', \`${macros[key].replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger" style="padding: 0.5rem 0.75rem;" onclick="deleteMacro('${key}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

            container.appendChild(macroItem);
        });
    } catch (e) {
    }
}

document.getElementById('add-macro-btn').onclick = () => {
    currentEditingMacroKey = null;
    document.getElementById('macro-edit-title').textContent = 'Add New Macro';
    document.getElementById('macro-key-input').value = '';
    document.getElementById('macro-key-input').readOnly = false;
    document.getElementById('macro-text-input').value = '';
    document.getElementById('macro-preview').textContent = 'Type macro text to see preview...';
    document.getElementById('macro-edit-dialog').classList.add('active');
};

window.editMacro = (key, text) => {
    currentEditingMacroKey = key;
    document.getElementById('macro-edit-title').textContent = `Edit Macro: ${key}`;
    document.getElementById('macro-key-input').value = key;
    document.getElementById('macro-key-input').readOnly = true;
    document.getElementById('macro-text-input').value = text;
    updateMacroPreview();
    document.getElementById('macro-edit-dialog').classList.add('active');
};

window.deleteMacro = async (key) => {
    if (!confirm(`Are you sure you want to delete macro "${key}"?`)) {
        return;
    }

    try {
        const response = await fetch('/api/macros/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key})
        });

        if (response.ok) {
            await loadMacroEditor();
            await loadConfig();
            showToast(`Macro "${key}" deleted successfully!`, 'success');
        } else {
            showToast('Failed to delete macro', 'error');
        }
    } catch (e) {
        showToast('Error deleting macro', 'error');
    }
};

document.getElementById('macro-text-input').oninput = updateMacroPreview;

async function updateMacroPreview() {
    const text = document.getElementById('macro-text-input').value;
    if (!text) {
        document.getElementById('macro-preview').textContent = 'Type macro text to see preview...';
        return;
    }

    try {
        const response = await fetch('/api/macros/expand', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, last_call: lastCall || null})
        });

        const data = await response.json();
        document.getElementById('macro-preview').textContent = data.expanded_text;
    } catch (e) {
        document.getElementById('macro-preview').textContent = 'Error generating preview';
    }
}

document.getElementById('save-macro-edit-btn').onclick = async () => {
    const key = document.getElementById('macro-key-input').value.trim();
    const text = document.getElementById('macro-text-input').value;

    if (!key) {
        showToast('Please enter a macro key', 'warning');
        return;
    }

    if (!text) {
        showToast('Please enter macro text', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/macros/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({key, text})
        });

        if (response.ok) {
            document.getElementById('macro-edit-dialog').classList.remove('active');
            await loadMacroEditor();
            await loadConfig();
            showToast(`Macro "${key}" saved successfully!`, 'success');
        } else {
            showToast('Failed to save macro', 'error');
        }
    } catch (e) {
        showToast('Error saving macro', 'error');
    }
};

const TUTORIAL_STEPS = [
    {
        title: "Connecting to FLDIGI",
        content: `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-plug" style="font-size: 4rem; color: var(--accent);"></i>
            </div>
            <p style="margin-bottom: 1rem;">First, make sure <strong>FLDIGI is running</strong> on your computer with <strong>XML-RPC enabled</strong> (port 7362).</p>
            <div style="background: var(--success-light); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--success);">
                <strong>Tip:</strong> The status indicator will turn green when connected!
            </div>
        `
    },
    {
        title: "Selecting a Modem",
        content: `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-wave-square" style="font-size: 4rem; color: var(--accent);"></i>
            </div>
            <p style="margin-bottom: 1rem;">Use the <strong>Modem</strong> panel on the left to select your digital mode:</p>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
                <li>BPSK31 - Most popular, good for beginners</li>
                <li>RTTY - Classic teletype mode</li>
                <li>Olivia - Excellent for weak signals</li>
            </ul>
            <p>Search for modes or browse by category, then click <strong>"Apply Mode"</strong>.</p>
        `
    },
    {
        title: "Receiving & Transmitting",
        content: `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-satellite-dish" style="font-size: 4rem; color: var(--accent);"></i>
            </div>
            <p style="margin-bottom: 1rem;"><strong>Receive Window:</strong> Shows incoming text from other stations in real-time (green text). You can resize the window by dragging the bottom-right corner.</p>
            <p style="margin-bottom: 1rem;"><strong>Transmit Buffer:</strong> Type your message here and click <strong>"Send"</strong> or press <strong>Ctrl+Enter</strong>. You can continue typing while your message is being transmitted, but you can only backspace—you cannot edit prior lines. This window is also resizable.</p>
            <p style="margin-bottom: 1rem;"><strong>Auto-Stop:</strong> The program automatically ends transmission when you stop typing—no need to manually press Ctrl+R or stop the transmission!</p>
            <div style="background: var(--warning-light); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--warning);">
                <strong>Note:</strong> TX text appears in red in the RX buffer to show what you've sent!
            </div>
        `
    },
    {
        title: "Using Macros",
        content: `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-keyboard" style="font-size: 4rem; color: var(--accent);"></i>
            </div>
            <p style="margin-bottom: 1rem;"><strong>Macros</strong> are pre-written messages with placeholders for quick communication:</p>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
                <li>&lt;MYCALL&gt; - Your callsign</li>
                <li>&lt;CALL&gt; - Last contacted station</li>
                <li>&lt;TIME&gt;, &lt;DATE&gt; - Current time/date</li>
            </ul>
            <p style="margin-bottom: 1rem;">Click <strong>"Edit Macros"</strong> to create custom macros!</p>
            <p>Use keyboard shortcuts <strong>Alt+1</strong> through <strong>Alt+5</strong> for quick macro access.</p>
        `
    },
    {
        title: "You're All Set!",
        content: `
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <i class="fas fa-check-circle" style="font-size: 4rem; color: var(--success);"></i>
            </div>
            <p style="margin-bottom: 1rem;"><strong>Congratulations!</strong> You're ready to use DigiShell.</p>
            <p style="margin-bottom: 1rem;"><strong>Quick Tips:</strong></p>
            <ul style="margin-left: 1.5rem; margin-bottom: 1rem;">
                <li>Click the keyboard icon for all shortcuts</li>
                <li>Adjust carrier frequency with the slider for optimal signal</li>
                <li>Use macros (Alt+1-5) for quick, error-free communication</li>
                <li>Monitor your rig frequency in the status bar</li>
            </ul>
            <div style="background: var(--accent-light); padding: 1rem; border-radius: var(--radius-md); border-left: 4px solid var(--accent); text-align: center;">
                <strong>73 and good DX! 📡</strong>
            </div>
        `
    }
];

let currentTutorialStep = 0;

window.addEventListener('load', async () => {
    await loadWebConfig();

    try {
        const response = await fetch('/api/macros/config');
        const config = await response.json();
        currentConfig = config;

        const shouldShowWelcome = !window.webConfig.hasSeenWelcome || config.callsign === 'NOCALL';

        if (shouldShowWelcome) {
            setTimeout(() => {
                document.getElementById('welcome-modal').classList.add('active');
            }, 500);
        }

        document.getElementById('station-call').textContent = config.callsign;
        document.getElementById('station-name').textContent = config.name;
        document.getElementById('station-qth').textContent = config.qth;
        document.getElementById('config-callsign').value = config.callsign;
        document.getElementById('config-name').value = config.name;
        document.getElementById('config-qth').value = config.qth;
        loadMacros(config.macros);
    } catch (e) {
        setTimeout(() => {
            document.getElementById('welcome-modal').classList.add('active');
        }, 500);
    }

    loadModems();
});

document.getElementById('welcome-continue-btn').onclick = async () => {
    const callsign = document.getElementById('welcome-callsign').value.trim().toUpperCase();

    if (!callsign) {
        showToast('Please enter your callsign to continue', 'warning');
        return;
    }

    const name = document.getElementById('welcome-name').value.trim() || 'Operator';
    const qth = document.getElementById('welcome-qth').value.trim() || 'Somewhere';

    try {
        await fetch('/api/macros/config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({callsign, name, qth})
        });
        await loadConfig();
    } catch (e) {
    }

    window.webConfig.hasSeenWelcome = true;
    await saveWebConfig();
    document.getElementById('welcome-modal').classList.remove('active');

    if (document.getElementById('welcome-tutorial-toggle').checked) {
        setTimeout(() => {
            startTutorial();
        }, 300);
    }
};

function startTutorial() {
    currentTutorialStep = 0;
    showTutorialStep(0);
    document.getElementById('tutorial-modal').classList.add('active');
}

function showTutorialStep(step) {
    if (step < 0 || step >= TUTORIAL_STEPS.length) return;

    currentTutorialStep = step;
    const tutorialData = TUTORIAL_STEPS[step];

    document.getElementById('tutorial-title').textContent =
        `Quick Tutorial (${step + 1}/${TUTORIAL_STEPS.length}) - ${tutorialData.title}`;
    document.getElementById('tutorial-content').innerHTML = tutorialData.content;

    document.getElementById('tutorial-prev-btn').disabled = step === 0;
    document.getElementById('tutorial-prev-btn').style.opacity = step === 0 ? '0.5' : '1';

    const nextBtn = document.getElementById('tutorial-next-btn');
    if (step === TUTORIAL_STEPS.length - 1) {
        nextBtn.innerHTML = '<i class="fas fa-check"></i> Finish';
    } else {
        nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
    }
}

document.getElementById('tutorial-prev-btn').onclick = () => {
    showTutorialStep(currentTutorialStep - 1);
};

document.getElementById('tutorial-next-btn').onclick = () => {
    if (currentTutorialStep === TUTORIAL_STEPS.length - 1) {
        document.getElementById('tutorial-modal').classList.remove('active');
    } else {
        showTutorialStep(currentTutorialStep + 1);
    }
};

document.getElementById('close-tutorial-btn').onclick = () => {
    document.getElementById('tutorial-modal').classList.remove('active');
};

document.getElementById('shortcuts-help-btn').addEventListener('dblclick', () => {
    startTutorial();
});

const DEFAULT_KEYBINDS = {
    'send_tx': { keys: 'Ctrl+Enter', description: 'Send TX message', action: 'sendTx' },
    'clear_rx': { keys: 'Ctrl+K', description: 'Clear RX buffer', action: 'clearRx' },
    'abort_tx': { keys: 'Escape', description: 'Abort transmission', action: 'abort' },
    'toggle_connection': { keys: 'Ctrl+D', description: 'Connect/Disconnect', action: 'toggleConnection' },
    'start_rx': { keys: 'Ctrl+R', description: 'Start RX', action: 'startRx' },
};

let currentKeybinds = {...DEFAULT_KEYBINDS};
let macroKeybinds = {};
let capturedKeybind = null;
let capturingElement = null;

window.currentKeybinds = currentKeybinds;
window.macroKeybinds = macroKeybinds;
window.capturingElement = null;

async function loadStoredKeybinds() {
    await loadWebConfig();
    if (window.webConfig.custom_keybinds) {
        try {
            currentKeybinds = {...DEFAULT_KEYBINDS, ...window.webConfig.custom_keybinds.default};
            macroKeybinds = window.webConfig.custom_keybinds.macros || {};
        } catch (e) {
        }
    }

    if (Object.keys(macroKeybinds).length === 0) {
        macroKeybinds = {
            'Alt+1': '1',
            'Alt+2': '2',
            'Alt+3': '3',
            'Alt+4': '4',
            'Alt+5': '5'
        };
    }

    window.currentKeybinds = currentKeybinds;
    window.macroKeybinds = macroKeybinds;
}

async function saveKeybinds() {
    window.webConfig.custom_keybinds = {
        default: currentKeybinds,
        macros: macroKeybinds
    };
    await saveWebConfig();
}

function keyEventToString(event) {
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
        return parts.join('+');
    }

    return null;
}

async function loadKeybinds() {
    await loadStoredKeybinds();

    const defaultList = document.getElementById('default-keybinds-list');
    defaultList.innerHTML = '';

    Object.entries(currentKeybinds).forEach(([id, bind]) => {
        const row = document.createElement('div');
        row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.875rem 1rem; background: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 0.625rem;';
        row.innerHTML = `
            <div>
                <div style="font-weight: 600; color: var(--text-primary);">${bind.description}</div>
            </div>
            <input type="text" value="${bind.keys}" readonly data-keybind-id="${id}"
                   style="width: 180px; cursor: pointer; text-align: center; font-weight: 600; font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;">
        `;
        const input = row.querySelector('input');
        input.addEventListener('click', () => startKeybindCapture(input, id, false));
        defaultList.appendChild(row);
    });

    const macroList = document.getElementById('macro-keybinds-list');
    macroList.innerHTML = '';

    if (Object.keys(macroKeybinds).length === 0) {
        macroList.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">No macro shortcuts configured. Click "Add Macro Shortcut" to create one.</div>';
    } else {
        Object.entries(macroKeybinds).forEach(([keys, macroKey]) => {
            const row = document.createElement('div');
            row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.875rem 1rem; background: var(--bg-secondary); border-radius: var(--radius-md); margin-bottom: 0.625rem;';
            row.innerHTML = `
                <div>
                    <div style="font-weight: 600; color: var(--accent);">Macro: ${macroKey}</div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <input type="text" value="${keys}" readonly data-macro-key="${macroKey}"
                           style="width: 120px; cursor: pointer; text-align: center; font-weight: 600; font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace; padding: 0.375rem 0.75rem; background: var(--bg-tertiary); border: 1px solid var(--border-medium); border-radius: 6px; font-size: 0.75rem; color: var(--accent);">
                    <button class="btn btn-danger" style="padding: 0.5rem 0.75rem;" onclick="deleteMacroKeybind('${keys}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            const input = row.querySelector('input');
            input.addEventListener('click', () => startMacroKeybindCapture(input, macroKey, keys));
            macroList.appendChild(row);
        });
    }
}

function startKeybindCapture(inputElement, bindId, isMacro) {
    capturingElement = inputElement;
    window.capturingElement = inputElement;
    capturedKeybind = { bindId, isMacro };
    inputElement.value = 'Press a key combination...';
    inputElement.style.background = 'var(--accent-light)';
    inputElement.style.borderColor = 'var(--accent)';

    const handleKeydown = (e) => {
        e.preventDefault();
        e.stopPropagation();

        const keyString = keyEventToString(e);
        if (keyString) {
            inputElement.value = keyString;

            if (!isMacro) {
                currentKeybinds[bindId].keys = keyString;
            }

            inputElement.style.background = '';
            inputElement.style.borderColor = '';

            document.removeEventListener('keydown', handleKeydown, true);
            capturingElement = null;
            window.capturingElement = null;
        }
    };

    document.addEventListener('keydown', handleKeydown, true);
}

function startMacroKeybindCapture(inputElement, macroKey, oldKeys) {
    capturingElement = inputElement;
    window.capturingElement = inputElement;
    inputElement.value = 'Press a key combination...';
    inputElement.style.background = 'var(--accent-light)';
    inputElement.style.borderColor = 'var(--accent)';

    const handleKeydown = (e) => {
        e.preventDefault();
        e.stopPropagation();

        const keyString = keyEventToString(e);
        if (keyString) {
            if (macroKeybinds[oldKeys] === macroKey) {
                delete macroKeybinds[oldKeys];
            }

            macroKeybinds[keyString] = macroKey;

            inputElement.value = keyString;
            inputElement.style.background = '';
            inputElement.style.borderColor = '';

            document.removeEventListener('keydown', handleKeydown, true);
            capturingElement = null;
            window.capturingElement = null;

            loadKeybinds();
        }
    };

    document.addEventListener('keydown', handleKeydown, true);
}

document.getElementById('add-macro-keybind-btn').onclick = async () => {
    try {
        const response = await fetch('/api/macros/macros');
        const data = await response.json();
        const select = document.getElementById('macro-keybind-select');
        select.innerHTML = '';

        Object.keys(data.macros).forEach(key => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `Macro ${key}: ${data.macros[key].substring(0, 50)}${data.macros[key].length > 50 ? '...' : ''}`;
            select.appendChild(option);
        });

        document.getElementById('macro-keybind-input').value = '';
        document.getElementById('add-macro-keybind-modal').classList.add('active');
    } catch (e) {
        showToast('Failed to load macros', 'error');
    }
};

document.getElementById('close-add-macro-keybind-btn').onclick = () => {
    document.getElementById('add-macro-keybind-modal').classList.remove('active');
};

document.getElementById('cancel-macro-keybind-btn').onclick = () => {
    document.getElementById('add-macro-keybind-modal').classList.remove('active');
};

document.getElementById('macro-keybind-input').addEventListener('click', function() {
    window.capturingElement = this;
    this.value = 'Press a key combination...';
    this.style.background = 'var(--accent-light)';
    this.style.borderColor = 'var(--accent)';

    const handleKeydown = (e) => {
        e.preventDefault();
        e.stopPropagation();

        const keyString = keyEventToString(e);
        if (keyString) {
            this.value = keyString;
            this.style.background = '';
            this.style.borderColor = '';
            document.removeEventListener('keydown', handleKeydown, true);
            window.capturingElement = null;
        }
    };

    document.addEventListener('keydown', handleKeydown, true);
});

document.getElementById('save-macro-keybind-btn').onclick = async () => {
    const macroKey = document.getElementById('macro-keybind-select').value;
    const keys = document.getElementById('macro-keybind-input').value;

    if (!macroKey || !keys || keys === 'Press a key combination...') {
        showToast('Please select a macro and press a key combination', 'warning');
        return;
    }

    if (Object.keys(currentKeybinds).find(id => currentKeybinds[id].keys === keys)) {
        showToast(`This shortcut is already used by: ${currentKeybinds[Object.keys(currentKeybinds).find(id => currentKeybinds[id].keys === keys)].description}`, 'warning');
        return;
    }

    macroKeybinds[keys] = macroKey;
    document.getElementById('add-macro-keybind-modal').classList.remove('active');
    showToast(`Macro shortcut ${keys} added!`, 'success');
    await loadKeybinds();
};

window.deleteMacroKeybind = async (keys) => {
    delete macroKeybinds[keys];
    showToast('Macro shortcut removed', 'success');
    await loadKeybinds();
};

document.getElementById('reset-default-keybinds-btn').onclick = async () => {
    if (confirm('Reset all keybinds to defaults?')) {
        currentKeybinds = {...DEFAULT_KEYBINDS};
        showToast('Keybinds reset to defaults', 'success');
        await loadKeybinds();
    }
};

document.getElementById('save-keybinds-btn').onclick = async () => {
    await saveKeybinds();
    document.getElementById('keybinds-modal').classList.remove('active');
    showToast('Keybinds saved successfully!', 'success');
};

(async () => {
    await loadStoredKeybinds();
})();
