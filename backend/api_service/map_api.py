from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.map import Map, MapTile, City, Railway, Station, TerrainType
from ..models.company import Company

# 创建路由器
router = APIRouter()

# 地图数据模型
from pydantic import BaseModel, Field
from enum import Enum

class TerrainTypeEnum(str, Enum):
    PLAIN = "平原"
    HILL = "丘陵"
    MOUNTAIN = "山地"
    WATER = "水域"
    FOREST = "森林"
    DESERT = "沙漠"
    SNOW = "雪地"
    URBAN = "城市"

class MapCreate(BaseModel):
    name: str
    width: int
    height: int
    seed: int
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class MapUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None

class MapResponse(BaseModel):
    id: int
    name: str
    width: int
    height: int
    seed: int
    description: Optional[str] = None
    is_active: bool
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class CityCreate(BaseModel):
    name: str
    population: int
    economic_level: float
    x: int
    y: int
    map_id: int
    properties: Optional[Dict[str, Any]] = None

class CityResponse(BaseModel):
    id: int
    name: str
    population: int
    economic_level: float
    x: int
    y: int
    map_id: int
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 获取所有地图
@router.get("/", response_model=List[MapResponse])
async def get_maps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    maps = db.query(Map).offset(skip).limit(limit).all()
    return maps

# 获取单个地图
@router.get("/{map_id}", response_model=MapResponse)
async def get_map(map_id: int, db: Session = Depends(get_db)):
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if map_obj is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    return map_obj

# 创建地图
@router.post("/", response_model=MapResponse, status_code=status.HTTP_201_CREATED)
async def create_map(map_data: MapCreate, db: Session = Depends(get_db)):
    # 创建地图对象
    db_map = Map(
        name=map_data.name,
        width=map_data.width,
        height=map_data.height,
        seed=map_data.seed,
        description=map_data.description,
        properties=map_data.properties
    )
    
    # 保存到数据库
    db.add(db_map)
    db.commit()
    db.refresh(db_map)
    
    # 触发地图生成任务
    from ..game_engine.world_generator.tasks import generate_map_tiles
    generate_map_tiles.delay(db_map.id)
    
    return db_map

# 更新地图
@router.put("/{map_id}", response_model=MapResponse)
async def update_map(map_id: int, map_data: MapUpdate, db: Session = Depends(get_db)):
    # 查找地图
    db_map = db.query(Map).filter(Map.id == map_id).first()
    if db_map is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    
    # 更新地图信息
    if map_data.name is not None:
        db_map.name = map_data.name
    if map_data.description is not None:
        db_map.description = map_data.description
    if map_data.is_active is not None:
        db_map.is_active = map_data.is_active
    if map_data.properties is not None:
        db_map.properties = map_data.properties
    
    # 保存到数据库
    db.commit()
    db.refresh(db_map)
    
    return db_map

# 删除地图
@router.delete("/{map_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_map(map_id: int, db: Session = Depends(get_db)):
    # 查找地图
    db_map = db.query(Map).filter(Map.id == map_id).first()
    if db_map is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    
    # 删除地图
    db.delete(db_map)
    db.commit()
    
    return {"status": "success"}

# 获取地图瓦片
@router.get("/{map_id}/tiles", response_model=List[dict])
async def get_map_tiles(map_id: int, x_min: int = 0, y_min: int = 0, 
                       x_max: Optional[int] = None, y_max: Optional[int] = None, 
                       db: Session = Depends(get_db)):
    # 查找地图
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if map_obj is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    
    # 设置默认值
    if x_max is None:
        x_max = map_obj.width - 1
    if y_max is None:
        y_max = map_obj.height - 1
    
    # 获取瓦片
    tiles = db.query(MapTile).filter(
        MapTile.map_id == map_id,
        MapTile.x >= x_min,
        MapTile.x <= x_max,
        MapTile.y >= y_min,
        MapTile.y <= y_max
    ).all()
    
    return [{
        "id": tile.id,
        "x": tile.x,
        "y": tile.y,
        "terrain_type": tile.terrain_type.value,
        "elevation": tile.elevation,
        "properties": tile.properties
    } for tile in tiles]

# 获取地图城市
@router.get("/{map_id}/cities", response_model=List[CityResponse])
async def get_map_cities(map_id: int, db: Session = Depends(get_db)):
    # 查找地图
    map_obj = db.query(Map).filter(Map.id == map_id).first()
    if map_obj is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    
    # 获取城市
    cities = db.query(City).filter(City.map_id == map_id).all()
    
    return cities

# 创建城市
@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(city_data: CityCreate, db: Session = Depends(get_db)):
    # 检查地图是否存在
    map_obj = db.query(Map).filter(Map.id == city_data.map_id).first()
    if map_obj is None:
        raise HTTPException(status_code=404, detail="地图不存在")
    
    # 创建城市对象
    db_city = City(
        name=city_data.name,
        population=city_data.population,
        economic_level=city_data.economic_level,
        x=city_data.x,
        y=city_data.y,
        map_id=city_data.map_id,
        properties=city_data.properties
    )
    
    # 保存到数据库
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    
    return db_city

# 获取单个城市
@router.get("/cities/{city_id}", response_model=CityResponse)
async def get_city(city_id: int, db: Session = Depends(get_db)):
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail="城市不存在")
    return city

# 获取城市车站
@router.get("/cities/{city_id}/stations", response_model=List[dict])
async def get_city_stations(city_id: int, db: Session = Depends(get_db)):
    # 查找城市
    city = db.query(City).filter(City.id == city_id).first()
    if city is None:
        raise HTTPException(status_code=404, detail="城市不存在")
    
    # 获取车站
    stations = db.query(Station).filter(Station.city_id == city_id).all()
    
    return [{
        "id": station.id,
        "name": station.name,
        "station_level": station.station_level,
        "platforms": station.platforms,
        "tracks": station.tracks,
        "company_id": station.company_id,
        "properties": station.properties
    } for station in stations]

# 获取铁路网络
@router.get("/railways", response_model=List[dict])
async def get_railways(company_id: Optional[int] = None, db: Session = Depends(get_db)):
    # 构建查询
    query = db.query(Railway)
    
    # 如果指定了公司ID，则过滤
    if company_id is not None:
        query = query.filter(Railway.company_id == company_id)
    
    # 获取铁路
    railways = query.all()
    
    return [{
        "id": railway.id,
        "name": railway.name,
        "railway_level": railway.railway_level,
        "is_electrified": railway.is_electrified,
        "length": railway.length,
        "company_id": railway.company_id,
        "start_station_id": railway.start_station_id,
        "end_station_id": railway.end_station_id,
        "properties": railway.properties
    } for railway in railways]