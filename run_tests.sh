#!/bin/bash
# 铁路大亨模拟器测试运行脚本
# 用于运行单元测试和集成测试

echo "铁路大亨模拟器测试运行器"
echo "============================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python安装。请安装Python 3.7或更高版本。"
    exit 1
fi

# 检查是否存在虚拟环境，如果存在则激活
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境。"
else
    echo "警告: 未找到虚拟环境。使用系统Python环境。"
fi

# 检查是否安装了测试依赖
if ! python3 -m pip show pytest &> /dev/null; then
    echo "正在安装测试依赖..."
    python3 -m pip install pytest pytest-cov
    if [ $? -ne 0 ]; then
        echo "错误: 安装测试依赖失败。"
        exit 1
    fi
fi

# 解析命令行参数
if [ -z "$1" ]; then
    echo "可用的测试选项:"
    echo "  all        - 运行所有测试"
    echo "  unit       - 只运行单元测试"
    echo "  integration - 只运行集成测试"
    echo "  coverage   - 运行测试并生成覆盖率报告"
    echo ""
    read -p "请选择测试类型 [all]: " TEST_TYPE
    TEST_TYPE=${TEST_TYPE:-all}
else
    TEST_TYPE=$1
fi

echo ""
echo "开始运行测试: $TEST_TYPE"
echo "============================"
echo ""

case "$TEST_TYPE" in
    all)
        python3 tests/run_tests.py
        ;;
    unit)
        python3 tests/run_tests.py unit
        ;;
    integration)
        python3 tests/run_tests.py integration
        ;;
    coverage)
        python3 -m pytest --cov=backend --cov=frontend tests/
        echo ""
        echo "覆盖率报告已生成。"
        ;;
    *)
        echo "错误: 未知的测试类型 '$TEST_TYPE'"
        echo "可用选项: all, unit, integration, coverage"
        exit 1
        ;;
esac

echo ""
echo "测试完成。"

# 如果使用了虚拟环境，则退出虚拟环境
if [ -f "venv/bin/activate" ]; then
    deactivate
fi