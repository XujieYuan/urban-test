"""
Simple test script for API executor with GitHub API (no authentication required)
"""

import requests
import json
import os
import sys

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_github_api_direct():
    """直接测试 GitHub API"""
    print("="*60)
    print("Testing GitHub API - Direct Call")
    print("="*60)

    url = "https://api.github.com/users/torvalds"
    headers = {"Accept": "application/json"}

    try:
        print(f"\n📡 Requesting GitHub user data: torvalds (Linux creator)")
        print(f"🔗 URL: {url}\n")

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        data = response.json()

        print("✅ API Call Successful!")
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 User Info:")
        print(f"  - Name: {data.get('name')}")
        print(f"  - Location: {data.get('location')}")
        print(f"  - Public Repos: {data.get('public_repos')}")
        print(f"  - Followers: {data.get('followers')}")
        print(f"  - Bio: {data.get('bio')}")

        return True, data

    except requests.exceptions.RequestException as e:
        print(f"❌ API Call Failed: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False, None


def test_api_executor_integration():
    """测试 API Executor 集成"""
    print("\n" + "="*60)
    print("Testing API Executor Integration")
    print("="*60)

    from executors import APIExecutor

    executor = APIExecutor()

    # API 配置
    config = {
        "name": "github_user_info",
        "endpoint": "https://api.github.com/users/{username}",
        "method": "GET",
        "headers": {
            "Accept": "application/json"
        },
        "params": {
            "username": {"type": "string", "required": True}
        }
    }

    arguments = {
        "username": "torvalds"
    }

    try:
        print(f"\n⚙️  Executing github_user_info tool with arguments: {arguments}")
        result = executor.execute(config, arguments)

        if result["success"]:
            print("✅ Tool Execution Successful!")
            data = result.get("result", {})
            print(f"📝 User Info:")
            print(f"  - Name: {data.get('name')}")
            print(f"  - Location: {data.get('location')}")
            print(f"  - Public Repos: {data.get('public_repos')}")
            print(f"  - Followers: {data.get('followers')}")
        else:
            print(f"❌ Tool Execution Failed: {result['error']}")

        return result["success"]

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 API Executor Integration Test - GitHub API\n")

    # Test 1: Direct API call
    success1, data = test_github_api_direct()

    # Test 2: Executor integration
    success2 = test_api_executor_integration()

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Direct API Call: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Executor Integration: {'PASSED' if success2 else 'FAILED'}")

    if success1 and success2:
        print("\n🎉 All tests passed! API Executor is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

    print("="*60 + "\n")
