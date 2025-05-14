# 游戏引擎包初始化文件

from .world_generator import WorldGenerator
from .economy import EconomyManager, Market, ResourceType
from .company import CompanyManager, RailwayCompany, AssetType
from .game_state import GameState

class GameEngine:
    """游戏引擎主类，整合世界生成、经济系统、公司管理和游戏状态"""
    
    def __init__(self, seed=None):
        """初始化游戏引擎
        
        Args:
            seed (int, optional): 随机种子
        """
        self.seed = seed
        self.game_state = None
        self.world_generator = None
        self.economy_manager = None
        self.company_manager = None
    
    def create_new_game(self, world_width=200, world_height=200, num_cities=20, difficulty='normal'):
        """创建新游戏
        
        Args:
            world_width (int): 世界地图宽度
            world_height (int): 世界地图高度
            num_cities (int): 城市数量
            difficulty (str): 游戏难度
            
        Returns:
            GameState: 游戏状态对象
        """
        # 创建世界生成器并生成世界
        self.world_generator = WorldGenerator(world_width, world_height, self.seed)
        world_data = self.world_generator.generate_world(num_cities)
        
        # 创建经济系统
        self.economy_manager = EconomyManager(self.world_generator, self.seed)
        
        # 创建公司管理系统
        self.company_manager = CompanyManager(self.world_generator, self.economy_manager, self.seed)
        
        # 创建游戏状态管理器
        self.game_state = GameState(self.seed)
        self.game_state.initialize_game(self.world_generator, self.economy_manager, self.company_manager)
        
        # 设置游戏难度
        self.game_state.set_difficulty(difficulty)
        
        return self.game_state
    
    def load_game(self, save_dir):
        """加载游戏
        
        Args:
            save_dir (str): 保存目录
            
        Returns:
            GameState: 游戏状态对象
        """
        self.game_state = GameState.load_game(save_dir)
        
        if self.game_state:
            self.world_generator = self.game_state.world_generator
            self.economy_manager = self.game_state.economy_manager
            self.company_manager = self.game_state.company_manager
        
        return self.game_state
    
    def save_game(self, save_dir):
        """保存游戏
        
        Args:
            save_dir (str): 保存目录
            
        Returns:
            bool: 是否成功
        """
        if self.game_state:
            return self.game_state.save_game(save_dir)
        return False
    
    def update(self, time_delta):
        """更新游戏状态
        
        Args:
            time_delta (float): 时间增量（秒）
            
        Returns:
            dict: 更新结果
        """
        if self.game_state:
            return self.game_state.update(time_delta)
        return {'status': 'error', 'message': '游戏未初始化'}
    
    def create_player_company(self, name, company_type, player_id, initial_cash=1000000):
        """创建玩家公司
        
        Args:
            name (str): 公司名称
            company_type: 公司类型
            player_id: 玩家ID
            initial_cash (float): 初始资金
            
        Returns:
            公司实例
        """
        if self.company_manager:
            return self.company_manager.create_company(
                name=name,
                company_type=company_type,
                owner_id=player_id,
                is_ai=False,
                initial_cash=initial_cash
            )
        return None
    
    def create_ai_companies(self, count=3, initial_cash=1000000):
        """创建AI公司
        
        Args:
            count (int): 创建数量
            initial_cash (float): 初始资金
            
        Returns:
            list: AI公司ID列表
        """
        if not self.company_manager:
            return []
        
        from .company import CompanyType
        
        ai_companies = []
        for i in range(count):
            company = self.company_manager.create_company(
                name=f"AI铁路公司 {i+1}",
                company_type=CompanyType.RAILWAY,
                owner_id=f"AI_{i+1}",
                is_ai=True,
                initial_cash=initial_cash
            )
            if company:
                ai_companies.append(company.company_id)
        
        return ai_companies