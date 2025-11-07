# Urban Computing Tool System - Project Overview

## 📋 项目总结

这是一个**极简的 Urban Computing 工具系统**，专为单步查询任务设计。

### 核心特点
- ✅ **极简架构**：只有 3 个核心 Python 文件（~500 行代码）
- ✅ **配置驱动**：所有工具通过 JSON 配置，无需修改代码
- ✅ **三种工具类型**：MCP 服务、REST API、GitHub 代码
- ✅ **LangChain 集成**：统一的工具接口，易于扩展
- ✅ **智能选择**：LLM 自动选择最合适的工具

---

## 📁 项目文件说明

### 核心文件（必需）

| 文件 | 行数 | 作用 | 重要性 |
|------|------|------|--------|
| `main.py` | ~200 | 主流程：查询处理、工具选择、答案生成 | ⭐⭐⭐ |
| `tool_manager.py` | ~150 | 工具池管理：加载配置、转换为 LangChain Tools | ⭐⭐⭐ |
| `tool_executor.py` | ~250 | 工具执行：调用 MCP/API/Code | ⭐⭐⭐ |
| `urban_tools.json` | ~100 | 工具配置：定义所有可用工具 | ⭐⭐⭐ |

### 配置文件

| 文件 | 作用 |
|------|------|
| `.env.example` | 环境变量模板 |
| `requirements.txt` | Python 依赖 |

### 文档文件

| 文件 | 作用 |
|------|------|
| `README.md` | 完整使用文档 |
| `PROJECT_OVERVIEW.md` | 本文件 - 项目概览 |
| `test_tools.py` | 快速测试脚本 |

---

## 🔄 工作流程

```
1. 用户输入查询
   ↓
2. main.py 调用 LLM 选择工具
   ↓
3. tool_manager.py 获取对应的 LangChain Tool
   ↓
4. tool_executor.py 根据类型执行：
   - MCP: HTTP 请求外部服务
   - API: HTTP 请求 REST API
   - Code: 本地调用（先转 MCP）
   ↓
5. main.py 用 LLM 生成最终答案
   ↓
6. 输出结果
```

---

## 🎯 与父项目的区别

| 维度 | 父项目（AgenticRAG-TOOL-MCP） | Urban 子项目 |
|------|----------------------------|-------------|
| **目标** | 从 GitHub 搜索并转化仓库 | 使用预定义工具池 |
| **工具来源** | 动态搜索 | 静态配置 |
| **架构复杂度** | 中（LangGraph + RAG） | 极简（纯 Python） |
| **任务类型** | 单步 + 多步 | 单步优化 |
| **代码量** | ~2000 行 | ~500 行 |
| **学习曲线** | 中等 | 低 |

---

## 🚀 快速开始（3 步）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API keys
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 3. 运行
python main.py
```

---

## 🔧 如何添加新工具

### 示例：添加一个天气 API

编辑 `urban_tools.json`，添加：

```json
{
  "name": "get_weather",
  "type": "api",
  "description": "Get current weather for a city",
  "api_endpoint": "https://api.weatherapi.com/v1/current.json",
  "method": "GET",
  "headers": {
    "key": "${WEATHER_API_KEY}"
  },
  "parameters_schema": {
    "city": {
      "type": "string",
      "description": "City name"
    }
  }
}
```

然后在 `.env` 中添加：
```bash
WEATHER_API_KEY=your_api_key_here
```

完成！系统会自动识别新工具。

---

## 📊 技术栈

### 核心依赖
- **LangChain** (0.1.0+): LLM 调用和工具管理
- **requests** (2.31.0+): HTTP 请求
- **python-dotenv** (1.0.0+): 环境变量管理

### LLM 支持
- OpenAI (GPT-4, GPT-3.5)
- Aliyun DashScope
- 可轻松扩展到 Anthropic, DeepSeek 等

---

## 🎨 设计原则

1. **简单优于复杂**
   - 不使用 LangGraph（单步任务不需要）
   - 直接的函数调用，避免过度抽象

2. **配置优于代码**
   - 工具通过 JSON 定义
   - 环境变量管理敏感信息

3. **可扩展性**
   - 统一的工具接口
   - 易于添加新工具类型

4. **可维护性**
   - 清晰的文件结构
   - 完善的文档和注释

---

## 🔮 未来扩展方向

### 短期（保持简单）
- [ ] 添加更多 Urban Computing 工具
- [ ] 改进工具选择的 Prompt
- [ ] 添加结果缓存

### 中期（增强能力）
- [ ] 支持多步任务（引入 LangGraph）
- [ ] 添加工具使用统计
- [ ] Web UI 界面

### 长期（生态建设）
- [ ] 自动发现 mcp.so 上的工具
- [ ] 工具质量评分系统
- [ ] 社区工具共享平台

---

## 🤝 迁移到独立项目

当你准备将此项目迁移出父目录时：

### 需要处理的依赖

1. **MCP 转换功能**（`tool_executor.py` 中）
   ```python
   # 当前依赖父项目的 MCP.py
   from MCP import process_github_repos

   # 迁移后有两个选择：
   # 1. 复制 MCP-agent-github-repo-output 目录
   # 2. 将其作为 Git submodule 引入
   ```

2. **MCP_Memory 路径**
   - 当前：`urban/MCP_Memory/`
   - 迁移后：需要在新位置创建

### 迁移步骤

```bash
# 1. 复制整个 urban 目录
cp -r urban ~/my-urban-project

# 2. 决定如何处理 MCP 转换
# 选项 A: 复制 MCP-agent-github-repo-output
cp -r MCP-agent-github-repo-output ~/my-urban-project/

# 选项 B: 使用 Git submodule
cd ~/my-urban-project
git submodule add <MCP-agent-repo-url> MCP-agent-github-repo-output

# 3. 更新 tool_executor.py 中的路径

# 4. 测试
cd ~/my-urban-project
python test_tools.py
```

---

## 📚 学习路径

### 新手
1. 阅读 `README.md`
2. 运行 `test_tools.py`
3. 查看 `urban_tools.json` 了解工具配置
4. 修改示例查询并运行 `main.py`

### 进阶
1. 添加自己的工具到 `urban_tools.json`
2. 修改 `main.py` 中的 Prompt 优化工具选择
3. 在 `tool_executor.py` 中添加新的工具类型支持

### 高级
1. 集成 LangGraph 支持多步任务
2. 添加工具结果缓存机制
3. 构建 Web 界面

---

## 🐛 常见问题

### Q: 为什么不用 LangGraph？
A: 单步任务用简单的函数调用就够了。LangGraph 适合需要多步推理、动态路由的复杂场景。

### Q: 如何支持其他 LLM（如 Claude）？
A: 安装 `langchain-anthropic`，然后在代码中替换：
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
```

### Q: 外部 MCP 服务的 URL 格式是什么？
A: 取决于服务提供商。mcp.so 通常是 `https://mcp.so/servers/{server-id}/execute`。查看服务文档获取准确 URL。

### Q: GitHub 代码转 MCP 需要多久？
A: 首次转换需要 1-5 分钟（取决于仓库大小）。转换后结果会缓存在 `MCP_Memory/`。

---

## 📞 支持

遇到问题？
1. 查看 `README.md` 的 Troubleshooting 部分
2. 运行 `python test_tools.py` 诊断
3. 检查 `.env` 文件配置
4. 参考父项目的 Issues

---

## ✨ 致谢

本项目基于 AgenticRAG-TOOL-MCP 的设计理念，简化为适合 Urban Computing 单步任务的轻量级版本。

---

**Happy Urban Computing! 🏙️**
