export class WebSocketClient {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 1000;
        this.maxReconnectInterval = 30000;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.isConnecting = false;
        this.handlers = {
            status_update: [],
            text_update: [],
            connection_status: [],
            error: []
        };
    }

    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            return;
        }

        this.isConnecting = true;

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const port = window.location.port || '8000';
        const wsUrl = `${protocol}//${host}:${port}/ws`;

        console.log('[WebSocket] Location details:');
        console.log('  - protocol:', window.location.protocol);
        console.log('  - hostname:', window.location.hostname);
        console.log('  - port:', window.location.port);
        console.log('  - computed wsUrl:', wsUrl);

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.reconnectInterval = 1000;
                this.clearReconnectTimer();
            };

            this.ws.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnecting = false;
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnecting = false;
                this.scheduleReconnect();
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }

    disconnect() {
        this.clearReconnectTimer();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            console.log('WebSocket message:', message);

            const { type, data: messageData } = message;

            if (this.handlers[type]) {
                this.handlers[type].forEach(handler => {
                    try {
                        handler(messageData);
                    } catch (error) {
                        console.error(`Error in handler for ${type}:`, error);
                    }
                });
            }

        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }

    on(type, handler) {
        if (!this.handlers[type]) {
            this.handlers[type] = [];
        }
        this.handlers[type].push(handler);
    }

    off(type, handler) {
        if (this.handlers[type]) {
            this.handlers[type] = this.handlers[type].filter(h => h !== handler);
        }
    }

    scheduleReconnect() {
        this.clearReconnectTimer();

        const interval = Math.min(
            this.reconnectInterval * Math.pow(2, this.reconnectAttempts),
            this.maxReconnectInterval
        );

        console.log(`Reconnecting in ${interval}ms (attempt ${this.reconnectAttempts + 1})...`);

        this.reconnectTimer = setTimeout(() => {
            this.reconnectAttempts++;
            console.log('Attempting to reconnect WebSocket...');
            this.connect();
        }, interval);
    }

    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

export const wsClient = new WebSocketClient();
