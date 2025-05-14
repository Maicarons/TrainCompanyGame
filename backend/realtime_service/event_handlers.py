# 游戏事件处理系统

from typing import Dict, List, Any, Optional, Callable
import asyncio
from datetime import datetime

from .websocket_service import GameEvent, websocket_manager
from ..game_engine import GameEngine, GameState

class GameEventSystem:
    """游戏事件系统，负责处理游戏中的各种事件"""
    
    def __init__(self, game_engine: Optional[GameEngine] = None):
        """初始化游戏事件系统
        
        Args:
            game_engine: 游戏引擎实例
        """
        self.game_engine = game_engine
        self.register_event_handlers()
    
    def set_game_engine(self, game_engine: GameEngine):
        """设置游戏引擎
        
        Args:
            game_engine: 游戏引擎实例
        """
        self.game_engine = game_engine
    
    def register_event_handlers(self):
        """注册事件处理器"""
        # 游戏状态更新事件
        websocket_manager.register_event_handler("game_state_update", self.handle_game_state_update)
        
        # 公司相关事件
        websocket_manager.register_event_handler("company_created", self.handle_company_created)
        websocket_manager.register_event_handler("company_updated", self.handle_company_updated)
        
        # 经济相关事件
        websocket_manager.register_event_handler("market_update", self.handle_market_update)
        websocket_manager.register_event_handler("economy_event", self.handle_economy_event)
        
        # 玩家操作事件
        websocket_manager.register_event_handler("player_action", self.handle_player_action)
        
        # 游戏控制事件
        websocket_manager.register_event_handler("start_game", self.handle_start_game)
        websocket_manager.register_event_handler("pause_game", self.handle_pause_game)
        websocket_manager.register_event_handler("resume_game", self.handle_resume_game)
        websocket_manager.register_event_handler("save_game", self.handle_save_game)
        websocket_manager.register_event_handler("load_game", self.handle_load_game)
    
    async def handle_game_state_update(self, event: GameEvent):
        """处理游戏状态更新事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine or not self.game_engine.game_state:
            return
        
        # 获取最新的游戏状态数据
        game_state = self.game_engine.game_state
        
        # 创建状态更新事件并广播
        state_update_event = GameEvent(
            "game_state_updated",
            {
                "current_date": game_state.current_date.isoformat(),
                "time_scale": game_state.time_scale,
                "paused": game_state.paused,
                "statistics": game_state.statistics
            }
        )
        
        await websocket_manager.queue_event(state_update_event)
    
    async def handle_company_created(self, event: GameEvent):
        """处理公司创建事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine or not self.game_engine.company_manager:
            return
        
        company_id = event.data.get("company_id")
        if not company_id:
            return
        
        # 获取公司信息
        company = self.game_engine.company_manager.get_company(company_id)
        if not company:
            return
        
        # 创建公司信息更新事件并广播
        company_info_event = GameEvent(
            "company_info",
            {
                "company_id": company_id,
                "name": company.name,
                "company_type": company.company_type.name,
                "owner_id": company.owner_id,
                "is_ai": company.is_ai,
                "cash": company.finances.cash,
                "assets": [{
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type.name,
                    "name": asset.name,
                    "value": asset.value
                } for asset in company.assets]
            }
        )
        
        await websocket_manager.queue_event(company_info_event)
    
    async def handle_company_updated(self, event: GameEvent):
        """处理公司更新事件
        
        Args:
            event: 游戏事件
        """
        # 与公司创建事件处理类似，但可能只更新部分信息
        await self.handle_company_created(event)
    
    async def handle_market_update(self, event: GameEvent):
        """处理市场更新事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine or not self.game_engine.economy_manager:
            return
        
        # 获取市场数据
        markets = self.game_engine.economy_manager.markets
        market_data = []
        
        for market_id, market in markets.items():
            market_info = {
                "market_id": market_id,
                "name": market.name,
                "location": market.location,
                "resources": []
            }
            
            for resource_type, price_info in market.prices.items():
                market_info["resources"].append({
                    "resource_type": resource_type.name,
                    "price": price_info["price"],
                    "supply": price_info["supply"],
                    "demand": price_info["demand"]
                })
            
            market_data.append(market_info)
        
        # 创建市场更新事件并广播
        market_update_event = GameEvent(
            "market_data",
            {"markets": market_data}
        )
        
        await websocket_manager.queue_event(market_update_event)
    
    async def handle_economy_event(self, event: GameEvent):
        """处理经济事件
        
        Args:
            event: 游戏事件
        """
        # 处理经济系统中的特殊事件，如经济危机、繁荣等
        await websocket_manager.queue_event(event)
    
    async def handle_player_action(self, event: GameEvent):
        """处理玩家操作事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine:
            return
        
        action_type = event.data.get("action_type")
        if not action_type:
            return
        
        # 根据不同的操作类型执行相应的逻辑
        if action_type == "create_company":
            # 创建公司
            name = event.data.get("name")
            company_type = event.data.get("company_type")
            player_id = event.data.get("player_id")
            initial_cash = event.data.get("initial_cash", 1000000)
            
            if name and company_type and player_id:
                company = self.game_engine.create_player_company(
                    name=name,
                    company_type=company_type,
                    player_id=player_id,
                    initial_cash=initial_cash
                )
                
                if company:
                    # 创建公司成功事件
                    success_event = GameEvent(
                        "action_result",
                        {
                            "success": True,
                            "action_type": action_type,
                            "company_id": company.company_id
                        },
                        target_clients=[player_id]
                    )
                    await websocket_manager.queue_event(success_event)
                    
                    # 触发公司创建事件
                    company_created_event = GameEvent(
                        "company_created",
                        {"company_id": company.company_id}
                    )
                    await websocket_manager.queue_event(company_created_event)
                else:
                    # 创建失败事件
                    fail_event = GameEvent(
                        "action_result",
                        {
                            "success": False,
                            "action_type": action_type,
                            "message": "创建公司失败"
                        },
                        target_clients=[player_id]
                    )
                    await websocket_manager.queue_event(fail_event)
        
        # 可以添加更多的玩家操作处理逻辑
    
    async def handle_start_game(self, event: GameEvent):
        """处理开始游戏事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine:
            return
        
        # 获取游戏参数
        world_width = event.data.get("world_width", 200)
        world_height = event.data.get("world_height", 200)
        num_cities = event.data.get("num_cities", 20)
        difficulty = event.data.get("difficulty", "normal")
        
        # 创建新游戏
        game_state = self.game_engine.create_new_game(
            world_width=world_width,
            world_height=world_height,
            num_cities=num_cities,
            difficulty=difficulty
        )
        
        if game_state:
            # 游戏创建成功事件
            game_created_event = GameEvent(
                "game_created",
                {
                    "world_width": world_width,
                    "world_height": world_height,
                    "num_cities": num_cities,
                    "difficulty": difficulty,
                    "start_date": game_state.start_date.isoformat()
                }
            )
            await websocket_manager.queue_event(game_created_event)
            
            # 触发游戏状态更新事件
            state_update_event = GameEvent("game_state_update", {})
            await websocket_manager.queue_event(state_update_event)
    
    async def handle_pause_game(self, event: GameEvent):
        """处理暂停游戏事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine or not self.game_engine.game_state:
            return
        
        self.game_engine.game_state.paused = True
        
        # 发送游戏暂停事件
        pause_event = GameEvent(
            "game_paused",
            {"timestamp": datetime.now().isoformat()}
        )
        await websocket_manager.queue_event(pause_event)
    
    async def handle_resume_game(self, event: GameEvent):
        """处理恢复游戏事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine or not self.game_engine.game_state:
            return
        
        self.game_engine.game_state.paused = False
        
        # 发送游戏恢复事件
        resume_event = GameEvent(
            "game_resumed",
            {"timestamp": datetime.now().isoformat()}
        )
        await websocket_manager.queue_event(resume_event)
    
    async def handle_save_game(self, event: GameEvent):
        """处理保存游戏事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine:
            return
        
        save_dir = event.data.get("save_dir")
        if not save_dir:
            return
        
        success = self.game_engine.save_game(save_dir)
        
        # 发送保存结果事件
        save_result_event = GameEvent(
            "save_game_result",
            {
                "success": success,
                "save_dir": save_dir,
                "timestamp": datetime.now().isoformat()
            }
        )
        await websocket_manager.queue_event(save_result_event)
    
    async def handle_load_game(self, event: GameEvent):
        """处理加载游戏事件
        
        Args:
            event: 游戏事件
        """
        if not self.game_engine:
            return
        
        save_dir = event.data.get("save_dir")
        if not save_dir:
            return
        
        game_state = self.game_engine.load_game(save_dir)
        
        # 发送加载结果事件
        load_result_event = GameEvent(
            "load_game_result",
            {
                "success": game_state is not None,
                "save_dir": save_dir,
                "timestamp": datetime.now().isoformat()
            }
        )
        await websocket_manager.queue_event(load_result_event)
        
        if game_state:
            # 触发游戏状态更新事件
            state_update_event = GameEvent("game_state_update", {})
            await websocket_manager.queue_event(state_update_event)

# 创建全局游戏事件系统实例
game_event_system = GameEventSystem()