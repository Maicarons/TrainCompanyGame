# 公司管理系统

import numpy as np
from enum import Enum, auto
from datetime import datetime
from ..economy.company_finances import CompanyFinances

class CompanyType(Enum):
    """公司类型枚举"""
    RAILWAY = auto()      # 铁路公司
    INDUSTRY = auto()     # 工业公司
    COMMERCIAL = auto()   # 商业公司

class CompanyManager:
    """公司管理器，负责管理游戏中的所有公司"""
    
    def __init__(self, world_generator=None, economy_manager=None, seed=None):
        """初始化公司管理器
        
        Args:
            world_generator: 世界生成器实例
            economy_manager: 经济系统管理器实例
            seed (int, optional): 随机种子
        """
        self.world_generator = world_generator
        self.economy_manager = economy_manager
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # 公司字典，键为公司ID，值为公司实例
        self.companies = {}
        
        # 公司ID计数器
        self.company_id_counter = 1
        
        # AI公司管理
        self.ai_companies = []
    
    def create_company(self, name, company_type, owner_id=None, is_ai=False, initial_cash=1000000):
        """创建新公司
        
        Args:
            name (str): 公司名称
            company_type (CompanyType): 公司类型
            owner_id: 所有者ID（玩家ID或AI ID）
            is_ai (bool): 是否为AI公司
            initial_cash (float): 初始资金
            
        Returns:
            公司实例
        """
        # 生成公司ID
        company_id = self.company_id_counter
        self.company_id_counter += 1
        
        # 创建公司财务
        finances = CompanyFinances(
            company_id=company_id,
            company_name=name,
            initial_cash=initial_cash,
            seed=self.rng.randint(0, 10000)
        )
        
        # 根据公司类型创建不同类型的公司
        company = None
        if company_type == CompanyType.RAILWAY:
            from .railway_company import RailwayCompany
            company = RailwayCompany(
                company_id=company_id,
                name=name,
                finances=finances,
                owner_id=owner_id,
                world_generator=self.world_generator,
                economy_manager=self.economy_manager,
                seed=self.rng.randint(0, 10000)
            )
        # 可以在这里添加其他类型的公司创建逻辑
        
        # 如果是AI公司，添加到AI公司列表
        if is_ai and company:
            self.ai_companies.append(company_id)
        
        # 添加到公司字典
        if company:
            self.companies[company_id] = company
        
        return company
    
    def get_company(self, company_id):
        """获取公司实例
        
        Args:
            company_id: 公司ID
            
        Returns:
            公司实例或None
        """
        return self.companies.get(company_id)
    
    def get_companies_by_owner(self, owner_id):
        """获取特定所有者的所有公司
        
        Args:
            owner_id: 所有者ID
            
        Returns:
            list: 公司实例列表
        """
        return [company for company in self.companies.values() if company.owner_id == owner_id]
    
    def get_ai_companies(self):
        """获取所有AI公司
        
        Returns:
            list: AI公司实例列表
        """
        return [self.companies[company_id] for company_id in self.ai_companies if company_id in self.companies]
    
    def update_companies(self, game_time, time_delta):
        """更新所有公司
        
        Args:
            game_time: 当前游戏时间
            time_delta: 自上次更新以来的时间增量（秒）
            
        Returns:
            dict: 更新结果
        """
        results = {}
        
        for company_id, company in self.companies.items():
            # 更新公司
            company_result = company.update(game_time, time_delta)
            results[company_id] = company_result
            
            # 更新公司财务
            if hasattr(company, 'finances'):
                company.finances.update_finances(time_delta, self.economy_manager)
        
        # 更新AI公司决策
        self._update_ai_companies(game_time, time_delta)
        
        return results
    
    def _update_ai_companies(self, game_time, time_delta):
        """更新AI公司决策
        
        Args:
            game_time: 当前游戏时间
            time_delta: 自上次更新以来的时间增量（秒）
        """
        for company_id in self.ai_companies:
            if company_id in self.companies:
                company = self.companies[company_id]
                # 调用AI决策逻辑
                if hasattr(company, 'make_ai_decisions'):
                    company.make_ai_decisions(game_time, time_delta)
    
    def delete_company(self, company_id):
        """删除公司
        
        Args:
            company_id: 公司ID
            
        Returns:
            bool: 是否成功
        """
        if company_id in self.companies:
            # 如果是AI公司，从AI公司列表中移除
            if company_id in self.ai_companies:
                self.ai_companies.remove(company_id)
            
            # 从公司字典中移除
            del self.companies[company_id]
            return True
        
        return False
    
    def merge_companies(self, acquirer_id, target_id):
        """合并公司（收购）
        
        Args:
            acquirer_id: 收购方公司ID
            target_id: 目标公司ID
            
        Returns:
            bool: 是否成功
        """
        if acquirer_id not in self.companies or target_id not in self.companies:
            return False
        
        acquirer = self.companies[acquirer_id]
        target = self.companies[target_id]
        
        # 检查公司类型是否兼容
        if type(acquirer) != type(target):
            return False
        
        # 执行合并逻辑（具体实现取决于公司类型）
        if hasattr(acquirer, 'merge_with'):
            success = acquirer.merge_with(target)
            if success:
                # 合并成功后删除目标公司
                self.delete_company(target_id)
                return True
        
        return False
    
    def get_company_ranking(self, metric='net_worth'):
        """获取公司排名
        
        Args:
            metric (str): 排名指标，可选值：'net_worth', 'revenue', 'profit', 'assets'
            
        Returns:
            list: 排序后的公司列表
        """
        companies_list = list(self.companies.values())
        
        if metric == 'net_worth':
            # 按净资产排序
            companies_list.sort(key=lambda c: c.finances.cash + c.finances.assets_value - c.finances.loans, reverse=True)
        elif metric == 'revenue':
            # 按收入排序
            companies_list.sort(key=lambda c: sum(t['amount'] for t in c.finances.transaction_history 
                                              if t['type'].name == 'INCOME' and 
                                              t['timestamp'] >= datetime.now().replace(day=1)), reverse=True)
        elif metric == 'profit':
            # 按利润排序
            companies_list.sort(key=lambda c: self._calculate_profit(c), reverse=True)
        elif metric == 'assets':
            # 按资产价值排序
            companies_list.sort(key=lambda c: c.finances.assets_value, reverse=True)
        
        return companies_list
    
    def _calculate_profit(self, company):
        """计算公司当月利润
        
        Args:
            company: 公司实例
            
        Returns:
            float: 利润
        """
        # 获取当月交易
        current_month = datetime.now().replace(day=1)
        transactions = [t for t in company.finances.transaction_history 
                       if t['timestamp'] >= current_month]
        
        # 计算收入和支出
        income = sum(t['amount'] for t in transactions if t['type'].name == 'INCOME')
        expenses = sum(t['amount'] for t in transactions if t['type'].name in ['EXPENSE', 'INTEREST', 'TAX', 'DEPRECIATION'])
        
        return income - expenses
    
    def save_companies_data(self, file_path):
        """保存公司数据
        
        Args:
            file_path (str): 保存路径
        """
        companies_data = {
            'seed': self.seed,
            'company_id_counter': self.company_id_counter,
            'ai_companies': self.ai_companies,
            'companies': {company_id: company.to_dict() for company_id, company in self.companies.items()}
        }
        np.savez(file_path, **companies_data)
        print(f"公司数据已保存到: {file_path}")
    
    @classmethod
    def load_companies_data(cls, file_path, world_generator=None, economy_manager=None):
        """加载公司数据
        
        Args:
            file_path (str): 数据文件路径
            world_generator: 世界生成器实例
            economy_manager: 经济系统管理器实例
            
        Returns:
            CompanyManager: 公司管理器实例
        """
        data = np.load(file_path, allow_pickle=True)
        
        # 创建公司管理器实例
        manager = cls(world_generator, economy_manager, int(data['seed']))
        manager.company_id_counter = int(data['company_id_counter'])
        manager.ai_companies = data['ai_companies'].tolist()
        
        # 加载公司数据
        if 'companies' in data:
            companies_data = data['companies'].item()
            for company_id, company_data in companies_data.items():
                # 根据公司类型创建不同类型的公司
                company_type = company_data['company_type']
                if company_type == CompanyType.RAILWAY.name:
                    from .railway_company import RailwayCompany
                    manager.companies[company_id] = RailwayCompany.from_dict(
                        company_data, world_generator, economy_manager
                    )
                # 可以在这里添加其他类型的公司加载逻辑
        
        print(f"已加载公司数据: {file_path}")
        return manager