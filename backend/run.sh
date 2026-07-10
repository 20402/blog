#!/usr/bin/env bash
# 茶猫小栈 - 一键启动喵~

cd "$(dirname "$0")"

if [ "$1" = "kill" ]; then
  echo "🔪 干掉 8000 端口的坏进程喵~"
  fuser -k 8000/tcp 2>/dev/null && echo "✅ 清理完毕！" || echo "🔍 没有进程在 8000 端口上喵~"
  exit 0
fi

PYTHON=".venv/bin/python3"

# 自动清理旧进程
fuser -k 8000/tcp 2>/dev/null
sleep 1

# 构建前端
cd ../frontend
echo "🚀 构建前端喵~"
pnpm run build 2>&1 | tail -3
cd ../backend

echo ""
echo "🌐 茶猫小栈 启动啦~"
echo "   🏠 博客:    http://localhost:8000/"
echo "   📝 管理后台: http://localhost:8000/admin/"
echo "   🔌 API文档:  http://localhost:8000/docs"
echo "   🔑 密码:    ${BLOG_ADMIN_PASSWORD:-cat123}"
echo ""

# 自动打开浏览器
xdg-open http://localhost:8000/ 2>/dev/null || true

exec $PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000
