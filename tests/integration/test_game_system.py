# 游戏系统集成测试

import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend.game_engine.game_state import GameState
from backend.game_engine.economy.economy_manager import EconomyManager
from backend.realtime_service.websocket_service import WebSocketManager, GameEvent

class TestGameSystemIntegration(unittest.TestCase):
    """测试游戏系统集成功能"""
    
    def setUp(self):
        """测试前准备"""
        # 初始化游戏状态
        self.game_state = GameState(seed=12345)
        
        # 初始化经济系统
        self.economy_manager = EconomyManager(seed=12345)
        self.game_state.economy_manager = self.economy_manager
        
        # 初始化WebSocket管理器
        self.ws_manager = WebSocketManager()
    
    def test_game_state_economy_integration(self):
        """测试游戏状态与经济系统集成"""
        # 设置游戏为非暂停状态
        self.game_state.paused = False
        
        # 记录初始经济指标
        initial_inflation = self.economy_manager.inflation_rate
        initial_interest = self.economy_manager.interest_rate
        
        # 模拟游戏时间推进（一个月）
        for _ in range(30):
            self.game_state.update(timedelta(days=1).total_seconds())
        
        # 验证经济系统已更新
        self.assertNotEqual(self.economy_manager.inflation_rate, initial_inflation)
        self.assertNotEqual(self.economy_manager.interest_rate, initial_interest)
    
    @patch('backend.realtime_service.websocket_service.WebSocketManager.broadcast')
    async def test_economy_events_websocket_integration(self, mock_broadcast):
        """测试经济事件与WebSocket集成"""
        # 生成经济事件
        current_time = datetime(2023, 1, 1)
        events = self.economy_manager.generate_economic_events(current_time, timedelta(days=90))
        
        # 通过WebSocket广播事件
        for event_data in events:
            game_event = GameEvent("economy_event", event_data)
            await self.ws_manager.broadcast(game_event)
        
        # 验证广播方法被调用了正确的次数
        self.assertEqual(mock_broadcast.call_count, len(events))
    
    def test_game_state_serialization(self):
        """测试游戏状态序列化与反序列化"""
        # 设置游戏状态
        self.game_state.current_date = datetime(1950, 3, 15)
        self.game_state.time_scale = 2.0
        self.game_state.paused = False
        self.game_state.statistics['game_days_elapsed'] = 74
        
        # 序列化游戏状态
        state_data = self.game_state.serialize()
        
        # 创建新的游戏状态并加载序列化数据
        new_game_state = GameState()
        new_game_state.deserialize(state_data)
        
        # 验证状态是否正确恢复
        self.assertEqual(new_game_state.current_date, datetime(1950, 3, 15))
        self.assertEqual(new_game_state.time_scale, 2.0)
        self.assertEqual(new_game_state.paused, False)
        self.assertEqual(new_game_state.statistics['game_days_elapsed'], 74)
    
    def test_realtime_updates(self):
        """测试实时更新流程"""
        # 模拟游戏状态变化
        self.game_state.paused = False
        self.game_state.update(timedelta(days=1).total_seconds())
        
        # 创建游戏状态更新事件
        state_data = self.game_state.serialize()
        event = GameEvent("game_state_updated", state_data)
        
        # 验证事件数据
        self.assertEqual(event.event_type, "game_state_updated")
        self.assertEqual(event.data, state_data)
        
        # 验证事件包含正确的游戏日期
        self.assertIn("current_date", event.data)
        self.assertEqual(event.data["current_date"], self.game_state.current_date.isoformat())

if __name__ == '__main__':
    unittest.main()