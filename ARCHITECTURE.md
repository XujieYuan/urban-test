## Urban Computing Tool System - 架构文档 🏗️

### 设计理念：适合团队协作的模块化架构

---

## 📊 架构图

```
┌─────────────────────────────────────────────────────────┐
│                       User Query                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │       main.py              │  ← 你负责
        │  (主流程控制)              │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   tool_manager.py       │  ← 你负责
        │  (工具池管理)              │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │    urban_tools.json        │  ← 共同维护
        │  (工具配置)                │
        └────────────┬───────────────┘
                     │
         ┌───────────┴───────────┬───────────┐
         ▼                       ▼           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ mcp_executor.py  │  │ api_executor.py  │  │ code_executor.py │
│  (MCP 开发者)    │  │  (API 开发者)    │  │  (Code 开发者)   │
└────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  MCP Services    │  │   REST APIs      │  │  GitHub Repos    │
│ (mcp.so etc.)    │  │ (RapidAPI etc.)  │  │  (Converted)     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  tools/          │  │  tools/          │  │  tools/          │
│  mcp/      │  │  api/      │  │  code/     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🎯 核心设计原则

### 1. 接口统一，实现分离

**统一接口**：
```python
def execute(config: Dict, arguments: Dict) -> Dict[str, Any]:
    return {
        "success": bool,
        "result": Any,
        "error": str | None
    }
```

**好处**：
- ✅ 三个开发者互不干扰
- ✅ 易于测试和调试
- ✅ 可以独立迭代

### 2. 配置驱动

所有工具通过 `urban_tools.json` 配置，分三个独立数组：
```json
{
  "mcp": [...],    // MCP 开发者关注
  "api": [...],    // API 开发者关注
  "code": [...]    // Code 开发者关注
}
```

### 3. 缓存优先

每种工具类型都有独立的缓存目录：
```
tools/
├── mcp/     # MCP 调用结果
├── api/     # API 响应
└── code/    # 转换后的代码工具
```

### 4. 职责明确

| 角色 | 职责 | 文件 |
|------|------|------|
| **项目负责人** | 主框架、工具管理 | `main.py`, `tool_manager.py` |
| **MCP 开发者** | MCP 协议实现 | `executors/mcp_executor.py` |
| **API 开发者** | REST API 调用 | `executors/api_executor.py` |
| **Code 开发者** | 代码转换和调用 | `executors/code_executor.py` |

---

## 📁 目录结构

```
urban/
├── main.py                      # 主流程（你负责）
├── tool_manager.py              # 旧版（单体架构）
├── tool_manager.py           # 新版（模块化架构）⭐
├── urban_tools.json             # 工具配置
│
├── executors/                   # 执行器模块 ⭐
│   ├── __init__.py
│   ├── mcp_executor.py          # MCP 团队
│   ├── api_executor.py          # API 团队
│   └── code_executor.py         # Code 团队
│
├── tools/                       # 缓存目录 ⭐
│   ├── mcp/
│   ├── api/
│   └── code/
│
├── docs/                        # 文档
│   ├── TEAM_GUIDE.md           # 团队协作指南
│   ├── ARCHITECTURE.md         # 本文档
│   └── API.md                  # API 参考
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔄 数据流

### 完整流程

```
1. 用户查询
   ↓
2. main.py 调用 LLM 选择工具
   ↓
3. tool_manager 获取对应的 LangChain Tool
   ↓
4. 根据工具类型调用对应的 executor
   ├─ MCP → mcp_executor.execute()
   ├─ API → api_executor.execute()
   └─ Code → code_executor.execute()
   ↓
5. Executor 检查缓存
   ├─ 命中 → 返回缓存结果
   └─ 未命中 → 调用外部服务/转换代码
   ↓
6. 保存缓存（如果需要）
   ↓
7. 返回统一格式的结果
   ↓
8. main.py 用 LLM 生成最终答案
```

---

## 💡 为什么需要缓存？

### MCP 缓存

**场景**：高德地图地理编码
```
查询："北京市朝阳区"
- 第一次：调用 MCP server → 500ms
- 第二次：读缓存 → 5ms （提速 100x）
```

**策略**：
- 静态数据（地理编码）→ 永久缓存
- 动态数据（实时路况）→ 5-10 分钟缓存

### API 缓存

**场景**：天气 API（RapidAPI 收费）
```
查询："北京天气"
- 第一次：调用 API → 花钱 + 500ms
- 1小时内再次查询：读缓存 → 免费 + 5ms
```

**策略**：
- 天气数据：1 小时
- POI 数据：24 小时
- 交通数据：5 分钟

### Code 缓存

**场景**：GeoPandas 空间分析
```
第一次使用：
  克隆仓库 → 1 分钟
  转换为 MCP → 2 分钟
  总计：3 分钟

第二次使用：
  读取缓存 → 0.1 秒 （提速 1800x）
```

---

## 🛠️ 开发工作流

### 阶段 1：框架搭建（你已完成）

- [x] 项目结构
- [x] 统一接口定义
- [x] 工具管理器
- [x] 配置文件格式
- [x] 团队协作文档

### 阶段 2：并行开发（三个团队）

**MCP 团队**：
- [ ] 实现 MCP stdio 通信
- [ ] 测试高德地图工具
- [ ] 添加缓存机制

**API 团队**：
- [ ] 实现 HTTP 请求封装
- [ ] 测试天气 API
- [ ] 添加缓存和重试

**Code 团队**：
- [ ] 优化代码转换流程
- [ ] 测试 GeoPandas 工具
- [ ] 管理转换缓存

### 阶段 3：集成测试

- [ ] 端到端测试
- [ ] 性能优化
- [ ] 错误处理完善

---

## 🚦 关键决策

### Q1: 为什么分三个 executor 而不是一个？

**A**: 隔离复杂度
- MCP 协议复杂（stdio, SSE）
- API 需要处理限流、重试
- Code 需要管理转换流程

分离后每个团队只需关注自己的部分。

### Q2: 为什么需要 tool_manager？

**A**: 旧版 `tool_manager.py` 是单体架构，新版支持模块化执行器。
- 旧版：适合快速原型
- 新版：适合团队协作

### Q3: 缓存应该放在哪一层？

**A**: Executor 层
- 不在 `tool_manager`：不同工具类型缓存策略不同
- 在 `executor`：每个团队控制自己的缓存逻辑

### Q4: 如何保证接口一致性？

**A**:
1. 统一的返回格式（`success`, `result`, `error`）
2. 在 `executors/__init__.py` 中导出所有执行器
3. 通过测试验证

---

## 📊 性能优化建议

### 1. 并行调用（未来）

如果需要调用多个工具：
```python
# 当前：串行
result1 = tool1.invoke(...)
result2 = tool2.invoke(...)

# 优化：并行
import asyncio
results = await asyncio.gather(
    tool1.ainvoke(...),
    tool2.ainvoke(...)
)
```

### 2. 缓存预热

启动时预加载常用查询：
```python
# 在 main.py 启动时
preload_queries = [
    "北京市朝阳区",
    "上海市浦东新区",
    ...
]
```

### 3. 连接池

MCP 和 API 都可以使用连接池：
```python
# MCP executor
self.connection_pool = {}  # 复用 MCP 连接

# API executor
self.session = requests.Session()  # 复用 HTTP 连接
```

---

## 🧪 测试策略

### 单元测试

每个 executor 独立测试：
```bash
pytest tests/test_mcp_executor.py
pytest tests/test_api_executor.py
pytest tests/test_code_executor.py
```

### 集成测试

测试完整流程：
```bash
pytest tests/test_integration.py
```

### 性能测试

测试缓存效果：
```bash
python benchmarks/cache_performance.py
```

---

## 📝 下一步计划

### 短期（1-2 周）
- [ ] 三个团队完成各自 executor 的基本实现
- [ ] 集成测试通过
- [ ] 文档完善

### 中期（1 个月）
- [ ] 添加更多工具到配置文件
- [ ] 优化缓存策略
- [ ] 添加监控和日志

### 长期（2-3 个月）
- [ ] 支持异步调用
- [ ] 添加 Web UI
- [ ] 工具质量评分

---

## 🤝 团队协作最佳实践

1. **定期同步**：每周一次站会
2. **文档先行**：修改接口前先更新文档
3. **测试驱动**：先写测试再实现功能
4. **Code Review**：所有代码必须经过审查
5. **问题追踪**：使用 GitHub Issues

---

**架构设计完成！现在每个团队可以独立开发了。** 🎉
