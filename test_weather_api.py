"""
测试天气 API 调用
直接测试 API Executor 的功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入 API Executor
from executors.api_executor import APIExecutor


def test_weather_api():
    """测试天气 API 调用"""
    print("="*60)
    print("Testing Weather API Executor")
    print("="*60)

    # 创建执行器
    executor = APIExecutor()

    # API 配置（来自 urban_tools.json）
    config = {
        "name": "weather_forecast",
        "endpoint": "https://weather-api167.p.rapidapi.com/api/weather/forecast",
        "method": "GET",
        "headers": {
            "x-rapidapi-key": "${RAPIDAPI_KEY}",
            "x-rapidapi-host": "weather-api167.p.rapidapi.com",
            "Accept": "application/json"
        },
        "params": {
            "place": {"type": "string", "required": True},
            "cnt": {"type": "string", "default": "3"},
            "units": {"type": "string", "default": "metric"},
            "lang": {"type": "string", "default": "en"}
        }
    }

    # 测试用例 1: 伦敦天气
    print("\n📍 Test 1: London Weather")
    print("-" * 60)
    arguments = {
        "place": "London,GB",
        "cnt": "3",
        "units": "metric",
        "lang": "en"
    }

    result = executor.execute(config, arguments)

    if result["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result.get('from_cache', False)}")

        # 打印部分结果
        data = result["result"]
        if "list" in data:
            print(f"\nForecast for {arguments['place']}:")
            for forecast in data["list"][:3]:
                print(f"  - Time: {forecast.get('dt_txt', 'N/A')}")
                print(f"    Temp: {forecast.get('main', {}).get('temp', 'N/A')}°C")
                print(f"    Weather: {forecast.get('weather', [{}])[0].get('description', 'N/A')}")
    else:
        print(f"❌ API call failed: {result['error']}")

    # 测试用例 2: 北京天气（测试缓存）
    print("\n\n📍 Test 2: Beijing Weather")
    print("-" * 60)
    arguments2 = {
        "place": "Beijing,CN",
        "cnt": "3",
        "units": "metric"
    }

    result2 = executor.execute(config, arguments2)

    if result2["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result2.get('from_cache', False)}")
    else:
        print(f"❌ API call failed: {result2['error']}")

    # 测试用例 3: 重复调用伦敦天气（测试缓存）
    print("\n\n📍 Test 3: London Weather (Again - Testing Cache)")
    print("-" * 60)

    result3 = executor.execute(config, arguments)

    if result3["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result3.get('from_cache', False)}")
        if result3.get('from_cache'):
            print("🚀 Cache is working! This request was served from cache.")
    else:
        print(f"❌ API call failed: {result3['error']}")

    print("\n" + "="*60)
    print("Weather API Test Complete")
    print("="*60)


if __name__ == "__main__":
    # 检查 API Key
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or api_key == "your-rapidapi-key-here":
        print("❌ Error: RAPIDAPI_KEY not set in .env file")
        print("Please edit .env and set your RapidAPI key")
        sys.exit(1)

    test_weather_api()
