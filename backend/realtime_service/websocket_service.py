# WebSocket服务模块

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional, Callable
import json
import asyncio
from datetime import datetime

from ..game_engine import GameEngine

class GameEvent:
    """游戏事件类，用于定义游戏中的各种事件"""
    
    def __init__(self, event_type: str, data: Dict[str, Any], target_clients: Optional[List[str]] = None):
        """初始化游戏事件
        
        Args:
            event_type: 事件类型
            data: 事件数据
            target_clients: 目标客户端ID列表，None表示广播给所有客户端
        """
        self.event_type = event_type
        self.data = data
        self.target_clients = target_clients
        self.timestamp = datetime.now().isoformat()
    
    def to_json(self) -> str:
        """将事件转换为JSON字符串"""
        return json.dumps({
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp
        })

class WebSocketManager:
    """WebSocket连接管理器，负责管理所有WebSocket连接和事件分发"""
    
    def __init__(self, game_engine: Optional[GameEngine] = None):
        """初始化WebSocket管理器
        
        Args:
            game_engine: 游戏引擎实例
        """
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.game_engine = game_engine
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.running = False
    
    async def start_event_processor(self):
        """启动事件处理器"""
        self.running = True
        while self.running:
            try:
                event = await self.event_queue.get()
                await self.process_event(event)
                self.event_queue.task_done()
            except Exception as e:
                print(f"事件处理错误: {str(e)}")
    
    async def stop_event_processor(self):
        """停止事件处理器"""
        self.running = False
        # 等待队列中的所有事件处理完成
        await self.event_queue.join()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """处理新的WebSocket连接
        
        Args:
            websocket: WebSocket连接
            client_id: 客户端ID
        """
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        
        # 发送连接成功事件
        connect_event = GameEvent(
            "connection_established",
            {"client_id": client_id, "message": "连接成功"}
        )
        await self.send_personal_event(connect_event, client_id)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """处理WebSocket断开连接
        
        Args:
            websocket: WebSocket连接
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
    
    async def send_personal_event(self, event: GameEvent, client_id: str):
        """发送个人事件
        
        Args:
            event: 游戏事件
            client_id: 客户端ID
        """
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_text(event.to_json())
    
    async def broadcast_event(self, event: GameEvent):
        """广播事件给所有客户端
        
        Args:
            event: 游戏事件
        """
        for client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                await connection.send_text(event.to_json())
    
    async def process_event(self, event: GameEvent):
        """处理游戏事件
        
        Args:
            event: 游戏事件
        """
        # 如果有指定目标客户端，则只发送给目标客户端
        if event.target_clients:
            for client_id in event.target_clients:
                await self.send_personal_event(event, client_id)
        else:
            # 否则广播给所有客户端
            await self.broadcast_event(event)
        
        # 调用事件处理器
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"事件处理器错误: {str(e)}")
    
    async def queue_event(self, event: GameEvent):
        """将事件加入队列
        
        Args:
            event: 游戏事件
        """
        await self.event_queue.put(event)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def handle_client_message(self, client_id: str, message: str):
        """处理客户端消息
        
        Args:
            client_id: 客户端ID
            message: 消息内容
        """
        try:
            data = json.loads(message)
            if "event_type" in data and "data" in data:
                event = GameEvent(
                    event_type=data["event_type"],
                    data=data["data"],
                    target_clients=data.get("target_clients")
                )
                await self.queue_event(event)
            else:
                # 发送错误消息
                error_event = GameEvent(
                    "error",
                    {"message": "无效的消息格式", "original_message": message}
                )
                await self.send_personal_event(error_event, client_id)
        except json.JSONDecodeError:
            # 发送JSON解析错误
            error_event = GameEvent(
                "error",
                {"message": "无效的JSON格式", "original_message": message}
            )
            await self.send_personal_event(error_event, client_id)
        except Exception as e:
            # 发送通用错误
            error_event = GameEvent(
                "error",
                {"message": f"处理消息时发生错误: {str(e)}", "original_message": message}
            )
            await self.send_personal_event(error_event, client_id)

# 创建全局WebSocket管理器实例
websocket_manager = WebSocketManager()

# WebSocket路由处理函数
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点处理函数
    
    Args:
        websocket: WebSocket连接
        client_id: 客户端ID
    """
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_client_message(client_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, client_id)
        # 通知其他客户端有客户端断开连接
        disconnect_event = GameEvent(
            "client_disconnected",
            {"client_id": client_id}
        )
        await websocket_manager.queue_event(disconnect_event)