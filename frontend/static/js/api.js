class APIClient {
    constructor(baseUrl = null) {
        if (!baseUrl) {
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port || '8000';
            this.baseUrl = `${protocol}//${host}:${port}`;
        } else {
            this.baseUrl = baseUrl;
        }
        console.log('API Client initialized with baseUrl:', this.baseUrl);
    }

    async request(url, options = {}) {
        const fullUrl = this.baseUrl + url;
        console.log(`[API] ${options.method || 'GET'} ${fullUrl}`);

        try {
            const response = await fetch(fullUrl, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            console.log(`[API] Response status: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                const error = await response.json().catch(() => ({
                    detail: `HTTP ${response.status}: ${response.statusText}`
                }));
                console.error(`[API] Error response:`, error);
                throw new Error(error.detail || 'Request failed');
            }

            const data = await response.json();
            console.log(`[API] Response data:`, data);
            return data;
        } catch (error) {
            console.error(`[API] Request failed for ${fullUrl}:`, error);
            throw error;
        }
    }

    async getConnectionStatus() {
        return this.request('/api/connection');
    }

    async connect() {
        return this.request('/api/connection/connect', { method: 'POST' });
    }

    async disconnect() {
        return this.request('/api/connection/disconnect', { method: 'POST' });
    }

    async getModemInfo() {
        return this.request('/api/modem/');
    }

    async setModem(modemName) {
        return this.request('/api/modem/set', {
            method: 'POST',
            body: JSON.stringify({ modem_name: modemName })
        });
    }

    async setCarrier(frequency) {
        return this.request('/api/modem/carrier', {
            method: 'POST',
            body: JSON.stringify({ frequency })
        });
    }

    async getCarrier() {
        return this.request('/api/modem/carrier');
    }

    async setBandwidth(bandwidth) {
        return this.request('/api/modem/bandwidth', {
            method: 'POST',
            body: JSON.stringify({ bandwidth })
        });
    }

    async getBandwidth() {
        return this.request('/api/modem/bandwidth');
    }

    async getQuality() {
        return this.request('/api/modem/quality');
    }

    async getRsid() {
        return this.request('/api/modem/rsid');
    }

    async setRsid(enabled) {
        return this.request('/api/modem/rsid?enabled=' + enabled, {
            method: 'POST'
        });
    }

    async getTxid() {
        return this.request('/api/modem/txid');
    }

    async setTxid(enabled) {
        return this.request('/api/modem/txid?enabled=' + enabled, {
            method: 'POST'
        });
    }

    async getTxRxStatus() {
        return this.request('/api/txrx/status');
    }

    async startTx() {
        return this.request('/api/txrx/tx', { method: 'POST' });
    }

    async startRx() {
        return this.request('/api/txrx/rx', { method: 'POST' });
    }

    async startTune() {
        return this.request('/api/txrx/tune', { method: 'POST' });
    }

    async abort() {
        return this.request('/api/txrx/abort', { method: 'POST' });
    }

    async getRxText() {
        return this.request('/api/txrx/text/rx');
    }

    async sendTxText(text) {
        return this.request('/api/txrx/text/tx', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
    }

    async clearRx() {
        return this.request('/api/txrx/text/clear/rx', { method: 'POST' });
    }

    async clearTx() {
        return this.request('/api/txrx/text/clear/tx', { method: 'POST' });
    }

    async startLiveTx(text) {
        return this.request('/api/txrx/text/tx/live/start', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
    }

    async addTxCharsLive(text, startTx = true) {
        return this.request('/api/txrx/text/tx/live/add', {
            method: 'POST',
            body: JSON.stringify({ text, start_tx: startTx })
        });
    }

    async sendBackspaceLive(count = 1) {
        return this.request('/api/txrx/text/tx/live/backspace', {
            method: 'POST',
            body: JSON.stringify({ count })
        });
    }

    async endTxLive() {
        return this.request('/api/txrx/text/tx/live/end', {
            method: 'POST'
        });
    }

    async getRigInfo() {
        return this.request('/api/rig/');
    }

    async setRigFrequency(frequency) {
        return this.request('/api/rig/frequency', {
            method: 'POST',
            body: JSON.stringify({ frequency })
        });
    }

    async getRigFrequency() {
        return this.request('/api/rig/frequency');
    }

    async setRigMode(mode) {
        return this.request('/api/rig/mode', {
            method: 'POST',
            body: JSON.stringify({ mode })
        });
    }

    async getRigMode() {
        return this.request('/api/rig/mode');
    }

    async getFullStatus() {
        return this.request('/api/status');
    }

    async healthCheck() {
        return this.request('/health');
    }

    // Preset Frequencies
    async getPresets(modeFilter = null) {
        const url = modeFilter ? `/api/presets/?mode_filter=${modeFilter}` : '/api/presets/';
        return this.request(url);
    }

    async getDefaultPresets() {
        return this.request('/api/presets/defaults');
    }

    async getCustomPresets() {
        return this.request('/api/presets/custom');
    }

    async createPreset(presetData) {
        return this.request('/api/presets/', {
            method: 'POST',
            body: JSON.stringify(presetData)
        });
    }

    async deletePreset(presetId) {
        return this.request(`/api/presets/${presetId}`, {
            method: 'DELETE'
        });
    }

    async applyPreset(presetId) {
        return this.request(`/api/presets/${presetId}/apply`, {
            method: 'POST'
        });
    }
}

export const api = new APIClient();
