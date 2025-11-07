# Urban Computing Tool System 🏙️

An intelligent tool selection and execution system for urban computing tasks, powered by LLM and supporting three types of tools: MCP services, APIs, and GitHub code repositories.

---

## 🎯 Features

- **Intelligent Tool Selection**: LLM automatically selects the most suitable tool based on user queries
- **Three Tool Types**:
  - 🔌 **MCP Services**: External MCP servers (e.g., mcp.so)
  - 🌐 **REST APIs**: Public APIs (e.g., RapidAPI)
  - 💻 **GitHub Code**: Automatically converts code repos to MCP tools
- **Simple Configuration**: JSON-based tool pool management
- **LangChain Integration**: Easy to extend with more LLM providers
- **Single-Step Tasks**: Optimized for straightforward queries

---

## 📂 Project Structure

```
urban/
├── main.py                   # Main entry point
├── tool_manager.py           # Tool pool manager
├── tool_executor.py          # Tool execution logic
├── urban_tools.json          # Tool configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── README.md                 # This file
└── MCP_Memory/               # Cache for converted GitHub repos
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd urban
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# Required
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Optional (if using API tools)
RAPIDAPI_KEY=your-rapidapi-key

# Optional (if using GitHub code tools)
GITHUB_TOKEN=ghp_your-token
```

### 3. Configure Your Tool Pool

Edit `urban_tools.json` to add or modify tools. Example structure:

```json
{
  "tools": [
    {
      "name": "sentiment_analysis",
      "type": "mcp",
      "description": "Analyze sentiment of text",
      "mcp_url": "https://mcp.so/servers/sentiment-analysis",
      "tool_name": "analyze_sentiment",
      "parameters_schema": {
        "text": {"type": "string", "description": "Text to analyze"}
      }
    },
    {
      "name": "get_traffic_data",
      "type": "api",
      "description": "Get traffic data",
      "api_endpoint": "https://traffic-data.p.rapidapi.com/v1/data",
      "method": "GET",
      "headers": {
        "X-RapidAPI-Key": "${RAPIDAPI_KEY}"
      }
    },
    {
      "name": "spatial_analysis",
      "type": "code",
      "description": "Run spatial analysis",
      "github_url": "https://github.com/geopandas/geopandas",
      "needs_conversion": true
    }
  ]
}
```

### 4. Run the System

```bash
python main.py
```

---

## 💡 How It Works

### Workflow

```
User Query
    ↓
1. LLM selects appropriate tool from pool
    ↓
2. Execute tool based on type:
   - MCP: Call external MCP service (HTTP)
   - API: Call REST API (HTTP)
   - Code: Convert to MCP (if needed) → Local call
    ↓
3. LLM generates final answer from tool result
    ↓
Final Answer
```

### Example Query

```python
query = "Analyze the sentiment of: 'Urban planning is fascinating!'"

# System automatically:
# 1. Selects: sentiment_analysis (MCP tool)
# 2. Executes: Calls https://mcp.so/servers/sentiment-analysis
# 3. Generates: "The text expresses a positive sentiment..."
```

---

## 🛠️ Adding New Tools

### Add an MCP Tool

```json
{
  "name": "your_mcp_tool",
  "type": "mcp",
  "description": "What this tool does",
  "mcp_url": "https://your-mcp-server.com/api",
  "tool_name": "tool_function_name",
  "parameters_schema": {
    "param1": {"type": "string", "description": "Description"}
  }
}
```

### Add an API Tool

```json
{
  "name": "your_api_tool",
  "type": "api",
  "description": "What this API does",
  "api_endpoint": "https://api.example.com/endpoint",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer ${YOUR_API_KEY}"
  },
  "parameters_schema": {
    "param1": {"type": "string", "description": "Description"}
  }
}
```

### Add a Code Tool

```json
{
  "name": "your_code_tool",
  "type": "code",
  "description": "What this code does",
  "github_url": "https://github.com/user/repo",
  "needs_conversion": true,
  "method_name": "function_to_call",
  "parameters_schema": {
    "param1": {"type": "string", "description": "Description"}
  }
}
```

---

## 🔧 Advanced Usage

### Programmatic Usage

```python
from tool_manager import UrbanToolManager

# Initialize
manager = UrbanToolManager("./urban_tools.json")

# Get all tools
tools = manager.get_tools()

# Get specific tool
tool = manager.get_tool_by_name("sentiment_analysis")

# Execute tool
result = tool.invoke({"text": "Urban planning rocks!"})
print(result)
```

### Custom Query Processing

```python
from main import process_query, load_env
from tool_manager import UrbanToolManager

load_env()
manager = UrbanToolManager("./urban_tools.json")

result = process_query("Your custom query here", manager)
print(result['final_answer'])
```

---

## 📊 Tool Types Comparison

| Feature | MCP | API | Code |
|---------|-----|-----|------|
| **Deployment** | External server | External server | Local (after conversion) |
| **Speed** | Fast | Fast | Medium (first time slower) |
| **Setup** | None | API key | GitHub token |
| **Offline** | ❌ | ❌ | ✅ (after conversion) |

---

## 🤝 Integration with Parent Project

This urban computing system can be used alongside the main AgenticRAG-TOOL-MCP project:

```python
# In parent project
import sys
sys.path.insert(0, './urban')

from tool_manager import UrbanToolManager

# Use urban tools
urban_tools = UrbanToolManager('./urban/urban_tools.json')
```

---

## 📝 Example Queries

- "Analyze the sentiment of: 'Beijing is an amazing city!'"
- "Get traffic data for Shanghai on 2024-01-15"
- "Get POI data for restaurants in New York within 5km radius"
- "Run spatial analysis on city boundary data"

---

## 🐛 Troubleshooting

### Tool Execution Failed

1. Check if external services (MCP/API) are accessible
2. Verify API keys in `.env` file
3. Check network connection

### Code Tool Conversion Failed

1. Verify `GITHUB_TOKEN` is set
2. Check if parent project's `MCP.py` is accessible
3. Ensure sufficient disk space for cloning repos

### LLM Not Selecting Correct Tool

1. Improve tool descriptions in `urban_tools.json`
2. Add more details to `parameters_schema`
3. Use a more capable model (e.g., gpt-4o instead of gpt-3.5-turbo)

---

## 🔮 Future Enhancements

- [ ] Multi-step task support (integrate LangGraph)
- [ ] Tool result caching
- [ ] Streaming responses
- [ ] Web UI interface
- [ ] Tool usage analytics
- [ ] Auto-discovery of tools from mcp.so

---

## 📄 License

This project inherits the license from the parent AgenticRAG-TOOL-MCP project.

---

## 🤝 Contributing

When you migrate this project out of the parent directory, feel free to:
1. Add more urban computing tools to the pool
2. Improve LLM prompts for better tool selection
3. Add support for more LLM providers
4. Implement caching mechanisms

---

## 📧 Contact

For questions or issues, please refer to the parent project's issue tracker.
