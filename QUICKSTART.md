# Urban Computing Tool System - 快速开始 🚀

## ⚡ 30 秒快速测试

```bash
# 1. 测试工具加载
python tool_manager.py

# 2. 查看项目结构
ls -la
```

---

## 📋 完整设置步骤

### 1. 环境配置（5 分钟）

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 填入你的 API keys
```

**必需的环境变量**：
```bash
OPENAI_API_KEY=sk-xxx       # OpenAI API key
OPENAI_BASE_URL=xxx         # API endpoint
```

**可选的环境变量**（根据使用的工具类型）：
```bash
AMAP_API_KEY=xxx           # 高德地图（如果用 MCP）
RAPIDAPI_KEY=xxx           # RapidAPI（如果用 API 工具）
GITHUB_TOKEN=ghp_xxx       # GitHub（如果用代码工具）
```

### 2. 验证安装

```bash
python tool_manager.py
```

**预期输出**：
```
============================================================
Urban Computing Tool Manager - Team Collaboration Version
============================================================

=== MCP Services ===
1. amap_maps (MCP)
   ...

=== REST APIs ===
2. weather_forecast (API)
3. traffic_data (API)
   ...

=== GitHub Code Tools ===
4. geopandas_spatial (Code)
   ...

============================================================
Total: 4 tools loaded
  - MCP tools: 1
  - API tools: 2
  - Code tools: 1
============================================================
```

---

## 👥 团队开发分工

### 你（项目负责人）✅
- [x] 主框架搭建完成
- [x] 工具管理器完成
- [x] 文档编写完成

### MCP 开发者
**文件**: `executors/mcp_executor.py`

**任务**:
1. 实现 MCP stdio 通信
2. 测试高德地图工具
3. 添加缓存机制

**开始方式**:
```bash
vim executors/mcp_executor.py
# 搜索 "TODO" 查看待实现功能
```

### API 开发者
**文件**: `executors/api_executor.py`

**任务**:
1. 实现智能重试机制
2. 测试天气 API
3. 优化缓存策略

**开始方式**:
```bash
vim executors/api_executor.py
# 搜索 "TODO" 查看待实现功能
```

### Code 开发者
**文件**: `executors/code_executor.py`

**任务**:
1. 优化代码转换流程
2. 测试 GeoPandas 工具
3. 管理转换缓存

**开始方式**:
```bash
vim executors/code_executor.py
# 搜索 "TODO" 查看待实现功能
```

---

## 📁 项目结构一览

```
urban/
├── main.py                  # 主程序（你负责）✅
├── tool_manager.py          # 工具管理器（你负责）✅
├── urban_tools.json         # 工具配置（共同维护）
│
├── executors/               # 执行器模块（三个团队）
│   ├── mcp_executor.py      # MCP 团队 ← TODO
│   ├── api_executor.py      # API 团队 ← TODO
│   └── code_executor.py     # Code 团队 ← TODO
│
├── tools/                   # 工具存储目录
│   ├── mcp/                 # MCP 工具缓存
│   ├── api/                 # API 响应缓存
│   └── code/                # 代码工具缓存
│
└── 文档/
    ├── QUICKSTART.md       # 本文档 ⭐
    ├── README.md           # 完整用户指南
    ├── TEAM_GUIDE.md       # 团队协作指南 ⭐⭐⭐
    ├── ARCHITECTURE.md     # 架构设计文档
    └── ...
```

---

## 🎯 核心概念（5 分钟理解）

### 1. 三种工具类型

| 类型 | 来源 | 存储位置 | 负责团队 |
|------|------|---------|---------|
| **MCP** | mcp.so 等外部服务 | `tools/mcp/` | MCP 开发者 |
| **API** | RapidAPI 等 REST API | `tools/api/` | API 开发者 |
| **Code** | GitHub 代码仓库 | `tools/code/` | Code 开发者 |

### 2. 统一接口

所有执行器都实现同一个接口：
```python
def execute(config: Dict, arguments: Dict) -> Dict[str, Any]:
    return {
        "success": bool,
        "result": Any,
        "error": str | None
    }
```

### 3. 工具流程

```
用户查询
    ↓
LLM 选择工具
    ↓
tool_manager 获取 Tool
    ↓
根据类型调用对应 executor
    ↓
executor 执行（可能使用缓存）
    ↓
返回结果
    ↓
LLM 生成答案
```

---

## 🛠️ 开发工作流

### 第一天：环境搭建

```bash
# 1. 克隆项目（如果从 Git）
git clone <repo-url>
cd urban

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp .env.example .env
# 编辑 .env

# 4. 验证
python tool_manager.py
```

### 第二天：阅读文档

1. **必读** ⭐⭐⭐: [TEAM_GUIDE.md](TEAM_GUIDE.md)
   - 你的职责
   - 接口规范
   - TODO 列表

2. **推荐**: [ARCHITECTURE.md](ARCHITECTURE.md)
   - 架构设计
   - 为什么这样设计

3. **参考**: [README.md](README.md)
   - 用户使用指南

### 第三天起：开始开发

```bash
# 1. 创建分支
git checkout -b feature/implement-mcp-executor

# 2. 实现功能
vim executors/mcp_executor.py

# 3. 测试
python executors/mcp_executor.py

# 4. 提交
git add executors/mcp_executor.py
git commit -m "Implement MCP stdio communication"
git push origin feature/implement-mcp-executor
```

---

## 🧪 测试指南

### 单元测试（独立测试你的模块）

```bash
# MCP 开发者
python executors/mcp_executor.py

# API 开发者
python executors/api_executor.py

# Code 开发者
python executors/code_executor.py
```

### 集成测试（测试整体流程）

```bash
python main.py
```

---

## 📚 常用命令

```bash
# 查看工具配置
cat urban_tools.json

# 查看缓存
ls -la tools/mcp/
ls -la tools/api/
ls -la tools/code/

# 清除缓存
rm -rf tools/*/

# 查看日志（如果有）
tail -f logs/*.log
```

---

## 🐛 常见问题

### Q: 工具加载失败？
```bash
# 检查配置文件
python -m json.tool urban_tools.json

# 检查执行器导入
python -c "from executors import MCPExecutor, APIExecutor, CodeExecutor"
```

### Q: 缓存在哪里？
```bash
# 三个目录
tools/mcp/    # MCP 缓存
tools/api/    # API 缓存
tools/code/   # 代码工具缓存
```

### Q: 如何添加新工具？
1. 编辑 `urban_tools.json`
2. 在对应的数组中添加配置
3. 运行 `python tool_manager.py` 验证

---

## 📞 获取帮助

- **团队协作问题**: 查看 [TEAM_GUIDE.md](TEAM_GUIDE.md)
- **架构设计问题**: 查看 [ARCHITECTURE.md](ARCHITECTURE.md)
- **使用问题**: 查看 [README.md](README.md)
- **变更记录**: 查看 [CHANGELOG.md](CHANGELOG.md)

---

## 🎉 下一步

### 立即行动
1. ✅ 运行 `python tool_manager.py` 验证环境
2. 📖 阅读 [TEAM_GUIDE.md](TEAM_GUIDE.md) 了解你的职责
3. 💻 开始实现你负责的 executor

### 本周目标
- [ ] 完成环境搭建
- [ ] 阅读完团队协作指南
- [ ] 实现基本功能
- [ ] 通过单元测试

---

**准备好了吗？开始开发吧！** 🚀

如有问题，随时查阅文档或在团队群沟通。
