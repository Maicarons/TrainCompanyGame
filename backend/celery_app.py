from celery import Celery
from config import settings

# 创建Celery实例
celery_app = Celery(
    "tcgame",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        # 游戏引擎任务
        "game_engine.world_generator.tasks",
        "game_engine.economy_system.tasks",
        "game_engine.company_manager.tasks",
        "game_engine.group_system.tasks",
        "game_engine.scheduler.tasks",
        # 实时服务任务
        "realtime_service.notification.tasks",
        "realtime_service.market.tasks",
    ]
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    # 定时任务配置
    beat_schedule={
        "update-game-state": {
            "task": "game_engine.scheduler.tasks.update_game_state",
            "schedule": settings.GAME_TICK_INTERVAL,
        },
        "backup-game-state": {
            "task": "game_engine.scheduler.tasks.backup_game_state",
            "schedule": 3600,  # 每小时备份一次
        },
    },
)

if __name__ == "__main__":
    celery_app.start()