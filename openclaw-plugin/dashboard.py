# -*- coding: utf-8 -*-
"""
MemoryX OpenClaw Plugin - Dashboard Server
启动 Web Dashboard 服务
"""
import os
import sys
from pathlib import Path

# 确保 memoryx 可导入
plugin_dir = Path(__file__).parent
if str(plugin_dir.parent) not in sys.path:
    sys.path.insert(0, str(plugin_dir.parent))


def start_dashboard(port: int = None):
    """启动 MemoryX Dashboard"""
    from memoryx.dashboard.main import run_dashboard
    
    # 从配置读取端口
    if port is None:
        port = int(os.getenv("MEMORYX_DASHBOARD_PORT", "19876"))
    
    print(f"Starting MemoryX Dashboard on port {port}...")
    print(f"Access at: http://localhost:{port}")
    
    run_dashboard(port=port)


def get_dashboard_url() -> str:
    """获取 Dashboard URL"""
    port = os.getenv("MEMORYX_DASHBOARD_PORT", "19876")
    return f"http://localhost:{port}"


# OpenClaw 技能入口
if __name__ == "__main__":
    start_dashboard()
