"""
茶猫小栈 - 生产模式启动器
构建前端 + FastAPI 统一服务，一个端口全搞定喵~
"""

import subprocess
import sys
from pathlib import Path

import uvicorn

if __name__ == "__main__":
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    dist_dir = frontend_dir / "dist"

    # 1. 构建前端
    print("🚀 正在构建前端喵~")
    result = subprocess.run(
        [sys.executable, "-m", "astro", "build"],
        cwd=str(frontend_dir),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print("❌ 前端构建失败:", result.stderr)
        sys.exit(1)
    print("✅ 前端构建成功！")

    # 2. 启动统一服务（托管前端静态文件 + API + 管理后台）
    print(f"🌐 服务启动：http://localhost:8000")
    print(f"📝 管理后台：http://localhost:8000/admin/")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
