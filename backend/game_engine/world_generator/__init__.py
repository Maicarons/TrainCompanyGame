# 世界生成器包初始化文件

from .terrain_generator import TerrainGenerator, TerrainType
from .city_generator import CityGenerator, City, CitySize, CityType
from .railway_network import RailwayNetworkGenerator, RailwayStation, RailwayLine, RailwayType
import os
import numpy as np

class WorldGenerator:
    """世界生成器主类，整合地形、城市和铁路网络生成"""
    
    def __init__(self, width=200, height=200, seed=None):
        """初始化世界生成器
        
        Args:
            width (int): 世界地图宽度
            height (int): 世界地图高度
            seed (int, optional): 随机种子
        """
        self.width = width
        self.height = height
        self.seed = seed
        
        # 初始化各个生成器组件
        self.terrain_generator = TerrainGenerator(width, height, seed)
        self.city_generator = None
        self.railway_generator = None
    
    def generate_world(self, num_cities=20, min_city_distance=10):
        """生成完整的游戏世界
        
        Args:
            num_cities (int): 要生成的城市数量
            min_city_distance (int): 城市之间的最小距离
            
        Returns:
            dict: 包含世界数据的字典
        """
        # 1. 生成地形
        print("正在生成地形...")
        terrain_map = self.terrain_generator.generate_terrain_map()
        
        # 2. 生成城市
        print("正在生成城市...")
        self.city_generator = CityGenerator(self.terrain_generator, self.seed)
        cities = self.city_generator.generate_cities(num_cities, min_city_distance)
        
        # 3. 生成铁路网络
        print("正在生成铁路网络...")
        self.railway_generator = RailwayNetworkGenerator(self.terrain_generator, self.city_generator, self.seed)
        stations = self.railway_generator.generate_stations()
        railway_lines = self.railway_generator.generate_railway_network()
        
        # 返回世界数据
        return {
            'width': self.width,
            'height': self.height,
            'seed': self.seed,
            'terrain_map': terrain_map,
            'cities': cities,
            'stations': stations,
            'railway_lines': railway_lines
        }
    
    def save_world(self, directory):
        """保存世界数据到指定目录
        
        Args:
            directory (str): 保存目录路径
        """
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)
        
        # 保存地形数据
        terrain_file = os.path.join(directory, 'terrain.npz')
        self.terrain_generator.save_map(terrain_file)
        
        # 保存城市数据
        if self.city_generator:
            city_file = os.path.join(directory, 'cities.npz')
            self.city_generator.save_cities(city_file)
        
        # 保存铁路网络数据
        if self.railway_generator:
            railway_file = os.path.join(directory, 'railway.npz')
            self.railway_generator.save_network(railway_file)
        
        # 保存世界元数据
        metadata = {
            'width': self.width,
            'height': self.height,
            'seed': self.seed
        }
        metadata_file = os.path.join(directory, 'world_metadata.npz')
        np.savez(metadata_file, **metadata)
        
        print(f"世界数据已保存到目录: {directory}")
    
    @classmethod
    def load_world(cls, directory):
        """从指定目录加载世界数据
        
        Args:
            directory (str): 数据目录路径
            
        Returns:
            WorldGenerator: 加载的世界生成器实例
        """
        # 加载元数据
        metadata_file = os.path.join(directory, 'world_metadata.npz')
        metadata = np.load(metadata_file)
        width = int(metadata['width'])
        height = int(metadata['height'])
        seed = int(metadata['seed'])
        
        # 创建世界生成器实例
        world = cls(width, height, seed)
        
        # 加载地形数据
        terrain_file = os.path.join(directory, 'terrain.npz')
        world.terrain_generator = TerrainGenerator.load_map(terrain_file)
        
        # 加载城市数据
        city_file = os.path.join(directory, 'cities.npz')
        world.city_generator = CityGenerator.load_cities(city_file, world.terrain_generator)
        
        # 加载铁路网络数据
        railway_file = os.path.join(directory, 'railway.npz')
        world.railway_generator = RailwayNetworkGenerator.load_network(
            railway_file, world.terrain_generator, world.city_generator
        )
        
        print(f"已从目录加载世界数据: {directory}")
        return world