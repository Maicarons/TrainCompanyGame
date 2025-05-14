# 游戏状态管理器

import numpy as np
from datetime import datetime, timedelta
import os

class GameState:
    """游戏状态管理器，负责管理游戏的整体状态和协调各个子系统"""
    
    def __init__(self, seed=None):
        """初始化游戏状态管理器
        
        Args:
            seed (int, optional): 随机种子
        """
        self.seed = seed if seed is not None else np.random.randint(0, 100000)
        self.rng = np.random.RandomState(self.seed)
        
        # 游戏时间
        self.start_date = datetime(1950, 1, 1)  # 游戏开始日期
        self.current_date = self.start_date.copy()  # 当前游戏日期
        self.time_scale = 1.0  # 时间流逝速度倍率
        self.paused = True  # 游戏是否暂停
        
        # 游戏子系统
        self.world_generator = None  # 世界生成器
        self.economy_manager = None  # 经济系统
        self.company_manager = None  # 公司管理系统
        
        # 游戏设置
        self.difficulty = 'normal'  # 游戏难度
        self.game_mode = 'standard'  # 游戏模式
        
        # 游戏统计数据
        self.statistics = {
            'game_days_elapsed': 0,
            'total_companies': 0,
            'player_companies': 0,
            'ai_companies': 0,
            'global_economy_index': 100,
            'total_railway_length': 0,
            'total_passengers': 0,
            'total_freight': 0
        }
        
        # 游戏事件
        self.events = []
        self.event_history = []
        
        # 上次更新时间（真实时间）
        self.last_update_time = datetime.now()
    
    def initialize_game(self, world_generator, economy_manager, company_manager):
        """初始化游戏，设置各个子系统
        
        Args:
            world_generator: 世界生成器实例
            economy_manager: 经济系统管理器实例
            company_manager: 公司管理系统实例
        """
        self.world_generator = world_generator
        self.economy_manager = economy_manager
        self.company_manager = company_manager
        
        # 更新统计数据
        if company_manager:
            self.statistics['total_companies'] = len(company_manager.companies)
            self.statistics['ai_companies'] = len(company_manager.ai_companies)
            self.statistics['player_companies'] = self.statistics['total_companies'] - self.statistics['ai_companies']
        
        # 初始化游戏事件
        self._initialize_events()
        
        print(f"游戏已初始化，开始日期: {self.start_date.strftime('%Y-%m-%d')}，难度: {self.difficulty}")
    
    def _initialize_events(self):
        """初始化游戏事件"""
        # 历史事件（基于真实历史）
        historical_events = [
            {
                'date': datetime(1956, 2, 25),
                'title': '苏联领导人赫鲁晓夫发表秘密报告',
                'description': '苏联领导人赫鲁晓夫在苏共二十大上发表秘密报告，批评斯大林的个人崇拜。',
                'effects': {'economic_growth': -0.01}
            },
            {
                'date': datetime(1957, 10, 4),
                'title': '人类首颗人造卫星发射成功',
                'description': '苏联成功发射世界首颗人造地球卫星"斯普特尼克1号"，标志着太空时代的开始。',
                'effects': {'technology_boost': 0.05, 'economic_growth': 0.02}
            },
            {
                'date': datetime(1973, 10, 17),
                'title': '石油危机爆发',
                'description': '阿拉伯石油输出国组织宣布石油禁运，导致全球石油价格暴涨。',
                'effects': {'oil_price': 2.5, 'economic_growth': -0.05, 'inflation_rate': 0.1}
            },
            {
                'date': datetime(1986, 4, 26),
                'title': '切尔诺贝利核事故',
                'description': '苏联切尔诺贝利核电站发生严重事故，造成大规模核辐射泄漏。',
                'effects': {'economic_growth': -0.03, 'environmental_concern': 0.2}
            },
            {
                'date': datetime(1989, 11, 9),
                'title': '柏林墙倒塌',
                'description': '东德政府宣布开放边界，柏林墙倒塌，标志着冷战即将结束。',
                'effects': {'economic_growth': 0.04, 'trade_boost': 0.1}
            },
            {
                'date': datetime(2008, 9, 15),
                'title': '雷曼兄弟破产，金融危机爆发',
                'description': '美国投资银行雷曼兄弟宣布破产，引发全球金融危机。',
                'effects': {'economic_growth': -0.08, 'interest_rate': -0.03, 'stock_market': -0.3}
            }
        ]
        
        # 随机事件模板
        random_event_templates = [
            {
                'title': '技术突破',
                'description': '铁路技术取得重大突破，提高了运营效率。',
                'effects': {'operational_efficiency': 0.1, 'maintenance_cost': -0.05},
                'duration': 365  # 持续天数
            },
            {
                'title': '经济衰退',
                'description': '经济衰退导致客运和货运需求下降。',
                'effects': {'passenger_demand': -0.2, 'freight_demand': -0.15, 'economic_growth': -0.03},
                'duration': 180
            },
            {
                'title': '燃料价格上涨',
                'description': '全球燃料价格大幅上涨，增加了运营成本。',
                'effects': {'operational_cost': 0.2, 'ticket_price': 0.1},
                'duration': 90
            },
            {
                'title': '旅游热潮',
                'description': '旅游业蓬勃发展，增加了客运需求。',
                'effects': {'passenger_demand': 0.25},
                'duration': 60
            },
            {
                'title': '贸易协定',
                'description': '新的国际贸易协定签署，促进了货物流通。',
                'effects': {'freight_demand': 0.2, 'economic_growth': 0.02},
                'duration': 120
            }
        ]
        
        # 添加历史事件
        self.events.extend(historical_events)
        
        # 生成一些随机事件
        game_years = 100  # 游戏时间跨度（年）
        num_random_events = int(game_years * 0.8)  # 平均每1.25年一个随机事件
        
        for _ in range(num_random_events):
            # 随机选择事件模板
            template = self.rng.choice(random_event_templates)
            
            # 随机生成事件日期（在游戏时间范围内）
            days_offset = self.rng.randint(30, 365 * game_years - 30)
            event_date = self.start_date + timedelta(days=days_offset)
            
            # 创建事件
            event = {
                'date': event_date,
                'title': template['title'],
                'description': template['description'],
                'effects': template['effects'],
                'duration': template['duration']
            }
            
            self.events.append(event)
        
        # 按日期排序
        self.events.sort(key=lambda e: e['date'])
    
    def update(self, real_time_delta):
        """更新游戏状态
        
        Args:
            real_time_delta (float): 真实时间增量（秒）
            
        Returns:
            dict: 更新结果
        """
        if self.paused:
            return {'status': 'paused'}
        
        # 计算游戏时间增量
        game_time_delta = real_time_delta * self.time_scale
        game_days_delta = game_time_delta / (24 * 3600)  # 转换为游戏天数
        
        # 更新游戏日期
        old_date = self.current_date
        self.current_date += timedelta(days=game_days_delta)
        self.statistics['game_days_elapsed'] += game_days_delta
        
        # 检查并触发事件
        triggered_events = self._check_events(old_date, self.current_date)
        
        # 更新各个子系统
        update_results = {}
        
        # 更新经济系统
        if self.economy_manager:
            economy_results = self.economy_manager.update_economy(self.current_date, game_time_delta)
            update_results['economy'] = economy_results
            
            # 更新全球经济指数
            self.statistics['global_economy_index'] = 100 * (1 + self.economy_manager.economic_growth)
        
        # 更新公司
        if self.company_manager:
            company_results = self.company_manager.update_companies(self.current_date, game_time_delta)
            update_results['companies'] = company_results
            
            # 更新公司统计数据
            self.statistics['total_companies'] = len(self.company_manager.companies)
            self.statistics['ai_companies'] = len(self.company_manager.ai_companies)
            self.statistics['player_companies'] = self.statistics['total_companies'] - self.statistics['ai_companies']
            
            # 更新铁路统计数据
            self._update_railway_statistics()
        
        # 记录更新时间
        self.last_update_time = datetime.now()
        
        return {
            'status': 'running',
            'current_date': self.current_date,
            'days_elapsed': game_days_delta,
            'triggered_events': triggered_events,
            'statistics': self.statistics,
            'updates': update_results
        }
    
    def _check_events(self, start_date, end_date):
        """检查并触发事件
        
        Args:
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
            
        Returns:
            list: 触发的事件列表
        """
        triggered_events = []
        
        # 检查是否有事件在这个时间段内触发
        for event in self.events:
            if start_date < event['date'] <= end_date:
                # 触发事件
                self._apply_event_effects(event)
                
                # 添加到历史记录
                self.event_history.append({
                    'event': event,
                    'triggered_date': self.current_date
                })
                
                triggered_events.append(event)
                
                print(f"事件触发: {event['title']} - {event['description']}")
        
        return triggered_events
    
    def _apply_event_effects(self, event):
        """应用事件效果
        
        Args:
            event (dict): 事件数据
        """
        effects = event.get('effects', {})
        
        # 应用到经济系统
        if self.economy_manager:
            if 'economic_growth' in effects:
                self.economy_manager.economic_growth += effects['economic_growth']
            
            if 'inflation_rate' in effects:
                self.economy_manager.inflation_rate += effects['inflation_rate']
            
            if 'interest_rate' in effects:
                self.economy_manager.interest_rate += effects['interest_rate']
            
            if 'oil_price' in effects and hasattr(self.economy_manager, 'global_market'):
                from ..economy.market import ResourceType
                oil_price = self.economy_manager.global_market.get_price(ResourceType.OIL)
                self.economy_manager.global_market.price_models[ResourceType.OIL].current_price = oil_price * effects['oil_price']
        
        # 应用到公司系统
        if self.company_manager:
            for company in self.company_manager.companies.values():
                if 'operational_efficiency' in effects and hasattr(company, 'operation_stats'):
                    company.operation_stats['operational_efficiency'] += effects['operational_efficiency']
                
                if 'maintenance_cost' in effects and hasattr(company, 'assets'):
                    for asset in company.assets.values():
                        asset.properties['maintenance_factor'] *= (1 + effects['maintenance_cost'])
                
                if 'passenger_demand' in effects and hasattr(company, 'railway_lines'):
                    for line in company.railway_lines.values():
                        if 'passenger_demand' in line['properties']:
                            line['properties']['passenger_demand'] *= (1 + effects['passenger_demand'])
                
                if 'freight_demand' in effects and hasattr(company, 'railway_lines'):
                    for line in company.railway_lines.values():
                        if 'freight_demand' in line['properties']:
                            line['properties']['freight_demand'] *= (1 + effects['freight_demand'])
    
    def _update_railway_statistics(self):
        """更新铁路统计数据"""
        total_railway_length = 0
        total_passengers = 0
        total_freight = 0
        
        for company in self.company_manager.companies.values():
            if hasattr(company, 'assets'):
                # 计算铁路总长度
                for asset in company.assets.values():
                    if hasattr(asset, 'asset_type') and asset.asset_type.name == 'RAILWAY' and 'length' in asset.properties:
                        total_railway_length += asset.properties['length']
            
            if hasattr(company, 'operation_stats'):
                # 累计客运和货运量
                total_passengers += company.operation_stats.get('passengers_transported', 0)
                total_freight += company.operation_stats.get('freight_transported', 0)
        
        self.statistics['total_railway_length'] = total_railway_length
        self.statistics['total_passengers'] = total_passengers
        self.statistics['total_freight'] = total_freight
    
    def set_time_scale(self, scale):
        """设置时间流逝速度
        
        Args:
            scale (float): 时间流逝速度倍率
            
        Returns:
            float: 更新后的时间流逝速度
        """
        self.time_scale = max(0.1, min(10.0, scale))  # 限制在0.1到10倍之间
        return self.time_scale
    
    def pause_game(self):
        """暂停游戏
        
        Returns:
            bool: 游戏是否暂停
        """
        self.paused = True
        return self.paused
    
    def resume_game(self):
        """恢复游戏
        
        Returns:
            bool: 游戏是否暂停
        """
        self.paused = False
        return self.paused
    
    def set_difficulty(self, difficulty):
        """设置游戏难度
        
        Args:
            difficulty (str): 游戏难度，可选值：'easy', 'normal', 'hard'
            
        Returns:
            str: 更新后的游戏难度
        """
        if difficulty in ['easy', 'normal', 'hard']:
            self.difficulty = difficulty
            
            # 根据难度调整游戏参数
            if difficulty == 'easy':
                # 简单难度：经济增长更快，维护成本更低
                if self.economy_manager:
                    self.economy_manager.economic_growth *= 1.2
                    self.economy_manager.interest_rate *= 0.8
                
                # 调整公司参数
                if self.company_manager:
                    for company in self.company_manager.companies.values():
                        if hasattr(company, 'assets'):
                            for asset in company.assets.values():
                                if 'maintenance_factor' in asset.properties:
                                    asset.properties['maintenance_factor'] *= 0.8
            
            elif difficulty == 'hard':
                # 困难难度：经济增长更慢，维护成本更高
                if self.economy_manager:
                    self.economy_manager.economic_growth *= 0.8
                    self.economy_manager.interest_rate *= 1.2
                
                # 调整公司参数
                if self.company_manager:
                    for company in self.company_manager.companies.values():
                        if hasattr(company, 'assets'):
                            for asset in company.assets.values():
                                if 'maintenance_factor' in asset.properties:
                                    asset.properties['maintenance_factor'] *= 1.2
        
        return self.difficulty
    
    def save_game(self, save_dir):
        """保存游戏
        
        Args:
            save_dir (str): 保存目录
            
        Returns:
            bool: 是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)
            
            # 保存游戏状态数据
            game_state_data = {
                'seed': self.seed,
                'current_date': self.current_date.isoformat(),
                'start_date': self.start_date.isoformat(),
                'time_scale': self.time_scale,
                'paused': self.paused,
                'difficulty': self.difficulty,
                'game_mode': self.game_mode,
                'statistics': self.statistics,
                'events': self.events,
                'event_history': self.event_history
            }
            np.savez(os.path.join(save_dir, 'game_state.npz'), **game_state_data)
            
            # 保存世界数据
            if self.world_generator:
                self.world_generator.save_world(os.path.join(save_dir, 'world'))
            
            # 保存经济系统数据
            if self.economy_manager:
                self.economy_manager.save_economy_data(os.path.join(save_dir, 'economy.npz'))
            
            # 保存公司数据
            if self.company_manager:
                self.company_manager.save_companies_data(os.path.join(save_dir, 'companies.npz'))
            
            print(f"游戏已保存到: {save_dir}")
            return True
        
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    @classmethod
    def load_game(cls, save_dir):
        """加载游戏
        
        Args:
            save_dir (str): 保存目录
            
        Returns:
            GameState: 游戏状态实例
        """
        try:
            # 加载游戏状态数据
            game_state_file = os.path.join(save_dir, 'game_state.npz')
            data = np.load(game_state_file, allow_pickle=True)
            
            # 创建游戏状态实例
            game_state = cls(int(data['seed']))
            game_state.current_date = datetime.fromisoformat(str(data['current_date']))
            game_state.start_date = datetime.fromisoformat(str(data['start_date']))
            game_state.time_scale = float(data['time_scale'])
            game_state.paused = bool(data['paused'])
            game_state.difficulty = str(data['difficulty'])
            game_state.game_mode = str(data['game_mode'])
            game_state.statistics = data['statistics'].item()
            game_state.events = data['events'].tolist()
            game_state.event_history = data['event_history'].tolist()
            
            # 加载世界数据
            from .world_generator import WorldGenerator
            world_dir = os.path.join(save_dir, 'world')
            world_generator = WorldGenerator.load_world(world_dir)
            
            # 加载经济系统数据
            from .economy import EconomyManager
            economy_file = os.path.join(save_dir, 'economy.npz')
            economy_manager = EconomyManager.load_economy_data(economy_file, world_generator)
            
            # 加载公司数据
            from .company import CompanyManager
            companies_file = os.path.join(save_dir, 'companies.npz')
            company_manager = CompanyManager.load_companies_data(companies_file, world_generator, economy_manager)
            
            # 初始化游戏
            game_state.initialize_game(world_generator, economy_manager, company_manager)
            
            print(f"游戏已从 {save_dir} 加载")
            return game_state
        
        except Exception as e:
            print(f"加载游戏失败: {e}")
            return None