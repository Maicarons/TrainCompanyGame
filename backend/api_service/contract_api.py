from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.contract import Contract, ContractType, ContractStatus, ContractEvent, ContractTemplate
from ..models.company import Company

# 创建路由器
router = APIRouter()

# 合同数据模型
from pydantic import BaseModel, Field
from enum import Enum

class ContractTypeEnum(str, Enum):
    RAILWAY_USAGE = "铁路使用"
    SERVICE_PROVISION = "服务提供"
    MAINTENANCE = "维护"
    CONSTRUCTION = "建设"
    LEASE = "租赁"
    OTHER = "其他"

class ContractStatusEnum(str, Enum):
    DRAFT = "草稿"
    PENDING = "待签署"
    ACTIVE = "生效中"
    COMPLETED = "已完成"
    TERMINATED = "已终止"
    EXPIRED = "已过期"

class ContractCreate(BaseModel):
    title: str
    contract_type: ContractTypeEnum
    description: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None
    value: float
    payment_terms: Optional[str] = None
    penalty_terms: Optional[str] = None
    start_date: datetime
    end_date: datetime
    provider_id: int
    receiver_id: int
    properties: Optional[Dict[str, Any]] = None

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ContractStatusEnum] = None
    terms: Optional[Dict[str, Any]] = None
    value: Optional[float] = None
    payment_terms: Optional[str] = None
    penalty_terms: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    properties: Optional[Dict[str, Any]] = None

class ContractResponse(BaseModel):
    id: int
    title: str
    contract_type: str
    status: str
    description: Optional[str] = None
    terms: Optional[Dict[str, Any]] = None
    value: float
    payment_terms: Optional[str] = None
    penalty_terms: Optional[str] = None
    start_date: datetime
    end_date: datetime
    provider_id: int
    receiver_id: int
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 获取所有合同
@router.get("/", response_model=List[ContractResponse])
async def get_contracts(skip: int = 0, limit: int = 100, 
                       company_id: Optional[int] = None,
                       status: Optional[ContractStatusEnum] = None,
                       db: Session = Depends(get_db)):
    # 构建查询
    query = db.query(Contract)
    
    # 如果指定了公司ID，则过滤
    if company_id is not None:
        query = query.filter(
            (Contract.provider_id == company_id) | (Contract.receiver_id == company_id)
        )
    
    # 如果指定了状态，则过滤
    if status is not None:
        query = query.filter(Contract.status == ContractStatus(status.value))
    
    # 获取合同
    contracts = query.offset(skip).limit(limit).all()
    
    return contracts

# 获取单个合同
@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    return contract

# 创建合同
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(contract_data: ContractCreate, db: Session = Depends(get_db)):
    # 检查提供方公司是否存在
    provider = db.query(Company).filter(Company.id == contract_data.provider_id).first()
    if provider is None:
        raise HTTPException(status_code=404, detail="提供方公司不存在")
    
    # 检查接收方公司是否存在
    receiver = db.query(Company).filter(Company.id == contract_data.receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=404, detail="接收方公司不存在")
    
    # 创建合同对象
    db_contract = Contract(
        title=contract_data.title,
        contract_type=ContractType(contract_data.contract_type.value),
        status=ContractStatus.DRAFT,  # 初始状态为草稿
        description=contract_data.description,
        terms=contract_data.terms,
        value=contract_data.value,
        payment_terms=contract_data.payment_terms,
        penalty_terms=contract_data.penalty_terms,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        provider_id=contract_data.provider_id,
        receiver_id=contract_data.receiver_id,
        properties=contract_data.properties
    )
    
    # 保存到数据库
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    # 创建合同事件
    contract_event = ContractEvent(
        contract_id=db_contract.id,
        event_type="创建",
        description=f"合同 '{db_contract.title}' 已创建"
    )
    db.add(contract_event)
    db.commit()
    
    return db_contract

# 更新合同
@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(contract_id: int, contract_data: ContractUpdate, db: Session = Depends(get_db)):
    # 查找合同
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    # 更新合同信息
    if contract_data.title is not None:
        db_contract.title = contract_data.title
    if contract_data.description is not None:
        db_contract.description = contract_data.description
    if contract_data.status is not None:
        old_status = db_contract.status
        db_contract.status = ContractStatus(contract_data.status.value)
        
        # 创建状态变更事件
        contract_event = ContractEvent(
            contract_id=db_contract.id,
            event_type="状态变更",
            description=f"合同状态从 '{old_status.value}' 变更为 '{db_contract.status.value}'"
        )
        db.add(contract_event)
    
    if contract_data.terms is not None:
        db_contract.terms = contract_data.terms
    if contract_data.value is not None:
        db_contract.value = contract_data.value
    if contract_data.payment_terms is not None:
        db_contract.payment_terms = contract_data.payment_terms
    if contract_data.penalty_terms is not None:
        db_contract.penalty_terms = contract_data.penalty_terms
    if contract_data.start_date is not None:
        db_contract.start_date = contract_data.start_date
    if contract_data.end_date is not None:
        db_contract.end_date = contract_data.end_date
    if contract_data.properties is not None:
        db_contract.properties = contract_data.properties
    
    # 保存到数据库
    db.commit()
    db.refresh(db_contract)
    
    return db_contract

# 删除合同
@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    # 查找合同
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if db_contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    # 删除合同
    db.delete(db_contract)
    db.commit()
    
    return {"status": "success"}

# 获取合同事件
@router.get("/{contract_id}/events", response_model=List[dict])
async def get_contract_events(contract_id: int, db: Session = Depends(get_db)):
    # 查找合同
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="合同不存在")
    
    # 获取事件
    events = db.query(ContractEvent).filter(ContractEvent.contract_id == contract_id).order_by(ContractEvent.created_at.desc()).all()
    
    return [{
        "id": event.id,
        "event_type": event.event_type,
        "description": event.description,
        "properties": event.properties,
        "created_at": event.created_at
    } for event in events]

# 获取合同模板
@router.get("/templates", response_model=List[dict])
async def get_contract_templates(contract_type: Optional[ContractTypeEnum] = None, db: Session = Depends(get_db)):
    # 构建查询
    query = db.query(ContractTemplate)
    
    # 如果指定了合同类型，则过滤
    if contract_type is not None:
        query = query.filter(ContractTemplate.contract_type == ContractType(contract_type.value))
    
    # 获取模板
    templates = query.all()
    
    return [{
        "id": template.id,
        "name": template.name,
        "contract_type": template.contract_type.value,
        "description": template.description,
        "template": template.template
    } for template in templates]

# 根据模板创建合同
@router.post("/from-template/{template_id}", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract_from_template(template_id: int, provider_id: int, receiver_id: int, db: Session = Depends(get_db)):
    # 查找模板
    template = db.query(ContractTemplate).filter(ContractTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=404, detail="合同模板不存在")
    
    # 检查提供方公司是否存在
    provider = db.query(Company).filter(Company.id == provider_id).first()
    if provider is None:
        raise HTTPException(status_code=404, detail="提供方公司不存在")
    
    # 检查接收方公司是否存在
    receiver = db.query(Company).filter(Company.id == receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=404, detail="接收方公司不存在")
    
    # 从模板创建合同
    from datetime import datetime, timedelta
    
    # 设置默认开始和结束日期
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)  # 默认30天合同期
    
    # 创建合同对象
    db_contract = Contract(
        title=f"{template.name} - {provider.name} 与 {receiver.name}",
        contract_type=template.contract_type,
        status=ContractStatus.DRAFT,
        description=template.description,
        terms=template.template.get("terms"),
        value=template.template.get("default_value", 0.0),
        payment_terms=template.template.get("payment_terms"),
        penalty_terms=template.template.get("penalty_terms"),
        start_date=start_date,
        end_date=end_date,
        provider_id=provider_id,
        receiver_id=receiver_id,
        properties=template.template.get("properties")
    )
    
    # 保存到数据库
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    
    # 创建合同事件
    contract_event = ContractEvent(
        contract_id=db_contract.id,
        event_type="创建",
        description=f"合同 '{db_contract.title}' 已从模板 '{template.name}' 创建"
    )
    db.add(contract_event)
    db.commit()
    
    return db_contract