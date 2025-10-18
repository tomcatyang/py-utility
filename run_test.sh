#!/bin/bash
# -*- coding: utf-8 -*-
"""
运行测试
"""

echo "开始运行 py-utility 测试..."

python3 tests/run_tests.py

echo "开始运行 demo.example..."
python -m demo.example