import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # 基础配置
    PROJECT_NAME: str = "TrainCompanyGame"
    PROJECT_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # 数据库配置
    MYSQL_USER: str = os.getenv("MYSQL_USER", "tcgame")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "tcgame123")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "tcgame")
    DATABASE_URL: str = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Celery配置
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # 游戏配置
    GAME_DAYS_PER_SEASON: int = 21
    GAME_BREAK_DAYS: int = 7
    GAME_TICK_INTERVAL: int = 60  # 游戏时钟间隔（秒）
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tcgame_secret_key_please_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天

settings = Settings()