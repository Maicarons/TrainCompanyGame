from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from ..database import Base

# 地形类型枚举
class TerrainType(enum.Enum):
    PLAIN = "平原"
    HILL = "丘陵"
    MOUNTAIN = "山地"
    WATER = "水域"
    FOREST = "森林"
    DESERT = "沙漠"
    SNOW = "雪地"
    URBAN = "城市"

# 地图模型
class Map(Base):
    __tablename__ = "maps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # 地图属性
    width = Column(Integer)  # 地图宽度
    height = Column(Integer)  # 地图高度
    seed = Column(Integer)  # 生成种子
    is_active = Column(Boolean, default=True)
    
    # 地图特定属性
    properties = Column(JSON, nullable=True)
    
    # 关系
    tiles = relationship("MapTile", back_populates="map")
    cities = relationship("City", back_populates="map")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Map {self.name} ({self.width}x{self.height})>"

# 地图瓦片模型
class MapTile(Base):
    __tablename__ = "map_tiles"
    
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer)  # X坐标
    y = Column(Integer)  # Y坐标
    terrain_type = Column(Enum(TerrainType))
    elevation = Column(Float, default=0.0)  # 海拔高度
    
    # 瓦片特定属性
    properties = Column(JSON, nullable=True)
    
    # 所属地图
    map_id = Column(Integer, ForeignKey("maps.id"))
    map = relationship("Map", back_populates="tiles")
    
    # 关系
    railways = relationship("Railway", back_populates="tile")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MapTile ({self.x},{self.y}) {self.terrain_type.value}>"

# 城市模型
class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    population = Column(Integer, default=10000)  # 人口
    economic_level = Column(Float, default=50.0)  # 经济水平(0-100)
    
    # 位置
    x = Column(Integer)  # X坐标
    y = Column(Integer)  # Y坐标
    
    # 城市特定属性
    properties = Column(JSON, nullable=True)
    
    # 所属地图
    map_id = Column(Integer, ForeignKey("maps.id"))
    map = relationship("Map", back_populates="cities")
    
    # 关系
    stations = relationship("Station", back_populates="city")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<City {self.name} (人口: {self.population})>"

# 铁路模型
class Railway(Base):
    __tablename__ = "railways"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    railway_level = Column(Integer, default=1)  # 铁路等级(1-5)
    is_electrified = Column(Boolean, default=False)  # 是否电气化
    length = Column(Float)  # 长度(公里)
    
    # 铁路特定属性
    properties = Column(JSON, nullable=True)
    
    # 所属瓦片
    tile_id = Column(Integer, ForeignKey("map_tiles.id"))
    tile = relationship("MapTile", back_populates="railways")
    
    # 所属公司
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company")
    
    # 起点和终点站
    start_station_id = Column(Integer, ForeignKey("stations.id"))
    end_station_id = Column(Integer, ForeignKey("stations.id"))
    start_station = relationship("Station", foreign_keys=[start_station_id])
    end_station = relationship("Station", foreign_keys=[end_station_id])
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Railway {self.name or 'Unnamed'} (等级: {self.railway_level})>"

# 车站模型
class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    station_level = Column(Integer, default=1)  # 车站等级
    platforms = Column(Integer, default=1)  # 站台数量
    tracks = Column(Integer, default=1)  # 股道数量
    
    # 车站特定属性
    properties = Column(JSON, nullable=True)
    
    # 所属城市
    city_id = Column(Integer, ForeignKey("cities.id"))
    city = relationship("City", back_populates="stations")
    
    # 所属公司
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Station {self.name} (等级: {self.station_level})>"