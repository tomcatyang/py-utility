#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """运行测试"""
    print("开始运行 py-utility 测试...")
    
    # 获取项目根目录（tests目录的父目录）
    project_root = Path(__file__).parent.parent
    
    # 运行pytest
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--cov=src",
            "--cov-report=term-missing"
        ], cwd=project_root, check=True)
        
        print("\n✅ 所有测试通过！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 测试失败，退出码: {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ 未找到 pytest，请先安装: pip install pytest pytest-cov")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
