# 测试配置文件

import pytest
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def game_state_fixture():
    """提供游戏状态实例用于测试"""
    from backend.game_engine.game_state import GameState
    return GameState(seed=12345)

@pytest.fixture
def economy_manager_fixture():
    """提供经济管理器实例用于测试"""
    from backend.game_engine.economy.economy_manager import EconomyManager
    return EconomyManager(seed=12345)

@pytest.fixture
def websocket_manager_fixture():
    """提供WebSocket管理器实例用于测试"""
    from backend.realtime_service.websocket_service import WebSocketManager
    return WebSocketManager()

@pytest.fixture
def mock_map_data():
    """提供模拟地图数据用于测试"""
    return {
        "terrain": [[0, 0, 1], [0, 2, 1], [1, 1, 0]],
        "cities": [
            {"id": 1, "name": "城市A", "x": 100, "y": 100, "population": 500000, "type": "industrial"},
            {"id": 2, "name": "城市B", "x": 300, "y": 200, "population": 300000, "type": "commercial"}
        ],
        "railways": [
            {"id": 1, "from_city": 1, "to_city": 2, "path": [[100, 100], [200, 150], [300, 200]], "length": 250}
        ]
    }