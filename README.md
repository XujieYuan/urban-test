# Urban Computing Tool System 🏙️

An intelligent LLM-powered system that automatically selects and executes tools to answer user queries.

## ✨ Features

- **Intelligent Tool Selection**: LLM automatically chooses the best tool for each query
- **Multiple Tool Types**: REST APIs, MCP services, GitHub code repositories
- **Response Caching**: Avoid redundant API calls with automatic caching
- **Easy Configuration**: JSON-based tool pool management

---

## 📂 Project Structure

```
urban-test/
├── main.py                 # Main entry point
├── tool_manager.py         # Tool pool manager
├── urban_tools.json        # Tool configuration
├── executors/              # Tool execution engines
│   ├── api_executor.py     # REST API executor
│   ├── mcp_executor.py     # MCP service executor (coming soon)
│   └── code_executor.py    # Code executor (coming soon)
├── Cache/                  # API response cache
├── Test/                   # Test scripts and results
├── requirements.txt        # Python dependencies
└── .env                    # API keys and credentials
```

---

## 🚀 Quick Start for Users

### 1. Setup Environment

```bash
# Create conda environment
conda create -n urban-test python=3.10
conda activate urban-test

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
OPENAI_API_KEY=sk-your-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. Run the System

```bash
python3 main.py
```

Results will be saved to `Test/results_{timestamp}.json`

---

## 📊 Available Tools

### 1. GitHub User Info
```
Query: "Get GitHub user information for Linus Torvalds"
→ Returns: User profile, repos, followers, etc.
```

### 2. Weather Forecast (RapidAPI)
```
Query: "What is the weather in London?"
→ Returns: 3-hour interval forecasts with temperature, humidity, wind
```

### 3. Weather Forecast (Open-Meteo - Free)
```
Query: "Weather for Beijing (39.9042°N, 116.4074°E)"
→ Returns: 7-day daily forecast
```

---

## 🔧 For Developers

### Adding a New API Tool

Edit `urban_tools.json`:

```json
{
  "api_tools": [
    {
      "name": "my_api_tool",
      "description": "What this tool does",
      "endpoint": "https://api.example.com/endpoint",
      "method": "GET",
      "headers": {
        "Authorization": "Bearer ${MY_API_KEY}"
      },
      "params": {
        "param1": {
          "type": "string",
          "required": true,
          "description": "Parameter description"
        }
      }
    }
  ]
}
```

### Updating Parameter Extraction Rules

Edit `main.py` in the system prompt:

```python
# Add your tool's parameter extraction rules
IMPORTANT PARAMETER EXTRACTION RULES:
- For my_tool: use "param" in format "value"
```

### Testing Your Tool

```bash
python3 Test/api/test_rapidapi_weather.py
```

---

## 🧪 Testing

### Run Full End-to-End Test
```bash
python3 main.py
```

### Run Specific API Test
```bash
python3 Test/api/test_rapidapi_weather.py
```

### Check Results
```bash
# View latest results
ls -ltr Test/results_*.json | tail -1

# View cached API responses
ls -lh Cache/api/
```

---

## 🔌 How It Works

```
User Query
    ↓
LLM selects best tool
    ↓
Tool executes (API/MCP/Code)
    ↓
Response cached
    ↓
LLM generates answer
    ↓
Results saved with timestamp
```