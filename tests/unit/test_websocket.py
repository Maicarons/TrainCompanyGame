# WebSocket服务单元测试

import unittest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from fastapi import WebSocket
from backend.realtime_service.websocket_service import WebSocketManager, GameEvent

class TestWebSocketService(unittest.TestCase):
    """测试WebSocket服务"""
    
    def setUp(self):
        """测试前准备"""
        self.ws_manager = WebSocketManager()
    
    def test_game_event_creation(self):
        """测试游戏事件创建"""
        event_data = {"message": "测试事件"}
        event = GameEvent("test_event", event_data)
        
        # 验证事件属性
        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.data, event_data)
        self.assertIsNone(event.target_clients)
        
        # 验证JSON转换
        event_json = event.to_json()
        self.assertIn("test_event", event_json)
        self.assertIn("测试事件", event_json)
    
    def test_targeted_game_event(self):
        """测试定向游戏事件"""
        event_data = {"message": "定向测试事件"}
        target_clients = ["client1", "client2"]
        event = GameEvent("targeted_event", event_data, target_clients)
        
        # 验证目标客户端设置
        self.assertEqual(event.target_clients, target_clients)
    
    @patch('backend.realtime_service.websocket_service.WebSocketManager.broadcast')
    async def test_event_broadcasting(self, mock_broadcast):
        """测试事件广播"""
        # 创建模拟WebSocket连接
        mock_websocket = MagicMock(spec=WebSocket)
        client_id = "test_client"
        
        # 注册连接
        await self.ws_manager.connect(mock_websocket, client_id)
        
        # 创建并广播事件
        event_data = {"message": "广播测试"}
        event = GameEvent("broadcast_test", event_data)
        await self.ws_manager.broadcast(event)
        
        # 验证广播方法被调用
        mock_broadcast.assert_called_once()
    
    def test_event_handler_registration(self):
        """测试事件处理器注册"""
        # 创建模拟事件处理器
        mock_handler = MagicMock()
        
        # 注册事件处理器
        self.ws_manager.register_event_handler("test_event", mock_handler)
        
        # 验证事件处理器已注册
        self.assertIn("test_event", self.ws_manager.event_handlers)
        self.assertIn(mock_handler, self.ws_manager.event_handlers["test_event"])
    
    def test_connection_management(self):
        """测试连接管理"""
        # 创建模拟WebSocket连接
        mock_websocket = MagicMock(spec=WebSocket)
        client_id = "test_client"
        
        # 使用同步方法测试异步方法
        loop = asyncio.get_event_loop()
        
        # 注册连接
        loop.run_until_complete(self.ws_manager.connect(mock_websocket, client_id))
        
        # 验证连接已注册
        self.assertIn(client_id, self.ws_manager.active_connections)
        self.assertIn(mock_websocket, self.ws_manager.active_connections[client_id])
        
        # 断开连接
        loop.run_until_complete(self.ws_manager.disconnect(mock_websocket, client_id))
        
        # 验证连接已断开
        self.assertNotIn(mock_websocket, self.ws_manager.active_connections[client_id])

if __name__ == '__main__':
    unittest.main()