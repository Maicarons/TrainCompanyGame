# 铁路网络生成器模块

import random
import numpy as np
from enum import Enum
from .terrain_generator import TerrainType, TerrainGenerator
from .city_generator import City, CityGenerator, CitySize

class RailwayType(Enum):
    """铁路类型枚举"""
    LOCAL = 0       # 地方铁路
    REGIONAL = 1    # 区域铁路
    NATIONAL = 2    # 国家铁路
    HIGH_SPEED = 3  # 高速铁路

class RailwayStation:
    """铁路站点类"""
    
    def __init__(self, name, x, y, city=None, station_type=None):
        """初始化铁路站点
        
        Args:
            name (str): 站点名称
            x (int): x坐标
            y (int): y坐标
            city (City, optional): 关联的城市
            station_type (RailwayType, optional): 站点类型
        """
        self.name = name
        self.x = x
        self.y = y
        self.city = city
        self.station_type = station_type or RailwayType.LOCAL
        self.connections = []  # 与其他站点的连接
        self.passenger_traffic = 0  # 客运量
        self.cargo_traffic = 0      # 货运量
    
    def add_connection(self, other_station, railway_type, distance):
        """添加与其他站点的连接
        
        Args:
            other_station (RailwayStation): 连接的站点
            railway_type (RailwayType): 铁路类型
            distance (float): 两站点间的距离
        """
        self.connections.append({
            'station': other_station,
            'type': railway_type,
            'distance': distance
        })
    
    def calculate_traffic(self):
        """计算站点的客运和货运量"""
        # 如果站点关联了城市，根据城市规模和类型计算交通量
        if self.city:
            # 根据城市人口计算客运量
            population = self.city.population
            size_multiplier = {
                CitySize.VILLAGE: 0.05,
                CitySize.TOWN: 0.1,
                CitySize.CITY: 0.2,
                CitySize.METROPOLIS: 0.3
            }
            self.passenger_traffic = population * size_multiplier[self.city.size]
            
            # 根据城市资源和需求计算货运量
            total_resources = sum(self.city.resources.values())
            total_demand = sum(self.city.demand.values())
            self.cargo_traffic = (total_resources + total_demand) * 0.5
        else:
            # 对于不关联城市的站点，设置较低的交通量
            self.passenger_traffic = random.randint(100, 1000)
            self.cargo_traffic = random.randint(50, 500)

class RailwayLine:
    """铁路线路类"""
    
    def __init__(self, name, railway_type, stations=None):
        """初始化铁路线路
        
        Args:
            name (str): 线路名称
            railway_type (RailwayType): 铁路类型
            stations (list, optional): 线路经过的站点列表
        """
        self.name = name
        self.railway_type = railway_type
        self.stations = stations or []
        self.total_length = 0  # 线路总长度
        self.construction_cost = 0  # 建设成本
        self.maintenance_cost = 0  # 维护成本
        self.path_segments = []  # 线路路径段
    
    def add_station(self, station):
        """添加站点到线路
        
        Args:
            station (RailwayStation): 要添加的站点
        """
        self.stations.append(station)
    
    def calculate_path(self, terrain_generator):
        """计算线路的具体路径
        
        Args:
            terrain_generator (TerrainGenerator): 地形生成器实例
        """
        self.path_segments = []
        self.total_length = 0
        
        # 如果站点少于2个，无法形成线路
        if len(self.stations) < 2:
            return
        
        # 计算相邻站点之间的路径
        for i in range(len(self.stations) - 1):
            start = self.stations[i]
            end = self.stations[i + 1]
            
            # 计算直线距离
            dx = end.x - start.x
            dy = end.y - start.y
            distance = (dx**2 + dy**2)**0.5
            
            # 创建路径段
            segment = {
                'start': start,
                'end': end,
                'distance': distance,
                'path': self._calculate_path_between(start, end, terrain_generator)
            }
            
            self.path_segments.append(segment)
            self.total_length += distance
        
        # 计算建设和维护成本
        self._calculate_costs(terrain_generator)
    
    def _calculate_path_between(self, start, end, terrain_generator):
        """计算两站点之间的具体路径
        
        Args:
            start (RailwayStation): 起始站点
            end (RailwayStation): 终点站点
            terrain_generator (TerrainGenerator): 地形生成器实例
            
        Returns:
            list: 路径点列表
        """
        # 这里使用简化的直线路径
        # 实际项目中可以使用A*或其他寻路算法，考虑地形因素
        path = []
        
        # 添加起点
        path.append((start.x, start.y))
        
        # 计算中间点（简化为直线上的点）
        steps = max(abs(end.x - start.x), abs(end.y - start.y))
        if steps > 0:
            for i in range(1, steps):
                t = i / steps
                x = int(start.x + (end.x - start.x) * t)
                y = int(start.y + (end.y - start.y) * t)
                path.append((x, y))
        
        # 添加终点
        path.append((end.x, end.y))
        
        return path
    
    def _calculate_costs(self, terrain_generator):
        """计算线路的建设和维护成本
        
        Args:
            terrain_generator (TerrainGenerator): 地形生成器实例
        """
        # 基础成本系数
        base_construction_cost = {
            RailwayType.LOCAL: 100,
            RailwayType.REGIONAL: 200,
            RailwayType.NATIONAL: 300,
            RailwayType.HIGH_SPEED: 500
        }
        
        base_maintenance_cost = {
            RailwayType.LOCAL: 10,
            RailwayType.REGIONAL: 20,
            RailwayType.NATIONAL: 30,
            RailwayType.HIGH_SPEED: 50
        }
        
        total_construction = 0
        total_maintenance = 0
        
        # 计算每个路径段的成本
        for segment in self.path_segments:
            path = segment['path']
            segment_construction = 0
            segment_maintenance = 0
            
            # 计算路径上每个点的成本
            for x, y in path:
                # 确保坐标在地图范围内
                if 0 <= x < terrain_generator.width and 0 <= y < terrain_generator.height:
                    terrain = terrain_generator.get_terrain_at(x, y)
                    cost_multiplier = terrain_generator.get_terrain_cost_multiplier(terrain)
                    
                    # 累加建设和维护成本
                    segment_construction += base_construction_cost[self.railway_type] * cost_multiplier
                    segment_maintenance += base_maintenance_cost[self.railway_type] * cost_multiplier
            
            # 将段成本添加到总成本
            total_construction += segment_construction
            total_maintenance += segment_maintenance
        
        self.construction_cost = total_construction
        self.maintenance_cost = total_maintenance

class RailwayNetworkGenerator:
    """铁路网络生成器类"""
    
    def __init__(self, terrain_generator, city_generator, seed=None):
        """初始化铁路网络生成器
        
        Args:
            terrain_generator (TerrainGenerator): 地形生成器实例
            city_generator (CityGenerator): 城市生成器实例
            seed (int, optional): 随机种子
        """
        self.terrain_generator = terrain_generator
        self.city_generator = city_generator
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.stations = []  # 所有站点
        self.lines = []     # 所有线路
        
        # 设置随机种子
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def generate_stations(self):
        """为城市生成铁路站点
        
        Returns:
            list: 生成的站点列表
        """
        # 为每个城市创建站点
        for city in self.city_generator.cities:
            # 根据城市规模确定站点类型
            station_type = self._determine_station_type(city)
            
            # 创建主站点
            station_name = city.name + "站"
            main_station = RailwayStation(station_name, city.x, city.y, city, station_type)
            self.stations.append(main_station)
            
            # 对于大城市，可能有多个站点
            if city.size in [CitySize.CITY, CitySize.METROPOLIS]:
                num_extra_stations = 1 if city.size == CitySize.CITY else 2
                
                for i in range(num_extra_stations):
                    # 在城市周围随机位置创建额外站点
                    offset_x = random.randint(-3, 3)
                    offset_y = random.randint(-3, 3)
                    x = max(0, min(city.x + offset_x, self.terrain_generator.width - 1))
                    y = max(0, min(city.y + offset_y, self.terrain_generator.height - 1))
                    
                    # 检查地形是否适合建站
                    terrain = self.terrain_generator.get_terrain_at(x, y)
                    if terrain not in [TerrainType.WATER, TerrainType.MOUNTAIN]:
                        sub_name = city.name + ["东", "南", "西", "北", "中"][i % 5] + "站"
                        sub_station = RailwayStation(sub_name, x, y, city, RailwayType.LOCAL)
                        self.stations.append(sub_station)
        
        # 计算每个站点的交通量
        for station in self.stations:
            station.calculate_traffic()
        
        return self.stations
    
    def generate_railway_network(self):
        """生成铁路网络
        
        Returns:
            list: 生成的铁路线路列表
        """
        # 确保已经生成站点
        if not self.stations:
            self.generate_stations()
        
        # 生成主干线路
        self._generate_main_lines()
        
        # 生成区域线路
        self._generate_regional_lines()
        
        # 生成地方线路
        self._generate_local_lines()
        
        # 计算所有线路的路径和成本
        for line in self.lines:
            line.calculate_path(self.terrain_generator)
        
        return self.lines
    
    def _determine_station_type(self, city):
        """根据城市规模确定站点类型
        
        Args:
            city (City): 城市实例
            
        Returns:
            RailwayType: 站点类型
        """
        if city.size == CitySize.METROPOLIS:
            return RailwayType.HIGH_SPEED
        elif city.size == CitySize.CITY:
            return RailwayType.NATIONAL
        elif city.size == CitySize.TOWN:
            return RailwayType.REGIONAL
        else:  # VILLAGE
            return RailwayType.LOCAL
    
    def _generate_main_lines(self):
        """生成主干线路"""
        # 找出所有大城市和特大城市的站点
        major_stations = [s for s in self.stations if s.city and s.city.size in [CitySize.CITY, CitySize.METROPOLIS]]
        
        if len(major_stations) < 2:
            return  # 大城市太少，无法形成主干网络
        
        # 创建高速铁路网络
        high_speed_stations = [s for s in major_stations if s.station_type == RailwayType.HIGH_SPEED]
        if len(high_speed_stations) >= 2:
            # 创建高铁线路
            line_name = "高速铁路干线"
            line = RailwayLine(line_name, RailwayType.HIGH_SPEED, high_speed_stations)
            self.lines.append(line)
            
            # 添加站点间连接
            for i, station in enumerate(high_speed_stations):
                for j, other in enumerate(high_speed_stations):
                    if i != j:
                        dx = abs(station.x - other.x)
                        dy = abs(station.y - other.y)
                        distance = (dx**2 + dy**2)**0.5
                        station.add_connection(other, RailwayType.HIGH_SPEED, distance)
        
        # 创建国家铁路网络
        national_stations = [s for s in major_stations if s.station_type in [RailwayType.NATIONAL, RailwayType.HIGH_SPEED]]
        if len(national_stations) >= 2:
            # 创建国铁线路
            line_name = "国家铁路干线"
            line = RailwayLine(line_name, RailwayType.NATIONAL, national_stations)
            self.lines.append(line)
            
            # 添加站点间连接
            for i, station in enumerate(national_stations):
                for j, other in enumerate(national_stations):
                    if i != j:
                        dx = abs(station.x - other.x)
                        dy = abs(station.y - other.y)
                        distance = (dx**2 + dy**2)**0.5
                        station.add_connection(other, RailwayType.NATIONAL, distance)
    
    def _generate_regional_lines(self):
        """生成区域线路"""
        # 找出所有中小城市的站点
        regional_stations = [s for s in self.stations if s.city and s.city.size in [CitySize.TOWN]]
        major_stations = [s for s in self.stations if s.city and s.city.size in [CitySize.CITY, CitySize.METROPOLIS]]
        
        # 将区域站点分组，每组连接到最近的主要站点
        for major in major_stations:
            nearby_stations = []
            
            # 找出距离该主要站点较近的区域站点
            for regional in regional_stations:
                dx = abs(regional.x - major.x)
                dy = abs(regional.y - major.y)
                distance = (dx**2 + dy**2)**0.5
                
                if distance < 30:  # 距离阈值
                    nearby_stations.append((regional, distance))
            
            # 按距离排序
            nearby_stations.sort(key=lambda x: x[1])
            
            # 取最近的几个站点创建区域线路
            if len(nearby_stations) >= 2:
                line_stations = [major] + [s[0] for s in nearby_stations[:5]]  # 限制每条线路的站点数
                line_name = major.city.name + "区域线"
                line = RailwayLine(line_name, RailwayType.REGIONAL, line_stations)
                self.lines.append(line)
                
                # 添加站点间连接
                for station in line_stations:
                    for other in line_stations:
                        if station != other:
                            dx = abs(station.x - other.x)
                            dy = abs(station.y - other.y)
                            distance = (dx**2 + dy**2)**0.5
                            station.add_connection(other, RailwayType.REGIONAL, distance)
    
    def _generate_local_lines(self):
        """生成地方线路"""
        # 找出所有小村庄的站点
        local_stations = [s for s in self.stations if s.city and s.city.size == CitySize.VILLAGE]
        town_stations = [s for s in self.stations if s.city and s.city.size == CitySize.TOWN]
        
        # 将地方站点连接到最近的小镇站点
        for town in town_stations:
            nearby_stations = []
            
            # 找出距离该小镇站点较近的地方站点
            for local in local_stations:
                dx = abs(local.x - town.x)
                dy = abs(local.y - town.y)
                distance = (dx**2 + dy**2)**0.5
                
                if distance < 20:  # 距离阈值
                    nearby_stations.append((local, distance))
            
            # 按距离排序
            nearby_stations.sort(key=lambda x: x[1])
            
            # 取最近的几个站点创建地方线路
            if len(nearby_stations) >= 1:
                line_stations = [town] + [s[0] for s in nearby_stations[:3]]  # 限制每条线路的站点数
                line_name = town.city.name + "地方线"
                line = RailwayLine(line_name, RailwayType.LOCAL, line_stations)
                self.lines.append(line)
                
                # 添加站点间连接
                for station in line_stations:
                    for other in line_stations:
                        if station != other:
                            dx = abs(station.x - other.x)
                            dy = abs(station.y - other.y)
                            distance = (dx**2 + dy**2)**0.5
                            station.add_connection(other, RailwayType.LOCAL, distance)
    
    def get_station_at(self, x, y, tolerance=2):
        """获取指定坐标附近的站点
        
        Args:
            x (int): x坐标
            y (int): y坐标
            tolerance (int): 容差范围
            
        Returns:
            RailwayStation: 找到的站点，如果没有则返回None
        """
        for station in self.stations:
            dx = abs(station.x - x)
            dy = abs(station.y - y)
            if dx <= tolerance and dy <= tolerance:
                return station
        return None
    
    def save_network(self, filename):
        """保存铁路网络数据到文件
        
        Args:
            filename (str): 文件名
        """
        # 将站点数据转换为可序列化的格式
        station_data = []
        for i, station in enumerate(self.stations):
            connections = [{
                'station_index': self.stations.index(conn['station']),
                'type': conn['type'].value,
                'distance': conn['distance']
            } for conn in station.connections]
            
            station_data.append({
                'name': station.name,
                'x': station.x,
                'y': station.y,
                'city_index': self.city_generator.cities.index(station.city) if station.city else -1,
                'type': station.station_type.value,
                'connections': connections,
                'passenger_traffic': station.passenger_traffic,
                'cargo_traffic': station.cargo_traffic
            })
        
        # 将线路数据转换为可序列化的格式
        line_data = []
        for line in self.lines:
            stations_indices = [self.stations.index(station) for station in line.stations]
            
            path_segments = []
            for segment in line.path_segments:
                path_segments.append({
                    'start_index': self.stations.index(segment['start']),
                    'end_index': self.stations.index(segment['end']),
                    'distance': segment['distance'],
                    'path': segment['path']
                })
            
            line_data.append({
                'name': line.name,
                'type': line.railway_type.value,
                'stations': stations_indices,
                'total_length': line.total_length,
                'construction_cost': line.construction_cost,
                'maintenance_cost': line.maintenance_cost,
                'path_segments': path_segments
            })
        
        # 保存数据
        np.savez(
            filename,
            stations=station_data,
            lines=line_data,
            seed=self.seed
        )
    
    @classmethod
    def load_network(cls, filename, terrain_generator, city_generator):
        """从文件加载铁路网络数据
        
        Args:
            filename (str): 文件名
            terrain_generator (TerrainGenerator): 地形生成器实例
            city_generator (CityGenerator): 城市生成器实例
            
        Returns:
            RailwayNetworkGenerator: 铁路网络生成器实例
        """
        data = np.load(filename, allow_pickle=True)
        station_data = data['stations']
        line_data = data['lines']
        seed = int(data['seed'])
        
        # 创建铁路网络生成器
        generator = cls(terrain_generator, city_generator, seed)
        
        # 重建站点
        for station_info in station_data:
            city = None
            if station_info['city_index'] >= 0:
                city = city_generator.cities[station_info['city_index']]
            
            station = RailwayStation(
                station_info['name'],
                int(station_info['x']),
                int(station_info['y']),
                city,
                RailwayType(station_info['type'])
            )
            station.passenger_traffic = float(station_info['passenger_traffic'])
            station.cargo_traffic = float(station_info['cargo_traffic'])
            generator.stations.append(station)
        
        # 重建站点连接
        for i, station_info in enumerate(station_data):
            for conn in station_info['connections']:
                station_index = int(conn['station_index'])
                railway_type = RailwayType(conn['type'])
                distance = float(conn['distance'])
                generator.stations[i].add_connection(generator.stations[station_index], railway_type, distance)
        
        # 重建线路
        for line_info in line_data:
            station_indices = line_info['stations']
            stations = [generator.stations[idx] for idx in station_indices]
            
            line = RailwayLine(
                line_info['name'],
                RailwayType(line_info['type']),
                stations
            )
            line.total_length = float(line_info['total_length'])
            line.construction_cost = float(line_info['construction_cost'])
            line.maintenance_cost = float(line_info['maintenance_cost'])
            
            # 重建路径段
            for segment in line_info['path_segments']:
                start_index = int(segment['start_index'])
                end_index = int(segment['end_index'])
                
                path_segment = {
                    'start': generator.stations[start_index],
                    'end': generator.stations[end_index],
                    'distance': float(segment['distance']),
                    'path': segment['path'].tolist()
                }
                line.path_segments.append(path_segment)
            
            generator.lines.append(line)
        
        return generator