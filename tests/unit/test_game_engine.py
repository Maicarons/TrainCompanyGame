# 游戏引擎单元测试

import unittest
import numpy as np
from datetime import datetime, timedelta
from backend.game_engine.game_state import GameState

class TestGameState(unittest.TestCase):
    """测试游戏状态管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.game_state = GameState(seed=12345)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.game_state.seed, 12345)
        self.assertEqual(self.game_state.start_date, datetime(1950, 1, 1))
        self.assertEqual(self.game_state.current_date, datetime(1950, 1, 1))
        self.assertEqual(self.game_state.time_scale, 1.0)
        self.assertTrue(self.game_state.paused)
    
    def test_time_advancement(self):
        """测试时间推进"""
        # 设置游戏为非暂停状态
        self.game_state.paused = False
        
        # 模拟时间推进
        self.game_state.update(timedelta(days=1).total_seconds())
        
        # 验证游戏时间已经推进了一天
        expected_date = datetime(1950, 1, 2)
        self.assertEqual(self.game_state.current_date, expected_date)
        self.assertEqual(self.game_state.statistics['game_days_elapsed'], 1)
    
    def test_time_scale_adjustment(self):
        """测试时间缩放调整"""
        # 设置时间缩放为2倍速
        self.game_state.set_time_scale(2.0)
        self.assertEqual(self.game_state.time_scale, 2.0)
        
        # 设置游戏为非暂停状态
        self.game_state.paused = False
        
        # 模拟时间推进
        self.game_state.update(timedelta(days=1).total_seconds())
        
        # 验证游戏时间已经推进了两天（因为2倍速）
        expected_date = datetime(1950, 1, 3)
        self.assertEqual(self.game_state.current_date, expected_date)
    
    def test_pause_resume(self):
        """测试暂停和恢复"""
        # 初始状态为暂停
        self.assertTrue(self.game_state.paused)
        
        # 恢复游戏
        self.game_state.resume()
        self.assertFalse(self.game_state.paused)
        
        # 暂停游戏
        self.game_state.pause()
        self.assertTrue(self.game_state.paused)
        
        # 暂停状态下时间不应该推进
        initial_date = self.game_state.current_date
        self.game_state.update(timedelta(days=1).total_seconds())
        self.assertEqual(self.game_state.current_date, initial_date)

if __name__ == '__main__':
    unittest.main()