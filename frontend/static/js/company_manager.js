/**
 * 公司管理模块
 * 负责处理公司相关的前端逻辑
 */

class CompanyManager {
    constructor() {
        this.companies = [];
        this.playerCompany = null;
        this.aiCompanies = [];
        
        // 初始化
        this.initialize();
    }
    
    /**
     * 初始化公司管理器
     */
    initialize() {
        // 注册WebSocket事件处理器
        if (typeof wsManager !== 'undefined') {
            wsManager.on('company_info', this.handleCompanyInfo.bind(this));
            wsManager.on('company_created', this.handleCompanyCreated.bind(this));
            wsManager.on('company_updated', this.handleCompanyUpdated.bind(this));
            wsManager.on('company_list', this.handleCompanyList.bind(this));
        }
        
        // 初始化公司创建表单
        this.initCompanyForm();
    }
    
    /**
     * 初始化公司创建表单
     */
    initCompanyForm() {
        const createCompanyForm = document.getElementById('create-company-form');
        if (!createCompanyForm) return;
        
        createCompanyForm.addEventListener('submit', (event) => {
            event.preventDefault();
            
            const companyName = document.getElementById('company-name').value;
            const companyType = document.getElementById('company-type').value;
            const initialCash = parseInt(document.getElementById('initial-cash').value);
            
            this.createCompany(companyName, companyType, initialCash);
            
            // 关闭模态框
            document.getElementById('create-company-modal').style.display = 'none';
        });
    }
    
    /**
     * 创建公司
     * @param {string} name 公司名称
     * @param {string} companyType 公司类型
     * @param {number} initialCash 初始资金
     */
    createCompany(name, companyType, initialCash) {
        if (!wsManager || !wsManager.connected) {
            console.error('WebSocket未连接，无法创建公司');
            return;
        }
        
        // 发送创建公司事件
        wsManager.sendEvent('player_action', {
            action_type: 'create_company',
            name: name,
            company_type: companyType,
            player_id: wsManager.clientId,
            initial_cash: initialCash
        });
    }
    
    /**
     * 处理公司信息事件
     * @param {Object} data 公司信息数据
     */
    handleCompanyInfo(data) {
        // 更新公司信息
        const company = this.findOrCreateCompany(data.company_id);
        Object.assign(company, data);
        
        // 如果是玩家公司，更新玩家公司引用
        if (data.owner_id === wsManager.clientId) {
            this.playerCompany = company;
        }
        
        // 更新UI
        this.updateCompanyUI(company);
    }
    
    /**
     * 处理公司创建事件
     * @param {Object} data 公司创建数据
     */
    handleCompanyCreated(data) {
        // 请求获取公司详细信息
        if (wsManager && wsManager.connected) {
            wsManager.sendEvent('player_action', {
                action_type: 'get_company_info',
                company_id: data.company_id
            });
        }
    }
    
    /**
     * 处理公司更新事件
     * @param {Object} data 公司更新数据
     */
    handleCompanyUpdated(data) {
        // 请求获取公司详细信息
        if (wsManager && wsManager.connected) {
            wsManager.sendEvent('player_action', {
                action_type: 'get_company_info',
                company_id: data.company_id
            });
        }
    }
    
    /**
     * 处理公司列表事件
     * @param {Object} data 公司列表数据
     */
    handleCompanyList(data) {
        if (!data.companies || !Array.isArray(data.companies)) return;
        
        // 更新公司列表
        this.companies = data.companies.map(companyData => {
            const company = this.findOrCreateCompany(companyData.company_id);
            return Object.assign(company, companyData);
        });
        
        // 更新玩家公司和AI公司
        this.playerCompany = this.companies.find(company => company.owner_id === wsManager.clientId);
        this.aiCompanies = this.companies.filter(company => company.is_ai);
        
        // 更新UI
        this.updateCompaniesUI();
    }
    
    /**
     * 查找或创建公司
     * @param {string} companyId 公司ID
     * @returns {Object} 公司对象
     */
    findOrCreateCompany(companyId) {
        let company = this.companies.find(c => c.company_id === companyId);
        
        if (!company) {
            company = { company_id: companyId };
            this.companies.push(company);
        }
        
        return company;
    }
    
    /**
     * 更新公司UI
     * @param {Object} company 公司对象
     */
    updateCompanyUI(company) {
        // 如果是玩家公司，更新公司信息面板
        if (company.owner_id === wsManager.clientId) {
            const companyInfo = document.getElementById('company-info');
            if (!companyInfo) return;
            
            companyInfo.innerHTML = `
                <p>公司名称: ${company.name}</p>
                <p>公司类型: ${translateCompanyType(company.company_type)}</p>
                <p>成立日期: ${formatDate(company.founded_date) || '未知'}</p>
            `;
            
            // 更新财务信息
            document.getElementById('cash-value').textContent = formatMoney(company.cash);
            
            // 计算资产总值
            const assetsValue = company.assets ? company.assets.reduce((total, asset) => total + asset.value, 0) : 0;
            document.getElementById('assets-value').textContent = formatMoney(assetsValue);
            
            // 计算负债
            const debt = company.debt || 0;
            document.getElementById('debt-value').textContent = formatMoney(debt);
            
            // 计算净值
            const netWorth = company.cash + assetsValue - debt;
            document.getElementById('net-worth-value').textContent = formatMoney(netWorth);
        }
    }
    
    /**
     * 更新公司列表UI
     */
    updateCompaniesUI() {
        // TODO: 实现公司列表UI更新
        // 这里可以添加一个公司列表面板，显示所有公司的基本信息
    }
    
    /**
     * 获取公司信息
     * @param {string} companyId 公司ID
     */
    getCompanyInfo(companyId) {
        if (!wsManager || !wsManager.connected) {
            console.error('WebSocket未连接，无法获取公司信息');
            return;
        }
        
        wsManager.sendEvent('player_action', {
            action_type: 'get_company_info',
            company_id: companyId
        });
    }
    
    /**
     * 获取公司列表
     */
    getCompanyList() {
        if (!wsManager || !wsManager.connected) {
            console.error('WebSocket未连接，无法获取公司列表');
            return;
        }
        
        wsManager.sendEvent('player_action', {
            action_type: 'get_company_list'
        });
    }
}

// 创建公司管理器实例
const companyManager = new CompanyManager();

// 导出公司管理器
window.companyManager = companyManager;

// 辅助函数

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
 * 格式化日期
 * @param {string} dateString ISO日期字符串
 * @returns {string} 格式化后的日期字符串
 */
function formatDate(dateString) {
    if (!dateString) return null;
    
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