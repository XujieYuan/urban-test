"""
模块化工具池管理器
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from langchain.tools import StructuredTool

from executors import MCPExecutor, APIExecutor, CodeExecutor


class UrbanToolManager:
    """Urban Computing 工具池管理器"""

    def __init__(self, config_path: str = "./urban_tools.json"):
        """
        初始化工具管理器

        Args:
            config_path: 工具配置文件路径
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Tool configuration file not found: {config_path}")

        # 加载配置
        with open(config_file) as f:
            data = json.load(f)
            self.mcp_tools = data.get("mcp_tools", [])
            self.api_tools = data.get("api_tools", [])
            self.code_tools = data.get("code_tools", [])

        # 初始化三个独立的执行器（由不同开发者实现）
        self.mcp_executor = MCPExecutor()
        self.api_executor = APIExecutor()
        self.code_executor = CodeExecutor()

        # LangChain 工具列表
        self.langchain_tools = []

        # 构建工具
        self._build_langchain_tools()

    def _build_langchain_tools(self):
        """将配置转换为 LangChain Tools"""

        # 注册 MCP 工具
        for config in self.mcp_tools:
            self._register_tool("mcp", config, self.mcp_executor)

        # 注册 API 工具
        for config in self.api_tools:
            self._register_tool("api", config, self.api_executor)

        # 注册代码工具
        for config in self.code_tools:
            self._register_tool("code", config, self.code_executor)

    def _register_tool(self, tool_type: str, config: Dict, executor):
        """
        注册工具（统一接口）

        Args:
            tool_type: 工具类型 (mcp/api/code)
            config: 工具配置
            executor: 对应的执行器
        """
        def tool_func(**kwargs):
            """工具函数包装器"""
            return executor.execute(config, kwargs)

        lc_tool = StructuredTool.from_function(
            func=tool_func,
            name=config["name"],
            description=config["description"]
        )

        self.langchain_tools.append(lc_tool)

    def get_tools(self) -> List[StructuredTool]:
        """获取所有 LangChain 工具"""
        return self.langchain_tools

    def get_tool_by_name(self, name: str) -> StructuredTool:
        """根据名称获取工具"""
        for tool in self.langchain_tools:
            if tool.name == name:
                return tool
        return None

    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具的基本信息"""
        tools_info = []

        for config in self.mcp_tools:
            tools_info.append({
                "name": config["name"],
                "type": "mcp",
                "description": config["description"]
            })

        for config in self.api_tools:
            tools_info.append({
                "name": config["name"],
                "type": "api",
                "description": config["description"]
            })

        for config in self.code_tools:
            tools_info.append({
                "name": config["name"],
                "type": "code",
                "description": config["description"]
            })

        return tools_info

    def get_tools_description(self) -> str:
        """获取格式化的工具描述（用于 LLM Prompt）"""
        descriptions = []
        idx = 1

        # MCP 工具
        if self.mcp_tools:
            descriptions.append("\n=== MCP Services ===")
            for config in self.mcp_tools:
                desc = f"{idx}. {config['name']} (MCP)\n"
                desc += f"   {config['description']}\n"
                if "capabilities" in config:
                    desc += f"   Capabilities: {', '.join(config['capabilities'])}\n"
                descriptions.append(desc)
                idx += 1

        # API 工具
        if self.api_tools:
            descriptions.append("\n=== REST APIs ===")
            for config in self.api_tools:
                desc = f"{idx}. {config['name']} (API)\n"
                desc += f"   {config['description']}\n"
                if "params" in config:
                    required_params = [
                        k for k, v in config["params"].items()
                        if v.get("required", False)
                    ]
                    if required_params:
                        desc += f"   Required params: {', '.join(required_params)}\n"
                descriptions.append(desc)
                idx += 1

        # 代码工具
        if self.code_tools:
            descriptions.append("\n=== GitHub Code Tools ===")
            for config in self.code_tools:
                desc = f"{idx}. {config['name']} (Code)\n"
                desc += f"   {config['description']}\n"
                descriptions.append(desc)
                idx += 1

        return "\n".join(descriptions)


# 测试代码
if __name__ == "__main__":
    manager = UrbanToolManager()

    print("=" * 60)
    print("Urban Computing Tool Manager - Team Collaboration Version")
    print("=" * 60)

    print(manager.get_tools_description())

    print(f"\n{'=' * 60}")
    print(f"Total: {len(manager.get_tools())} tools loaded")
    print(f"  - MCP tools: {len(manager.mcp_tools)}")
    print(f"  - API tools: {len(manager.api_tools)}")
    print(f"  - Code tools: {len(manager.code_tools)}")
    print("=" * 60)
