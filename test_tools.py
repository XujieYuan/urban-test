"""
Simple test script to verify tool configuration
Run this to check if your tools are properly loaded
"""

from tool_manager import UrbanToolManager


def test_tool_loading():
    """Test if tools can be loaded from config"""
    print("="*60)
    print("Testing Tool Loading")
    print("="*60)

    try:
        manager = UrbanToolManager("./urban_tools.json")
        print(f"✅ Successfully loaded {len(manager.get_tools())} tools\n")

        print("Available Tools:")
        print(manager.get_tools_description())

        return True
    except Exception as e:
        print(f"❌ Failed to load tools: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_retrieval():
    """Test retrieving individual tools"""
    print("\n" + "="*60)
    print("Testing Tool Retrieval")
    print("="*60)

    try:
        manager = UrbanToolManager("./urban_tools.json")

        # Test getting tool by name
        tool_names = ["sentiment_analysis", "get_traffic_data", "get_poi_data"]

        for name in tool_names:
            tool = manager.get_tool_by_name(name)
            if tool:
                print(f"✅ Found tool: {name}")
            else:
                print(f"❌ Tool not found: {name}")

        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 Urban Computing Tool System - Quick Test\n")

    success = True
    success = test_tool_loading() and success
    success = test_tool_retrieval() and success

    print("\n" + "="*60)
    if success:
        print("✅ All tests passed! Tools are properly configured.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your API keys")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*60 + "\n")
