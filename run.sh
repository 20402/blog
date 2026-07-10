#!/bin/bash
# 茶猫小栈 - 一键启动脚本
# 同时启动前端 (Astro) 和后端 (FastAPI)

BLOG_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🐱 茶猫小栈启动啦~"
echo "=================="

# 启动后端
echo "📡 启动后端 API (port 8000)..."
cd "$BLOG_DIR/backend"
"$BLOG_DIR/backend/venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 启动前端
echo "🌐 启动前端博客 (port 4321)..."
cd "$BLOG_DIR/frontend"
"$BLOG_DIR/frontend/node_modules/.pnpm/astro@5.13.10_@types+node@24.5.2_jiti@1.21.7_lightningcss@1.29.3_rollup@2.79.2_sass@1.80.4_st_s7hqsa4qywm5m5vu4ywkwg7ioa/node_modules/astro/astro.js" dev --host 0.0.0.0 --port 4321 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"

echo ""
echo "✅ 启动完成！"
echo "   前端: http://$(hostname -I 2>/dev/null | awk '{print $1}'):4321"
echo "   后端: http://$(hostname -I 2>/dev/null | awk '{print $1}'):8000"
echo "   API:  http://$(hostname -I 2>/dev/null | awk '{print $1}'):8000/api/health"
echo ""
echo "按 Ctrl+C 停止所有服务"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '👋 茶猫小栈关闭啦~'; exit" SIGINT SIGTERM
wait
