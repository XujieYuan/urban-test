"""
Tool Executors Package

各执行器必须实现统一接口：
- execute(config: Dict, arguments: Dict) -> Dict[str, Any]

返回格式:
{
    "success": bool,
    "result": Any,
    "error": str | None
}
"""

from .mcp_executor import MCPExecutor
from .api_executor import APIExecutor
from .code_executor import CodeExecutor

__all__ = ["MCPExecutor", "APIExecutor", "CodeExecutor"]
