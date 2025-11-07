"""
RapidAPI 天气 API 测试脚本
用于测试 RapidAPI Weather API 的集成和功能
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from tool_manager import UrbanToolManager
from executors import APIExecutor
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()


def test_rapidapi_direct():
    """直接测试 RapidAPI 天气 API"""
    print("="*60)
    print("Test 1: Direct RapidAPI Weather API Call")
    print("="*60)

    import requests

    url = "https://weather-api167.p.rapidapi.com/api/weather/forecast"

    querystring = {
        "place": "London,GB",
        "cnt": "5",
        "units": "metric",
        "type": "three_hour",
        "mode": "json",
        "lang": "en"
    }

    headers = {
        "x-rapidapi-key": "93b538cb11msh05c0ef72610bd44p1f13ddjsn9155b4fae6ca",
        "x-rapidapi-host": "weather-api167.p.rapidapi.com",
        "Accept": "application/json"
    }

    print(f"\n📡 URL: {url}")
    print(f"📍 Location: {querystring['place']}")
    print(f"📋 Parameters: {querystring}")

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        print(f"\n✓ Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API Call Successful!")
            print(f"\n📊 Response Summary:")
            print(f"  Status Code: {data.get('cod')}")
            print(f"  Number of forecasts: {data.get('cnt')}")

            if 'list' in data and len(data['list']) > 0:
                first = data['list'][0]
                print(f"\n📍 First Forecast:")
                print(f"  Summary: {first.get('summery', 'N/A')[:100]}")
                if 'main' in first:
                    main = first['main']
                    print(f"  Temperature: {main.get('temprature')} {main.get('temprature_unit')}")
                    print(f"  Humidity: {main.get('humidity')}%")

            return True, data
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False, None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return False, None


def test_rapidapi_via_executor():
    """通过 APIExecutor 测试 RapidAPI 天气工具"""
    print("\n" + "="*60)
    print("Test 2: RapidAPI Weather via APIExecutor")
    print("="*60)

    manager = UrbanToolManager("./urban_tools.json")
    executor = APIExecutor()

    # 找到 weather_forecast 工具
    weather_tool = None
    for tool in manager.api_tools:
        if tool['name'] == 'weather_forecast':
            weather_tool = tool
            break

    if not weather_tool:
        print("❌ weather_forecast tool not found")
        return False

    print(f"\n✓ Found weather_forecast tool")
    print(f"  Description: {weather_tool['description']}")

    # 测试多个城市
    test_locations = [
        ("London,GB", "英国伦敦"),
        ("Tokyo,JP", "日本东京"),
        ("Beijing,CN", "中国北京"),
        ("Paris,FR", "法国巴黎"),
    ]

    results = []

    for place, description in test_locations:
        print(f"\n⚙️  Testing {description} ({place})...")

        arguments = {
            "place": place,
            "cnt": "3",
            "units": "metric",
            "type": "three_hour",
            "lang": "en"
        }

        result = executor.execute(weather_tool, arguments)

        if result['success']:
            print(f"  ✅ Success")
            data = result['result']
            print(f"    - Forecasts: {data.get('cnt')}")
            if 'list' in data and len(data['list']) > 0:
                first = data['list'][0]
                print(f"    - Summary: {first.get('summery', 'N/A')[:60]}")
            results.append({
                "location": place,
                "success": True,
                "cnt": data.get('cnt')
            })
        else:
            print(f"  ❌ Failed: {result['error']}")
            results.append({
                "location": place,
                "success": False,
                "error": result['error']
            })

    return True, results


def test_llm_tool_selection():
    """测试 LLM 工具选择"""
    print("\n" + "="*60)
    print("Test 3: LLM-based Tool Selection")
    print("="*60)

    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )

    manager = UrbanToolManager("./urban_tools.json")
    executor = APIExecutor()

    # 获取工具描述
    tool_descriptions = []
    for tool in manager.langchain_tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}")

    tools_text = "\n".join(tool_descriptions)

    test_queries = [
        "What is the weather in London?",
        "Get me the weather forecast for Tokyo",
        "Weather in New York?",
        "Tell me about Beijing's weather",
    ]

    print(f"\n📋 Available Tools:")
    for desc in tool_descriptions:
        print(f"  {desc[:80]}...")

    results = []

    for query in test_queries:
        print(f"\n🔍 Query: {query}")

        system_msg = f"""You are an urban computing expert. Select the best tool.

Available Tools:
{tools_text}

IMPORTANT PARAMETER EXTRACTION RULES:
- For weather_forecast (RapidAPI): Use "place" parameter with format "City,CountryCode"
- For weather_forecast_free (Open-Meteo): Use "latitude" and "longitude" parameters

Respond as JSON only: {{"tool_name": "X", "reasoning": "Y", "parameters": {{}}}}"""

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": query}
        ]

        try:
            response = llm.invoke(messages)
            content = response.content.strip()

            # 提取 JSON
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            tool_selection = json.loads(content)

            print(f"  ✓ Selected: {tool_selection['tool_name']}")
            print(f"  ✓ Parameters: {tool_selection['parameters']}")

            # 执行工具
            tool_config = None
            for tool in manager.api_tools:
                if tool['name'] == tool_selection['tool_name']:
                    tool_config = tool
                    break

            if tool_config:
                result = executor.execute(tool_config, tool_selection['parameters'])
                if result['success']:
                    print(f"  ✅ Execution: SUCCESS")
                else:
                    print(f"  ❌ Execution: FAILED")

            results.append({
                "query": query,
                "tool": tool_selection['tool_name'],
                "success": True
            })

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "success": False
            })

    return True, results


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "RapidAPI Weather Integration Tests" + " "*9 + "║")
    print("╚" + "="*58 + "╝")

    all_passed = True

    # Test 1: Direct API call
    success, data = test_rapidapi_direct()
    if not success:
        all_passed = False

    # Test 2: Via APIExecutor
    success, results = test_rapidapi_via_executor()
    if not success:
        all_passed = False
    else:
        passed = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n  Summary: {passed}/{total} locations tested successfully")

    # Test 3: LLM Tool Selection
    success, results = test_llm_tool_selection()
    if not success:
        all_passed = False
    else:
        passed = sum(1 for r in results if r['success'])
        total = len(results)
        print(f"\n  Summary: {passed}/{total} queries processed successfully")

    # Final status
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests PASSED")
    else:
        print("⚠️  Some tests FAILED")
    print("="*60 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
