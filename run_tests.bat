@echo off
REM 铁路大亨模拟器测试运行脚本
REM 用于运行单元测试和集成测试

setlocal

echo 铁路大亨模拟器测试运行器
echo ============================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未检测到Python安装。请安装Python 3.7或更高版本。
    exit /b 1
)

REM 检查是否存在虚拟环境，如果存在则激活
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 已激活虚拟环境。
) else (
    echo 警告: 未找到虚拟环境。使用系统Python环境。
)

REM 检查是否安装了测试依赖
pip show pytest >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 正在安装测试依赖...
    pip install pytest pytest-cov
    if %ERRORLEVEL% NEQ 0 (
        echo 错误: 安装测试依赖失败。
        exit /b 1
    )
)

REM 解析命令行参数
if "%1"=="" (
    echo 可用的测试选项:
    echo   all        - 运行所有测试
    echo   unit       - 只运行单元测试
    echo   integration - 只运行集成测试
    echo   coverage   - 运行测试并生成覆盖率报告
    echo.
    set /p TEST_TYPE=请选择测试类型 [all]: 
    if "!TEST_TYPE!"=="" set TEST_TYPE=all
) else (
    set TEST_TYPE=%1
)

echo.
echo 开始运行测试: %TEST_TYPE%
echo ============================
echo.

if "%TEST_TYPE%"=="all" (
    python tests\run_tests.py
) else if "%TEST_TYPE%"=="unit" (
    python tests\run_tests.py unit
) else if "%TEST_TYPE%"=="integration" (
    python tests\run_tests.py integration
) else if "%TEST_TYPE%"=="coverage" (
    pytest --cov=backend --cov=frontend tests/
    echo.
    echo 覆盖率报告已生成。
) else (
    echo 错误: 未知的测试类型 '%TEST_TYPE%'
    echo 可用选项: all, unit, integration, coverage
    exit /b 1
)

echo.
echo 测试完成。

REM 如果使用了虚拟环境，则退出虚拟环境
if exist venv\Scripts\activate.bat (
    deactivate
)

endlocal