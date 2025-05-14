from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

from ..database import Base

# 合同类型枚举
class ContractType(enum.Enum):
    RAILWAY_USAGE = "铁路使用"  # 铁路使用合同(R公司与T公司)
    SERVICE_PROVISION = "服务提供"  # 服务提供合同(T公司与S公司)
    MAINTENANCE = "维护"  # 维护合同
    CONSTRUCTION = "建设"  # 建设合同
    LEASE = "租赁"  # 租赁合同
    OTHER = "其他"  # 其他类型

# 合同状态枚举
class ContractStatus(enum.Enum):
    DRAFT = "草稿"  # 草稿状态
    PENDING = "待签署"  # 等待签署
    ACTIVE = "生效中"  # 生效中
    COMPLETED = "已完成"  # 已完成
    TERMINATED = "已终止"  # 已终止
    EXPIRED = "已过期"  # 已过期

# 合同模型
class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    contract_type = Column(Enum(ContractType))
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    description = Column(Text, nullable=True)
    
    # 合同条款
    terms = Column(JSON, nullable=True)
    
    # 财务信息
    value = Column(Float)  # 合同总价值
    payment_terms = Column(Text, nullable=True)  # 支付条款
    penalty_terms = Column(Text, nullable=True)  # 违约条款
    
    # 时间信息
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # 合同双方
    provider_id = Column(Integer, ForeignKey("companies.id"))
    receiver_id = Column(Integer, ForeignKey("companies.id"))
    provider = relationship("Company", foreign_keys=[provider_id], back_populates="contracts_provided")
    receiver = relationship("Company", foreign_keys=[receiver_id], back_populates="contracts_received")
    
    # 合同特定属性
    properties = Column(JSON, nullable=True)
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Contract {self.title} ({self.contract_type.value})>"

# 合同事件模型
class ContractEvent(Base):
    __tablename__ = "contract_events"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    event_type = Column(String(50))  # 事件类型(创建、修改、终止等)
    description = Column(Text)
    
    # 事件特定属性
    properties = Column(JSON, nullable=True)
    
    # 关系
    contract = relationship("Contract")
    
    # 创建时间
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<ContractEvent {self.event_type} for Contract #{self.contract_id}>"

# 合同模板模型
class ContractTemplate(Base):
    __tablename__ = "contract_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    contract_type = Column(Enum(ContractType))
    description = Column(Text, nullable=True)
    
    # 模板内容
    template = Column(JSON)
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ContractTemplate {self.name} ({self.contract_type.value})>"