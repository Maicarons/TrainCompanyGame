# 铁路大亨模拟器部署指南

本文档提供了使用Docker部署铁路大亨模拟器项目的详细说明。

## 前提条件

在开始部署之前，请确保您的系统已安装以下软件：

- Docker (20.10.0或更高版本)
- Docker Compose (2.0.0或更高版本)

## 部署步骤

### 1. 准备环境

1. 克隆项目代码库：
   ```bash
   git clone <项目仓库URL>
   cd tcgame
   ```

2. 创建环境配置文件：
   ```bash
   cp .env.example .env
   ```
   
3. 根据需要修改`.env`文件中的配置参数。

### 2. 启动服务

#### Windows环境

双击运行`start.bat`文件，或在命令提示符中执行：

```cmd
start.bat
```

#### Linux/Mac环境

执行以下命令：

```bash
chmod +x start.sh
./start.sh
```

或者，您也可以直接使用Docker Compose命令：

```bash
docker-compose up -d --build
```

### 3. 访问服务

服务启动成功后，您可以通过以下地址访问：

- **前端界面**：http://localhost:80
- **API文档**：http://localhost:8000/docs

### 4. 服务管理

#### 查看日志

```bash
docker-compose logs -f
```

#### 停止服务

```bash
docker-compose down
```

#### 重启服务

```bash
docker-compose restart
```

## 容器说明

本项目包含以下Docker容器：

1. **frontend**：前端服务，基于Nginx提供静态资源服务
2. **backend**：后端API服务，基于FastAPI
3. **redis**：缓存服务，用于存储会话和实时数据
4. **mysql**：数据库服务，用于持久化存储游戏数据
5. **celery_worker**：异步任务处理服务，处理耗时操作

## 数据持久化

项目使用Docker卷来持久化存储数据：

- **redis_data**：Redis数据
- **mysql_data**：MySQL数据

## 常见问题

### 端口冲突

如果遇到端口冲突问题，请修改`docker-compose.yml`文件中的端口映射配置。

### 数据库连接问题

确保MySQL服务已正常启动，并且环境变量中的数据库连接信息正确。

### 容器启动失败

使用以下命令查看容器日志，排查问题：

```bash
docker-compose logs <服务名>
```

## 生产环境部署

对于生产环境部署，建议：

1. 修改`.env`文件中的`APP_ENV`为`production`
2. 设置强密码并更改默认的数据库凭据
3. 配置HTTPS证书
4. 实施适当的备份策略

---

如有任何部署问题，请参考项目文档或联系开发团队。