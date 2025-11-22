/**
 * FlDigi Waterfall Streaming Module
 *
 * Handles waterfall window streaming from FlDigi to the web interface.
 * This is a BETA feature and disabled by default.
 */

class WaterfallViewer {
    constructor() {
        this.websocket = null;
        this.canvas = document.getElementById('waterfall-canvas');
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.placeholder = document.getElementById('waterfall-placeholder');
        this.enableToggle = document.getElementById('waterfall-enable-toggle');
        this.settingsToggle = document.getElementById('waterfall-streaming-settings-toggle');
        this.waterfallPanel = document.getElementById('waterfall-panel');
        this.statusSpan = document.getElementById('waterfall-status');
        this.enabled = false;
        this.connected = false;
        this.lastFrameTime = 0;
        this.frameCount = 0;
        this.fpsDisplay = 0;

        this.setupEventListeners();
    }

    setupEventListeners() {
        // Toggle waterfall streaming on/off
        if (this.enableToggle) {
            this.enableToggle.addEventListener('change', async (e) => {
                if (e.target.checked) {
                    await this.enable();
                } else {
                    await this.disable();
                }
            });
        }

        // Settings toggle (in settings modal)
        if (this.settingsToggle) {
            this.settingsToggle.addEventListener('change', async (e) => {
                window.webConfig.waterfallStreamingEnabled = e.target.checked;
                await window.saveWebConfig();
                this.applySettings();
            });
        }

        // Handle canvas clicks to send to FlDigi (future feature)
        if (this.canvas) {
            this.canvas.addEventListener('click', (e) => {
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    const rect = this.canvas.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    // Send click coordinates to backend
                    this.websocket.send(JSON.stringify({
                        type: 'mouse_click',
                        x: x,
                        y: y,
                        canvasWidth: this.canvas.width,
                        canvasHeight: this.canvas.height
                    }));
                }
            });
        }
    }

    applySettings() {
        // Show/hide waterfall panel based on settings
        const showWaterfall = window.webConfig.waterfallStreamingEnabled === true;

        if (this.waterfallPanel) {
            this.waterfallPanel.style.display = showWaterfall ? '' : 'none';
        }

        // Sync settings toggle with config
        if (this.settingsToggle) {
            this.settingsToggle.checked = showWaterfall;
        }

        // Disable waterfall if it was enabled but setting is now off
        if (!showWaterfall && this.enabled) {
            this.enableToggle.checked = false;
            this.disable();
        }
    }

    async checkStatus() {
        try {
            const response = await fetch('/api/waterfall/status');
            if (response.ok) {
                const status = await response.json();
                return status;
            }
        } catch (e) {
            console.error('Failed to check waterfall status:', e);
        }
        return null;
    }

    async enable() {
        try {
            this.updateStatus('Enabling...');

            // Enable the backend service
            const response = await fetch('/api/waterfall/enable', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: true })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to enable waterfall streaming');
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Failed to enable waterfall streaming');
            }

            // Connect WebSocket
            this.connectWebSocket();
            this.enabled = true;
            this.updateStatus('Connecting...');

        } catch (error) {
            console.error('Error enabling waterfall:', error);
            this.enableToggle.checked = false;
            this.updateStatus('Error: ' + error.message);
            window.showToast(error.message, 'error');
        }
    }

    async disable() {
        try {
            this.updateStatus('Disabling...');

            // Disconnect WebSocket
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }

            // Disable the backend service
            const response = await fetch('/api/waterfall/enable', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: false })
            });

            if (!response.ok) {
                console.error('Failed to disable waterfall streaming');
            }

            this.enabled = false;
            this.connected = false;
            this.hideCanvas();
            this.updateStatus('Disabled');

        } catch (error) {
            console.error('Error disabling waterfall:', error);
            this.updateStatus('Error');
        }
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/api/waterfall/ws`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
            console.log('Waterfall WebSocket connected');
            this.connected = true;
            this.updateStatus('Streaming');
        };

        this.websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.type === 'waterfall_frame') {
                    this.renderFrame(data.image);
                }
            } catch (e) {
                console.error('Error processing waterfall frame:', e);
            }
        };

        this.websocket.onerror = (error) => {
            console.error('Waterfall WebSocket error:', error);
            this.updateStatus('Connection Error');
        };

        this.websocket.onclose = () => {
            console.log('Waterfall WebSocket closed');
            this.connected = false;

            if (this.enabled) {
                this.updateStatus('Disconnected - Retrying...');
                // Try to reconnect after 3 seconds
                setTimeout(() => {
                    if (this.enabled) {
                        this.connectWebSocket();
                    }
                }, 3000);
            } else {
                this.updateStatus('Disabled');
            }
        };
    }

    renderFrame(base64Image) {
        if (!this.canvas || !this.ctx) return;

        const img = new Image();
        img.onload = () => {
            // Set canvas size to match image on first frame
            if (this.canvas.width !== img.width || this.canvas.height !== img.height) {
                this.canvas.width = img.width;
                this.canvas.height = img.height;
            }

            // Draw the image
            this.ctx.drawImage(img, 0, 0);

            // Show canvas, hide placeholder
            this.showCanvas();

            // Update FPS counter
            this.updateFPS();
        };
        img.src = 'data:image/jpeg;base64,' + base64Image;
    }

    showCanvas() {
        if (this.canvas && this.placeholder) {
            this.canvas.style.display = 'block';
            this.placeholder.style.display = 'none';
        }
    }

    hideCanvas() {
        if (this.canvas && this.placeholder) {
            this.canvas.style.display = 'none';
            this.placeholder.style.display = 'flex';
        }
    }

    updateStatus(status) {
        if (this.statusSpan) {
            this.statusSpan.textContent = status;
        }
    }

    updateFPS() {
        const now = performance.now();
        if (this.lastFrameTime) {
            this.frameCount++;
            const elapsed = (now - this.lastFrameTime) / 1000;

            // Update FPS every second
            if (elapsed >= 1.0) {
                this.fpsDisplay = Math.round(this.frameCount / elapsed);
                this.frameCount = 0;
                this.lastFrameTime = now;

                // Update status with FPS
                if (this.connected && this.enabled) {
                    this.updateStatus(`Streaming (${this.fpsDisplay} fps)`);
                }
            }
        } else {
            this.lastFrameTime = now;
        }
    }
}

// Initialize waterfall viewer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.waterfallViewer = new WaterfallViewer();

    // Apply settings after initialization if config is already loaded
    if (window._applyWaterfallSettingsOnReady || (window.webConfig && window.webConfig.waterfallStreamingEnabled)) {
        window.waterfallViewer.applySettings();
        window._applyWaterfallSettingsOnReady = false;
    }
});
