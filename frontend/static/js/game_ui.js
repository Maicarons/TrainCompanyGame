/**
 * 游戏UI模块
 * 负责处理游戏界面的交互和更新
 */

class GameUI {
    constructor() {
        this.gameState = {
            currentDate: new Date('1950-01-01'),
            timeScale: 1.0,
            paused: true,
            difficulty: 'normal',
            statistics: {}
        };
        
        // 初始化
        this.initialize();
    }
    
    /**
     * 初始化游戏UI
     */
    initialize() {
        // 注册WebSocket事件处理器
        if (typeof wsManager !== 'undefined') {
            wsManager.on('game_state_updated', this.handleGameStateUpdate.bind(this));
            wsManager.on('game_created', this.handleGameCreated.bind(this));
            wsManager.on('game_paused', this.handleGamePaused.bind(this));
            wsManager.on('game_resumed', this.handleGameResumed.bind(this));
            wsManager.on('save_game_result', this.handleSaveGameResult.bind(this));
            wsManager.on('load_game_result', this.handleLoadGameResult.bind(this));
            wsManager.on('economy_event', this.handleEconomyEvent.bind(this));
        }
        
        // 初始化游戏控制按钮
        this.initGameControls();
        
        // 初始化通知系统
        this.initNotificationSystem();
        
        // 更新UI
        this.updateUI();
    }
    
    /**
     * 初始化游戏控制按钮
     */
    initGameControls() {
        // 暂停按钮
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                if (!this.gameState.paused) {
                    wsManager.sendEvent('pause_game', {});
                }
            });
        }
        
        // 播放按钮
        const playBtn = document.getElementById('play-btn');
        if (playBtn) {
            playBtn.addEventListener('click', () => {
                if (this.gameState.paused) {
                    wsManager.sendEvent('resume_game', {});
                }
            });
        }
        
        // 快进按钮
        const fastForwardBtn = document.getElementById('fast-forward-btn');
        if (fastForwardBtn) {
            fastForwardBtn.addEventListener('click', () => {
                // 切换游戏速度
                const newTimeScale = this.gameState.timeScale >= 2.0 ? 1.0 : 2.0;
                
                wsManager.sendEvent('player_action', {
                    action_type: 'change_time_scale',
                    time_scale: newTimeScale
                });
            });
        }
    }
    
    /**
     * 初始化通知系统
     */
    initNotificationSystem() {
        // 创建通知容器
        const notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    /**
     * 处理游戏状态更新事件
     * @param {Object} data 游戏状态数据
     */
    handleGameStateUpdate(data) {
        // 更新游戏状态
        if (data.current_date) {
            this.gameState.currentDate = new Date(data.current_date);
        }
        
        if (data.time_scale !== undefined) {
            this.gameState.timeScale = data.time_scale;
        }
        
        if (data.paused !== undefined) {
            this.gameState.paused = data.paused;
        }
        
        if (data.difficulty) {
            this.gameState.difficulty = data.difficulty;
        }
        
        if (data.statistics) {
            this.gameState.statistics = data.statistics;
        }
        
        // 更新UI
        this.updateUI();
    }
    
    /**
     * 处理游戏创建事件
     * @param {Object} data 游戏创建数据
     */
    handleGameCreated(data) {
        // 更新游戏状态
        if (data.start_date) {
            this.gameState.currentDate = new Date(data.start_date);
        }
        
        if (data.difficulty) {
            this.gameState.difficulty = data.difficulty;
        }
        
        // 显示通知
        this.showNotification('游戏已创建', `已创建新游戏，开始日期: ${this.formatDate(this.gameState.currentDate)}`);
        
        // 更新UI
        this.updateUI();
    }
    
    /**
     * 处理游戏暂停事件
     * @param {Object} data 游戏暂停数据
     */
    handleGamePaused(data) {
        this.gameState.paused = true;
        this.updateUI();
        this.showNotification('游戏已暂停', '游戏时间已暂停');
    }
    
    /**
     * 处理游戏恢复事件
     * @param {Object} data 游戏恢复数据
     */
    handleGameResumed(data) {
        this.gameState.paused = false;
        this.updateUI();
        this.showNotification('游戏已恢复', '游戏时间继续流逝');
    }
    
    /**
     * 处理保存游戏结果事件
     * @param {Object} data 保存结果数据
     */
    handleSaveGameResult(data) {
        if (data.success) {
            this.showNotification('保存成功', `游戏已保存到 ${data.save_dir}`);
        } else {
            this.showNotification('保存失败', data.message || '保存游戏时发生错误', 'error');
        }
    }
    
    /**
     * 处理加载游戏结果事件
     * @param {Object} data 加载结果数据
     */
    handleLoadGameResult(data) {
        if (data.success) {
            this.showNotification('加载成功', `已加载游戏 ${data.save_dir}`);
        } else {
            this.showNotification('加载失败', data.message || '加载游戏时发生错误', 'error');
        }
    }
    
    /**
     * 处理经济事件
     * @param {Object} data 经济事件数据
     */
    handleEconomyEvent(data) {
        // 显示经济事件通知
        this.showNotification(data.title || '经济事件', data.description || '发生了一个经济事件', 'info');
        
        // TODO: 可以添加更多的经济事件处理逻辑，如显示详细信息、影响等
    }
    
    /**
     * 更新UI
     */
    updateUI() {
        // 更新游戏日期
        const gameDateElement = document.getElementById('game-date');
        if (gameDateElement) {
            gameDateElement.textContent = this.formatDate(this.gameState.currentDate);
        }
        
        // 更新难度
        const difficultyElement = document.getElementById('difficulty-level');
        if (difficultyElement) {
            difficultyElement.textContent = this.translateDifficulty(this.gameState.difficulty);
        }
        
        // 更新经济指数
        const economyIndexElement = document.getElementById('economy-index');
        if (economyIndexElement) {
            economyIndexElement.textContent = this.gameState.statistics.global_economy_index || 100;
        }
        
        // 更新暂停/播放按钮状态
        const pauseBtn = document.getElementById('pause-btn');
        const playBtn = document.getElementById('play-btn');
        
        if (pauseBtn && playBtn) {
            if (this.gameState.paused) {
                pauseBtn.classList.add('disabled');
                playBtn.classList.remove('disabled');
            } else {
                pauseBtn.classList.remove('disabled');
                playBtn.classList.add('disabled');
            }
        }
        
        // 更新快进按钮状态
        const fastForwardBtn = document.getElementById('fast-forward-btn');
        if (fastForwardBtn) {
            if (this.gameState.timeScale > 1.0) {
                fastForwardBtn.classList.add('active');
            } else {
                fastForwardBtn.classList.remove('active');
            }
        }
    }
    
    /**
     * 显示通知
     * @param {string} title 通知标题
     * @param {string} message 通知消息
     * @param {string} type 通知类型 (success, error, info)
     */
    showNotification(title, message, type = 'success') {
        const notificationContainer = document.querySelector('.notification-container');
        if (!notificationContainer) return;
        
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        `;
        
        // 添加到容器
        notificationContainer.appendChild(notification);
        
        // 显示通知
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // 3秒后隐藏通知
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    /**
     * 格式化日期
     * @param {Date} date 日期对象
     * @returns {string} 格式化后的日期字符串
     */
    formatDate(date) {
        if (!date) return 'N/A';
        
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    }
    
    /**
     * 翻译难度级别
     * @param {string} difficulty 难度级别
     * @returns {string} 翻译后的难度级别
     */
    translateDifficulty(difficulty) {
        const difficultyMap = {
            'easy': '简单',
            'normal': '普通',
            'hard': '困难'
        };
        return difficultyMap[difficulty] || difficulty;
    }
}

// 创建游戏UI实例
const gameUI = new GameUI();

// 导出游戏UI
window.gameUI = gameUI;