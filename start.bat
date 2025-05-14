@echo off
echo 正在启动铁路大亨模拟器...

:: 检查Docker是否安装
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Docker，请先安装Docker Desktop
    exit /b 1
)

:: 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Docker Compose，请先安装Docker Desktop
    exit /b 1
)

:: 构建并启动容器
echo 正在构建并启动容器...
docker-compose up -d --build

:: 等待服务启动
echo 等待服务启动...
timeout /t 5 /nobreak >nul

:: 检查服务状态
echo 检查服务状态:
docker-compose ps

echo.
echo 铁路大亨模拟器已启动!
echo.
echo 访问地址:
echo - 前端界面: http://localhost:80
echo - API文档: http://localhost:8000/docs
echo.
echo 使用以下命令查看日志:
echo docker-compose logs -f
echo.
echo 使用以下命令停止服务:
echo docker-compose down
echo.

pause