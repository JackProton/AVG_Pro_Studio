# src/my_avg_studio/__init__.py

"""
AVG Pro Studio 核心逻辑包
包含：
- manager.py: 项目与配置管理
- engine.py: CrewAI 多 Agent 调度引擎
- models.py: 数据结构定义
"""

# 为了让外部引用更简洁，我们在这里提前暴露核心类
from .manager import ProjectManager
from .engine import AvgEngine
from .models import LogicScriptNode, FlagChange

# 定义对外暴露的接口列表 (规范化做法)
__all__ = [
    "ProjectManager",
    "AvgEngine",
    "LogicScriptNode",
    "FlagChange"
]