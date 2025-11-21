// Theme UI Management for DigiShell

let currentEditingThemeId = null;

// Initialize theme UI
function initThemeUI() {
    setupSettingsTabs();
    setupThemeGrids();
    setupCustomThemeModal();

    // Load themes when settings modal is opened
    document.getElementById('settings-btn').addEventListener('click', () => {
        loadThemeGrids();
    });
}

// Setup settings tabs
function setupSettingsTabs() {
    const tabs = document.querySelectorAll('.settings-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            const targetTab = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update active content
            document.querySelectorAll('.settings-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`settings-content-${targetTab}`).classList.add('active');

            // Load modem settings when modem tab is clicked
            if (targetTab === 'modem' && typeof window.loadModemSettings === 'function') {
                await window.loadModemSettings();
            }
        });
    });
}

// Create theme preview HTML
function createThemePreview(theme) {
    const colors = theme.colors;
    return `
        <div class="theme-preview" style="background: ${colors['--bg-primary']}; border: 1px solid ${colors['--border-light']};">
            <div class="theme-preview-header" style="background: ${colors['--bg-secondary']};">
                <div class="theme-preview-dot" style="background: ${colors['--danger']};"></div>
                <div class="theme-preview-dot" style="background: ${colors['--warning']};"></div>
                <div class="theme-preview-dot" style="background: ${colors['--success']};"></div>
            </div>
            <div class="theme-preview-body" style="background: ${colors['--bg-primary']};">
                <div class="theme-preview-line" style="background: ${colors['--accent']}; width: 70%;"></div>
                <div class="theme-preview-line" style="background: ${colors['--text-secondary']}; width: 85%;"></div>
                <div class="theme-preview-line" style="background: ${colors['--text-muted']}; width: 60%;"></div>
            </div>
        </div>
    `;
}

// Create theme card
function createThemeCard(themeId, theme, isCustom = false) {
    const card = document.createElement('div');
    card.className = 'theme-card';
    if (window.themeManager && window.themeManager.currentTheme === themeId) {
        card.classList.add('active');
    }

    card.innerHTML = `
        ${isCustom ? `<button class="theme-delete" data-theme-id="${themeId}"><i class="fas fa-trash"></i></button>` : ''}
        ${createThemePreview(theme)}
        <div class="theme-name">${theme.name}</div>
    `;

    // Click to apply theme
    card.addEventListener('click', async (e) => {
        if (!e.target.closest('.theme-delete')) {
            await applyThemeFromCard(themeId, isCustom);
        }
    });

    // Delete custom theme
    if (isCustom) {
        const deleteBtn = card.querySelector('.theme-delete');
        deleteBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            await deleteCustomTheme(themeId);
        });
    }

    return card;
}

// Apply theme from card click
async function applyThemeFromCard(themeId, isCustom) {
    if (!window.themeManager) return;

    await window.themeManager.applyTheme(themeId, isCustom);
    loadThemeGrids(); // Refresh to show active state

    if (window.showToast) {
        const theme = window.themeManager.getTheme(themeId);
        window.showToast(`Theme "${theme.name}" applied!`, 'success');
    }
}

// Delete custom theme
async function deleteCustomTheme(themeId) {
    if (!confirm('Delete this custom theme?')) return;

    if (!window.themeManager) return;

    const theme = window.themeManager.getTheme(themeId);
    await window.themeManager.deleteCustomTheme(themeId);
    loadThemeGrids();

    if (window.showToast) {
        window.showToast(`Theme "${theme.name}" deleted`, 'success');
    }
}

// Load theme grids (exposed globally for use from app.js)
window.loadThemeGrids = function loadThemeGrids() {
    if (!window.themeManager) return;

    const lightGrid = document.getElementById('light-themes-grid');
    const darkGrid = document.getElementById('dark-themes-grid');
    const customGrid = document.getElementById('custom-themes-grid');

    // Clear grids
    lightGrid.innerHTML = '';
    darkGrid.innerHTML = '';
    customGrid.innerHTML = '';

    // Load light themes
    const lightThemes = window.themeManager.getLightThemes();
    Object.entries(lightThemes).forEach(([themeId, theme]) => {
        const isCustom = themeId.startsWith('custom-');
        if (!isCustom) {
            lightGrid.appendChild(createThemeCard(themeId, theme, false));
        }
    });

    // Load dark themes
    const darkThemes = window.themeManager.getDarkThemes();
    Object.entries(darkThemes).forEach(([themeId, theme]) => {
        const isCustom = themeId.startsWith('custom-');
        if (!isCustom) {
            darkGrid.appendChild(createThemeCard(themeId, theme, false));
        }
    });

    // Load custom themes
    const customThemes = window.themeManager.getCustomThemes();
    if (Object.keys(customThemes).length === 0) {
        customGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.875rem;">No custom themes yet. Click "Create Custom Theme" to get started!</div>';
    } else {
        Object.entries(customThemes).forEach(([themeId, theme]) => {
            customGrid.appendChild(createThemeCard(themeId, theme, true));
        });
    }
}

// Setup theme grids
function setupThemeGrids() {
    document.getElementById('create-custom-theme-btn').addEventListener('click', () => {
        openCustomThemeModal();
    });
}

// Setup custom theme modal
function setupCustomThemeModal() {
    const modal = document.getElementById('custom-theme-modal');
    const closeBtn = document.getElementById('close-custom-theme-btn');
    const cancelBtn = document.getElementById('cancel-custom-theme-btn');
    const saveBtn = document.getElementById('save-custom-theme-btn');

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    saveBtn.addEventListener('click', async () => {
        await saveCustomTheme();
    });

    // Setup color pickers
    setupColorPickers();
}

// Setup color pickers with sync between color input and hex input
function setupColorPickers() {
    const colorFields = [
        { color: 'custom-accent', hex: 'custom-accent-hex', var: '--accent' },
        { color: 'custom-bg-primary', hex: 'custom-bg-primary-hex', var: '--bg-primary' },
        { color: 'custom-bg-secondary', hex: 'custom-bg-secondary-hex', var: '--bg-secondary' },
        { color: 'custom-text-primary', hex: 'custom-text-primary-hex', var: '--text-primary' }
    ];

    colorFields.forEach(field => {
        const colorInput = document.getElementById(field.color);
        const hexInput = document.getElementById(field.hex);

        colorInput.addEventListener('input', (e) => {
            hexInput.value = e.target.value;
            updateCustomThemePreview();
        });

        hexInput.addEventListener('input', (e) => {
            const hex = e.target.value;
            if (/^#[0-9A-F]{6}$/i.test(hex)) {
                colorInput.value = hex;
                updateCustomThemePreview();
            }
        });
    });

    // Base theme change
    document.getElementById('custom-theme-base').addEventListener('change', () => {
        loadBaseThemeColors();
    });
}

// Load base theme colors into custom theme editor
function loadBaseThemeColors() {
    const baseType = document.getElementById('custom-theme-base').value;
    const baseThemeId = baseType === 'dark' ? 'dark' : 'light';

    if (!window.themeManager) return;

    const baseTheme = window.themeManager.getTheme(baseThemeId);
    if (!baseTheme) return;

    document.getElementById('custom-accent').value = baseTheme.colors['--accent'];
    document.getElementById('custom-accent-hex').value = baseTheme.colors['--accent'];

    document.getElementById('custom-bg-primary').value = baseTheme.colors['--bg-primary'];
    document.getElementById('custom-bg-primary-hex').value = baseTheme.colors['--bg-primary'];

    document.getElementById('custom-bg-secondary').value = baseTheme.colors['--bg-secondary'];
    document.getElementById('custom-bg-secondary-hex').value = baseTheme.colors['--bg-secondary'];

    document.getElementById('custom-text-primary').value = baseTheme.colors['--text-primary'];
    document.getElementById('custom-text-primary-hex').value = baseTheme.colors['--text-primary'];

    updateCustomThemePreview();
}

// Update custom theme preview
function updateCustomThemePreview() {
    const preview = document.getElementById('theme-preview');
    const accent = document.getElementById('custom-accent-hex').value || '#0ea5e9';
    const bgPrimary = document.getElementById('custom-bg-primary-hex').value || '#ffffff';
    const bgSecondary = document.getElementById('custom-bg-secondary-hex').value || '#f8fafc';
    const textPrimary = document.getElementById('custom-text-primary-hex').value || '#0f172a';

    preview.style.background = bgPrimary;
    preview.style.borderColor = accent;
    preview.style.color = textPrimary;

    const button = preview.querySelector('.btn-primary');
    if (button) {
        button.style.background = `linear-gradient(135deg, ${accent}, ${accent})`;
    }
}

// Open custom theme modal
function openCustomThemeModal(themeId = null) {
    currentEditingThemeId = themeId;
    const modal = document.getElementById('custom-theme-modal');
    const title = document.getElementById('custom-theme-title');

    if (themeId) {
        title.textContent = 'Edit Custom Theme';
        // Load existing theme data
        const theme = window.themeManager.getTheme(themeId);
        document.getElementById('custom-theme-name').value = theme.name;
        document.getElementById('custom-theme-base').value = theme.base;

        // Load colors
        document.getElementById('custom-accent').value = theme.colors['--accent'];
        document.getElementById('custom-accent-hex').value = theme.colors['--accent'];
        document.getElementById('custom-bg-primary').value = theme.colors['--bg-primary'];
        document.getElementById('custom-bg-primary-hex').value = theme.colors['--bg-primary'];
        document.getElementById('custom-bg-secondary').value = theme.colors['--bg-secondary'];
        document.getElementById('custom-bg-secondary-hex').value = theme.colors['--bg-secondary'];
        document.getElementById('custom-text-primary').value = theme.colors['--text-primary'];
        document.getElementById('custom-text-primary-hex').value = theme.colors['--text-primary'];
    } else {
        title.textContent = 'Create Custom Theme';
        document.getElementById('custom-theme-name').value = '';
        document.getElementById('custom-theme-base').value = 'dark';
        loadBaseThemeColors();
    }

    updateCustomThemePreview();
    modal.classList.add('active');
}

// Save custom theme
async function saveCustomTheme() {
    const name = document.getElementById('custom-theme-name').value.trim();
    if (!name) {
        if (window.showToast) {
            window.showToast('Please enter a theme name', 'warning');
        }
        return;
    }

    const baseType = document.getElementById('custom-theme-base').value;
    const baseThemeId = baseType === 'dark' ? 'dark' : 'light';

    const customColors = {
        '--accent': document.getElementById('custom-accent-hex').value,
        '--bg-primary': document.getElementById('custom-bg-primary-hex').value,
        '--bg-secondary': document.getElementById('custom-bg-secondary-hex').value,
        '--text-primary': document.getElementById('custom-text-primary-hex').value
    };

    if (!window.themeManager) return;

    let themeId;
    if (currentEditingThemeId) {
        // Update existing theme
        await window.themeManager.updateCustomTheme(currentEditingThemeId, {
            name: name,
            colors: customColors
        });
        themeId = currentEditingThemeId;
    } else {
        // Create new theme
        themeId = await window.themeManager.createCustomTheme(name, baseThemeId, customColors);
    }

    // Close modal
    document.getElementById('custom-theme-modal').classList.remove('active');

    // Apply the new theme
    await window.themeManager.applyTheme(themeId, true);

    // Refresh theme grids
    loadThemeGrids();

    if (window.showToast) {
        window.showToast(`Theme "${name}" ${currentEditingThemeId ? 'updated' : 'created'}!`, 'success');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeUI);
} else {
    initThemeUI();
}
