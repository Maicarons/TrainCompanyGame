from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from ..database import Base

# 公司类型枚举
class CompanyType(enum.Enum):
    RAILWAY = "R"  # 铁道运营公司
    TRAIN = "T"    # 车辆运营公司
    SERVICE = "S"  # 服务运营公司

# 公司模型
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    type = Column(Enum(CompanyType))
    description = Column(Text, nullable=True)
    
    # 财务信息
    balance = Column(Float, default=1000000.0)  # 初始资金100万
    income = Column(Float, default=0.0)
    expenses = Column(Float, default=0.0)
    
    # 公司属性
    reputation = Column(Float, default=50.0)  # 声誉(0-100)
    founded_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # 所属用户
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="companies")
    
    # 所属集团
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    group = relationship("Group", back_populates="companies")
    
    # 公司特定属性(根据公司类型不同而不同)
    properties = Column(JSON, nullable=True)
    
    # 关系
    assets = relationship("Asset", back_populates="company")
    contracts_provided = relationship("Contract", foreign_keys="Contract.provider_id", back_populates="provider")
    contracts_received = relationship("Contract", foreign_keys="Contract.receiver_id", back_populates="receiver")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Company {self.name} ({self.type.value})>"

# 资产模型
class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(50))  # 资产类型(铁路、车站、车辆等)
    description = Column(Text, nullable=True)
    
    # 资产属性
    value = Column(Float)  # 当前价值
    purchase_value = Column(Float)  # 购买价值
    condition = Column(Float, default=100.0)  # 状态(0-100)
    maintenance_cost = Column(Float, default=0.0)  # 维护成本
    
    # 资产特定属性
    properties = Column(JSON, nullable=True)
    
    # 所属公司
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="assets")
    
    # 地理位置(如适用)
    location_x = Column(Float, nullable=True)
    location_y = Column(Float, nullable=True)
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Asset {self.name} ({self.type})>"

# 集团模型
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # 集团属性
    reputation = Column(Float, default=50.0)  # 声誉(0-100)
    founded_date = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # 关系
    companies = relationship("Company", back_populates="group")
    
    # 集团特定属性
    properties = Column(JSON, nullable=True)
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Group {self.name}>"