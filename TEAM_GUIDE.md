# Urban Computing Tool System - 团队协作指南 👥

## 📋 项目架构

### 模块分工

```
项目负责人（你）：
├── main.py                    # 主流程框架
├── tool_manager.py         # 工具管理器
└── urban_tools.json           # 工具配置（共同维护）

MCP 开发者：
└── executors/mcp_executor.py  # MCP 服务调用实现

API 开发者：
└── executors/api_executor.py  # REST API 调用实现

Code 开发者：
└── executors/code_executor.py # GitHub 代码工具实现
```

---

## 🎯 统一接口规范

### 所有执行器必须实现的接口

```python
class XxxExecutor:
    def execute(self, config: Dict, arguments: Dict) -> Dict[str, Any]:
        """
        执行工具调用

        Args:
            config: 工具配置（来自 urban_tools.json）
            arguments: 用户传入的参数

        Returns:
            {
                "success": bool,      # 是否成功
                "result": Any,        # 结果数据
                "error": str | None   # 错误信息（成功时为 None）
            }
        """
        pass
```

### 为什么这样设计？

✅ **接口统一**：三个开发者只需实现 `execute()` 方法
✅ **互不干扰**：各自负责自己的模块，不会冲突
✅ **易于测试**：每个执行器可以独立测试
✅ **易于扩展**：未来可以轻松添加新的工具类型

---

## 👤 MCP 开发者职责

### 文件：`executors/mcp_executor.py`

### 核心任务

1. **实现 MCP 协议通信**
   - stdio 模式（标准输入输出）
   - SSE 模式（Server-Sent Events）

2. **管理 MCP 服务生命周期**
   - 启动 MCP server（如 `npx -y @amap/amap-maps-mcp-server`）
   - 维护连接池
   - 处理服务重启

3. **实现调用缓存**
   - 缓存常用查询结果
   - 避免重复调用外部服务

### 配置格式示例

```json
{
  "name": "amap_maps",
  "command": "npx",
  "args": ["-y", "@amap/amap-maps-mcp-server"],
  "env": {
    "AMAP_MAPS_API_KEY": "${AMAP_API_KEY}"
  }
}
```

### 关键问题

- **Q: MCP 服务如何启动？**
  A: 使用 `subprocess.Popen` 启动，通过 stdin/stdout 通信

- **Q: 需要缓存吗？**
  A: 建议缓存，特别是地理编码等静态数据

- **Q: 如何处理服务崩溃？**
  A: 实现自动重启机制

### 测试方法

```bash
cd urban
python executors/mcp_executor.py
```

---

## 🌐 API 开发者职责

### 文件：`executors/api_executor.py`

### 核心任务

1. **实现 HTTP 请求**
   - 支持 GET、POST、PUT、DELETE
   - 处理请求头和认证

2. **响应缓存机制**
   - 避免重复调用付费 API
   - 设置合理的 TTL（Time To Live）

3. **速率限制处理**
   - RapidAPI 等有调用限制
   - 实现重试和退避策略

4. **错误处理**
   - 网络超时
   - API 返回错误
   - 熔断机制

### 配置格式示例

```json
{
  "name": "weather_forecast",
  "endpoint": "https://weather-api167.p.rapidapi.com/api/weather/forecast",
  "method": "GET",
  "headers": {
    "x-rapidapi-key": "${RAPIDAPI_KEY}",
    "x-rapidapi-host": "weather-api167.p.rapidapi.com"
  },
  "params": {
    "place": {"type": "string", "required": true},
    "units": {"type": "string", "default": "metric"}
  }
}
```

### 关键问题

- **Q: 缓存有效期多久？**
  A: 天气数据：1小时，POI数据：24小时，交通数据：5分钟

- **Q: API key 如何管理？**
  A: 从环境变量读取，格式 `${VAR_NAME}`

- **Q: 如何处理分页？**
  A: 根据 API 文档自动处理，或在配置中标明

### 测试方法

```bash
cd urban
export RAPIDAPI_KEY=your_key
python executors/api_executor.py
```

---

## 💻 Code 开发者职责

### 文件：`executors/code_executor.py`

### 核心任务

1. **管理代码转换流程**
   - 调用 `MCP-agent-github-repo-output` 转换代码
   - 处理转换失败情况

2. **缓存管理**
   - 避免重复转换同一仓库
   - 支持版本更新（git pull）

3. **本地 MCP 调用**
   - 动态加载转换后的模块
   - 处理不同的调用方式（Adapter / mcp_service）

4. **大型仓库优化**
   - 只克隆必要的文件
   - 支持浅克隆（shallow clone）

### 配置格式示例

```json
{
  "name": "geopandas_spatial",
  "github_url": "https://github.com/geopandas/geopandas",
  "entry_function": "spatial_operation",
  "params": {
    "operation": {"type": "string", "required": true},
    "geometry": {"type": "object", "required": true}
  }
}
```

### 关键问题

- **Q: 转换需要多久？**
  A: 小仓库 1-2 分钟，大仓库 5-10 分钟

- **Q: 如何避免重复转换？**
  A: 检查 `tools/code/{repo_name}/` 是否存在

- **Q: 转换失败怎么办？**
  A: 返回错误信息，提供手动重试选项

### 测试方法

```bash
cd urban
python executors/code_executor.py
```

---

## 🔄 协作流程

### 1. 添加新工具

**步骤 1：编辑配置文件**（任何人）

```bash
vim urban_tools.json
# 在对应的数组中添加新工具配置
```

**步骤 2：实现执行逻辑**（对应开发者）

```bash
# MCP 开发者
vim executors/mcp_executor.py

# API 开发者
vim executors/api_executor.py

# Code 开发者
vim executors/code_executor.py
```

**步骤 3：测试**

```bash
python tool_manager.py  # 检查工具是否正确加载
python main.py             # 端到端测试
```

### 2. Git 工作流

```bash
# 创建功能分支
git checkout -b feature/add-traffic-api

# 开发并提交
git add executors/api_executor.py urban_tools.json
git commit -m "Add traffic data API support"

# 推送并创建 PR
git push origin feature/add-traffic-api
```

### 3. 代码审查要点

- ✅ 是否遵循统一接口规范？
- ✅ 是否正确处理错误？
- ✅ 是否添加了缓存机制？
- ✅ 是否更新了配置文件？
- ✅ 是否通过了测试？

---

## 🛠️ 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd urban
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入必要的 API keys
```

### 4. 测试你的模块

```bash
# MCP 开发者
python executors/mcp_executor.py

# API 开发者
python executors/api_executor.py

# Code 开发者
python executors/code_executor.py
```

---

## 📊 缓存策略建议

### MCP 缓存

- **位置**：`tools/mcp/`
- **策略**：按查询内容缓存
- **有效期**：静态数据永久，动态数据根据业务定

### API 缓存

- **位置**：`tools/api/`
- **策略**：按 (endpoint + params) 哈希缓存
- **有效期**：
  - 天气：1 小时
  - POI：24 小时
  - 交通：5 分钟

### Code 缓存

- **位置**：`tools/code/`
- **策略**：按仓库名缓存转换结果
- **有效期**：手动更新（或实现 git pull 检测）

---

## 🐛 调试技巧

### 1. 单独测试执行器

```python
# 测试 API executor
from executors.api_executor import APIExecutor

executor = APIExecutor()
config = {...}  # 你的配置
arguments = {...}  # 测试参数

result = executor.execute(config, arguments)
print(result)
```

### 2. 查看缓存

```bash
# 查看 API 缓存
ls -lh tools/api/

# 查看缓存内容
cat tools/api/<cache_key>.json
```

### 3. 清除缓存

```bash
# 清除所有缓存
rm -rf tools/*/

# 只清除特定类型
rm -rf tools/api/*
```

---

## 📝 TODO 列表

### MCP 开发者
- [ ] 实现 MCP stdio 通信
- [ ] 实现 MCP SSE 通信
- [ ] 添加连接池管理
- [ ] 实现缓存机制
- [ ] 处理服务自动重启

### API 开发者
- [ ] 实现智能重试机制
- [ ] 实现速率限制检测
- [ ] 优化缓存策略（TTL）
- [ ] 处理 API 分页
- [ ] 添加熔断机制

### Code 开发者
- [ ] 优化转换流程
- [ ] 实现增量更新
- [ ] 支持版本管理
- [ ] 处理大型仓库
- [ ] 添加转换失败回退

---

## 🤝 沟通建议

### 定期同步会议

- **频率**：每周一次
- **内容**：
  - 进度更新
  - 遇到的问题
  - 接口变更讨论

### 技术文档

- **位置**：`docs/` 目录
- **内容**：
  - 各模块的设计文档
  - API 接口说明
  - 常见问题解答

### Issue 跟踪

- 使用 GitHub Issues 跟踪任务
- 标签：`mcp`, `api`, `code`, `bug`, `enhancement`

---

## 🎓 学习资源

### MCP 协议
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/python-mcp)

### API 开发
- [Requests 文档](https://requests.readthedocs.io/)
- [RapidAPI 指南](https://rapidapi.com/guides)

### Code 工具
- [GitPython](https://gitpython.readthedocs.io/)
- [Subprocess 文档](https://docs.python.org/3/library/subprocess.html)

---

**祝开发顺利！有问题随时在团队群沟通。** 🚀
