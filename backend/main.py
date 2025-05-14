from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# 导入API路由
from api_service.company_api import router as company_router
from api_service.map_api import router as map_router
from api_service.contract_api import router as contract_router
from api_service.admin_api import router as admin_router

# 导入实时服务模块
from realtime_service.websocket_service import websocket_manager, websocket_endpoint
from realtime_service.event_handlers import game_event_system
from game_engine import GameEngine

# 创建FastAPI应用
app = FastAPI(
    title="TrainCompanyGame API",
    description="铁路大亨模拟器后端API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(company_router, prefix="/api/company", tags=["公司管理"])
app.include_router(map_router, prefix="/api/map", tags=["地图"])
app.include_router(contract_router, prefix="/api/contract", tags=["合同"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理"])

# 初始化游戏引擎
game_engine = GameEngine()

# 设置游戏事件系统的游戏引擎
game_event_system.set_game_engine(game_engine)

# 注册WebSocket路由
@app.websocket("/ws/{client_id}")
async def websocket_route(websocket: WebSocket, client_id: str):
    await websocket_endpoint(websocket, client_id)

@app.get("/")
async def root():
    return {"message": "欢迎使用铁路大亨模拟器API"}

# 启动事件处理器
@app.on_event("startup")
async def startup_event():
    # 启动WebSocket事件处理器
    asyncio.create_task(websocket_manager.start_event_processor())
    print("WebSocket事件处理器已启动")

# 关闭事件处理器
@app.on_event("shutdown")
async def shutdown_event():
    # 停止WebSocket事件处理器
    await websocket_manager.stop_event_processor()
    print("WebSocket事件处理器已关闭")

# 挂载静态文件服务
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)