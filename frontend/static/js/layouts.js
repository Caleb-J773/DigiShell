/**
 * Layout system for DigiShell web interface
 */

export const LAYOUTS = {
    default: {
        name: 'Default',
        description: 'Standard layout with sidebar and main content',
        cssClass: 'layout-default'
    },
    compact: {
        name: 'Compact',
        description: 'Narrow sidebar, maximize RX/TX space',
        cssClass: 'layout-compact'
    },
    split: {
        name: 'Split Screen',
        description: 'RX and TX side-by-side',
        cssClass: 'layout-split'
    },
    minimal: {
        name: 'Minimal',
        description: 'Just essentials, maximum communication area',
        cssClass: 'layout-minimal'
    },
    widescreen: {
        name: 'Widescreen',
        description: '3-column layout for ultrawide monitors',
        cssClass: 'layout-widescreen'
    },
    focus: {
        name: 'Focus Mode',
        description: 'Distraction-free RX with quick-access controls',
        cssClass: 'layout-focus'
    },
    contest: {
        name: 'Contest',
        description: 'Fast operation with prominent macros',
        cssClass: 'layout-contest'
    },
    monitor: {
        name: 'Monitor',
        description: 'Large RX display for passive monitoring',
        cssClass: 'layout-monitor'
    },
    dashboard: {
        name: 'Dashboard',
        description: 'All-in-one overview grid',
        cssClass: 'layout-dashboard'
    },
    mobile: {
        name: 'Mobile',
        description: 'Optimized for phones and tablets',
        cssClass: 'layout-mobile'
    }
};

let currentLayout = 'default';

/**
 * Apply a layout
 */
export function applyLayout(layoutId) {
    if (!LAYOUTS[layoutId]) {
        console.error(`Unknown layout: ${layoutId}`);
        return false;
    }

    // Remove all layout classes
    const body = document.body;
    Object.values(LAYOUTS).forEach(layout => {
        body.classList.remove(layout.cssClass);
    });

    // Add new layout class
    body.classList.add(LAYOUTS[layoutId].cssClass);
    currentLayout = layoutId;

    // Save preference
    localStorage.setItem('preferred-layout', layoutId);

    console.log(`Applied layout: ${LAYOUTS[layoutId].name}`);
    return true;
}

/**
 * Get current layout
 */
export function getCurrentLayout() {
    return currentLayout;
}

/**
 * Load saved layout preference
 */
export function loadLayoutPreference() {
    const saved = localStorage.getItem('preferred-layout');
    if (saved && LAYOUTS[saved]) {
        applyLayout(saved);
    } else {
        // Auto-detect mobile
        if (window.innerWidth < 768) {
            applyLayout('mobile');
        } else {
            applyLayout('default');
        }
    }
}

/**
 * Initialize layout system
 */
export function initLayoutSystem() {
    // Load saved preference
    loadLayoutPreference();

    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            // Auto-switch to mobile on small screens if not explicitly set by user
            const savedLayout = localStorage.getItem('preferred-layout');
            if (!savedLayout && window.innerWidth < 768 && currentLayout !== 'mobile') {
                applyLayout('mobile');
            } else if (!savedLayout && window.innerWidth >= 768 && currentLayout === 'mobile') {
                applyLayout('default');
            }
        }, 250);
    });

    console.log('Layout system initialized');
}
