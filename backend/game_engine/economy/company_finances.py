# 公司财务模块

import numpy as np
from datetime import datetime, timedelta
from enum import Enum, auto

class TransactionType(Enum):
    """交易类型枚举"""
    INCOME = auto()         # 收入
    EXPENSE = auto()        # 支出
    INVESTMENT = auto()     # 投资
    LOAN = auto()           # 贷款
    INTEREST = auto()       # 利息
    TAX = auto()            # 税收
    DEPRECIATION = auto()   # 折旧
    MAINTENANCE = auto()    # 维护费用

class FinancialReport:
    """财务报表类，用于生成公司财务报告"""
    
    def __init__(self, company_finances, start_date, end_date):
        """初始化财务报表
        
        Args:
            company_finances (CompanyFinances): 公司财务对象
            start_date (datetime): 报表开始日期
            end_date (datetime): 报表结束日期
        """
        self.company_finances = company_finances
        self.start_date = start_date
        self.end_date = end_date
        self.report_data = self._generate_report()
    
    def _generate_report(self):
        """生成财务报表数据
        
        Returns:
            dict: 财务报表数据
        """
        # 筛选时间范围内的交易记录
        transactions = [t for t in self.company_finances.transaction_history 
                       if self.start_date <= t['timestamp'] <= self.end_date]
        
        # 计算总收入
        total_income = sum(t['amount'] for t in transactions 
                          if t['type'] == TransactionType.INCOME)
        
        # 计算总支出
        total_expenses = sum(t['amount'] for t in transactions 
                            if t['type'] == TransactionType.EXPENSE)
        
        # 计算各类支出
        maintenance_cost = sum(t['amount'] for t in transactions 
                              if t['type'] == TransactionType.MAINTENANCE)
        
        interest_paid = sum(t['amount'] for t in transactions 
                           if t['type'] == TransactionType.INTEREST)
        
        taxes_paid = sum(t['amount'] for t in transactions 
                        if t['type'] == TransactionType.TAX)
        
        depreciation = sum(t['amount'] for t in transactions 
                          if t['type'] == TransactionType.DEPRECIATION)
        
        # 计算净利润
        net_profit = total_income - total_expenses
        
        # 计算资产负债情况
        current_assets = self.company_finances.cash
        fixed_assets = self.company_finances.assets_value
        total_assets = current_assets + fixed_assets
        
        total_liabilities = self.company_finances.loans
        equity = total_assets - total_liabilities
        
        # 计算财务比率
        debt_ratio = total_liabilities / total_assets if total_assets > 0 else 0
        profit_margin = net_profit / total_income if total_income > 0 else 0
        
        return {
            'company_id': self.company_finances.company_id,
            'company_name': self.company_finances.company_name,
            'report_period': f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}",
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'expense_breakdown': {
                'maintenance': maintenance_cost,
                'interest': interest_paid,
                'taxes': taxes_paid,
                'depreciation': depreciation,
                'other': total_expenses - maintenance_cost - interest_paid - taxes_paid - depreciation
            },
            'balance_sheet': {
                'assets': {
                    'current_assets': current_assets,
                    'fixed_assets': fixed_assets,
                    'total_assets': total_assets
                },
                'liabilities_and_equity': {
                    'total_liabilities': total_liabilities,
                    'equity': equity,
                    'total': total_liabilities + equity
                }
            },
            'financial_ratios': {
                'debt_ratio': debt_ratio,
                'profit_margin': profit_margin,
                'return_on_assets': net_profit / total_assets if total_assets > 0 else 0,
                'current_ratio': current_assets / total_liabilities if total_liabilities > 0 else float('inf')
            },
            'transaction_count': len(transactions)
        }
    
    def get_summary(self):
        """获取财务报表摘要
        
        Returns:
            dict: 财务报表摘要
        """
        return {
            'company_name': self.report_data['company_name'],
            'period': self.report_data['report_period'],
            'total_income': self.report_data['total_income'],
            'total_expenses': self.report_data['total_expenses'],
            'net_profit': self.report_data['net_profit'],
            'total_assets': self.report_data['balance_sheet']['assets']['total_assets'],
            'total_liabilities': self.report_data['balance_sheet']['liabilities_and_equity']['total_liabilities'],
            'equity': self.report_data['balance_sheet']['liabilities_and_equity']['equity']
        }
    
    def to_dict(self):
        """将财务报表转换为字典
        
        Returns:
            dict: 财务报表数据
        """
        return self.report_data

class CompanyFinances:
    """公司财务类，管理公司的财务状况"""
    
    def __init__(self, company_id, company_name, initial_cash=1000000, initial_loan=0, seed=None):
        """初始化公司财务
        
        Args:
            company_id: 公司ID
            company_name (str): 公司名称
            initial_cash (float): 初始现金
            initial_loan (float): 初始贷款
            seed (int, optional): 随机种子
        """
        self.company_id = company_id
        self.company_name = company_name
        self.cash = initial_cash
        self.loans = initial_loan
        self.assets_value = 0  # 固定资产价值
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # 财务参数
        self.tax_rate = 0.25  # 税率
        self.interest_rate = 0.05  # 贷款利率
        self.depreciation_rate = 0.1  # 资产折旧率
        
        # 交易历史
        self.transaction_history = []
        
        # 记录初始资金作为交易
        if initial_cash > 0:
            self.record_transaction(
                amount=initial_cash,
                transaction_type=TransactionType.INVESTMENT,
                description="初始资金",
                timestamp=datetime.now()
            )
        
        if initial_loan > 0:
            self.record_transaction(
                amount=initial_loan,
                transaction_type=TransactionType.LOAN,
                description="初始贷款",
                timestamp=datetime.now()
            )
    
    def record_transaction(self, amount, transaction_type, description="", related_entity=None, timestamp=None):
        """记录交易
        
        Args:
            amount (float): 交易金额
            transaction_type (TransactionType): 交易类型
            description (str, optional): 交易描述
            related_entity: 相关实体（如城市、路线等）
            timestamp (datetime, optional): 交易时间戳
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        transaction = {
            'amount': amount,
            'type': transaction_type,
            'description': description,
            'related_entity': related_entity,
            'timestamp': timestamp,
            'balance_after': self.cash
        }
        
        self.transaction_history.append(transaction)
        
        # 限制历史记录长度
        if len(self.transaction_history) > 10000:
            self.transaction_history = self.transaction_history[-10000:]
    
    def add_income(self, amount, description="", related_entity=None):
        """添加收入
        
        Args:
            amount (float): 收入金额
            description (str, optional): 收入描述
            related_entity: 相关实体
            
        Returns:
            bool: 是否成功
        """
        if amount <= 0:
            return False
        
        self.cash += amount
        self.record_transaction(amount, TransactionType.INCOME, description, related_entity)
        return True
    
    def add_expense(self, amount, description="", related_entity=None):
        """添加支出
        
        Args:
            amount (float): 支出金额
            description (str, optional): 支出描述
            related_entity: 相关实体
            
        Returns:
            bool: 是否成功
        """
        if amount <= 0 or amount > self.cash:
            return False
        
        self.cash -= amount
        self.record_transaction(amount, TransactionType.EXPENSE, description, related_entity)
        return True
    
    def add_asset(self, value, description="", related_entity=None):
        """添加资产
        
        Args:
            value (float): 资产价值
            description (str, optional): 资产描述
            related_entity: 相关实体
            
        Returns:
            bool: 是否成功
        """
        if value <= 0 or value > self.cash:
            return False
        
        self.cash -= value
        self.assets_value += value
        self.record_transaction(value, TransactionType.EXPENSE, f"购买资产: {description}", related_entity)
        return True
    
    def take_loan(self, amount, description=""):
        """获取贷款
        
        Args:
            amount (float): 贷款金额
            description (str, optional): 贷款描述
            
        Returns:
            bool: 是否成功
        """
        if amount <= 0:
            return False
        
        # 检查贷款上限（基于资产价值和现有贷款）
        max_loan = (self.assets_value * 0.7) - self.loans
        if amount > max_loan and max_loan > 0:
            return False
        
        self.cash += amount
        self.loans += amount
        self.record_transaction(amount, TransactionType.LOAN, description)
        return True
    
    def repay_loan(self, amount, description=""):
        """偿还贷款
        
        Args:
            amount (float): 偿还金额
            description (str, optional): 偿还描述
            
        Returns:
            bool: 是否成功
        """
        if amount <= 0 or amount > self.cash or amount > self.loans:
            return False
        
        self.cash -= amount
        self.loans -= amount
        self.record_transaction(amount, TransactionType.EXPENSE, f"偿还贷款: {description}")
        return True
    
    def update_finances(self, time_delta, economy_manager=None):
        """更新财务状况
        
        Args:
            time_delta: 时间增量（秒）
            economy_manager: 经济管理器实例，用于获取经济指标
            
        Returns:
            dict: 更新结果
        """
        # 计算时间因子（转换为年）
        time_factor = time_delta / (365 * 24 * 3600)
        
        # 获取当前利率（如果有经济管理器）
        current_interest_rate = self.interest_rate
        if economy_manager:
            current_interest_rate = economy_manager.interest_rate
        
        # 计算利息
        if self.loans > 0:
            interest_amount = self.loans * current_interest_rate * time_factor
            if interest_amount > 0 and self.cash >= interest_amount:
                self.cash -= interest_amount
                self.record_transaction(
                    amount=interest_amount,
                    transaction_type=TransactionType.INTEREST,
                    description="贷款利息"
                )
            else:
                # 如果现金不足以支付利息，将利息加入贷款本金
                self.loans += interest_amount
                self.record_transaction(
                    amount=interest_amount,
                    transaction_type=TransactionType.INTEREST,
                    description="贷款利息（资本化）"
                )
        
        # 计算资产折旧
        if self.assets_value > 0:
            depreciation_amount = self.assets_value * self.depreciation_rate * time_factor
            self.assets_value -= depreciation_amount
            self.record_transaction(
                amount=depreciation_amount,
                transaction_type=TransactionType.DEPRECIATION,
                description="资产折旧"
            )
        
        return {
            'cash': self.cash,
            'loans': self.loans,
            'assets_value': self.assets_value,
            'net_worth': self.cash + self.assets_value - self.loans
        }
    
    def generate_financial_report(self, period_days=30):
        """生成财务报表
        
        Args:
            period_days (int): 报表周期（天数）
            
        Returns:
            FinancialReport: 财务报表对象
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        return FinancialReport(self, start_date, end_date)
    
    def get_financial_status(self):
        """获取财务状况摘要
        
        Returns:
            dict: 财务状况数据
        """
        return {
            'company_id': self.company_id,
            'company_name': self.company_name,
            'cash': self.cash,
            'assets_value': self.assets_value,
            'loans': self.loans,
            'net_worth': self.cash + self.assets_value - self.loans,
            'transaction_count': len(self.transaction_history),
            'last_transaction': self.transaction_history[-1] if self.transaction_history else None
        }
    
    def to_dict(self):
        """将公司财务转换为字典
        
        Returns:
            dict: 公司财务数据
        """
        return {
            'company_id': self.company_id,
            'company_name': self.company_name,
            'cash': self.cash,
            'loans': self.loans,
            'assets_value': self.assets_value,
            'tax_rate': self.tax_rate,
            'interest_rate': self.interest_rate,
            'depreciation_rate': self.depreciation_rate,
            'seed': self.seed,
            'transaction_history': self.transaction_history
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建公司财务
        
        Args:
            data (dict): 公司财务数据
            
        Returns:
            CompanyFinances: 公司财务实例
        """
        finances = cls(
            company_id=data['company_id'],
            company_name=data['company_name'],
            initial_cash=0,  # 不使用初始值，而是直接设置
            initial_loan=0,
            seed=data['seed']
        )
        
        finances.cash = data['cash']
        finances.loans = data['loans']
        finances.assets_value = data['assets_value']
        finances.tax_rate = data['tax_rate']
        finances.interest_rate = data['interest_rate']
        finances.depreciation_rate = data['depreciation_rate']
        finances.transaction_history = data['transaction_history']
        
        return finances