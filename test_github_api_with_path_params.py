"""
测试带路径参数的 API 调用
测试 GitHub API 的 /users/{username} 端点
"""

from executors.api_executor import APIExecutor


def test_path_params():
    """测试 URL 路径参数功能"""
    print("="*60)
    print("Testing API Executor with Path Parameters")
    print("="*60)

    executor = APIExecutor()

    # 配置（使用路径参数 {username}）
    config = {
        "name": "github_user_info",
        "endpoint": "https://api.github.com/users/{username}",
        "method": "GET",
        "headers": {
            "Accept": "application/json",
            "User-Agent": "Urban-Test-App"
        },
        "params": {
            "username": {
                "type": "string",
                "required": True,
                "description": "GitHub username"
            }
        }
    }

    # 测试 1: octocat
    print("\n📍 Test 1: Get user 'octocat'")
    print("-" * 60)

    result = executor.execute(config, {"username": "octocat"})

    if result["success"]:
        print("✅ Success!")
        data = result["result"]
        print(f"  Login: {data['login']}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Repos: {data['public_repos']}")
        print(f"  From cache: {result.get('from_cache', False)}")
    else:
        print(f"❌ Failed: {result['error']}")

    # 测试 2: torvalds
    print("\n📍 Test 2: Get user 'torvalds'")
    print("-" * 60)

    result2 = executor.execute(config, {"username": "torvalds"})

    if result2["success"]:
        print("✅ Success!")
        data = result2["result"]
        print(f"  Login: {data['login']}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  From cache: {result2.get('from_cache', False)}")
    else:
        print(f"❌ Failed: {result2['error']}")

    # 测试 3: 重复请求 octocat（测试缓存）
    print("\n📍 Test 3: Get 'octocat' again (Cache Test)")
    print("-" * 60)

    result3 = executor.execute(config, {"username": "octocat"})

    if result3["success"]:
        print("✅ Success!")
        print(f"  From cache: {result3.get('from_cache', False)}")
        if result3.get('from_cache'):
            print("  🚀 Cache working perfectly!")
    else:
        print(f"❌ Failed: {result3['error']}")

    print("\n" + "="*60)
    print("Path Parameters Test Complete")
    print("="*60)


if __name__ == "__main__":
    test_path_params()
