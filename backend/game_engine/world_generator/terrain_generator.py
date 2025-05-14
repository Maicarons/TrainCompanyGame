# 地形生成器模块

import random
import numpy as np
from enum import Enum

class TerrainType(Enum):
    """地形类型枚举"""
    PLAIN = 0      # 平原
    HILL = 1       # 丘陵
    MOUNTAIN = 2   # 山地
    WATER = 3      # 水域
    FOREST = 4     # 森林
    DESERT = 5     # 沙漠

class TerrainGenerator:
    """地形生成器类"""
    
    def __init__(self, width, height, seed=None):
        """初始化地形生成器
        
        Args:
            width (int): 地图宽度
            height (int): 地图高度
            seed (int, optional): 随机种子，用于生成可重复的地形
        """
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.terrain_map = None
        self.elevation_map = None
        self.moisture_map = None
        
        # 设置随机种子
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def generate_elevation_map(self, octaves=6, persistence=0.5, lacunarity=2.0):
        """生成高度图，使用柏林噪声算法
        
        Args:
            octaves (int): 噪声叠加次数，越高细节越多
            persistence (float): 每层噪声的影响程度
            lacunarity (float): 每层噪声的频率变化
            
        Returns:
            numpy.ndarray: 生成的高度图
        """
        # 这里简化实现，实际项目中可以使用更复杂的噪声生成库如noise或opensimplex
        elevation = np.zeros((self.height, self.width))
        
        # 简单模拟柏林噪声
        for y in range(self.height):
            for x in range(self.width):
                nx = x / self.width - 0.5
                ny = y / self.height - 0.5
                elevation[y][x] = self._noise(nx, ny, octaves, persistence, lacunarity)
        
        # 归一化到0-1范围
        min_val = np.min(elevation)
        max_val = np.max(elevation)
        elevation = (elevation - min_val) / (max_val - min_val)
        
        self.elevation_map = elevation
        return elevation
    
    def generate_moisture_map(self, octaves=4, persistence=0.5, lacunarity=2.0):
        """生成湿度图，用于确定地形类型
        
        Args:
            octaves (int): 噪声叠加次数
            persistence (float): 每层噪声的影响程度
            lacunarity (float): 每层噪声的频率变化
            
        Returns:
            numpy.ndarray: 生成的湿度图
        """
        # 类似高度图的生成方式
        moisture = np.zeros((self.height, self.width))
        
        for y in range(self.height):
            for x in range(self.width):
                nx = x / self.width - 0.5
                ny = y / self.height - 0.5
                # 使用不同的种子偏移，生成不同的噪声图
                moisture[y][x] = self._noise(nx + 100, ny + 100, octaves, persistence, lacunarity)
        
        # 归一化
        min_val = np.min(moisture)
        max_val = np.max(moisture)
        moisture = (moisture - min_val) / (max_val - min_val)
        
        self.moisture_map = moisture
        return moisture
    
    def generate_terrain_map(self):
        """根据高度图和湿度图生成地形类型图
        
        Returns:
            numpy.ndarray: 地形类型图，每个元素是TerrainType枚举值
        """
        if self.elevation_map is None:
            self.generate_elevation_map()
        
        if self.moisture_map is None:
            self.generate_moisture_map()
        
        terrain = np.zeros((self.height, self.width), dtype=int)
        
        for y in range(self.height):
            for x in range(self.width):
                elevation = self.elevation_map[y][x]
                moisture = self.moisture_map[y][x]
                
                # 根据高度和湿度确定地形类型
                if elevation < 0.2:  # 低洼地区
                    terrain[y][x] = TerrainType.WATER.value
                elif elevation < 0.4:  # 平原
                    if moisture > 0.6:
                        terrain[y][x] = TerrainType.FOREST.value
                    else:
                        terrain[y][x] = TerrainType.PLAIN.value
                elif elevation < 0.7:  # 丘陵
                    terrain[y][x] = TerrainType.HILL.value
                elif elevation < 0.9:  # 山地
                    terrain[y][x] = TerrainType.MOUNTAIN.value
                else:  # 高山
                    if moisture < 0.3:  # 干燥高地
                        terrain[y][x] = TerrainType.DESERT.value
                    else:
                        terrain[y][x] = TerrainType.MOUNTAIN.value
        
        self.terrain_map = terrain
        return terrain
    
    def _noise(self, x, y, octaves, persistence, lacunarity):
        """简化的噪声函数，模拟柏林噪声
        
        Args:
            x (float): x坐标
            y (float): y坐标
            octaves (int): 噪声叠加次数
            persistence (float): 每层噪声的影响程度
            lacunarity (float): 每层噪声的频率变化
            
        Returns:
            float: 噪声值
        """
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0
        
        for i in range(octaves):
            # 使用简单的sin函数组合模拟噪声
            # 实际项目中应使用专业的噪声库
            nx = x * frequency
            ny = y * frequency
            total += self._simplex(nx, ny) * amplitude
            
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value
    
    def _simplex(self, x, y):
        """简化的二维噪声函数
        
        Args:
            x (float): x坐标
            y (float): y坐标
            
        Returns:
            float: 噪声值
        """
        # 这是一个极度简化的噪声函数，仅用于演示
        # 实际项目中应使用专业的噪声库如noise或opensimplex
        value = np.sin(x * 12.9898 + y * 78.233) * 43758.5453
        return value - np.floor(value)
    
    def get_terrain_at(self, x, y):
        """获取指定坐标的地形类型
        
        Args:
            x (int): x坐标
            y (int): y坐标
            
        Returns:
            TerrainType: 地形类型
        """
        if self.terrain_map is None:
            self.generate_terrain_map()
            
        if 0 <= x < self.width and 0 <= y < self.height:
            return TerrainType(self.terrain_map[y][x])
        else:
            raise ValueError(f"坐标({x}, {y})超出地图范围")
    
    def get_terrain_cost_multiplier(self, terrain_type):
        """获取不同地形的建设成本倍数
        
        Args:
            terrain_type (TerrainType): 地形类型
            
        Returns:
            float: 建设成本倍数
        """
        cost_map = {
            TerrainType.PLAIN: 1.0,    # 平原基准成本
            TerrainType.HILL: 2.0,     # 丘陵成本翻倍
            TerrainType.MOUNTAIN: 5.0, # 山地成本是平原的5倍
            TerrainType.WATER: 10.0,   # 水域成本是平原的10倍(桥梁)
            TerrainType.FOREST: 1.5,   # 森林成本是平原的1.5倍
            TerrainType.DESERT: 1.2,   # 沙漠成本是平原的1.2倍
        }
        return cost_map.get(terrain_type, 1.0)
    
    def save_map(self, filename):
        """保存地形图到文件
        
        Args:
            filename (str): 文件名
        """
        if self.terrain_map is None:
            self.generate_terrain_map()
            
        # 保存地形图、高度图和湿度图
        np.savez(
            filename,
            terrain=self.terrain_map,
            elevation=self.elevation_map,
            moisture=self.moisture_map,
            width=self.width,
            height=self.height,
            seed=self.seed
        )
    
    @classmethod
    def load_map(cls, filename):
        """从文件加载地形图
        
        Args:
            filename (str): 文件名
            
        Returns:
            TerrainGenerator: 加载的地形生成器实例
        """
        data = np.load(filename)
        
        width = int(data['width'])
        height = int(data['height'])
        seed = int(data['seed'])
        
        generator = cls(width, height, seed)
        generator.terrain_map = data['terrain']
        generator.elevation_map = data['elevation']
        generator.moisture_map = data['moisture']
        
        return generator