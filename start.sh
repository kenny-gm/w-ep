#!/bin/bash
# WB ERP 启动脚本

echo "========================================="
echo "  WB ERP - 启动脚本"
echo "========================================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装"
    exit 1
fi

echo "✓ Docker 环境检查通过"

# 停止旧容器
echo "正在停止旧容器..."
docker-compose down 2>/dev/null

# 构建并启动
echo "正在构建镜像..."
docker-compose build

echo "正在启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "========================================="
echo "  服务状态"
echo "========================================="
docker-compose ps

echo ""
echo "========================================="
echo "  访问地址"
echo "========================================="
echo "前端: http://localhost"
echo "后端: http://localhost/api"
echo "API文档: http://localhost/api/docs"
echo ""
echo "创建管理员账号:"
echo "docker exec -it wb-erp-backend python -c '"
echo "from app.database import SessionLocal"
echo "from app.models.models import User"
echo "from app.utils.security import get_password_hash"
echo "from app.models.models import UserRole"
echo "db = SessionLocal()"
echo "user = User(username=\"admin\", email=\"admin@example.com\", hashed_password=get_password_hash(\"admin123\"), role=UserRole.ADMIN, is_active=True)"
echo "db.add(user)"
echo "db.commit()"
echo "print(\"管理员创建成功: admin / admin123\")"
echo "'"
echo ""
