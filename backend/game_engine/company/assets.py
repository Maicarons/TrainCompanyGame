# 资产管理模块

from enum import Enum, auto
from datetime import datetime

class AssetType(Enum):
    """资产类型枚举"""
    RAILWAY = auto()   # 铁路资产
    VEHICLE = auto()   # 车辆资产
    STATION = auto()   # 车站资产
    LAND = auto()      # 土地资产
    BUILDING = auto()  # 建筑资产

class Asset:
    """资产基类"""
    
    def __init__(self, asset_id, name, initial_value, location=None, properties=None):
        """初始化资产
        
        Args:
            asset_id: 资产ID
            name (str): 资产名称
            initial_value (float): 初始价值
            location: 资产位置
            properties (dict, optional): 资产属性
        """
        self.asset_id = asset_id
        self.name = name
        self.initial_value = initial_value
        self.current_value = initial_value
        self.location = location
        self.properties = properties or {}
        self.purchase_date = datetime.now()
        self.condition = 1.0  # 资产状况，1.0表示全新
        self.maintenance_history = []
    
    def update_value(self, time_factor):
        """更新资产价值
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 更新后的价值
        """
        # 基础折旧率
        depreciation_rate = self.properties.get('depreciation_rate', 0.1)
        
        # 根据资产状况调整折旧率
        adjusted_rate = depreciation_rate * (2 - self.condition)
        
        # 计算折旧
        depreciation = self.current_value * adjusted_rate * time_factor
        self.current_value = max(0.1 * self.initial_value, self.current_value - depreciation)
        
        # 资产状况随时间降低
        condition_decay = 0.05 * time_factor
        self.condition = max(0.2, self.condition - condition_decay)
        
        return self.current_value
    
    def perform_maintenance(self, cost, description="常规维护"):
        """执行维护
        
        Args:
            cost (float): 维护成本
            description (str, optional): 维护描述
            
        Returns:
            float: 维护后的资产状况
        """
        # 记录维护历史
        maintenance_record = {
            'date': datetime.now(),
            'cost': cost,
            'description': description,
            'condition_before': self.condition
        }
        
        # 提升资产状况
        improvement = min(0.3, cost / (self.initial_value * 0.1))  # 维护费用与初始价值的比例决定改善程度
        self.condition = min(1.0, self.condition + improvement)
        
        maintenance_record['condition_after'] = self.condition
        self.maintenance_history.append(maintenance_record)
        
        return self.condition
    
    def calculate_maintenance_cost(self, time_factor):
        """计算维护成本
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 维护成本
        """
        # 基础维护因子
        maintenance_factor = self.properties.get('maintenance_factor', 0.05)
        
        # 根据资产状况和年龄调整维护因子
        age_factor = (datetime.now() - self.purchase_date).days / 365  # 资产年龄（年）
        condition_factor = 2 - self.condition  # 状况越差，维护因子越高
        
        adjusted_factor = maintenance_factor * (1 + 0.1 * age_factor) * condition_factor
        
        # 计算维护成本
        maintenance_cost = self.initial_value * adjusted_factor * time_factor
        
        return maintenance_cost
    
    def to_dict(self):
        """将资产转换为字典
        
        Returns:
            dict: 资产数据
        """
        return {
            'asset_id': self.asset_id,
            'name': self.name,
            'asset_type': self.asset_type.name,
            'initial_value': self.initial_value,
            'current_value': self.current_value,
            'location': self.location,
            'properties': self.properties,
            'purchase_date': self.purchase_date.isoformat(),
            'condition': self.condition,
            'maintenance_history': self.maintenance_history
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建资产
        
        Args:
            data (dict): 资产数据
            
        Returns:
            Asset: 资产实例
        """
        asset = cls(
            asset_id=data['asset_id'],
            name=data['name'],
            initial_value=data['initial_value'],
            location=data['location'],
            properties=data['properties']
        )
        
        asset.current_value = data['current_value']
        asset.purchase_date = datetime.fromisoformat(data['purchase_date'])
        asset.condition = data['condition']
        asset.maintenance_history = data['maintenance_history']
        
        return asset

class RailwayAsset(Asset):
    """铁路资产类"""
    
    def __init__(self, asset_id, name, initial_value, location=None, properties=None):
        """初始化铁路资产
        
        Args:
            asset_id: 资产ID
            name (str): 资产名称
            initial_value (float): 初始价值
            location: 资产位置（路线坐标）
            properties (dict, optional): 资产属性
        """
        super().__init__(asset_id, name, initial_value, location, properties)
        self.asset_type = AssetType.RAILWAY
        
        # 铁路特有属性
        self.properties.setdefault('length', 0)  # 铁路长度（公里）
        self.properties.setdefault('track_type', 'standard')  # 轨道类型
        self.properties.setdefault('max_speed', 120)  # 最大速度（公里/小时）
        self.properties.setdefault('electrified', False)  # 是否电气化
        self.properties.setdefault('double_track', False)  # 是否双轨
        self.properties.setdefault('maintenance_factor', 0.04)  # 维护因子
        self.properties.setdefault('depreciation_rate', 0.05)  # 折旧率
    
    def calculate_maintenance_cost(self, time_factor):
        """计算铁路维护成本
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 维护成本
        """
        base_cost = super().calculate_maintenance_cost(time_factor)
        
        # 根据铁路特性调整维护成本
        length_factor = self.properties['length'] / 10  # 每10公里的基础维护
        
        # 电气化和双轨铁路维护成本更高
        if self.properties['electrified']:
            base_cost *= 1.3
        
        if self.properties['double_track']:
            base_cost *= 1.5
        
        return base_cost * length_factor

class VehicleAsset(Asset):
    """车辆资产类"""
    
    def __init__(self, asset_id, name, initial_value, location=None, properties=None):
        """初始化车辆资产
        
        Args:
            asset_id: 资产ID
            name (str): 资产名称
            initial_value (float): 初始价值
            location: 资产位置
            properties (dict, optional): 资产属性
        """
        super().__init__(asset_id, name, initial_value, location, properties)
        self.asset_type = AssetType.VEHICLE
        
        # 车辆特有属性
        self.properties.setdefault('vehicle_type', 'locomotive')  # 车辆类型
        self.properties.setdefault('capacity', 100)  # 载客/载货量
        self.properties.setdefault('speed', 100)  # 最大速度（公里/小时）
        self.properties.setdefault('fuel_efficiency', 1.0)  # 燃油效率
        self.properties.setdefault('maintenance_factor', 0.08)  # 维护因子
        self.properties.setdefault('depreciation_rate', 0.15)  # 折旧率
        
        # 运行状态
        self.status = 'idle'  # idle, running, maintenance, broken
        self.mileage = 0  # 行驶里程
    
    def update_value(self, time_factor):
        """更新车辆价值
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 更新后的价值
        """
        # 车辆折旧与里程相关
        mileage_factor = 1.0 + (self.mileage / 10000) * 0.05  # 每10000公里增加5%折旧率
        
        # 调整折旧率
        original_rate = self.properties['depreciation_rate']
        self.properties['depreciation_rate'] = original_rate * mileage_factor
        
        # 计算折旧
        value = super().update_value(time_factor)
        
        # 恢复原始折旧率
        self.properties['depreciation_rate'] = original_rate
        
        return value
    
    def add_mileage(self, distance):
        """增加行驶里程
        
        Args:
            distance (float): 行驶距离（公里）
            
        Returns:
            float: 更新后的里程
        """
        self.mileage += distance
        
        # 里程增加会降低车辆状况
        condition_decay = distance / 50000  # 每50000公里降低1.0的状况
        self.condition = max(0.2, self.condition - condition_decay)
        
        return self.mileage
    
    def calculate_maintenance_cost(self, time_factor):
        """计算车辆维护成本
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 维护成本
        """
        base_cost = super().calculate_maintenance_cost(time_factor)
        
        # 根据里程调整维护成本
        mileage_factor = 1.0 + (self.mileage / 20000) * 0.1  # 每20000公里增加10%维护成本
        
        return base_cost * mileage_factor

class StationAsset(Asset):
    """车站资产类"""
    
    def __init__(self, asset_id, name, initial_value, location=None, properties=None):
        """初始化车站资产
        
        Args:
            asset_id: 资产ID
            name (str): 资产名称
            initial_value (float): 初始价值
            location: 资产位置
            properties (dict, optional): 资产属性
        """
        super().__init__(asset_id, name, initial_value, location, properties)
        self.asset_type = AssetType.STATION
        
        # 车站特有属性
        self.properties.setdefault('station_size', 'medium')  # 车站规模
        self.properties.setdefault('capacity', 500)  # 客运/货运容量
        self.properties.setdefault('facilities', [])  # 设施列表
        self.properties.setdefault('city_id', None)  # 所在城市ID
        self.properties.setdefault('maintenance_factor', 0.06)  # 维护因子
        self.properties.setdefault('depreciation_rate', 0.08)  # 折旧率
        
        # 车站状态
        self.passenger_traffic = 0  # 客流量
        self.freight_traffic = 0  # 货运量
    
    def calculate_maintenance_cost(self, time_factor):
        """计算车站维护成本
        
        Args:
            time_factor (float): 时间因子（年）
            
        Returns:
            float: 维护成本
        """
        base_cost = super().calculate_maintenance_cost(time_factor)
        
        # 根据车站规模和设施调整维护成本
        if self.properties['station_size'] == 'large':
            base_cost *= 1.5
        elif self.properties['station_size'] == 'small':
            base_cost *= 0.7
        
        # 设施增加维护成本
        facility_factor = 1.0 + len(self.properties['facilities']) * 0.1
        
        # 客流量和货运量增加维护成本
        traffic_factor = 1.0 + (self.passenger_traffic / 1000 + self.freight_traffic / 500) * 0.05
        
        return base_cost * facility_factor * traffic_factor
    
    def update_traffic(self, passengers, freight):
        """更新车站客流量和货运量
        
        Args:
            passengers (float): 客流量增加
            freight (float): 货运量增加
            
        Returns:
            tuple: (客流量, 货运量)
        """
        self.passenger_traffic += passengers
        self.freight_traffic += freight
        
        # 流量增加会降低车站状况
        traffic_impact = (passengers / 10000 + freight / 5000) * 0.01
        self.condition = max(0.3, self.condition - traffic_impact)
        
        return (self.passenger_traffic, self.freight_traffic)
    
    def add_facility(self, facility_name, cost):
        """添加车站设施
        
        Args:
            facility_name (str): 设施名称
            cost (float): 设施成本
            
        Returns:
            list: 更新后的设施列表
        """
        if facility_name not in self.properties['facilities']:
            self.properties['facilities'].append(facility_name)
            
            # 设施增加车站价值
            self.current_value += cost * 0.8  # 设施价值计入车站资产，但有一定折损
            
            # 某些设施可能提升车站容量
            if facility_name == 'expanded_platform':
                self.properties['capacity'] *= 1.2
            elif facility_name == 'freight_terminal':
                self.properties['capacity'] *= 1.3
            elif facility_name == 'modern_signaling':
                # 现代信号系统提高运营效率
                pass
        
        return self.properties['facilities']