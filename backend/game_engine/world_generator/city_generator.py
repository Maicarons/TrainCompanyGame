# 城市生成器模块

import random
import numpy as np
from enum import Enum
from .terrain_generator import TerrainType, TerrainGenerator

class CitySize(Enum):
    """城市规模枚举"""
    VILLAGE = 0     # 村庄
    TOWN = 1        # 小镇
    CITY = 2        # 城市
    METROPOLIS = 3  # 大都市

class CityType(Enum):
    """城市类型枚举"""
    AGRICULTURAL = 0  # 农业
    INDUSTRIAL = 1    # 工业
    COMMERCIAL = 2    # 商业
    MINING = 3        # 矿业
    TOURIST = 4       # 旅游

class City:
    """城市类，表示地图上的一个城市"""
    
    def __init__(self, name, x, y, size, city_type):
        """初始化城市
        
        Args:
            name (str): 城市名称
            x (int): x坐标
            y (int): y坐标
            size (CitySize): 城市规模
            city_type (CityType): 城市类型
        """
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.city_type = city_type
        self.population = self._calculate_population()
        self.connections = []  # 与其他城市的连接
        self.resources = {}    # 城市资源
        self.demand = {}       # 城市需求
        
    def _calculate_population(self):
        """根据城市规模计算人口
        
        Returns:
            int: 城市人口
        """
        base_population = {
            CitySize.VILLAGE: 500,
            CitySize.TOWN: 5000,
            CitySize.CITY: 50000,
            CitySize.METROPOLIS: 500000
        }
        
        # 添加一些随机变化
        base = base_population[self.size]
        variation = random.uniform(0.8, 1.2)  # 80%-120%的基础人口
        return int(base * variation)
    
    def add_connection(self, other_city, distance):
        """添加与其他城市的连接
        
        Args:
            other_city (City): 连接的城市
            distance (float): 两城市间的距离
        """
        self.connections.append({
            'city': other_city,
            'distance': distance
        })
    
    def generate_resources(self):
        """根据城市类型生成资源和需求"""
        # 根据城市类型设置资源生产
        if self.city_type == CityType.AGRICULTURAL:
            self.resources = {
                'food': self.population * 0.01,
                'wood': self.population * 0.005
            }
            self.demand = {
                'industrial_goods': self.population * 0.003,
                'consumer_goods': self.population * 0.005
            }
        elif self.city_type == CityType.INDUSTRIAL:
            self.resources = {
                'industrial_goods': self.population * 0.008,
                'machinery': self.population * 0.003
            }
            self.demand = {
                'food': self.population * 0.007,
                'raw_materials': self.population * 0.01,
                'coal': self.population * 0.005
            }
        elif self.city_type == CityType.COMMERCIAL:
            self.resources = {
                'consumer_goods': self.population * 0.007,
                'luxury_goods': self.population * 0.002
            }
            self.demand = {
                'food': self.population * 0.008,
                'industrial_goods': self.population * 0.004
            }
        elif self.city_type == CityType.MINING:
            self.resources = {
                'coal': self.population * 0.01,
                'iron': self.population * 0.008,
                'raw_materials': self.population * 0.01
            }
            self.demand = {
                'food': self.population * 0.006,
                'machinery': self.population * 0.004,
                'industrial_goods': self.population * 0.003
            }
        elif self.city_type == CityType.TOURIST:
            self.resources = {
                'luxury_goods': self.population * 0.005,
                'services': self.population * 0.01
            }
            self.demand = {
                'food': self.population * 0.01,
                'consumer_goods': self.population * 0.008
            }

class CityGenerator:
    """城市生成器类，负责在地图上生成城市"""
    
    def __init__(self, terrain_generator, seed=None):
        """初始化城市生成器
        
        Args:
            terrain_generator (TerrainGenerator): 地形生成器实例
            seed (int, optional): 随机种子
        """
        self.terrain_generator = terrain_generator
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.cities = []
        self.city_name_prefixes = ['北', '南', '东', '西', '新', '旧', '上', '下', '中', '大', '小']
        self.city_name_suffixes = ['京', '海', '州', '城', '镇', '村', '港', '湾', '岛', '山', '河']
        
        # 设置随机种子
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def generate_cities(self, num_cities, min_distance=10):
        """在地图上生成城市
        
        Args:
            num_cities (int): 要生成的城市数量
            min_distance (int): 城市之间的最小距离
            
        Returns:
            list: 生成的城市列表
        """
        width = self.terrain_generator.width
        height = self.terrain_generator.height
        
        # 确保地形图已生成
        if self.terrain_generator.terrain_map is None:
            self.terrain_generator.generate_terrain_map()
        
        # 生成城市
        attempts = 0
        max_attempts = num_cities * 10  # 最大尝试次数
        
        while len(self.cities) < num_cities and attempts < max_attempts:
            attempts += 1
            
            # 随机选择位置
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            
            # 检查地形是否适合建城市
            terrain_type = self.terrain_generator.get_terrain_at(x, y)
            if terrain_type in [TerrainType.WATER, TerrainType.MOUNTAIN]:
                continue  # 水域和高山不适合建城市
            
            # 检查与其他城市的距离
            if self._check_city_distance(x, y, min_distance):
                # 生成城市属性
                name = self._generate_city_name()
                size = self._determine_city_size(terrain_type)
                city_type = self._determine_city_type(terrain_type)
                
                # 创建城市
                city = City(name, x, y, size, city_type)
                city.generate_resources()
                self.cities.append(city)
        
        # 生成城市间连接
        self._generate_connections()
        
        return self.cities
    
    def _check_city_distance(self, x, y, min_distance):
        """检查新城市位置与现有城市的距离
        
        Args:
            x (int): x坐标
            y (int): y坐标
            min_distance (int): 最小距离
            
        Returns:
            bool: 如果距离足够远返回True
        """
        for city in self.cities:
            dx = abs(city.x - x)
            dy = abs(city.y - y)
            distance = (dx**2 + dy**2)**0.5
            if distance < min_distance:
                return False
        return True
    
    def _generate_city_name(self):
        """生成随机的城市名称
        
        Returns:
            str: 城市名称
        """
        prefix = random.choice(self.city_name_prefixes)
        suffix = random.choice(self.city_name_suffixes)
        return prefix + suffix
    
    def _determine_city_size(self, terrain_type):
        """根据地形确定城市规模
        
        Args:
            terrain_type (TerrainType): 地形类型
            
        Returns:
            CitySize: 城市规模
        """
        # 不同地形适合不同规模的城市
        if terrain_type == TerrainType.PLAIN:
            weights = [0.1, 0.3, 0.4, 0.2]  # 平原适合大城市
        elif terrain_type == TerrainType.HILL:
            weights = [0.2, 0.4, 0.3, 0.1]  # 丘陵适合中等城市
        elif terrain_type == TerrainType.FOREST:
            weights = [0.4, 0.4, 0.2, 0.0]  # 森林适合小城市
        elif terrain_type == TerrainType.DESERT:
            weights = [0.6, 0.3, 0.1, 0.0]  # 沙漠主要是小城市
        else:
            weights = [0.25, 0.25, 0.25, 0.25]  # 默认均匀分布
        
        sizes = list(CitySize)
        return random.choices(sizes, weights=weights, k=1)[0]
    
    def _determine_city_type(self, terrain_type):
        """根据地形确定城市类型
        
        Args:
            terrain_type (TerrainType): 地形类型
            
        Returns:
            CityType: 城市类型
        """
        # 不同地形适合不同类型的城市
        if terrain_type == TerrainType.PLAIN:
            weights = [0.4, 0.2, 0.3, 0.0, 0.1]  # 平原适合农业和商业
        elif terrain_type == TerrainType.HILL:
            weights = [0.1, 0.4, 0.2, 0.2, 0.1]  # 丘陵适合工业和矿业
        elif terrain_type == TerrainType.FOREST:
            weights = [0.3, 0.1, 0.1, 0.2, 0.3]  # 森林适合农业和旅游
        elif terrain_type == TerrainType.DESERT:
            weights = [0.1, 0.1, 0.1, 0.5, 0.2]  # 沙漠适合矿业
        else:
            weights = [0.2, 0.2, 0.2, 0.2, 0.2]  # 默认均匀分布
        
        types = list(CityType)
        return random.choices(types, weights=weights, k=1)[0]
    
    def _generate_connections(self):
        """生成城市之间的连接网络"""
        # 计算所有城市对之间的距离
        for i, city1 in enumerate(self.cities):
            for j, city2 in enumerate(self.cities):
                if i != j:  # 不与自己连接
                    dx = abs(city1.x - city2.x)
                    dy = abs(city1.y - city2.y)
                    distance = (dx**2 + dy**2)**0.5
                    
                    # 添加连接，这里可以根据需要设置连接条件
                    # 例如，只连接距离较近的城市，或者根据城市规模决定连接
                    if distance < 30:  # 简单示例：距离小于30的城市建立连接
                        city1.add_connection(city2, distance)
    
    def get_city_at(self, x, y, tolerance=3):
        """获取指定坐标附近的城市
        
        Args:
            x (int): x坐标
            y (int): y坐标
            tolerance (int): 容差范围
            
        Returns:
            City: 找到的城市，如果没有则返回None
        """
        for city in self.cities:
            dx = abs(city.x - x)
            dy = abs(city.y - y)
            if dx <= tolerance and dy <= tolerance:
                return city
        return None
    
    def save_cities(self, filename):
        """保存城市数据到文件
        
        Args:
            filename (str): 文件名
        """
        # 将城市数据转换为可序列化的格式
        city_data = []
        for city in self.cities:
            connections = [{
                'city_index': self.cities.index(conn['city']),
                'distance': conn['distance']
            } for conn in city.connections]
            
            city_data.append({
                'name': city.name,
                'x': city.x,
                'y': city.y,
                'size': city.size.value,
                'type': city.city_type.value,
                'population': city.population,
                'connections': connections,
                'resources': city.resources,
                'demand': city.demand
            })
        
        # 保存数据
        np.savez(
            filename,
            cities=city_data,
            seed=self.seed
        )
    
    @classmethod
    def load_cities(cls, filename, terrain_generator):
        """从文件加载城市数据
        
        Args:
            filename (str): 文件名
            terrain_generator (TerrainGenerator): 地形生成器实例
            
        Returns:
            CityGenerator: 城市生成器实例
        """
        data = np.load(filename, allow_pickle=True)
        city_data = data['cities']
        seed = int(data['seed'])
        
        # 创建城市生成器
        generator = cls(terrain_generator, seed)
        
        # 重建城市
        for city_info in city_data:
            city = City(
                city_info['name'],
                int(city_info['x']),
                int(city_info['y']),
                CitySize(city_info['size']),
                CityType(city_info['type'])
            )
            city.population = int(city_info['population'])
            city.resources = city_info['resources'].item()
            city.demand = city_info['demand'].item()
            generator.cities.append(city)
        
        # 重建连接
        for i, city_info in enumerate(city_data):
            for conn in city_info['connections']:
                city_index = int(conn['city_index'])
                distance = float(conn['distance'])
                generator.cities[i].add_connection(generator.cities[city_index], distance)
        
        return generator