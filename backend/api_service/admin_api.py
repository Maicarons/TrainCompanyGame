from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..models.company import Company, Group
from ..models.map import Map
from ..models.contract import Contract

# 创建路由器
router = APIRouter()

# 管理员数据模型
from pydantic import BaseModel, Field
from enum import Enum

class GameStatusResponse(BaseModel):
    active_users: int
    total_companies: int
    active_contracts: int
    server_uptime: str
    current_game_day: int
    current_season: int
    next_backup_time: datetime

class GameSettingsUpdate(BaseModel):
    game_tick_interval: Optional[int] = None
    backup_interval: Optional[int] = None
    max_companies_per_user: Optional[int] = None
    max_group_size: Optional[int] = None
    economic_difficulty: Optional[float] = None

# 获取游戏状态
@router.get("/status", response_model=GameStatusResponse)
async def get_game_status(db: Session = Depends(get_db)):
    # 获取活跃用户数
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 获取公司总数
    total_companies = db.query(Company).count()
    
    # 获取活跃合同数
    active_contracts = db.query(Contract).filter(Contract.status == "ACTIVE").count()
    
    # 获取服务器运行时间（模拟数据）
    import time
    server_uptime = "3天12小时34分钟"
    
    # 获取当前游戏日和赛季（模拟数据）
    current_game_day = 7
    current_season = 1
    
    # 获取下次备份时间（模拟数据）
    next_backup_time = datetime.now()
    
    return {
        "active_users": active_users,
        "total_companies": total_companies,
        "active_contracts": active_contracts,
        "server_uptime": server_uptime,
        "current_game_day": current_game_day,
        "current_season": current_season,
        "next_backup_time": next_backup_time
    }

# 更新游戏设置
@router.put("/settings", response_model=dict)
async def update_game_settings(settings: GameSettingsUpdate):
    # 在实际应用中，这里应该更新配置文件或数据库中的设置
    # 这里只是模拟返回
    return {
        "status": "success",
        "message": "游戏设置已更新",
        "updated_settings": settings.dict(exclude_unset=True)
    }

# 手动备份游戏状态
@router.post("/backup", response_model=dict)
async def backup_game_state(background_tasks: BackgroundTasks):
    # 在后台任务中执行备份
    background_tasks.add_task(perform_backup)
    
    return {
        "status": "success",
        "message": "游戏状态备份已开始",
        "backup_id": "backup_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    }

# 模拟备份函数
def perform_backup():
    # 在实际应用中，这里应该执行实际的备份逻辑
    import time
    time.sleep(5)  # 模拟备份过程
    print("备份完成")

# 获取所有用户
@router.get("/users", response_model=List[dict])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    
    return [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "level": user.level,
        "total_games": user.total_games,
        "created_at": user.created_at
    } for user in users]

# 更新用户角色
@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(user_id: int, role: str, db: Session = Depends(get_db)):
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新角色
    try:
        user.role = UserRole(role)
        db.commit()
        return {"status": "success", "message": f"用户 {user.username} 的角色已更新为 {role}"}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效的角色: {role}")

# 禁用/启用用户
@router.put("/users/{user_id}/status", response_model=dict)
async def update_user_status(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新状态
    user.is_active = is_active
    db.commit()
    
    status_str = "启用" if is_active else "禁用"
    return {"status": "success", "message": f"用户 {user.username} 已{status_str}"}

# 获取系统日志（模拟数据）
@router.get("/logs", response_model=List[dict])
async def get_system_logs(log_type: Optional[str] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    # 在实际应用中，这里应该从日志文件或数据库中获取日志
    # 这里只是返回模拟数据
    logs = [
        {
            "id": 1,
            "timestamp": datetime.now(),
            "level": "INFO",
            "source": "system",
            "message": "系统启动"
        },
        {
            "id": 2,
            "timestamp": datetime.now(),
            "level": "WARNING",
            "source": "database",
            "message": "数据库连接池接近上限"
        },
        {
            "id": 3,
            "timestamp": datetime.now(),
            "level": "ERROR",
            "source": "api",
            "message": "API请求失败: 404 Not Found"
        }
    ]
    
    # 根据参数过滤日志
    if log_type:
        logs = [log for log in logs if log["level"] == log_type.upper()]
    
    if start_date:
        logs = [log for log in logs if log["timestamp"] >= start_date]
    
    if end_date:
        logs = [log for log in logs if log["timestamp"] <= end_date]
    
    return logs

# 重置游戏（开始新赛季）
@router.post("/reset-game", response_model=dict)
async def reset_game(background_tasks: BackgroundTasks):
    # 在后台任务中执行游戏重置
    background_tasks.add_task(perform_game_reset)
    
    return {
        "status": "success",
        "message": "游戏重置已开始，新赛季即将开始",
        "reset_id": "reset_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    }

# 模拟游戏重置函数
def perform_game_reset():
    # 在实际应用中，这里应该执行实际的游戏重置逻辑
    import time
    time.sleep(10)  # 模拟重置过程
    print("游戏重置完成，新赛季已开始")

# 获取系统性能指标（模拟数据）
@router.get("/performance", response_model=dict)
async def get_system_performance():
    # 在实际应用中，这里应该获取实际的系统性能指标
    # 这里只是返回模拟数据
    return {
        "cpu_usage": 45.2,  # 百分比
        "memory_usage": 3.7,  # GB
        "disk_usage": 78.5,  # 百分比
        "network_in": 1.2,  # MB/s
        "network_out": 0.8,  # MB/s
        "active_connections": 32,
        "request_rate": 15.3  # 请求/秒
    }