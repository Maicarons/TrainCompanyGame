/**
 * WebSocket连接管理模块
 * 负责与后端WebSocket服务建立连接并处理消息
 */

class WebSocketManager {
    constructor() {
        this.socket = null;
        this.clientId = this._generateClientId();
        this.connected = false;
        this.eventHandlers = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3秒
    }

    /**
     * 生成客户端ID
     * @returns {string} 客户端ID
     */
    _generateClientId() {
        return 'client_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * 连接到WebSocket服务器
     */
    connect() {
        if (this.socket && this.connected) {
            console.log('WebSocket已连接');
            return;
        }

        // 获取当前主机和端口
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:8000';
        const wsUrl = `${protocol}//${host}/ws/${this.clientId}`;

        console.log(`正在连接到WebSocket服务器: ${wsUrl}`);
        this.socket = new WebSocket(wsUrl);

        // 设置事件处理器
        this.socket.onopen = this._onOpen.bind(this);
        this.socket.onmessage = this._onMessage.bind(this);
        this.socket.onclose = this._onClose.bind(this);
        this.socket.onerror = this._onError.bind(this);
    }

    /**
     * 断开WebSocket连接
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
            this.connected = false;
        }
    }

    /**
     * 发送事件到服务器
     * @param {string} eventType 事件类型
     * @param {Object} data 事件数据
     * @param {Array<string>} targetClients 目标客户端ID列表
     */
    sendEvent(eventType, data, targetClients = null) {
        if (!this.connected) {
            console.error('WebSocket未连接，无法发送事件');
            return false;
        }

        const event = {
            event_type: eventType,
            data: data
        };

        if (targetClients) {
            event.target_clients = targetClients;
        }

        try {
            this.socket.send(JSON.stringify(event));
            return true;
        } catch (error) {
            console.error('发送事件失败:', error);
            return false;
        }
    }

    /**
     * 注册事件处理器
     * @param {string} eventType 事件类型
     * @param {Function} handler 处理函数
     */
    on(eventType, handler) {
        if (!this.eventHandlers[eventType]) {
            this.eventHandlers[eventType] = [];
        }
        this.eventHandlers[eventType].push(handler);
    }

    /**
     * 移除事件处理器
     * @param {string} eventType 事件类型
     * @param {Function} handler 处理函数
     */
    off(eventType, handler) {
        if (!this.eventHandlers[eventType]) {
            return;
        }

        if (handler) {
            // 移除特定处理器
            this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(h => h !== handler);
        } else {
            // 移除所有该类型的处理器
            delete this.eventHandlers[eventType];
        }
    }

    /**
     * WebSocket连接打开事件处理
     * @param {Event} event 事件对象
     */
    _onOpen(event) {
        console.log('WebSocket连接已建立');
        this.connected = true;
        this.reconnectAttempts = 0;

        // 触发连接事件
        this._triggerEvent('connection_established', { clientId: this.clientId });
    }

    /**
     * WebSocket消息接收事件处理
     * @param {MessageEvent} event 消息事件
     */
    _onMessage(event) {
        try {
            const message = JSON.parse(event.data);
            if (message.event_type && message.data) {
                // 触发对应类型的事件
                this._triggerEvent(message.event_type, message.data);
            }
        } catch (error) {
            console.error('解析WebSocket消息失败:', error);
        }
    }

    /**
     * WebSocket连接关闭事件处理
     * @param {CloseEvent} event 关闭事件
     */
    _onClose(event) {
        console.log(`WebSocket连接已关闭: ${event.code} ${event.reason}`);
        this.connected = false;

        // 触发断开连接事件
        this._triggerEvent('connection_closed', { code: event.code, reason: event.reason });

        // 尝试重新连接
        this._attemptReconnect();
    }

    /**
     * WebSocket错误事件处理
     * @param {Event} event 错误事件
     */
    _onError(event) {
        console.error('WebSocket错误:', event);
        // 触发错误事件
        this._triggerEvent('connection_error', { error: 'WebSocket连接错误' });
    }

    /**
     * 尝试重新连接
     */
    _attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error(`已达到最大重连次数(${this.maxReconnectAttempts})，停止重连`);
            this._triggerEvent('reconnect_failed', { attempts: this.reconnectAttempts });
            return;
        }

        this.reconnectAttempts++;
        console.log(`尝试重新连接(${this.reconnectAttempts}/${this.maxReconnectAttempts})，${this.reconnectDelay}ms后重试...`);

        setTimeout(() => {
            console.log('正在重新连接...');
            this.connect();
        }, this.reconnectDelay);

        // 每次重连增加延迟时间
        this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000); // 最大30秒
    }

    /**
     * 触发事件处理器
     * @param {string} eventType 事件类型
     * @param {Object} data 事件数据
     */
    _triggerEvent(eventType, data) {
        // 触发特定类型的事件处理器
        if (this.eventHandlers[eventType]) {
            this.eventHandlers[eventType].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`执行事件处理器(${eventType})时出错:`, error);
                }
            });
        }

        // 触发通用事件处理器
        if (this.eventHandlers['*']) {
            this.eventHandlers['*'].forEach(handler => {
                try {
                    handler(eventType, data);
                } catch (error) {
                    console.error(`执行通用事件处理器时出错:`, error);
                }
            });
        }
    }
}

// 创建全局WebSocket管理器实例
const wsManager = new WebSocketManager();