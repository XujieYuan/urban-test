"""
Test script for Weather API integration
This script tests the weather API directly before integrating with the tool executor
"""

import requests
import json

def test_weather_api_direct():
    """Test weather API directly using Open-Meteo (free, no auth required)"""
    print("="*60)
    print("Testing Weather API - Direct Call")
    print("="*60)

    url = "https://api.open-meteo.com/v1/forecast"

    # Beijing coordinates (39.9042, 116.4074)
    querystring = {
        "latitude": 39.9042,
        "longitude": 116.4074,
        "hourly": "temperature_2m,humidity,wind_speed_10m",
        "temperature_unit": "celsius",
        "timezone": "auto"
    }

    headers = {
        "Accept": "application/json"
    }

    try:
        print(f"\n📡 Requesting weather data for: Beijing (39.9042°N, 116.4074°E)")
        print(f"🔗 URL: {url}")
        print(f"📋 Query: {querystring}\n")

        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()

        data = response.json()

        print("✅ API Call Successful!")
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response Data (first 600 chars):\n")
        resp_str = json.dumps(data, indent=2)
        print(resp_str[:600])
        if len(resp_str) > 600:
            print("...[truncated]")

        return True, data

    except requests.exceptions.RequestException as e:
        print(f"❌ API Call Failed: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False, None


def test_api_executor_integration():
    """Test the API Executor with weather API config"""
    print("\n" + "="*60)
    print("Testing API Executor Integration")
    print("="*60)

    from executors import APIExecutor

    executor = APIExecutor()

    # API 配置（从 urban_tools.json 中对应的配置）
    config = {
        "name": "weather_forecast",
        "endpoint": "https://api.open-meteo.com/v1/forecast",
        "method": "GET",
        "headers": {
            "Accept": "application/json"
        },
        "params": {
            "latitude": {"type": "number", "required": True},
            "longitude": {"type": "number", "required": True},
            "hourly": {"type": "string", "required": False, "default": "temperature_2m,humidity,wind_speed_10m"},
            "temperature_unit": {"type": "string", "required": False, "default": "celsius"},
            "timezone": {"type": "string", "required": False, "default": "auto"}
        }
    }

    arguments = {
        "latitude": 39.9042,
        "longitude": 116.4074
    }

    try:
        print(f"\n⚙️  Executing weather_forecast tool with arguments: {arguments}")
        result = executor.execute(config, arguments)

        if result["success"]:
            print("✅ Tool Execution Successful!")
            print(f"📊 Result (first 500 chars):\n")
            print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        else:
            print(f"❌ Tool Execution Failed: {result['error']}")

        return result["success"]

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Weather API Integration Tests\n")

    # Test 1: Direct API call
    success1, data = test_weather_api_direct()

    # Test 2: Executor integration
    success2 = test_api_executor_integration()

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"✅ Direct API Call: {'PASSED' if success1 else 'FAILED'}")
    print(f"✅ Executor Integration: {'PASSED' if success2 else 'FAILED'}")
    print("="*60 + "\n")
