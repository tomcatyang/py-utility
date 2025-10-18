#!/bin/bash
# 项目环境初始化脚本

echo "======================================"
echo "py-utility - 环境初始化"
echo "======================================"

# 检查Python版本
echo "检查Python版本..."
python3 --version

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
else
    echo "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境（仅在脚本执行期间有效）
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p logs
mkdir -p db

# 检查配置文件
if [ ! -f ".env.dev" ]; then
    echo "警告: .env.dev 配置文件不存在"
    echo "请复制 env.template 为 .env.dev 并填入实际配置值："
    echo "  cp env.template .env.dev"
    echo "  vim .env.dev"
fi

echo "======================================"
echo "环境初始化完成！"
echo "======================================"
echo ""
echo "⚠️  重要提示："
echo "   脚本中的虚拟环境激活仅在脚本执行期间有效"
echo "   请手动执行以下命令来激活虚拟环境："
echo ""
echo "   source venv/bin/activate"
echo ""
echo "======================================"
echo ""
echo "后续步骤："
echo "1. 激活虚拟环境（必须）："
echo "   source venv/bin/activate"
echo ""
echo "2. 配置环境变量："
echo "   cp env.template .env.dev"
echo "   vim .env.dev"
echo ""
echo "3. 初始化数据库："
echo "   mysql -u root -p < db/schema.sql"
echo ""
echo "4. 运行系统："
echo "   ./run.sh dev"
echo ""

