from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.company import Company, CompanyType, Asset, Group
from ..models.user import User

# 创建路由器
router = APIRouter()

# 公司数据模型
from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any, Optional

class CompanyTypeEnum(str, Enum):
    RAILWAY = "R"
    TRAIN = "T"
    SERVICE = "S"

class CompanyCreate(BaseModel):
    name: str
    type: CompanyTypeEnum
    description: Optional[str] = None
    user_id: int
    group_id: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    group_id: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    type: str
    description: Optional[str] = None
    balance: float
    income: float
    expenses: float
    reputation: float
    founded_date: datetime
    is_active: bool
    user_id: int
    group_id: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# 获取所有公司
@router.get("/", response_model=List[CompanyResponse])
async def get_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies

# 获取单个公司
@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="公司不存在")
    return company

# 创建公司
@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    # 检查用户是否存在
    user = db.query(User).filter(User.id == company.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查集团是否存在(如果提供了集团ID)
    if company.group_id:
        group = db.query(Group).filter(Group.id == company.group_id).first()
        if group is None:
            raise HTTPException(status_code=404, detail="集团不存在")
    
    # 创建公司对象
    db_company = Company(
        name=company.name,
        type=CompanyType(company.type.value),
        description=company.description,
        user_id=company.user_id,
        group_id=company.group_id,
        properties=company.properties
    )
    
    # 保存到数据库
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company

# 更新公司
@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: int, company: CompanyUpdate, db: Session = Depends(get_db)):
    # 查找公司
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="公司不存在")
    
    # 更新公司信息
    if company.name is not None:
        db_company.name = company.name
    if company.description is not None:
        db_company.description = company.description
    if company.group_id is not None:
        # 检查集团是否存在
        group = db.query(Group).filter(Group.id == company.group_id).first()
        if group is None:
            raise HTTPException(status_code=404, detail="集团不存在")
        db_company.group_id = company.group_id
    if company.properties is not None:
        db_company.properties = company.properties
    
    # 保存到数据库
    db.commit()
    db.refresh(db_company)
    
    return db_company

# 删除公司
@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, db: Session = Depends(get_db)):
    # 查找公司
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="公司不存在")
    
    # 删除公司
    db.delete(db_company)
    db.commit()
    
    return {"status": "success"}

# 获取公司资产
@router.get("/{company_id}/assets", response_model=List[dict])
async def get_company_assets(company_id: int, db: Session = Depends(get_db)):
    # 查找公司
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="公司不存在")
    
    # 获取资产
    assets = db.query(Asset).filter(Asset.company_id == company_id).all()
    
    return [{
        "id": asset.id,
        "name": asset.name,
        "type": asset.type,
        "value": asset.value,
        "condition": asset.condition,
        "properties": asset.properties
    } for asset in assets]

# 获取公司财务信息
@router.get("/{company_id}/finance", response_model=dict)
async def get_company_finance(company_id: int, db: Session = Depends(get_db)):
    # 查找公司
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="公司不存在")
    
    # 返回财务信息
    return {
        "balance": company.balance,
        "income": company.income,
        "expenses": company.expenses,
        "net_profit": company.income - company.expenses,
        "assets_value": sum(asset.value for asset in company.assets)
    }