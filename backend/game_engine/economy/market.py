# 市场系统模块

import numpy as np
from enum import Enum, auto
from datetime import datetime

class ResourceType(Enum):
    """资源类型枚举"""
    COAL = auto()        # 煤炭
    IRON = auto()        # 铁矿
    WOOD = auto()        # 木材
    STEEL = auto()       # 钢铁
    OIL = auto()         # 石油
    PASSENGERS = auto()  # 乘客
    MAIL = auto()        # 邮件
    LIVESTOCK = auto()   # 牲畜
    GRAIN = auto()       # 粮食
    GOODS = auto()       # 日用品

class PriceModel:
    """价格模型，用于模拟资源价格波动"""
    
    def __init__(self, base_price, volatility=0.1, trend=0, seasonality=None, seed=None):
        """初始化价格模型
        
        Args:
            base_price (float): 基础价格
            volatility (float): 价格波动率
            trend (float): 价格趋势（正值表示上涨趋势，负值表示下跌趋势）
            seasonality (dict, optional): 季节性影响，格式为{月份: 系数}
            seed (int, optional): 随机种子
        """
        self.base_price = base_price
        self.current_price = base_price
        self.volatility = volatility
        self.trend = trend
        self.seasonality = seasonality or {}
        self.rng = np.random.RandomState(seed)
        self.last_update = datetime.now()
    
    def update_price(self, time_delta, external_factors=None):
        """更新价格
        
        Args:
            time_delta: 时间增量（秒）
            external_factors (dict, optional): 外部因素影响，格式为{因素名: 影响系数}
            
        Returns:
            float: 更新后的价格
        """
        # 计算时间因子（转换为天）
        time_factor = time_delta / (24 * 3600)
        
        # 随机波动
        random_change = self.rng.normal(0, self.volatility) * time_factor
        
        # 趋势影响
        trend_change = self.trend * time_factor
        
        # 季节性影响
        current_month = datetime.now().month
        season_factor = self.seasonality.get(current_month, 1.0)
        season_change = (season_factor - 1.0) * 0.01 * time_factor
        
        # 外部因素影响
        external_change = 0
        if external_factors:
            for factor, value in external_factors.items():
                external_change += value * 0.01 * time_factor
        
        # 计算总变化
        total_change = random_change + trend_change + season_change + external_change
        
        # 更新价格（确保价格不会变为负数）
        self.current_price = max(0.01, self.current_price * (1 + total_change))
        
        # 更新时间
        self.last_update = datetime.now()
        
        return self.current_price
    
    def get_current_price(self):
        """获取当前价格
        
        Returns:
            float: 当前价格
        """
        return self.current_price
    
    def to_dict(self):
        """将价格模型转换为字典
        
        Returns:
            dict: 价格模型数据
        """
        return {
            'base_price': self.base_price,
            'current_price': self.current_price,
            'volatility': self.volatility,
            'trend': self.trend,
            'seasonality': self.seasonality
        }
    
    @classmethod
    def from_dict(cls, data, seed=None):
        """从字典创建价格模型
        
        Args:
            data (dict): 价格模型数据
            seed (int, optional): 随机种子
            
        Returns:
            PriceModel: 价格模型实例
        """
        model = cls(
            base_price=data['base_price'],
            volatility=data['volatility'],
            trend=data['trend'],
            seasonality=data['seasonality'],
            seed=seed
        )
        model.current_price = data['current_price']
        return model

class Market:
    """市场类，管理资源价格和交易"""
    
    def __init__(self, name, city=None, seed=None):
        """初始化市场
        
        Args:
            name (str): 市场名称
            city: 所属城市，如果为None则表示全球市场
            seed (int, optional): 随机种子
        """
        self.name = name
        self.city = city
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # 初始化各类资源的价格模型
        self.price_models = self._initialize_price_models()
        
        # 市场规模和活跃度（根据城市规模确定）
        self.market_size = 1.0 if city is None else self._calculate_market_size()
        self.activity_level = 1.0 if city is None else self._calculate_activity_level()
        
        # 交易历史
        self.transaction_history = []
    
    def _initialize_price_models(self):
        """初始化各类资源的价格模型
        
        Returns:
            dict: 资源类型到价格模型的映射
        """
        # 基础价格设置
        base_prices = {
            ResourceType.COAL: 100,
            ResourceType.IRON: 150,
            ResourceType.WOOD: 80,
            ResourceType.STEEL: 200,
            ResourceType.OIL: 180,
            ResourceType.PASSENGERS: 50,
            ResourceType.MAIL: 70,
            ResourceType.LIVESTOCK: 120,
            ResourceType.GRAIN: 90,
            ResourceType.GOODS: 160
        }
        
        # 波动率设置
        volatilities = {
            ResourceType.COAL: 0.05,
            ResourceType.IRON: 0.07,
            ResourceType.WOOD: 0.04,
            ResourceType.STEEL: 0.08,
            ResourceType.OIL: 0.1,
            ResourceType.PASSENGERS: 0.03,
            ResourceType.MAIL: 0.02,
            ResourceType.LIVESTOCK: 0.06,
            ResourceType.GRAIN: 0.05,
            ResourceType.GOODS: 0.04
        }
        
        # 趋势设置
        trends = {
            ResourceType.COAL: -0.01,  # 煤炭长期下降
            ResourceType.IRON: 0.005,
            ResourceType.WOOD: 0.002,
            ResourceType.STEEL: 0.007,
            ResourceType.OIL: 0.015,   # 石油长期上涨
            ResourceType.PASSENGERS: 0.003,
            ResourceType.MAIL: -0.005, # 邮件长期下降
            ResourceType.LIVESTOCK: 0.004,
            ResourceType.GRAIN: 0.006,
            ResourceType.GOODS: 0.008
        }
        
        # 季节性影响
        seasonality = {
            ResourceType.COAL: {1: 1.2, 2: 1.15, 12: 1.1},  # 冬季煤炭需求增加
            ResourceType.GRAIN: {9: 1.15, 10: 1.1},  # 收获季节粮食供应增加
            ResourceType.PASSENGERS: {7: 1.2, 8: 1.2},  # 暑假乘客增加
            ResourceType.LIVESTOCK: {4: 1.1, 5: 1.1}  # 春季牲畜交易活跃
        }
        
        # 创建价格模型
        price_models = {}
        for resource_type in ResourceType:
            # 如果是城市市场，根据城市特性调整价格
            base_price = base_prices[resource_type]
            if self.city:
                base_price = self._adjust_price_by_city(resource_type, base_price)
            
            # 创建价格模型
            price_models[resource_type] = PriceModel(
                base_price=base_price,
                volatility=volatilities[resource_type],
                trend=trends[resource_type],
                seasonality=seasonality.get(resource_type, {}),
                seed=self.rng.randint(0, 10000)  # 为每个价格模型生成不同的种子
            )
        
        return price_models
    
    def _adjust_price_by_city(self, resource_type, base_price):
        """根据城市特性调整资源基础价格
        
        Args:
            resource_type (ResourceType): 资源类型
            base_price (float): 基础价格
            
        Returns:
            float: 调整后的价格
        """
        # 这里可以根据城市类型、规模等特性调整价格
        adjustment = 1.0
        
        # 根据城市类型调整
        if hasattr(self.city, 'city_type'):
            from ..world_generator.city_generator import CityType
            
            if self.city.city_type == CityType.INDUSTRIAL:
                # 工业城市煤炭、铁矿便宜，钢铁产量高
                if resource_type in [ResourceType.COAL, ResourceType.IRON]:
                    adjustment *= 0.9
                elif resource_type == ResourceType.STEEL:
                    adjustment *= 0.85
            
            elif self.city.city_type == CityType.AGRICULTURAL:
                # 农业城市粮食、牲畜便宜
                if resource_type in [ResourceType.GRAIN, ResourceType.LIVESTOCK]:
                    adjustment *= 0.85
            
            elif self.city.city_type == CityType.COMMERCIAL:
                # 商业城市日用品便宜，客运需求高
                if resource_type == ResourceType.GOODS:
                    adjustment *= 0.9
                elif resource_type == ResourceType.PASSENGERS:
                    adjustment *= 1.1
        
        # 根据城市规模调整
        if hasattr(self.city, 'size'):
            from ..world_generator.city_generator import CitySize
            
            if self.city.size == CitySize.LARGE:
                # 大城市规模经济效应
                adjustment *= 0.95
            elif self.city.size == CitySize.SMALL:
                # 小城市供应链不完善
                adjustment *= 1.05
        
        return base_price * adjustment
    
    def _calculate_market_size(self):
        """计算市场规模
        
        Returns:
            float: 市场规模系数
        """
        if not self.city:
            return 1.0
        
        # 根据城市规模计算市场规模
        if hasattr(self.city, 'size'):
            from ..world_generator.city_generator import CitySize
            
            if self.city.size == CitySize.LARGE:
                return 1.5
            elif self.city.size == CitySize.MEDIUM:
                return 1.0
            elif self.city.size == CitySize.SMALL:
                return 0.6
        
        return 1.0
    
    def _calculate_activity_level(self):
        """计算市场活跃度
        
        Returns:
            float: 市场活跃度系数
        """
        if not self.city:
            return 1.0
        
        # 根据城市类型计算市场活跃度
        activity = 1.0
        
        if hasattr(self.city, 'city_type'):
            from ..world_generator.city_generator import CityType
            
            if self.city.city_type == CityType.COMMERCIAL:
                activity *= 1.3  # 商业城市市场更活跃
            elif self.city.city_type == CityType.INDUSTRIAL:
                activity *= 1.1  # 工业城市也较活跃
        
        return activity
    
    def update_prices(self, time_delta, external_factors=None):
        """更新所有资源价格
        
        Args:
            time_delta: 时间增量（秒）
            external_factors (dict, optional): 外部因素影响
            
        Returns:
            dict: 更新后的价格数据
        """
        updated_prices = {}
        
        for resource_type, price_model in self.price_models.items():
            # 获取资源特定的外部因素
            resource_factors = None
            if external_factors and resource_type in external_factors:
                resource_factors = external_factors[resource_type]
            
            # 更新价格
            new_price = price_model.update_price(time_delta, resource_factors)
            updated_prices[resource_type] = new_price
        
        return updated_prices
    
    def get_price(self, resource_type):
        """获取特定资源的当前价格
        
        Args:
            resource_type (ResourceType): 资源类型
            
        Returns:
            float: 资源价格
        """
        if resource_type in self.price_models:
            return self.price_models[resource_type].get_current_price()
        return 0.0
    
    def record_transaction(self, resource_type, quantity, price, buyer_id, seller_id, timestamp=None):
        """记录交易
        
        Args:
            resource_type (ResourceType): 资源类型
            quantity (float): 交易数量
            price (float): 交易价格
            buyer_id: 买方ID
            seller_id: 卖方ID
            timestamp (datetime, optional): 交易时间戳
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        transaction = {
            'resource_type': resource_type,
            'quantity': quantity,
            'price': price,
            'total_value': quantity * price,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'timestamp': timestamp,
            'market_name': self.name
        }
        
        self.transaction_history.append(transaction)
        
        # 限制历史记录长度
        if len(self.transaction_history) > 1000:
            self.transaction_history = self.transaction_history[-1000:]
    
    def get_market_data(self):
        """获取市场数据
        
        Returns:
            dict: 市场数据
        """
        return {
            'name': self.name,
            'city_id': self.city.id if self.city else None,
            'market_size': self.market_size,
            'activity_level': self.activity_level,
            'prices': {resource_type.name: model.get_current_price() 
                      for resource_type, model in self.price_models.items()},
            'recent_transactions': self.transaction_history[-10:] if self.transaction_history else []
        }
    
    def to_dict(self):
        """将市场转换为字典
        
        Returns:
            dict: 市场数据
        """
        return {
            'name': self.name,
            'city_id': self.city.id if self.city else None,
            'seed': self.seed,
            'market_size': self.market_size,
            'activity_level': self.activity_level,
            'price_models': {resource_type.name: model.to_dict() 
                           for resource_type, model in self.price_models.items()},
            'transaction_history': self.transaction_history
        }
    
    @classmethod
    def from_dict(cls, data, city=None):
        """从字典创建市场
        
        Args:
            data (dict): 市场数据
            city: 所属城市
            
        Returns:
            Market: 市场实例
        """
        market = cls(data['name'], city, data['seed'])
        market.market_size = data['market_size']
        market.activity_level = data['activity_level']
        
        # 加载价格模型
        for resource_name, model_data in data['price_models'].items():
            resource_type = ResourceType[resource_name]
            market.price_models[resource_type] = PriceModel.from_dict(model_data, data['seed'])
        
        # 加载交易历史
        market.transaction_history = data['transaction_history']
        
        return market