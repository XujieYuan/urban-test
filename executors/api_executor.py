"""
API Executor - 调用 REST API

1. 实现 HTTP 请求（GET/POST/PUT/DELETE）
2. 处理认证和 API keys
3. 管理 API 缓存
"""

import os
import json
import requests
import hashlib
import time
from typing import Dict, Any
from pathlib import Path


class APIExecutor:
    """REST API 工具执行器"""

    def __init__(self, tools_dir: str = "./Cache/api"):
        """
        初始化 API 执行器

        Args:
            tools_dir: API 工具缓存目录
        """
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)

        # 速率限制记录（可选实现）
        self.rate_limits = {}

    def execute(self, config: Dict, arguments: Dict) -> Dict[str, Any]:
        """
        执行 API 调用

        Args:
            config: API 配置
                - name: API 名称
                - endpoint: API 端点 URL
                - method: HTTP 方法 (GET/POST/PUT/DELETE)
                - headers: 请求头
                - params: 参数定义
            arguments: 实际调用参数

        Returns:
            {
                "success": bool,
                "result": Any,
                "error": str | None
            }
        """
        try:
            # 1. 检查缓存（如果启用）
            cache_key = self._generate_cache_key(config, arguments)
            cached = self._check_cache(cache_key)
            if cached:
                return {
                    "success": True,
                    "result": cached,
                    "error": None,
                    "from_cache": True
                }

            # 2. 检查速率限制
            # TODO: API 开发者实现

            # 3. 准备请求
            url = config["endpoint"]
            method = config.get("method", "GET").upper()
            headers = self._prepare_headers(config.get("headers", {}))

            # 4. 处理参数（添加默认值）
            params = self._prepare_params(config.get("params", {}), arguments)

            # 5. 处理 URL 路径参数（如 {username}）
            url, path_params = self._replace_url_params(url, arguments)

            # 6. 移除已用于路径的参数（避免重复传入）
            for param_name in path_params:
                params.pop(param_name, None)

            # 7. 发送请求
            response = self._send_request(method, url, headers, params)

            # 7. 保存缓存
            self._save_cache(cache_key, response)

            return {
                "success": True,
                "result": response,
                "error": None
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "result": None,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": f"Unexpected error: {str(e)}"
            }

    def _replace_url_params(self, url: str, arguments: Dict) -> tuple:
        """
        替换 URL 中的路径参数
        例如：https://api.github.com/users/{username} -> https://api.github.com/users/torvalds

        Args:
            url: 带有 {param} 占位符的 URL
            arguments: 参数字典

        Returns:
            (替换后的 URL, 已替换的参数名列表)
        """
        import re

        # 找到所有 {param} 格式的占位符
        placeholders = re.findall(r'\{(\w+)\}', url)
        used_params = []

        for placeholder in placeholders:
            if placeholder in arguments:
                url = url.replace(f'{{{placeholder}}}', str(arguments[placeholder]))
                used_params.append(placeholder)

        return url, used_params

    def _prepare_headers(self, headers: Dict) -> Dict:
        """
        准备请求头，替换环境变量

        Args:
            headers: 原始请求头配置

        Returns:
            处理后的请求头
        """
        processed = {}
        for key, value in headers.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                processed[key] = os.getenv(env_var, "")
            else:
                processed[key] = value
        return processed

    def _prepare_params(self, param_schema: Dict, arguments: Dict) -> Dict:
        """
        准备请求参数，填充默认值并进行类型转换

        Args:
            param_schema: 参数定义
            arguments: 用户提供的参数

        Returns:
            完整的参数字典
        """
        params = {}

        # 添加用户提供的参数，并进行类型转换
        for param_name, param_value in arguments.items():
            if param_name in param_schema:
                param_def = param_schema[param_name]
                param_type = param_def.get("type", "string")

                # 进行类型转换
                if param_type == "number":
                    try:
                        param_value = float(param_value) if isinstance(param_value, str) else param_value
                    except (ValueError, TypeError):
                        pass
                elif param_type == "integer":
                    try:
                        param_value = int(param_value) if isinstance(param_value, str) else param_value
                    except (ValueError, TypeError):
                        pass

            params[param_name] = param_value

        # 填充默认值
        for param_name, param_def in param_schema.items():
            if param_name not in params and "default" in param_def:
                params[param_name] = param_def["default"]

        return params

    def _send_request(self, method: str, url: str, headers: Dict, params: Dict) -> Any:
        """
        发送 HTTP 请求
        """
        timeout = 30  # 默认超时 30 秒

        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=params, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=params, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    def _generate_cache_key(self, config: Dict, arguments: Dict) -> str:
        """生成缓存 key"""
        cache_data = {
            "endpoint": config["endpoint"],
            "arguments": arguments
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _check_cache(self, cache_key: str, ttl: int = 3600) -> Any:
        """
        检查缓存

        Args:
            cache_key: 缓存键
            ttl: 缓存有效期（秒）

        TODO: API 开发者可以实现更复杂的缓存策略
        """
        cache_file = self.tools_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        # 检查缓存是否过期
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age > ttl:
            cache_file.unlink()  # 删除过期缓存
            return None

        with open(cache_file) as f:
            return json.load(f)

    def _save_cache(self, cache_key: str, data: Any):
        """保存缓存"""
        cache_file = self.tools_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump(data, f)


# 测试代码
if __name__ == "__main__":
    executor = APIExecutor()

    # 测试配置
    config = {
        "name": "weather_forecast",
        "endpoint": "https://weather-api167.p.rapidapi.com/api/weather/forecast",
        "method": "GET",
        "headers": {
            "x-rapidapi-key": "${RAPIDAPI_KEY}",
            "x-rapidapi-host": "weather-api167.p.rapidapi.com"
        },
        "params": {
            "place": {"type": "string", "required": True},
            "units": {"type": "string", "default": "metric"}
        }
    }

    arguments = {
        "place": "Beijing,CN"
    }

    result = executor.execute(config, arguments)
    print(json.dumps(result, indent=2, ensure_ascii=False))
