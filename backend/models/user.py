from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from passlib.context import CryptContext

from ..database import Base

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用户角色枚举
class UserRole(enum.Enum):
    PLAYER = "player"  # 普通玩家
    ADMIN = "admin"    # 管理员

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.PLAYER)
    
    # 用户信息
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(200), nullable=True)
    
    # 游戏统计
    experience = Column(Integer, default=0)  # 经验值
    level = Column(Integer, default=1)  # 等级
    total_games = Column(Integer, default=0)  # 总游戏次数
    wins = Column(Integer, default=0)  # 胜利次数
    
    # 账户状态
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # 用户特定属性
    preferences = Column(JSON, nullable=True)  # 用户偏好设置
    achievements = Column(JSON, nullable=True)  # 成就记录
    
    # 关系
    companies = relationship("Company", back_populates="user")
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
    
    def verify_password(self, plain_password):
        """验证密码"""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def get_password_hash(password):
        """获取密码哈希值"""
        return pwd_context.hash(password)

# 用户会话模型
class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String(100), unique=True, index=True)
    expires_at = Column(DateTime)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(200), nullable=True)
    
    # 关系
    user = relationship("User")
    
    # 创建时间
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserSession for User #{self.user_id}>"
    
    def is_expired(self):
        """检查会话是否过期"""
        return datetime.utcnow() > self.expires_at