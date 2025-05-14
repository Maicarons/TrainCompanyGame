#!/bin/bash

# 铁路大亨模拟器启动脚本
echo "正在启动铁路大亨模拟器..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未检测到Docker，请先安装Docker和Docker Compose"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未检测到Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 构建并启动容器
echo "正在构建并启动容器..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo "检查服务状态:"
docker-compose ps

echo "
铁路大亨模拟器已启动!

访问地址:
- 前端界面: http://localhost:80
- API文档: http://localhost:8000/docs

使用以下命令查看日志:
docker-compose logs -f

使用以下命令停止服务:
docker-compose down
"