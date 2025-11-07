"""
处理用户查询，选择合适工具，执行并生成答案
"""

import os
import json
from pathlib import Path
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from tool_manager import UrbanToolManager


def load_env():
    """加载环境变量"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment variables loaded from .env")
        except ImportError:
            print("⚠️  python-dotenv not installed, using system environment variables")
    else:
        print("ℹ️  No .env file found, using system environment variables")


def simple_tool_selection(query: str, tool_manager: UrbanToolManager) -> dict:
    """
    简单的工具选择（单步任务）
    使用 LLM 从工具池中选择最合适的工具

    Args:
        query: 用户查询
        tool_manager: 工具管理器

    Returns:
        选择结果 {"tool_name": "...", "reasoning": "...", "parameters": {...}}
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    # 获取工具描述
    tools_desc = tool_manager.get_tools_description()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an urban computing expert.
Given a user query, select the most suitable tool from the available tools.

Available Tools:
{tools}

Analyze the query and select the best tool to answer it.

IMPORTANT PARAMETER EXTRACTION RULES:
- For GitHub usernames: convert to lowercase, remove spaces (e.g., "Linus Torvalds" -> "torvalds")
- For weather_forecast (RapidAPI): Use "place" parameter with format "City,CountryCode" (e.g., "London,GB", "Beijing,CN", "Tokyo,JP")
- For weather_forecast_free (Open-Meteo): Use "latitude" and "longitude" parameters with decimal coordinates
- For coordinates queries: use the provided latitude/longitude values if available, otherwise use weather_forecast_free with location name
- Extract parameter values in the exact format expected by the tool

Respond ONLY with valid JSON in this exact format:
{{
  "tool_name": "exact_tool_name_from_list",
  "reasoning": "brief explanation of why this tool is suitable",
  "parameters": {{"param1": "value1", "param2": "value2"}}
}}

Do not include any markdown formatting or code blocks, just the raw JSON."""),
        ("user", "{query}")
    ])

    chain = prompt | llm
    response = chain.invoke({"query": query, "tools": tools_desc})

    # 解析 JSON
    try:
        # 清理可能的 markdown 代码块标记
        content = response.content.strip()
        if content.startswith("```"):
            # 移除 ```json 和 ```
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:].strip()

        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse LLM response as JSON: {e}")
        print(f"Raw response: {response.content}")
        raise


def generate_final_answer(query: str, tool_name: str, tool_result: dict) -> str:
    """
    用 LLM 生成最终答案

    Args:
        query: 用户查询
        tool_name: 使用的工具名称
        tool_result: 工具执行结果

    Returns:
        最终答案文本
    """
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an urban computing expert.
Generate a clear, comprehensive answer based on the tool execution result.

If the tool execution failed (success=False), explain the error to the user in a friendly way.
If the tool succeeded, interpret and present the results in a user-friendly format."""),
        ("user", """User Query: {query}

Tool Used: {tool_name}
Tool Result: {result}

Please provide a comprehensive answer to the user's query based on this result.""")
    ])

    chain = answer_prompt | llm
    final_answer = chain.invoke({
        "query": query,
        "tool_name": tool_name,
        "result": json.dumps(tool_result, indent=2)
    })

    return final_answer.content


def process_query(query: str, tool_manager: UrbanToolManager) -> dict:
    """
    处理单步查询的主流程

    Args:
        query: 用户查询
        tool_manager: 工具管理器

    Returns:
        处理结果字典
    """
    print(f"\n{'='*60}")
    print(f"🔍 Query: {query}")
    print(f"{'='*60}\n")

    # 1. 选择工具
    print("🤔 Selecting appropriate tool...")
    selection = simple_tool_selection(query, tool_manager)

    print(f"✅ Selected: {selection['tool_name']}")
    print(f"💡 Reasoning: {selection['reasoning']}")
    print(f"📋 Parameters: {json.dumps(selection['parameters'], indent=2)}")

    # 2. 执行工具
    tool = tool_manager.get_tool_by_name(selection['tool_name'])
    if not tool:
        error_msg = f"Tool '{selection['tool_name']}' not found in tool pool"
        print(f"❌ Error: {error_msg}")
        return {
            "query": query,
            "tool_used": selection['tool_name'],
            "tool_result": {"success": False, "error": error_msg},
            "final_answer": f"Error: {error_msg}"
        }

    print(f"\n⚙️  Executing tool '{selection['tool_name']}'...")
    tool_result = tool.invoke(selection['parameters'])

    if tool_result.get("success"):
        print("✅ Tool execution succeeded")
    else:
        print(f"❌ Tool execution failed: {tool_result.get('error')}")

    # 3. 生成最终答案
    print("\n🤖 Generating final answer...")
    final_answer = generate_final_answer(query, selection['tool_name'], tool_result)

    return {
        "query": query,
        "tool_used": selection['tool_name'],
        "tool_result": tool_result,
        "final_answer": final_answer
    }


def main():
    """主函数"""
    # 加载环境变量
    load_env()

    # 验证必要的环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not set")
        print("Please set it in .env file or environment variables")
        return

    # 初始化工具管理器
    try:
        tool_manager = UrbanToolManager("./urban_tools.json")
        print(f"\n📦 Loaded {len(tool_manager.get_tools())} tools from pool\n")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return

    # 示例查询（使用实际可用的 API 工具）
    queries = [
        "Get GitHub user information for Linus Torvalds",
        "What is the weather forecast for Beijing? (coordinates: 39.9042°N, 116.4074°E)",
    ]

    # 处理查询
    results = []
    for query in queries:
        try:
            result = process_query(query, tool_manager)
            results.append(result)

            # 打印最终答案
            print(f"\n📝 Final Answer:")
            print(f"{result['final_answer']}")
            print(f"\n{'='*60}\n")

        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            import traceback
            traceback.print_exc()

    # 保存结果到 Test 文件夹，带时间戳
    test_dir = Path(__file__).parent / "Test"
    test_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = test_dir / f"results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Results saved to {output_file}")


if __name__ == "__main__":
    main()
