// Theme Management System for DigiShell

const THEME_PRESETS = {
    // Light Mode Themes
    'light': {
        name: 'Light (Default)',
        base: 'light',
        colors: {
            '--bg-primary': '#ffffff',
            '--bg-secondary': '#f8fafc',
            '--bg-tertiary': '#f1f5f9',
            '--bg-hover': '#e2e8f0',
            '--text-primary': '#0f172a',
            '--text-secondary': '#64748b',
            '--text-muted': '#94a3b8',
            '--border-light': '#e2e8f0',
            '--border-medium': '#cbd5e1',
            '--accent': '#0ea5e9',
            '--accent-hover': '#0284c7',
            '--accent-light': '#e0f2fe',
            '--success': '#10b981',
            '--success-light': '#d1fae5',
            '--warning': '#f59e0b',
            '--warning-light': '#fef3c7',
            '--danger': '#ef4444',
            '--danger-light': '#fee2e2',
            '--terminal-bg': '#1e293b',
            '--terminal-text': '#10b981',
            '--terminal-tx': '#ef4444'
        }
    },
    'light-warm': {
        name: 'Light Warm',
        base: 'light',
        colors: {
            '--bg-primary': '#fefbf6',
            '--bg-secondary': '#faf5ed',
            '--bg-tertiary': '#f5ede0',
            '--bg-hover': '#ebe3d5',
            '--text-primary': '#292524',
            '--text-secondary': '#78716c',
            '--text-muted': '#a8a29e',
            '--border-light': '#e7e5e4',
            '--border-medium': '#d6d3d1',
            '--accent': '#ea580c',
            '--accent-hover': '#c2410c',
            '--accent-light': '#fed7aa',
            '--success': '#16a34a',
            '--success-light': '#d1fae5',
            '--warning': '#f59e0b',
            '--warning-light': '#fef3c7',
            '--danger': '#dc2626',
            '--danger-light': '#fee2e2',
            '--terminal-bg': '#292524',
            '--terminal-text': '#16a34a',
            '--terminal-tx': '#dc2626'
        }
    },
    'light-cool': {
        name: 'Light Cool',
        base: 'light',
        colors: {
            '--bg-primary': '#f8fafc',
            '--bg-secondary': '#f1f5f9',
            '--bg-tertiary': '#e2e8f0',
            '--bg-hover': '#cbd5e1',
            '--text-primary': '#0f172a',
            '--text-secondary': '#475569',
            '--text-muted': '#94a3b8',
            '--border-light': '#cbd5e1',
            '--border-medium': '#94a3b8',
            '--accent': '#3b82f6',
            '--accent-hover': '#2563eb',
            '--accent-light': '#dbeafe',
            '--success': '#10b981',
            '--success-light': '#d1fae5',
            '--warning': '#f59e0b',
            '--warning-light': '#fef3c7',
            '--danger': '#ef4444',
            '--danger-light': '#fee2e2',
            '--terminal-bg': '#1e293b',
            '--terminal-text': '#10b981',
            '--terminal-tx': '#ef4444'
        }
    },
    'light-high-contrast': {
        name: 'Light High Contrast',
        base: 'light',
        colors: {
            '--bg-primary': '#ffffff',
            '--bg-secondary': '#f5f5f5',
            '--bg-tertiary': '#e5e5e5',
            '--bg-hover': '#d4d4d4',
            '--text-primary': '#000000',
            '--text-secondary': '#404040',
            '--text-muted': '#737373',
            '--border-light': '#d4d4d4',
            '--border-medium': '#a3a3a3',
            '--accent': '#0066cc',
            '--accent-hover': '#0052a3',
            '--accent-light': '#cce5ff',
            '--success': '#008000',
            '--success-light': '#ccffcc',
            '--warning': '#ff8c00',
            '--warning-light': '#ffe5cc',
            '--danger': '#cc0000',
            '--danger-light': '#ffcccc',
            '--terminal-bg': '#000000',
            '--terminal-text': '#00ff00',
            '--terminal-tx': '#ff0000'
        }
    },

    // Dark Mode Themes
    'dark': {
        name: 'Dark (Default)',
        base: 'dark',
        colors: {
            '--bg-primary': '#0f172a',
            '--bg-secondary': '#1e293b',
            '--bg-tertiary': '#334155',
            '--bg-hover': '#475569',
            '--text-primary': '#f1f5f9',
            '--text-secondary': '#94a3b8',
            '--text-muted': '#64748b',
            '--border-light': '#334155',
            '--border-medium': '#475569',
            '--accent': '#38bdf8',
            '--accent-hover': '#0ea5e9',
            '--accent-light': '#164e63',
            '--success': '#10b981',
            '--success-light': '#064e3b',
            '--warning': '#f59e0b',
            '--warning-light': '#78350f',
            '--danger': '#ef4444',
            '--danger-light': '#7f1d1d',
            '--terminal-bg': '#020617',
            '--terminal-text': '#10b981',
            '--terminal-tx': '#ef4444'
        }
    },
    'dark-purple': {
        name: 'Dark Purple',
        base: 'dark',
        colors: {
            '--bg-primary': '#1e1b2e',
            '--bg-secondary': '#2d2a40',
            '--bg-tertiary': '#3d3a52',
            '--bg-hover': '#4d4a62',
            '--text-primary': '#e9e7f0',
            '--text-secondary': '#b4b1c4',
            '--text-muted': '#8580a0',
            '--border-light': '#3d3a52',
            '--border-medium': '#4d4a62',
            '--accent': '#a78bfa',
            '--accent-hover': '#8b5cf6',
            '--accent-light': '#2e1065',
            '--success': '#10b981',
            '--success-light': '#064e3b',
            '--warning': '#fbbf24',
            '--warning-light': '#78350f',
            '--danger': '#f87171',
            '--danger-light': '#7f1d1d',
            '--terminal-bg': '#0f0d1a',
            '--terminal-text': '#a78bfa',
            '--terminal-tx': '#f87171'
        }
    },
    'dark-green': {
        name: 'Dark Green',
        base: 'dark',
        colors: {
            '--bg-primary': '#0a1f1a',
            '--bg-secondary': '#0f2e26',
            '--bg-tertiary': '#1a4138',
            '--bg-hover': '#24544a',
            '--text-primary': '#e6f4f1',
            '--text-secondary': '#9fc5ba',
            '--text-muted': '#6b9688',
            '--border-light': '#1a4138',
            '--border-medium': '#24544a',
            '--accent': '#34d399',
            '--accent-hover': '#10b981',
            '--accent-light': '#064e3b',
            '--success': '#22c55e',
            '--success-light': '#052e16',
            '--warning': '#fbbf24',
            '--warning-light': '#78350f',
            '--danger': '#ef4444',
            '--danger-light': '#7f1d1d',
            '--terminal-bg': '#051810',
            '--terminal-text': '#34d399',
            '--terminal-tx': '#ef4444'
        }
    },
    'dark-amber': {
        name: 'Dark Amber',
        base: 'dark',
        colors: {
            '--bg-primary': '#1c1917',
            '--bg-secondary': '#292524',
            '--bg-tertiary': '#44403c',
            '--bg-hover': '#57534e',
            '--text-primary': '#fafaf9',
            '--text-secondary': '#a8a29e',
            '--text-muted': '#78716c',
            '--border-light': '#44403c',
            '--border-medium': '#57534e',
            '--accent': '#fbbf24',
            '--accent-hover': '#f59e0b',
            '--accent-light': '#78350f',
            '--success': '#10b981',
            '--success-light': '#064e3b',
            '--warning': '#fb923c',
            '--warning-light': '#7c2d12',
            '--danger': '#ef4444',
            '--danger-light': '#7f1d1d',
            '--terminal-bg': '#0c0a09',
            '--terminal-text': '#fbbf24',
            '--terminal-tx': '#ef4444'
        }
    },
    'dark-high-contrast': {
        name: 'Dark High Contrast',
        base: 'dark',
        colors: {
            '--bg-primary': '#000000',
            '--bg-secondary': '#1a1a1a',
            '--bg-tertiary': '#262626',
            '--bg-hover': '#404040',
            '--text-primary': '#ffffff',
            '--text-secondary': '#d4d4d4',
            '--text-muted': '#a3a3a3',
            '--border-light': '#404040',
            '--border-medium': '#525252',
            '--accent': '#0ea5e9',
            '--accent-hover': '#06b6d4',
            '--accent-light': '#164e63',
            '--success': '#22c55e',
            '--success-light': '#052e16',
            '--warning': '#fbbf24',
            '--warning-light': '#78350f',
            '--danger': '#f87171',
            '--danger-light': '#7f1d1d',
            '--terminal-bg': '#000000',
            '--terminal-text': '#22c55e',
            '--terminal-tx': '#f87171'
        }
    },
    'dark-ocean': {
        name: 'Dark Ocean',
        base: 'dark',
        colors: {
            '--bg-primary': '#0c1821',
            '--bg-secondary': '#1b2838',
            '--bg-tertiary': '#2a3f54',
            '--bg-hover': '#39566f',
            '--text-primary': '#e8f0f7',
            '--text-secondary': '#8fa9c4',
            '--text-muted': '#5e7a94',
            '--border-light': '#2a3f54',
            '--border-medium': '#39566f',
            '--accent': '#06b6d4',
            '--accent-hover': '#0891b2',
            '--accent-light': '#164e63',
            '--success': '#14b8a6',
            '--success-light': '#042f2e',
            '--warning': '#f59e0b',
            '--warning-light': '#78350f',
            '--danger': '#f43f5e',
            '--danger-light': '#881337',
            '--terminal-bg': '#020a0f',
            '--terminal-text': '#06b6d4',
            '--terminal-tx': '#f43f5e'
        }
    }
};

class ThemeManager {
    constructor() {
        this.currentTheme = 'dark';
        this.customThemes = {};
        this.isCustom = false;
    }

    async init() {
        await this.loadThemes();
        await this.applyCurrentTheme();
    }

    async loadThemes() {
        if (window.webConfig && window.webConfig.themes) {
            this.currentTheme = window.webConfig.themes.current || 'dark';
            this.customThemes = window.webConfig.themes.custom || {};
            this.isCustom = window.webConfig.themes.isCustom || false;
        }
    }

    async saveThemes() {
        if (!window.webConfig) {
            window.webConfig = {};
        }
        window.webConfig.themes = {
            current: this.currentTheme,
            custom: this.customThemes,
            isCustom: this.isCustom
        };
        if (window.saveWebConfig) {
            await window.saveWebConfig();
        }
    }

    getTheme(themeId) {
        if (themeId.startsWith('custom-')) {
            return this.customThemes[themeId];
        }
        return THEME_PRESETS[themeId];
    }

    async applyTheme(themeId, isCustom = false) {
        const theme = this.getTheme(themeId);
        if (!theme) {
            console.error('Theme not found:', themeId);
            return;
        }

        const root = document.documentElement;

        // Apply all theme colors
        Object.entries(theme.colors).forEach(([property, value]) => {
            root.style.setProperty(property, value);
        });

        // Update data-theme attribute for compatibility
        root.setAttribute('data-theme', theme.base);

        // Update theme toggle icon
        const themeIcon = document.querySelector('#theme-toggle i');
        if (themeIcon) {
            if (theme.base === 'dark') {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }

        this.currentTheme = themeId;
        this.isCustom = isCustom;

        // Update webConfig.theme for backward compatibility
        if (window.webConfig) {
            window.webConfig.theme = theme.base;
        }

        await this.saveThemes();
    }

    async applyCurrentTheme() {
        await this.applyTheme(this.currentTheme, this.isCustom);
    }

    async createCustomTheme(name, baseThemeId, customColors = {}) {
        const baseTheme = THEME_PRESETS[baseThemeId];
        if (!baseTheme) {
            console.error('Base theme not found:', baseThemeId);
            return null;
        }

        const customId = `custom-${Date.now()}`;
        const customTheme = {
            name: name,
            base: baseTheme.base,
            colors: { ...baseTheme.colors, ...customColors }
        };

        this.customThemes[customId] = customTheme;
        await this.saveThemes();
        return customId;
    }

    async updateCustomTheme(customId, updates) {
        if (!this.customThemes[customId]) {
            console.error('Custom theme not found:', customId);
            return;
        }

        if (updates.name) {
            this.customThemes[customId].name = updates.name;
        }

        if (updates.colors) {
            this.customThemes[customId].colors = {
                ...this.customThemes[customId].colors,
                ...updates.colors
            };
        }

        await this.saveThemes();

        // If this is the current theme, reapply it
        if (this.currentTheme === customId) {
            await this.applyTheme(customId, true);
        }
    }

    async deleteCustomTheme(customId) {
        if (!this.customThemes[customId]) {
            return;
        }

        delete this.customThemes[customId];
        await this.saveThemes();

        // If this was the current theme, switch to default
        if (this.currentTheme === customId) {
            await this.applyTheme('dark', false);
        }
    }

    getPresetThemes() {
        return THEME_PRESETS;
    }

    getCustomThemes() {
        return this.customThemes;
    }

    getAllThemes() {
        return { ...THEME_PRESETS, ...this.customThemes };
    }

    getLightThemes() {
        const themes = this.getAllThemes();
        return Object.entries(themes)
            .filter(([_, theme]) => theme.base === 'light')
            .reduce((acc, [id, theme]) => ({ ...acc, [id]: theme }), {});
    }

    getDarkThemes() {
        const themes = this.getAllThemes();
        return Object.entries(themes)
            .filter(([_, theme]) => theme.base === 'dark')
            .reduce((acc, [id, theme]) => ({ ...acc, [id]: theme }), {});
    }
}

// Create global instance
window.themeManager = new ThemeManager();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.themeManager.init();
    });
} else {
    window.themeManager.init();
}
