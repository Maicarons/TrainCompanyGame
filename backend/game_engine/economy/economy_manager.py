# 经济系统管理器

import numpy as np
from datetime import datetime
from .market import Market, ResourceType, PriceModel

class EconomyManager:
    """经济系统管理器，负责管理游戏世界的经济活动"""
    
    def __init__(self, world_generator=None, seed=None):
        """初始化经济系统管理器
        
        Args:
            world_generator: 世界生成器实例，用于获取城市和地形信息
            seed (int, optional): 随机种子
        """
        self.world_generator = world_generator
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # 初始化市场系统
        self.markets = {}
        self.global_market = None
        self.last_update_time = datetime.now()
        
        # 经济指标
        self.inflation_rate = 0.02  # 年通货膨胀率
        self.interest_rate = 0.05   # 基准利率
        self.economic_growth = 0.03  # 经济增长率
        
        # 如果提供了世界生成器，则初始化城市市场
        if world_generator:
            self._initialize_markets()
    
    def _initialize_markets(self):
        """初始化各城市市场和全球市场"""
        # 创建全球市场
        self.global_market = Market("全球市场", None, self.seed)
        
        # 为每个城市创建本地市场
        if hasattr(self.world_generator, 'city_generator') and self.world_generator.city_generator:
            for city_id, city in self.world_generator.city_generator.cities.items():
                # 根据城市规模和类型设置市场参数
                market = Market(f"{city.name}市场", city, self.seed)
                self.markets[city_id] = market
    
    def update_economy(self, game_time, time_delta):
        """更新经济系统
        
        Args:
            game_time: 当前游戏时间
            time_delta: 自上次更新以来的时间增量（秒）
            
        Returns:
            dict: 经济更新数据
        """
        # 更新全球市场
        if self.global_market:
            self.global_market.update_prices(time_delta)
        
        # 更新各城市市场
        for market in self.markets.values():
            market.update_prices(time_delta)
        
        # 计算经济指标变化
        self._update_economic_indicators(time_delta)
        
        # 记录更新时间
        self.last_update_time = datetime.now()
        
        return {
            'inflation_rate': self.inflation_rate,
            'interest_rate': self.interest_rate,
            'economic_growth': self.economic_growth,
            'markets': {market_id: market.get_market_data() for market_id, market in self.markets.items()}
        }
    
    def _update_economic_indicators(self, time_delta):
        """更新经济指标
        
        Args:
            time_delta: 时间增量（秒）
        """
        # 计算时间因子（转换为年）
        time_factor = time_delta / (365 * 24 * 3600)
        
        # 随机波动
        inflation_change = self.rng.normal(0, 0.005) * time_factor
        interest_change = self.rng.normal(0, 0.003) * time_factor
        growth_change = self.rng.normal(0, 0.007) * time_factor
        
        # 更新指标
        self.inflation_rate = max(0.001, min(0.2, self.inflation_rate + inflation_change))
        self.interest_rate = max(0.01, min(0.15, self.interest_rate + interest_change))
        self.economic_growth = max(-0.05, min(0.1, self.economic_growth + growth_change))
        
        # 指标之间的关联性
        if self.inflation_rate > 0.05 and self.interest_rate < 0.08:
            self.interest_rate += 0.002 * time_factor  # 高通胀时提高利率
        
        if self.economic_growth < 0 and self.interest_rate > 0.03:
            self.interest_rate -= 0.001 * time_factor  # 经济衰退时降低利率
    
    def get_resource_price(self, resource_type, city_id=None):
        """获取特定资源在特定城市的价格
        
        Args:
            resource_type (ResourceType): 资源类型
            city_id: 城市ID，如果为None则使用全球市场价格
            
        Returns:
            float: 资源价格
        """
        if city_id and city_id in self.markets:
            return self.markets[city_id].get_price(resource_type)
        elif self.global_market:
            return self.global_market.get_price(resource_type)
        else:
            return 0.0
    
    def save_economy_data(self, file_path):
        """保存经济系统数据
        
        Args:
            file_path (str): 保存路径
        """
        economy_data = {
            'seed': self.seed,
            'inflation_rate': self.inflation_rate,
            'interest_rate': self.interest_rate,
            'economic_growth': self.economic_growth,
            'global_market': self.global_market.to_dict() if self.global_market else None,
            'markets': {market_id: market.to_dict() for market_id, market in self.markets.items()}
        }
        np.savez(file_path, **economy_data)
        print(f"经济系统数据已保存到: {file_path}")
    
    @classmethod
    def load_economy_data(cls, file_path, world_generator=None):
        """加载经济系统数据
        
        Args:
            file_path (str): 数据文件路径
            world_generator: 世界生成器实例
            
        Returns:
            EconomyManager: 经济系统管理器实例
        """
        data = np.load(file_path, allow_pickle=True)
        
        # 创建经济管理器实例
        economy_manager = cls(world_generator, int(data['seed']))
        economy_manager.inflation_rate = float(data['inflation_rate'])
        economy_manager.interest_rate = float(data['interest_rate'])
        economy_manager.economic_growth = float(data['economic_growth'])
        
        # 加载市场数据
        if 'global_market' in data and data['global_market'].item():
            economy_manager.global_market = Market.from_dict(data['global_market'].item())
        
        if 'markets' in data:
            markets_data = data['markets'].item()
            for market_id, market_data in markets_data.items():
                # 获取对应的城市
                city = None
                if world_generator and hasattr(world_generator, 'city_generator'):
                    city = world_generator.city_generator.cities.get(market_id)
                
                economy_manager.markets[market_id] = Market.from_dict(market_data, city)
        
        print(f"已加载经济系统数据: {file_path}")
        return economy_manager