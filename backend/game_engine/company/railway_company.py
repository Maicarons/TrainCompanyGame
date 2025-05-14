# 铁路公司类

import numpy as np
from datetime import datetime
from enum import Enum, auto
from .assets import RailwayAsset, VehicleAsset, StationAsset, AssetType
from ..economy.company_finances import CompanyFinances, TransactionType

class RailwayCompany:
    """铁路公司类，管理铁路公司的特定功能和资产"""
    
    def __init__(self, company_id, name, finances, owner_id=None, world_generator=None, economy_manager=None, seed=None):
        """初始化铁路公司
        
        Args:
            company_id: 公司ID
            name (str): 公司名称
            finances (CompanyFinances): 公司财务对象
            owner_id: 所有者ID
            world_generator: 世界生成器实例
            economy_manager: 经济系统管理器实例
            seed (int, optional): 随机种子
        """
        self.company_id = company_id
        self.name = name
        self.finances = finances
        self.owner_id = owner_id
        self.world_generator = world_generator
        self.economy_manager = economy_manager
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        
        # 公司类型
        from .company_manager import CompanyType
        self.company_type = CompanyType.RAILWAY
        
        # 公司资产
        self.assets = {}
        self.asset_id_counter = 1
        
        # 铁路线路
        self.railway_lines = {}
        self.line_id_counter = 1
        
        # 车辆和车队
        self.vehicles = {}
        self.vehicle_id_counter = 1
        
        # 车站
        self.stations = {}
        
        # 运营数据
        self.operation_stats = {
            'passengers_transported': 0,
            'freight_transported': 0,
            'revenue_per_line': {},
            'maintenance_costs': 0,
            'operational_efficiency': 1.0,
            'customer_satisfaction': 0.8
        }
        
        # 公司声誉（影响客户满意度和合同获取）
        self.reputation = 50  # 0-100
        
        # 合同
        self.contracts = {}
        
        # 公司成立时间
        self.founded_date = datetime.now()
    
    def add_asset(self, asset_type, name, value, location=None, properties=None):
        """添加资产
        
        Args:
            asset_type (AssetType): 资产类型
            name (str): 资产名称
            value (float): 资产价值
            location: 资产位置
            properties (dict, optional): 资产属性
            
        Returns:
            asset_id: 资产ID或None
        """
        # 检查资金是否足够
        if self.finances.cash < value:
            return None
        
        # 生成资产ID
        asset_id = self.asset_id_counter
        self.asset_id_counter += 1
        
        # 创建资产对象
        asset = None
        if asset_type == AssetType.RAILWAY:
            asset = RailwayAsset(asset_id, name, value, location, properties)
        elif asset_type == AssetType.VEHICLE:
            asset = VehicleAsset(asset_id, name, value, location, properties)
        elif asset_type == AssetType.STATION:
            asset = StationAsset(asset_id, name, value, location, properties)
        
        # 添加资产并扣除资金
        if asset:
            self.assets[asset_id] = asset
            self.finances.add_asset(value, f"购买资产: {name}")
            
            # 根据资产类型添加到相应的集合
            if asset_type == AssetType.VEHICLE:
                self.vehicles[asset_id] = asset
            elif asset_type == AssetType.STATION:
                self.stations[asset_id] = asset
            
            return asset_id
        
        return None
    
    def remove_asset(self, asset_id, sale_value=None):
        """移除资产
        
        Args:
            asset_id: 资产ID
            sale_value (float, optional): 出售价值，如果为None则按资产当前价值计算
            
        Returns:
            bool: 是否成功
        """
        if asset_id not in self.assets:
            return False
        
        asset = self.assets[asset_id]
        
        # 计算出售价值
        if sale_value is None:
            sale_value = asset.current_value
        
        # 添加出售收入
        self.finances.add_income(sale_value, f"出售资产: {asset.name}")
        
        # 从相应的集合中移除
        if asset.asset_type == AssetType.VEHICLE and asset_id in self.vehicles:
            del self.vehicles[asset_id]
        elif asset.asset_type == AssetType.STATION and asset_id in self.stations:
            del self.stations[asset_id]
        
        # 从资产字典中移除
        del self.assets[asset_id]
        
        return True
    
    def add_railway_line(self, name, start_station_id, end_station_id, stops=None, properties=None):
        """添加铁路线路
        
        Args:
            name (str): 线路名称
            start_station_id: 起始站ID
            end_station_id: 终点站ID
            stops (list, optional): 途经站点ID列表
            properties (dict, optional): 线路属性
            
        Returns:
            line_id: 线路ID或None
        """
        # 检查起始站和终点站是否存在
        if start_station_id not in self.stations or end_station_id not in self.stations:
            return None
        
        # 生成线路ID
        line_id = self.line_id_counter
        self.line_id_counter += 1
        
        # 创建线路对象
        line = {
            'line_id': line_id,
            'name': name,
            'start_station_id': start_station_id,
            'end_station_id': end_station_id,
            'stops': stops or [],
            'properties': properties or {},
            'vehicles_assigned': [],
            'status': 'active',
            'created_date': datetime.now(),
            'stats': {
                'passengers_transported': 0,
                'freight_transported': 0,
                'revenue': 0,
                'expenses': 0,
                'efficiency': 1.0
            }
        }
        
        # 添加线路
        self.railway_lines[line_id] = line
        
        # 初始化线路收入统计
        self.operation_stats['revenue_per_line'][line_id] = 0
        
        return line_id
    
    def assign_vehicle_to_line(self, vehicle_id, line_id):
        """将车辆分配到线路
        
        Args:
            vehicle_id: 车辆ID
            line_id: 线路ID
            
        Returns:
            bool: 是否成功
        """
        if vehicle_id not in self.vehicles or line_id not in self.railway_lines:
            return False
        
        # 检查车辆是否已分配到其他线路
        for existing_line_id, line in self.railway_lines.items():
            if vehicle_id in line['vehicles_assigned']:
                # 从原线路中移除
                line['vehicles_assigned'].remove(vehicle_id)
        
        # 分配到新线路
        self.railway_lines[line_id]['vehicles_assigned'].append(vehicle_id)
        
        # 更新车辆位置
        self.vehicles[vehicle_id].location = self.stations[self.railway_lines[line_id]['start_station_id']].location
        
        return True
    
    def update(self, game_time, time_delta):
        """更新公司状态
        
        Args:
            game_time: 当前游戏时间
            time_delta: 自上次更新以来的时间增量（秒）
            
        Returns:
            dict: 更新结果
        """
        # 更新资产价值和折旧
        self._update_assets(time_delta)
        
        # 更新线路运营
        self._update_railway_operations(time_delta)
        
        # 更新声誉
        self._update_reputation(time_delta)
        
        # 更新合同
        self._update_contracts(time_delta)
        
        # 返回更新结果
        return {
            'company_id': self.company_id,
            'name': self.name,
            'finances': self.finances.get_financial_status(),
            'assets_count': len(self.assets),
            'railway_lines_count': len(self.railway_lines),
            'vehicles_count': len(self.vehicles),
            'stations_count': len(self.stations),
            'operation_stats': self.operation_stats,
            'reputation': self.reputation
        }
    
    def _update_assets(self, time_delta):
        """更新资产
        
        Args:
            time_delta: 时间增量（秒）
        """
        # 计算时间因子（转换为年）
        time_factor = time_delta / (365 * 24 * 3600)
        
        # 更新每个资产
        for asset_id, asset in self.assets.items():
            # 更新资产价值（折旧）
            asset.update_value(time_factor)
            
            # 计算维护费用
            maintenance_cost = asset.calculate_maintenance_cost(time_factor)
            if maintenance_cost > 0:
                self.finances.add_expense(
                    amount=maintenance_cost,
                    description=f"资产维护: {asset.name}",
                    related_entity=asset_id
                )
                self.operation_stats['maintenance_costs'] += maintenance_cost
    
    def _update_railway_operations(self, time_delta):
        """更新铁路运营
        
        Args:
            time_delta: 时间增量（秒）
        """
        # 计算时间因子（转换为天）
        time_factor = time_delta / (24 * 3600)
        
        # 更新每条线路的运营
        for line_id, line in self.railway_lines.items():
            # 检查线路状态
            if line['status'] != 'active':
                continue
            
            # 获取线路上的车辆数量
            vehicles_count = len(line['vehicles_assigned'])
            if vehicles_count == 0:
                continue
            
            # 计算线路运力
            capacity = 0
            for vehicle_id in line['vehicles_assigned']:
                if vehicle_id in self.vehicles:
                    vehicle = self.vehicles[vehicle_id]
                    capacity += vehicle.properties.get('capacity', 0)
            
            # 计算客运量和货运量（基于线路特性、车辆数量和经济状况）
            passenger_factor = line['properties'].get('passenger_demand', 0.5) * self.operation_stats['customer_satisfaction']
            freight_factor = line['properties'].get('freight_demand', 0.5)
            
            # 考虑经济影响
            if self.economy_manager:
                # 获取起始站和终点站所在城市的经济活跃度
                start_city_id = self.stations[line['start_station_id']].properties.get('city_id')
                end_city_id = self.stations[line['end_station_id']].properties.get('city_id')
                
                if start_city_id and start_city_id in self.economy_manager.markets:
                    passenger_factor *= self.economy_manager.markets[start_city_id].activity_level
                    freight_factor *= self.economy_manager.markets[start_city_id].activity_level
                
                if end_city_id and end_city_id in self.economy_manager.markets:
                    passenger_factor *= self.economy_manager.markets[end_city_id].activity_level
                    freight_factor *= self.economy_manager.markets[end_city_id].activity_level
                    
                # 取平均值
                passenger_factor = passenger_factor ** 0.5
                freight_factor = freight_factor ** 0.5
            
            # 计算实际运输量
            passengers_transported = capacity * passenger_factor * time_factor * self.operation_stats['operational_efficiency']
            freight_transported = capacity * freight_factor * time_factor * self.operation_stats['operational_efficiency']
            
            # 计算收入
            passenger_revenue = passengers_transported * line['properties'].get('passenger_fare', 50)
            freight_revenue = freight_transported * line['properties'].get('freight_fare', 100)
            total_revenue = passenger_revenue + freight_revenue
            
            # 更新统计数据
            line['stats']['passengers_transported'] += passengers_transported
            line['stats']['freight_transported'] += freight_transported
            line['stats']['revenue'] += total_revenue
            
            self.operation_stats['passengers_transported'] += passengers_transported
            self.operation_stats['freight_transported'] += freight_transported
            self.operation_stats['revenue_per_line'][line_id] += total_revenue
            
            # 添加收入
            self.finances.add_income(
                amount=total_revenue,
                description=f"线路运营收入: {line['name']}",
                related_entity=line_id
            )
    
    def _update_reputation(self, time_delta):
        """更新公司声誉
        
        Args:
            time_delta: 时间增量（秒）
        """
        # 计算时间因子（转换为月）
        time_factor = time_delta / (30 * 24 * 3600)
        
        # 基于运营效率和客户满意度更新声誉
        reputation_change = (
            (self.operation_stats['operational_efficiency'] - 0.8) * 10 +
            (self.operation_stats['customer_satisfaction'] - 0.7) * 15
        ) * time_factor
        
        # 更新声誉（限制在0-100范围内）
        self.reputation = max(0, min(100, self.reputation + reputation_change))
        
        # 声誉影响客户满意度
        self.operation_stats['customer_satisfaction'] = 0.5 + (self.reputation / 200)
    
    def _update_contracts(self, time_delta):
        """更新合同
        
        Args:
            time_delta: 时间增量（秒）
        """
        # 遍历所有合同
        contracts_to_remove = []
        for contract_id, contract in self.contracts.items():
            # 检查合同是否已过期
            if datetime.now() > contract['end_date']:
                # 合同完成度检查
                completion_rate = contract['current_progress'] / contract['target']
                
                # 根据完成度计算奖励或惩罚
                if completion_rate >= 0.95:
                    # 完成度高，获得全额奖励
                    bonus = contract['bonus']
                    self.finances.add_income(bonus, f"合同完成奖励: {contract['name']}")
                    self.reputation += 2  # 声誉提升
                elif completion_rate >= 0.7:
                    # 部分完成，获得部分奖励
                    partial_bonus = contract['bonus'] * (completion_rate - 0.7) / 0.25
                    self.finances.add_income(partial_bonus, f"合同部分完成奖励: {contract['name']}")
                else:
                    # 完成度低，支付违约金
                    penalty = contract['value'] * 0.2 * (0.7 - completion_rate) / 0.7
                    self.finances.add_expense(penalty, f"合同违约金: {contract['name']}")
                    self.reputation -= 5  # 声誉下降
                
                # 标记为移除
                contracts_to_remove.append(contract_id)
            else:
                # 更新合同进度（基于线路运营情况）
                if contract['type'] == 'passenger':
                    progress_increase = self.operation_stats['passengers_transported'] * contract['progress_factor'] * time_delta
                else:  # freight
                    progress_increase = self.operation_stats['freight_transported'] * contract['progress_factor'] * time_delta
                
                contract['current_progress'] += progress_increase
        
        # 移除已完成或过期的合同
        for contract_id in contracts_to_remove:
            del self.contracts[contract_id]
    
    def make_ai_decisions(self, game_time, time_delta):
        """AI决策逻辑
        
        Args:
            game_time: 当前游戏时间
            time_delta: 自上次更新以来的时间增量（秒）
        """
        # 简单的AI决策逻辑
        
        # 1. 资金管理
        cash = self.finances.cash
        assets_value = self.finances.assets_value
        loans = self.finances.loans
        
        # 如果现金过多，考虑投资新资产
        if cash > assets_value * 0.5 and len(self.assets) < 50:
            # 随机决定购买什么类型的资产
            asset_choice = self.rng.choice(['vehicle', 'station'])
            
            if asset_choice == 'vehicle' and cash > 500000:
                # 购买新车辆
                vehicle_name = f"AI车辆-{self.vehicle_id_counter}"
                vehicle_value = self.rng.uniform(300000, 500000)
                vehicle_properties = {
                    'capacity': self.rng.uniform(100, 200),
                    'speed': self.rng.uniform(80, 120),
                    'maintenance_factor': self.rng.uniform(0.05, 0.1)
                }
                
                self.add_asset(AssetType.VEHICLE, vehicle_name, vehicle_value, None, vehicle_properties)
                
                # 如果有线路，分配车辆
                if self.railway_lines:
                    line_id = self.rng.choice(list(self.railway_lines.keys()))
                    self.assign_vehicle_to_line(self.vehicle_id_counter - 1, line_id)
            
            elif asset_choice == 'station' and cash > 1000000 and self.world_generator:
                # 购买新车站
                # 在这里可以添加更复杂的逻辑来选择车站位置
                station_name = f"AI车站-{self.asset_id_counter}"
                station_value = self.rng.uniform(800000, 1200000)
                
                # 随机选择一个城市作为车站位置
                if hasattr(self.world_generator, 'city_generator') and self.world_generator.city_generator:
                    city_ids = list(self.world_generator.city_generator.cities.keys())
                    if city_ids:
                        city_id = self.rng.choice(city_ids)
                        city = self.world_generator.city_generator.cities[city_id]
                        
                        station_properties = {
                            'city_id': city_id,
                            'capacity': self.rng.uniform(500, 1000),
                            'maintenance_factor': self.rng.uniform(0.03, 0.07)
                        }
                        
                        self.add_asset(AssetType.STATION, station_name, station_value, city.location, station_properties)
        
        # 2. 线路管理
        # 如果有至少两个车站但没有线路，创建新线路
        if len(self.stations) >= 2 and not self.railway_lines:
            station_ids = list(self.stations.keys())
            start_station_id = station_ids[0]
            end_station_id = station_ids[1]
            
            line_name = f"AI线路-{self.line_id_counter}"
            line_properties = {
                'passenger_demand': self.rng.uniform(0.3, 0.7),
                'freight_demand': self.rng.uniform(0.3, 0.7),
                'passenger_fare': self.rng.uniform(40, 60),
                'freight_fare': self.rng.uniform(80, 120)
            }
            
            self.add_railway_line(line_name, start_station_id, end_station_id, None, line_properties)
        
        # 3. 贷款管理
        # 如果现金不足且有良好的资产价值，考虑贷款
        if cash < 100000 and assets_value > 1000000 and loans < assets_value * 0.5:
            loan_amount = min(500000, assets_value * 0.3)
            self.finances.take_loan(loan_amount, "AI决策贷款")
        
        # 如果现金充足且有贷款，考虑还款
        if cash > loans * 2 and loans > 0:
            repayment_amount = min(cash * 0.3, loans)
            self.finances.repay_loan(repayment_amount, "AI决策还款")
    
    def merge_with(self, target_company):
        """与目标公司合并
        
        Args:
            target_company: 目标公司实例
            
        Returns:
            bool: 是否成功
        """
        # 合并资产
        for asset_id, asset in target_company.assets.items():
            new_asset_id = self.asset_id_counter
            self.asset_id_counter += 1
            self.assets[new_asset_id] = asset
            asset.asset_id = new_asset_id
            
            # 根据资产类型添加到相应的集合
            if asset.asset_type == AssetType.VEHICLE:
                self.vehicles[new_asset_id] = asset
            elif asset.asset_type == AssetType.STATION:
                self.stations[new_asset_id] = asset
        
        # 合并线路
        for line_id, line in target_company.railway_lines.items():
            new_line_id = self.line_id_counter
            self.line_id_counter += 1
            
            # 创建新线路（需要更新站点ID和车辆ID的映射）
            new_line = line.copy()
            new_line['line_id'] = new_line_id
            new_line['vehicles_assigned'] = []  # 先清空，后面会重新分配
            
            self.railway_lines[new_line_id] = new_line
            self.operation_stats['revenue_per_line'][new_line_id] = 0
        
        # 合并财务（将目标公司的现金和资产转移到本公司）
        self.finances.cash += target_company.finances.cash
        self.finances.assets_value += target_company.finances.assets_value
        self.finances.loans += target_company.finances.loans
        
        # 记录合并交易
        self.finances.record_transaction(
            amount=target_company.finances.cash + target_company.finances.assets_value,
            transaction_type=TransactionType.INCOME,
            description=f"合并公司: {target_company.name}"
        )
        
        # 合并合同
        for contract_id, contract in target_company.contracts.items():
            self.contracts[f"merged_{contract_id}"] = contract
        
        # 合并运营数据
        self.operation_stats['passengers_transported'] += target_company.operation_stats['passengers_transported']
        self.operation_stats['freight_transported'] += target_company.operation_stats['freight_transported']
        self.operation_stats['maintenance_costs'] += target_company.operation_stats['maintenance_costs']
        
        # 声誉可能会受到影响（取平均值）
        self.reputation = (self.reputation + target_company.reputation) / 2
        
        return True
    
    def to_dict(self):
        """将公司转换为字典
        
        Returns:
            dict: 公司数据
        """
        return {
            'company_id': self.company_id,
            'name': self.name,
            'company_type': self.company_type.name,
            'owner_id': self.owner_id,
            'seed': self.seed,
            'finances': self.finances.to_dict(),
            'assets': {asset_id: asset.to_dict() for asset_id, asset in self.assets.items()},
            'asset_id_counter': self.asset_id_counter,
            'railway_lines': self.railway_lines,
            'line_id_counter': self.line_id_counter,
            'vehicles': {vehicle_id: vehicle.to_dict() for vehicle_id, vehicle in self.vehicles.items()},
            'vehicle_id_counter': self.vehicle_id_counter,
            'stations': {station_id: station.to_dict() for station_id, station in self.stations.items()},
            'operation_stats': self.operation_stats,
            'reputation': self.reputation,
            'contracts': self.contracts,
            'founded_date': self.founded_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data, world_generator=None, economy_manager=None):
        """从字典创建公司
        
        Args:
            data (dict): 公司数据
            world_generator: 世界生成器实例
            economy_manager: 经济系统管理器实例
            
        Returns:
            RailwayCompany: 公司实例
        """
        # 创建财务对象
        finances = CompanyFinances.from_dict(data['finances'])
        
        # 创建公司实例
        company = cls(
            company_id=data['company_id'],
            name=data['name'],
            finances=finances,
            owner_id=data['owner_id'],
            world_generator=world_generator,
            economy_manager=economy_manager,
            seed=data['seed']
        )
        
        # 加载资产
        company.asset_id_counter = data['asset_id_counter']
        for asset_id, asset_data in data['assets'].items():
            asset_type = AssetType[asset_data['asset_type']]
            if asset_type == AssetType.RAILWAY:
                company.assets[asset_id] = RailwayAsset.from_dict(asset_data)
            elif asset_type == AssetType.VEHICLE:
                vehicle = VehicleAsset.from_dict(asset_data)
                company.assets[asset_id] = vehicle
                company.vehicles[asset_id] = vehicle
            elif asset_type == AssetType.STATION:
                station = StationAsset.from_dict(asset_data)
                company.assets[asset_id] = station
                company.stations[asset_id] = station
        
        # 加载线路
        company.railway_lines = data['railway_lines']
        company.line_id_counter = data['line_id_counter']
        
        # 加载其他数据
        company.vehicle_id_counter = data['vehicle_id_counter']
        company.operation_stats = data['operation_stats']
        company.reputation = data['reputation']
        company.contracts = data['contracts']
        company.founded_date = datetime.fromisoformat(data['founded_date'])
        
        return company