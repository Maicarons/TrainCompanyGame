# 铁路大亨模拟器项目设置指南

## 项目概述

铁路大亨模拟器(TrainCompanyGame)是一款大型多人在线铁路经营策略模拟游戏，玩家将扮演铁路产业链中的不同角色，通过合作与竞争建立高效的铁路运输网络。

## 环境要求

### 后端环境
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### 前端环境
- Node.js 16+
- npm 8+

## 项目设置步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd tcgame
```

### 2. 后端设置

#### 安装依赖

```bash
pip install -r requirements.txt
```

#### 配置环境变量

编辑项目根目录下的`.env`文件，根据你的环境配置数据库和Redis连接信息。

#### 初始化数据库

```bash
python -c "from backend.database import init_db; init_db()"
```

#### 启动后端服务

```bash
cd backend
uvicorn main:app --reload
```

服务将在 http://localhost:8000 运行，API文档可在 http://localhost:8000/docs 访问。

#### 启动Celery工作进程

```bash
celery -A backend.celery_app worker --loglevel=info
```

#### 启动Celery定时任务

```bash
celery -A backend.celery_app beat --loglevel=info
```

### 3. 前端设置

#### 安装依赖

```bash
cd frontend
npm install
```

#### 启动开发服务器

```bash
npm run dev
```

前端将在 http://localhost:5173 运行。

## 项目结构

项目采用前后端分离架构，详细结构请参考`project_structure.md`文件。

### 后端主要模块

- **game_engine**: 游戏核心逻辑，包括地图生成、经济系统、公司管理等
- **api_service**: API服务层，提供RESTful接口
- **realtime_service**: 实时服务，处理WebSocket通信和事件
- **models**: 数据模型定义

### 前端主要模块

- **views**: 页面组件，包括公司管理、地图探索器等
- **components**: 通用组件
- **store**: 状态管理
- **api**: API调用封装

## 开发指南

### 后端开发

1. 所有新功能应该在对应的模块中实现
2. 使用SQLAlchemy ORM进行数据库操作
3. 长时间运行的任务应该使用Celery异步处理
4. 实时更新应通过WebSocket实现

### 前端开发

1. 使用Vue 3组合式API开发组件
2. 使用TypeScript确保类型安全
3. 使用Element Plus组件库构建UI
4. 使用ECharts进行数据可视化

## 测试

### 后端测试

```bash
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

## 部署

项目提供了Docker配置，可以使用Docker Compose进行部署：

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## 注意事项

- 开发环境中，确保MySQL和Redis服务已启动
- 生产环境中，请修改`.env`文件中的密钥和数据库密码
- 定期备份数据库，确保游戏数据安全

## 问题排查

如果遇到问题，请检查：

1. 数据库和Redis连接是否正常
2. 环境变量是否正确配置
3. 依赖包是否完整安装
4. 日志文件中是否有错误信息

## 联系方式

如有问题，请联系项目维护者。