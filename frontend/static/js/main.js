/**
 * 铁路大亨模拟器主脚本
 * 负责初始化游戏界面和WebSocket连接
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', () => {
    console.log('铁路大亨模拟器初始化中...');
    
    // 初始化UI组件
    initUI();
    
    // 连接WebSocket服务器
    wsManager.connect();
    
    // 注册WebSocket事件处理器
    registerWebSocketHandlers();
});

/**
 * 初始化UI组件
 */
function initUI() {
    // 初始化模态框
    initModals();
    
    // 初始化游戏控制按钮
    initGameControls();
    
    // 初始化公司创建表单
    initCompanyForm();
    
    // 初始化新游戏表单
    initNewGameForm();
}

/**
 * 初始化模态框
 */
function initModals() {
    // 获取所有模态框和关闭按钮
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close');
    
    // 点击关闭按钮关闭模态框
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            modals.forEach(modal => {
                modal.style.display = 'none';
            });
        });
    });
    
    // 点击模态框外部关闭模态框
    window.addEventListener('click', (event) => {
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // 创建公司按钮
    const createCompanyBtn = document.getElementById('create-company-btn');
    createCompanyBtn.addEventListener('click', () => {
        document.getElementById('create-company-modal').style.display = 'block';
    });
    
    // 新游戏按钮
    const newGameBtn = document.getElementById('new-game-btn');
    newGameBtn.addEventListener('click', () => {
        document.getElementById('new-game-modal').style.display = 'block';
    });
}

/**
 * 初始化游戏控制按钮
 */
function initGameControls() {
    // 暂停按钮
    const pauseBtn = document.getElementById('pause-btn');
    pauseBtn.addEventListener('click', () => {
        wsManager.sendEvent('pause_game', {});
    });
    
    // 播放按钮
    const playBtn = document.getElementById('play-btn');
    playBtn.addEventListener('click', () => {
        wsManager.sendEvent('resume_game', {});
    });
    
    // 快进按钮
    const fastForwardBtn = document.getElementById('fast-forward-btn');
    fastForwardBtn.addEventListener('click', () => {
        // 发送增加游戏速度事件
        wsManager.sendEvent('player_action', {
            action_type: 'change_time_scale',
            time_scale: 2.0 // 2倍速
        });
    });
    
    // 保存游戏按钮
    const saveGameBtn = document.getElementById('save-game-btn');
    saveGameBtn.addEventListener('click', () => {
        const saveDir = prompt('请输入保存目录:', 'saves/game1');
        if (saveDir) {
            wsManager.sendEvent('save_game', { save_dir: saveDir });
        }
    });
    
    // 加载游戏按钮
    const loadGameBtn = document.getElementById('load-game-btn');
    loadGameBtn.addEventListener('click', () => {
        const saveDir = prompt('请输入保存目录:', 'saves/game1');
        if (saveDir) {
            wsManager.sendEvent('load_game', { save_dir: saveDir });
        }
    });
}

/**
 * 初始化公司创建表单
 */
function initCompanyForm() {
    const createCompanyForm = document.getElementById('create-company-form');
    createCompanyForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const companyName = document.getElementById('company-name').value;
        const companyType = document.getElementById('company-type').value;
        const initialCash = parseInt(document.getElementById('initial-cash').value);
        
        // 发送创建公司事件
        wsManager.sendEvent('player_action', {
            action_type: 'create_company',
            name: companyName,
            company_type: companyType,
            player_id: wsManager.clientId,
            initial_cash: initialCash
        });
        
        // 关闭模态框
        document.getElementById('create-company-modal').style.display = 'none';
    });
}

/**
 * 初始化新游戏表单
 */
function initNewGameForm() {
    const newGameForm = document.getElementById('new-game-form');
    newGameForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const worldWidth = parseInt(document.getElementById('world-width').value);
        const worldHeight = parseInt(document.getElementById('world-height').value);
        const numCities = parseInt(document.getElementById('num-cities').value);
        const difficulty = document.getElementById('difficulty').value;
        
        // 发送开始游戏事件
        wsManager.sendEvent('start_game', {
            world_width: worldWidth,
            world_height: worldHeight,
            num_cities: numCities,
            difficulty: difficulty
        });
        
        // 关闭模态框
        document.getElementById('new-game-modal').style.display = 'none';
    });
}

/**
 * 注册WebSocket事件处理器
 */
function registerWebSocketHandlers() {
    // 连接建立事件
    wsManager.on('connection_established', (data) => {
        console.log('WebSocket连接已建立:', data);
        showNotification('连接成功', '已连接到游戏服务器');
    });
    
    // 连接关闭事件
    wsManager.on('connection_closed', (data) => {
        console.log('WebSocket连接已关闭:', data);
        showNotification('连接断开', '与游戏服务器的连接已断开', 'error');
    });
    
    // 游戏状态更新事件
    wsManager.on('game_state_updated', (data) => {
        updateGameState(data);
    });
    
    // 公司信息事件
    wsManager.on('company_info', (data) => {
        updateCompanyInfo(data);
    });
    
    // 市场数据事件
    wsManager.on('market_data', (data) => {
        updateMarketInfo(data);
    });
    
    // 游戏创建事件
    wsManager.on('game_created', (data) => {
        console.log('游戏已创建:', data);
        showNotification('游戏已创建', `已创建新游戏，开始日期: ${formatDate(data.start_date)}`);
    });
    
    // 操作结果事件
    wsManager.on('action_result', (data) => {
        handleActionResult(data);
    });
    
    // 错误事件
    wsManager.on('error', (data) => {
        console.error('收到错误事件:', data);
        showNotification('错误', data.message, 'error');
    });
}

/**
 * 更新游戏状态
 * @param {Object} data 游戏状态数据
 */
function updateGameState(data) {
    // 更新游戏日期
    const gameDate = document.getElementById('game-date');
    gameDate.textContent = formatDate(data.current_date);
    
    // 更新难度
    const difficultyLevel = document.getElementById('difficulty-level');
    difficultyLevel.textContent = translateDifficulty(data.difficulty || 'normal');
    
    // 更新经济指数
    const economyIndex = document.getElementById('economy-index');
    economyIndex.textContent = data.statistics?.global_economy_index || 100;
    
    // 更新其他统计数据
    // TODO: 添加更多统计数据的更新
}

/**
 * 更新公司信息
 * @param {Object} data 公司信息数据
 */
function updateCompanyInfo(data) {
    const companyInfo = document.getElementById('company-info');
    companyInfo.innerHTML = `
        <p>公司名称: ${data.name}</p>
        <p>公司类型: ${translateCompanyType(data.company_type)}</p>
        <p>拥有者: ${data.owner_id}</p>
    `;
    
    // 更新财务信息
    document.getElementById('cash-value').textContent = formatMoney(data.cash);
    
    // 计算资产总值
    const assetsValue = data.assets.reduce((total, asset) => total + asset.value, 0);
    document.getElementById('assets-value').textContent = formatMoney(assetsValue);
    
    // TODO: 添加负债信息
    document.getElementById('debt-value').textContent = formatMoney(0);
    
    // 计算净值
    const netWorth = data.cash + assetsValue;
    document.getElementById('net-worth-value').textContent = formatMoney(netWorth);
}

/**
 * 更新市场信息
 * @param {Object} data 市场数据
 */
function updateMarketInfo(data) {
    const marketInfo = document.getElementById('market-info');
    
    if (!data.markets || data.markets.length === 0) {
        marketInfo.innerHTML = '<p>暂无市场数据</p>';
        return;
    }
    
    // 显示第一个市场的信息
    const market = data.markets[0];
    let html = `<p>市场: ${market.name}</p><ul>`;
    
    market.resources.forEach(resource => {
        html += `<li>${translateResourceType(resource.resource_type)}: ${formatMoney(resource.price)}</li>`;
    });
    
    html += '</ul>';
    marketInfo.innerHTML = html;
}

/**
 * 处理操作结果
 * @param {Object} data 操作结果数据
 */
function handleActionResult(data) {
    if (data.success) {
        showNotification('操作成功', `${translateActionType(data.action_type)}操作已成功执行`);
    } else {
        showNotification('操作失败', data.message || `${translateActionType(data.action_type)}操作失败`, 'error');
    }
}

/**
 * 显示通知
 * @param {string} title 通知标题
 * @param {string} message 通知消息
 * @param {string} type 通知类型 (success, error, info)
 */
function showNotification(title, message, type = 'success') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-title">${title}</div>
        <div class="notification-message">${message}</div>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
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
 * @param {string} dateString ISO日期字符串
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * 格式化金额
 * @param {number} amount 金额
 * @returns {string} 格式化后的金额字符串
 */
function formatMoney(amount) {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * 翻译难度级别
 * @param {string} difficulty 难度级别
 * @returns {string} 翻译后的难度级别
 */
function translateDifficulty(difficulty) {
    const difficultyMap = {
        'easy': '简单',
        'normal': '普通',
        'hard': '困难'
    };
    return difficultyMap[difficulty] || difficulty;
}

/**
 * 翻译公司类型
 * @param {string} companyType 公司类型
 * @returns {string} 翻译后的公司类型
 */
function translateCompanyType(companyType) {
    const companyTypeMap = {
        'RAILWAY': '铁路公司'
    };
    return companyTypeMap[companyType] || companyType;
}

/**
 * 翻译资源类型
 * @param {string} resourceType 资源类型
 * @returns {string} 翻译后的资源类型
 */
function translateResourceType(resourceType) {
    const resourceTypeMap = {
        'COAL': '煤炭',
        'IRON': '铁矿',
        'WOOD': '木材',
        'STEEL': '钢铁',
        'OIL': '石油',
        'PASSENGER': '乘客',
        'MAIL': '邮件',
        'GOODS': '货物'
    };
    return resourceTypeMap[resourceType] || resourceType;
}

/**
 * 翻译操作类型
 * @param {string} actionType 操作类型
 * @returns {string} 翻译后的操作类型
 */
function translateActionType(actionType) {
    const actionTypeMap = {
        'create_company': '创建公司',
        'change_time_scale': '改变时间速度'
    };
    return actionTypeMap[actionType] || actionType;
}