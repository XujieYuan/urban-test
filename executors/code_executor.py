"""
Code Executor - 负责处理 GitHub 代码工具

⚠️ **COMING SOON** - This module is currently under development

开发者：Code 团队负责人
职责：
1. 管理 GitHub 代码仓库的克隆
2. 调用 MCP-agent-github-repo-output 转换代码为 MCP
3. 管理转换后的工具缓存
4. 处理本地 MCP 工具的调用

TODO for Code Developer:
- [ ] 实现增量更新（避免重复克隆）
- [ ] 添加版本管理（支持指定 commit/tag）
- [ ] 实现转换失败的回退机制
- [ ] 优化大型仓库的处理
- [ ] 添加工具元数据管理

依赖说明：
- 需要父项目的 MCP 转换功能或独立实现
- GitHub: 需要提供 MCP-agent-github-repo-output 项目地址
- 安装方式: git clone 到指定位置
"""

import os
import sys
import json
from typing import Dict, Any
from pathlib import Path


class CodeExecutor:
    """GitHub 代码工具执行器"""

    def __init__(self, tools_dir: str = "./tools/code"):
        """
        初始化代码执行器

        Args:
            tools_dir: 转换后的工具存储目录
        """
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        # 项目根目录（用于访问父项目的 MCP 转换功能）
        self.project_root = Path(__file__).parent.parent.parent

    def execute(self, config: Dict, arguments: Dict) -> Dict[str, Any]:
        """
        执行代码工具调用

        ⚠️ COMING SOON - Code tool support is under development

        Args:
            config: 工具配置
                - name: 工具名称
                - github_url: GitHub 仓库 URL
                - entry_function: 入口函数名
                - params: 参数定义
            arguments: 实际调用参数

        Returns:
            {
                "success": bool,
                "result": Any,
                "error": str | None
            }
        """
        # Code 工具支持正在开发中
        return {
            "success": False,
            "result": None,
            "error": (
                "⚠️ Code Executor is coming soon! "
                "This feature requires GitHub code to MCP conversion functionality. "
                f"Tool '{config.get('name', 'unknown')}' from '{config.get('github_url', 'unknown')}' cannot be executed yet. "
                "Please use API tools or check back later for updates."
            )
        }

    def _get_mcp_path(self, github_url: str) -> Path:
        """
        获取转换后的 MCP 工具路径

        Args:
            github_url: GitHub 仓库 URL

        Returns:
            MCP 插件目录路径
        """
        repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")
        return self.tools_dir / repo_name / "mcp_output" / "mcp_plugin"

    def _convert_to_mcp(self, github_url: str):
        """
        将 GitHub 代码转换为 MCP 工具

        TODO: Code 开发者需要实现/优化此部分
        - 处理转换失败的情况
        - 添加进度反馈
        - 支持指定版本/分支
        """
        import asyncio

        # 添加父项目目录到 sys.path
        parent_dir = str(self.project_root)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        try:
            # 调用父项目的 MCP 转换功能
            from MCP import process_github_repos

            result = asyncio.run(process_github_repos(github_url))
            print(f"✅ Conversion complete: {result.get('processed_names', [])}")

        except Exception as e:
            raise Exception(f"Failed to convert GitHub repo to MCP: {str(e)}")

    def _call_local_mcp(self, mcp_path: Path, config: Dict, arguments: Dict) -> Any:
        """
        调用本地 MCP 工具

        TODO: Code 开发者可以优化此部分
        - 支持更多的调用方式
        - 添加错误处理
        - 实现工具热重载

        Args:
            mcp_path: MCP 插件路径
            config: 工具配置
            arguments: 调用参数

        Returns:
            工具执行结果
        """
        # 添加 MCP 插件路径到 sys.path
        mcp_str = str(mcp_path)
        if mcp_str not in sys.path:
            sys.path.insert(0, mcp_str)

        try:
            # 方式 1: 尝试导入 Adapter
            from adapter import Adapter  # type: ignore

            adapter = Adapter()

            # 调用指定的入口函数
            entry_function = config.get("entry_function", "run")

            if not hasattr(adapter, entry_function):
                raise AttributeError(
                    f"Adapter does not have method: {entry_function}. "
                    f"Available methods: {[m for m in dir(adapter) if not m.startswith('_')]}"
                )

            method = getattr(adapter, entry_function)
            result = method(**arguments)

            return result

        except ImportError:
            # 方式 2: 尝试直接导入 mcp_service
            try:
                from mcp_service import mcp as mcp_instance  # type: ignore

                # 找到对应的工具
                tool_name = config.get("name", "")

                for tool in mcp_instance.tools:
                    if tool.name == tool_name:
                        return tool.fn(**arguments)

                raise ValueError(
                    f"Tool '{tool_name}' not found in MCP service. "
                    f"Available tools: {[t.name for t in mcp_instance.tools]}"
                )

            except ImportError as e:
                raise Exception(
                    f"Failed to import MCP module from {mcp_path}. "
                    f"Make sure the conversion was successful. Error: {str(e)}"
                )


# 开发者测试代码
if __name__ == "__main__":
    executor = CodeExecutor()

    # 测试配置
    config = {
        "name": "geopandas_spatial",
        "github_url": "https://github.com/geopandas/geopandas",
        "entry_function": "spatial_operation",
        "params": {
            "operation": {"type": "string", "required": True},
            "geometry": {"type": "object", "required": True}
        }
    }

    arguments = {
        "operation": "buffer",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "distance": 100
    }

    result = executor.execute(config, arguments)
    print(json.dumps(result, indent=2, ensure_ascii=False))
