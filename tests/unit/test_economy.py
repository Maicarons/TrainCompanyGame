# 经济系统单元测试

import unittest
import numpy as np
from datetime import datetime, timedelta
from backend.game_engine.economy.economy_manager import EconomyManager
from backend.game_engine.economy.market import Market, ResourceType

class TestEconomyManager(unittest.TestCase):
    """测试经济系统管理器"""
    
    def setUp(self):
        """测试前准备"""
        self.economy_manager = EconomyManager(seed=12345)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.economy_manager.seed, 12345)
        self.assertIsNotNone(self.economy_manager.rng)
        self.assertEqual(self.economy_manager.inflation_rate, 0.02)
        self.assertEqual(self.economy_manager.interest_rate, 0.05)
        self.assertEqual(self.economy_manager.economic_growth, 0.03)
    
    def test_market_creation(self):
        """测试市场创建"""
        # 创建一个测试市场
        market = Market("测试市场", None, 12345)
        
        # 验证市场属性
        self.assertEqual(market.name, "测试市场")
        self.assertIsNone(market.city)
        self.assertIsNotNone(market.price_models)
    
    def test_economy_update(self):
        """测试经济更新"""
        # 记录初始状态
        initial_inflation = self.economy_manager.inflation_rate
        initial_interest = self.economy_manager.interest_rate
        
        # 模拟经济更新（一个月）
        current_time = datetime(2023, 1, 1)
        self.economy_manager.update_economy(current_time, timedelta(days=30))
        
        # 验证经济指标有变化但在合理范围内
        self.assertIsNotNone(self.economy_manager.inflation_rate)
        self.assertIsNotNone(self.economy_manager.interest_rate)
        
        # 通货膨胀率应该在0-10%之间
        self.assertGreaterEqual(self.economy_manager.inflation_rate, 0)
        self.assertLessEqual(self.economy_manager.inflation_rate, 0.1)
        
        # 利率应该在1-10%之间
        self.assertGreaterEqual(self.economy_manager.interest_rate, 0.01)
        self.assertLessEqual(self.economy_manager.interest_rate, 0.1)
    
    def test_economic_event_generation(self):
        """测试经济事件生成"""
        # 模拟经济更新，触发事件生成
        current_time = datetime(2023, 1, 1)
        events = self.economy_manager.generate_economic_events(current_time, timedelta(days=90))
        
        # 验证返回的是事件列表
        self.assertIsInstance(events, list)

if __name__ == '__main__':
    unittest.main()