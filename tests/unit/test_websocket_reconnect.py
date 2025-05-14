# WebSocket重连机制单元测试

import unittest
from unittest.mock import MagicMock, patch
import json

# 模拟浏览器WebSocket环境
class MockWebSocket:
    def __init__(self, url):
        self.url = url
        self.onopen = None
        self.onmessage = None
        self.onclose = None
        self.onerror = None
        self.readyState = 0  # 0: CONNECTING, 1: OPEN, 2: CLOSING, 3: CLOSED
    
    def close(self):
        self.readyState = 3
        if self.onclose:
            self.onclose(MagicMock())

class MockConsole:
    def __init__(self):
        self.log_messages = []
        self.error_messages = []
    
    def log(self, message):
        self.log_messages.append(message)
    
    def error(self, message):
        self.error_messages.append(message)

class MockWindow:
    def __init__(self):
        self.location = MagicMock()
        self.location.protocol = 'http:'
        self.location.host = 'localhost:8000'
        self.setTimeout = MagicMock()
        self.console = MockConsole()

class TestWebSocketReconnect(unittest.TestCase):
    """测试WebSocket重连机制"""
    
    def setUp(self):
        """测试前准备"""
        # 保存原始WebSocket类
        self.original_websocket = None
        self.mock_window = MockWindow()
        
        # 模拟计时器ID
        self.timeout_id = 123
        self.mock_window.setTimeout.return_value = self.timeout_id
    
    @patch('frontend.static.js.websocket.WebSocket', MockWebSocket)
    @patch('frontend.static.js.websocket.window', MockWindow())
    @patch('frontend.static.js.websocket.console', MockConsole())
    def test_websocket_connect(self):
        """测试WebSocket连接"""
        # 导入WebSocketManager类
        from frontend.static.js.websocket import WebSocketManager
        
        # 创建WebSocketManager实例
        ws_manager = WebSocketManager()
        
        # 连接WebSocket
        ws_manager.connect()
        
        # 验证WebSocket已创建
        self.assertIsNotNone(ws_manager.socket)
        self.assertFalse(ws_manager.connected)
        
        # 模拟连接成功
        ws_manager.socket.readyState = 1
        ws_manager.socket.onopen(MagicMock())
        
        # 验证连接状态
        self.assertTrue(ws_manager.connected)
        self.assertEqual(ws_manager.reconnectAttempts, 0)
    
    @patch('frontend.static.js.websocket.WebSocket', MockWebSocket)
    @patch('frontend.static.js.websocket.window', MockWindow())
    @patch('frontend.static.js.websocket.console', MockConsole())
    def test_websocket_reconnect(self):
        """测试WebSocket重连机制"""
        # 导入WebSocketManager类
        from frontend.static.js.websocket import WebSocketManager
        
        # 创建WebSocketManager实例
        ws_manager = WebSocketManager()
        ws_manager.maxReconnectAttempts = 3
        ws_manager.reconnectDelay = 1000
        
        # 连接WebSocket
        ws_manager.connect()
        
        # 模拟连接成功
        ws_manager.socket.readyState = 1
        ws_manager.socket.onopen(MagicMock())
        self.assertTrue(ws_manager.connected)
        
        # 模拟连接关闭
        original_socket = ws_manager.socket
        ws_manager.socket.onclose({"code": 1006, "reason": "连接断开"})
        
        # 验证重连状态
        self.assertFalse(ws_manager.connected)
        self.assertEqual(ws_manager.reconnectAttempts, 1)
        
        # 验证setTimeout被调用以尝试重连
        self.mock_window.setTimeout.assert_called_once()
    
    @patch('frontend.static.js.websocket.WebSocket', MockWebSocket)
    @patch('frontend.static.js.websocket.window', MockWindow())
    @patch('frontend.static.js.websocket.console', MockConsole())
    def test_max_reconnect_attempts(self):
        """测试最大重连尝试次数"""
        # 导入WebSocketManager类
        from frontend.static.js.websocket import WebSocketManager
        
        # 创建WebSocketManager实例
        ws_manager = WebSocketManager()
        ws_manager.maxReconnectAttempts = 2
        ws_manager.reconnectDelay = 1000
        
        # 连接WebSocket
        ws_manager.connect()
        
        # 模拟连接成功后多次断开
        ws_manager.socket.readyState = 1
        ws_manager.socket.onopen(MagicMock())
        
        # 第一次断开连接
        ws_manager.socket.onclose({"code": 1006, "reason": "连接断开"})
        self.assertEqual(ws_manager.reconnectAttempts, 1)
        
        # 第二次断开连接
        ws_manager.socket.onclose({"code": 1006, "reason": "连接断开"})
        self.assertEqual(ws_manager.reconnectAttempts, 2)
        
        # 第三次断开连接（超过最大尝试次数）
        ws_manager.socket.onclose({"code": 1006, "reason": "连接断开"})
        self.assertEqual(ws_manager.reconnectAttempts, 3)
        
        # 验证不再尝试重连
        self.assertEqual(self.mock_window.setTimeout.call_count, 2)

if __name__ == '__main__':
    unittest.main()