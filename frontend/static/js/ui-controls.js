const DEFAULT_FONT_SIZES = {
    rx: 13,
    tx: 13
};

const MIN_FONT_SIZE = 10;
const MAX_FONT_SIZE = 24;

let uiPreferences = {
    fontSize: { ...DEFAULT_FONT_SIZES },
    collapsedPanels: []
};

async function loadUIPreferences() {
    if (window.webConfig && window.webConfig.uiPreferences) {
        uiPreferences = {
            fontSize: window.webConfig.uiPreferences.fontSize || { ...DEFAULT_FONT_SIZES },
            collapsedPanels: window.webConfig.uiPreferences.collapsedPanels || []
        };
    }
}

async function saveUIPreferences() {
    if (!window.webConfig) {
        return;
    }
    window.webConfig.uiPreferences = uiPreferences;
    if (window.saveWebConfig) {
        await window.saveWebConfig();
    }
}

function applyFontSize(target, size) {
    const element = target === 'rx'
        ? document.querySelector('.terminal-rx pre')
        : document.querySelector('.terminal-tx');

    if (element) {
        element.style.fontSize = `${size}px`;
    }

    const label = document.getElementById(`${target}-font-size-label`);
    if (label) {
        label.textContent = `${size}px`;
    }

    uiPreferences.fontSize[target] = size;
}

function initFontSizeControls() {
    document.querySelectorAll('.font-size-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const target = btn.dataset.target;
            const action = btn.dataset.action;
            let currentSize = uiPreferences.fontSize[target];

            if (action === 'increase' && currentSize < MAX_FONT_SIZE) {
                currentSize += 1;
            } else if (action === 'decrease' && currentSize > MIN_FONT_SIZE) {
                currentSize -= 1;
            }

            applyFontSize(target, currentSize);
            await saveUIPreferences();
        });
    });

    applyFontSize('rx', uiPreferences.fontSize.rx);
    applyFontSize('tx', uiPreferences.fontSize.tx);
}

function togglePanelCollapse(panelId) {
    const panel = document.querySelector(`[data-panel="${panelId}"]`).closest('.panel');
    const isCollapsed = panel.classList.contains('collapsed');

    if (isCollapsed) {
        panel.classList.remove('collapsed');
        uiPreferences.collapsedPanels = uiPreferences.collapsedPanels.filter(id => id !== panelId);
    } else {
        panel.classList.add('collapsed');
        if (!uiPreferences.collapsedPanels.includes(panelId)) {
            uiPreferences.collapsedPanels.push(panelId);
        }
    }

    saveUIPreferences();
}

function initCollapsiblePanels() {
    document.querySelectorAll('.panel-collapse-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const panelId = btn.dataset.panel;
            togglePanelCollapse(panelId);
        });
    });

    uiPreferences.collapsedPanels.forEach(panelId => {
        const btn = document.querySelector(`[data-panel="${panelId}"]`);
        if (btn) {
            const panel = btn.closest('.panel');
            panel.classList.add('collapsed');
        }
    });
}

async function initUIControls() {
    await loadUIPreferences();
    initFontSizeControls();
    initCollapsiblePanels();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUIControls);
} else {
    initUIControls();
}
