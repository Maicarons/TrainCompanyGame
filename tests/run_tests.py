#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试运行脚本
用于运行所有单元测试和集成测试
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
    """运行所有测试"""
    # 发现并加载所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

def run_unit_tests():
    """只运行单元测试"""
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(os.path.dirname(__file__), 'unit'), pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """只运行集成测试"""
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.join(os.path.dirname(__file__), 'integration'), pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # 解析命令行参数
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'unit':
            success = run_unit_tests()
        elif test_type == 'integration':
            success = run_integration_tests()
        else:
            print(f"未知的测试类型: {test_type}")
            print("可用选项: unit, integration, 或不指定运行所有测试")
            sys.exit(1)
    else:
        # 默认运行所有测试
        success = run_all_tests()
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)