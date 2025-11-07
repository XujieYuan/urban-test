"""
测试免费公开 API 调用
使用 GitHub API 作为示例（无需 API Key）
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入 API Executor
from executors.api_executor import APIExecutor


def test_github_api():
    """测试 GitHub API 调用（免费，无需 API Key）"""
    print("="*60)
    print("Testing API Executor with GitHub API")
    print("="*60)

    # 创建执行器
    executor = APIExecutor()

    # GitHub API 配置
    config = {
        "name": "github_user",
        "endpoint": "https://api.github.com/users/octocat",
        "method": "GET",
        "headers": {
            "Accept": "application/json",
            "User-Agent": "Urban-Test-App"
        },
        "params": {}
    }

    # 测试用例 1: 获取 GitHub 用户信息
    print("\n📍 Test 1: Get GitHub User Info (octocat)")
    print("-" * 60)

    result = executor.execute(config, {})

    if result["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result.get('from_cache', False)}")

        # 打印结果
        data = result["result"]
        print(f"\nUser Info:")
        print(f"  - Login: {data.get('login', 'N/A')}")
        print(f"  - Name: {data.get('name', 'N/A')}")
        print(f"  - Bio: {data.get('bio', 'N/A')}")
        print(f"  - Public Repos: {data.get('public_repos', 'N/A')}")
        print(f"  - Followers: {data.get('followers', 'N/A')}")
    else:
        print(f"❌ API call failed: {result['error']}")

    # 测试用例 2: 重复调用（测试缓存）
    print("\n\n📍 Test 2: Same Request (Testing Cache)")
    print("-" * 60)

    result2 = executor.execute(config, {})

    if result2["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result2.get('from_cache', False)}")
        if result2.get('from_cache'):
            print("🚀 Cache is working! This request was served from cache.")
        else:
            print("⚠️  Cache not working as expected.")
    else:
        print(f"❌ API call failed: {result2['error']}")

    # 测试用例 3: 不同用户
    print("\n\n📍 Test 3: Different User (torvalds)")
    print("-" * 60)

    config3 = {
        "name": "github_user",
        "endpoint": "https://api.github.com/users/torvalds",
        "method": "GET",
        "headers": {
            "Accept": "application/json",
            "User-Agent": "Urban-Test-App"
        },
        "params": {}
    }

    result3 = executor.execute(config3, {})

    if result3["success"]:
        print("✅ API call successful!")
        print(f"From cache: {result3.get('from_cache', False)}")

        data = result3["result"]
        print(f"\nUser Info:")
        print(f"  - Login: {data.get('login', 'N/A')}")
        print(f"  - Name: {data.get('name', 'N/A')}")
        print(f"  - Bio: {data.get('bio', 'N/A')}")
    else:
        print(f"❌ API call failed: {result3['error']}")

    print("\n" + "="*60)
    print("API Executor Test Complete")
    print("="*60)


def test_weather_with_rapidapi():
    """测试 RapidAPI 天气接口（需要有效的 API Key）"""
    print("\n\n" + "="*60)
    print("Testing RapidAPI Weather (Optional)")
    print("="*60)

    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key or api_key == "your-rapidapi-key-here":
        print("⚠️  RAPIDAPI_KEY not configured, skipping weather test")
        print("   To test weather API, set RAPIDAPI_KEY in .env file")
        return

    executor = APIExecutor()

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
            "place": {"type": "string", "default": "London,GB"},
            "cnt": {"type": "string", "default": "3"},
            "units": {"type": "string", "default": "metric"}
        }
    }

    print("\n📍 Testing Weather API for London")
    print("-" * 60)

    result = executor.execute(config, {"place": "London,GB"})

    if result["success"]:
        print("✅ Weather API call successful!")
        data = result["result"]
        if "list" in data:
            print(f"\nForecast:")
            for forecast in data["list"][:2]:
                print(f"  - Temp: {forecast.get('main', {}).get('temp', 'N/A')}°C")
    else:
        print(f"❌ Weather API call failed: {result['error']}")
        print("   (This is expected if API key is invalid or quota exceeded)")


if __name__ == "__main__":
    test_github_api()
    test_weather_with_rapidapi()
