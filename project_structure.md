# 铁路大亨模拟器项目结构

## 项目概述

根据README文档，本项目是一款大型多人在线铁路经营策略模拟游戏，玩家将扮演铁路产业链中的不同角色，通过合作与竞争建立高效的铁路运输网络。

## 目录结构

```
tcgame/
├── README.md                 # 项目说明文档
├── requirements.txt          # 后端依赖
├── .env                      # 环境变量配置
├── backend/                  # 后端代码
│   ├── main.py               # 主入口文件
│   ├── config.py             # 配置文件
│   ├── database.py           # 数据库连接
│   ├── celery_app.py         # Celery配置
│   ├── game_engine/          # 游戏核心逻辑
│   │   ├── __init__.py
│   │   ├── world_generator/  # 地图生成器
│   │   ├── economy_system/   # 经济模拟系统
│   │   ├── company_manager/  # 公司管理系统
│   │   ├── group_system/     # 集团系统
│   │   └── scheduler/        # 游戏时间调度
│   ├── api_service/          # API服务层
│   │   ├── __init__.py
│   │   ├── company_api.py    # 公司相关接口
│   │   ├── map_api.py        # 地图相关接口
│   │   ├── contract_api.py   # 合同系统接口
│   │   └── admin_api.py      # 管理接口
│   ├── realtime_service/     # 实时服务
│   │   ├── __init__.py
│   │   ├── notification.py   # 通知系统
│   │   ├── market.py         # 实时交易市场
│   │   └── event_bus.py      # 事件总线
│   └── models/               # 数据模型
│       ├── __init__.py
│       ├── company.py        # 公司模型
│       ├── map.py            # 地图模型
│       ├── contract.py       # 合同模型
│       └── user.py           # 用户模型
├── frontend/                 # 前端代码
│   ├── package.json          # 前端依赖
│   ├── vite.config.js        # Vite配置
│   ├── index.html            # 入口HTML
│   ├── src/                  # 源代码
│   │   ├── main.ts           # 主入口
│   │   ├── App.vue           # 根组件
│   │   ├── router/           # 路由
│   │   ├── store/            # 状态管理
│   │   ├── api/              # API调用
│   │   ├── components/       # 通用组件
│   │   └── views/            # 页面组件
│   │       ├── company-management/  # 公司管理
│   │       ├── map-explorer/        # 地图探索器
│   │       ├── operation-control/   # 运营控制台
│   │       ├── contract-center/     # 合同中心
│   │       ├── financial-report/    # 财务报告
│   │       ├── ranking-board/       # 排行榜
│   │       └── social-hub/          # 社交中心
│   ├── public/               # 静态资源
│   └── tests/                # 测试文件
└── docker/                   # Docker配置
    ├── docker-compose.yml    # 容器编排
    ├── Dockerfile.backend    # 后端Docker配置
    └── Dockerfile.frontend   # 前端Docker配置
```

## 技术栈

### 后端
- FastAPI: RESTful API框架
- WebSocket: 实时通信
- Celery: 异步任务队列
- Redis: 缓存和消息队列
- MySQL: 持久化存储
- SQLAlchemy: ORM框架

### 前端
- Vue 3: 前端框架
- TypeScript: 类型安全
- Element Plus: UI组件库
- ECharts: 数据可视化
- Pinia: 状态管理

## 开发计划

按照README中的开发路线图进行：

1. 核心原型 (1-2月): 基础经济系统、简单地图生成
2. Alpha测试 (3-4月): 核心玩法验证、压力测试
3. Beta测试 (5-6月): 内容完善、平衡性调整
4. 正式上线 (7月): 赛季系统上线、营销推广