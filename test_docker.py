#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
铁路大亨模拟器Docker环境测试脚本

此脚本用于测试Docker容器环境是否正常运行，检查各服务的可用性。
"""

import os
import sys
import time
import requests
import subprocess
from urllib.parse import urlparse

# 颜色输出
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'RESET': '\033[0m',
    'BOLD': '\033[1m'
}

def print_colored(text, color):
    """打印彩色文本"""
    if os.name == 'nt':  # Windows环境
        print(text)
    else:
        print(f"{COLORS[color]}{text}{COLORS['RESET']}")

def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print_colored(text, 'BOLD')
    print("=" * 60)

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_docker_running():
    """检查Docker是否运行"""
    print_header("检查Docker服务")
    success, output = run_command("docker info")
    if success:
        print_colored("✓ Docker服务正在运行", 'GREEN')
        return True
    else:
        print_colored("✗ Docker服务未运行，请先启动Docker", 'RED')
        return False

def check_containers_status():
    """检查容器状态"""
    print_header("检查容器状态")
    success, output = run_command("docker-compose ps")
    if not success:
        print_colored("✗ 无法获取容器状态，请确保在项目目录中运行此脚本", 'RED')
        return False
    
    print(output)
    
    # 检查所有容器是否都在运行
    success, output = run_command("docker-compose ps -q")
    if not success or not output.strip():
        print_colored("✗ 没有运行中的容器，请先启动服务", 'RED')
        return False
    
    container_ids = output.strip().split('\n')
    all_running = True
    
    for container_id in container_ids:
        success, status = run_command(f"docker inspect -f {{{{.State.Status}}}} {container_id}")
        if not success or status.strip() != 'running':
            all_running = False
            break
    
    if all_running:
        print_colored("✓ 所有容器都在正常运行", 'GREEN')
        return True
    else:
        print_colored("✗ 部分容器未正常运行，请检查日志", 'RED')
        return False

def check_service_availability():
    """检查服务可用性"""
    print_header("检查服务可用性")
    
    services = [
        {"name": "前端服务", "url": "http://localhost:80", "timeout": 5},
        {"name": "后端API", "url": "http://localhost:8000/docs", "timeout": 5},
    ]
    
    all_available = True
    
    for service in services:
        try:
            print(f"检查{service['name']}({service['url']})...")
            response = requests.get(service['url'], timeout=service['timeout'])
            if response.status_code < 400:
                print_colored(f"✓ {service['name']}可访问 (状态码: {response.status_code})", 'GREEN')
            else:
                print_colored(f"✗ {service['name']}返回错误 (状态码: {response.status_code})", 'YELLOW')
                all_available = False
        except requests.exceptions.RequestException as e:
            print_colored(f"✗ 无法连接到{service['name']}: {str(e)}", 'RED')
            all_available = False
    
    return all_available

def main():
    """主函数"""
    print_colored("\n铁路大亨模拟器Docker环境测试\n", 'BOLD')
    
    # 检查Docker是否运行
    if not check_docker_running():
        return 1
    
    # 检查容器状态
    if not check_containers_status():
        print_colored("\n提示: 使用 'docker-compose up -d' 启动所有服务", 'YELLOW')
        return 1
    
    # 检查服务可用性
    service_available = check_service_availability()
    
    # 总结
    print_header("测试结果")
    if service_available:
        print_colored("✓ 所有服务正常运行！", 'GREEN')
        return 0
    else:
        print_colored("✗ 部分服务不可用，请检查日志排查问题", 'YELLOW')
        print_colored("\n提示: 使用 'docker-compose logs -f' 查看详细日志", 'YELLOW')
        return 1

if __name__ == "__main__":
    sys.exit(main())