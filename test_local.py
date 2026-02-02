"""
Local testing script for the MCP server
Run this to test the server without Lambda
"""

import asyncio
import json
import os
from mcp_server import list_tools, call_tool

# Set test credentials (for local testing only)
# In production, these come from AWS Secrets Manager
# Can be set via environment variables or command line arguments
import sys

if len(sys.argv) >= 4:
    # Allow passing credentials as command line arguments
    os.environ['CONFLUENCE_BASE_URL'] = sys.argv[1]
    os.environ['CONFLUENCE_USERNAME'] = sys.argv[2]
    os.environ['CONFLUENCE_API_TOKEN'] = sys.argv[3]
else:
    # Use environment variables
    os.environ['CONFLUENCE_BASE_URL'] = os.getenv('TEST_CONFLUENCE_URL', os.getenv('CONFLUENCE_BASE_URL', ''))
    os.environ['CONFLUENCE_USERNAME'] = os.getenv('TEST_CONFLUENCE_USERNAME', os.getenv('CONFLUENCE_USERNAME', ''))
    os.environ['CONFLUENCE_API_TOKEN'] = os.getenv('TEST_CONFLUENCE_API_TOKEN', os.getenv('CONFLUENCE_API_TOKEN', ''))


async def test_list_tools():
    """Test listing available tools"""
    print("Testing list_tools...")
    tools = await list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    return tools


async def test_get_form_structure(page_id: str):
    """Test getting form structure"""
    print(f"\nTesting get_form_structure for page {page_id}...")
    try:
        result = await call_tool("get_form_structure", {"page_id": page_id})
        print("Result:")
        for content in result:
            print(content.text)
    except Exception as e:
        print(f"Error: {e}")


async def test_complete_form(page_id: str, form_data: dict):
    """Test completing a form"""
    print(f"\nTesting complete_confluence_form for page {page_id}...")
    try:
        result = await call_tool("complete_confluence_form", {
            "page_id": page_id,
            "form_data": form_data
        })
        print("Result:")
        for content in result:
            print(content.text)
    except Exception as e:
        print(f"Error: {e}")


async def main():
    """Main test function"""
    print("Confluence MCP Server - Local Test\n")
    print("=" * 50)
    
    # Test 1: List tools
    tools = await test_list_tools()
    
    # Test 2: Get form structure (uncomment and provide page_id)
    # await test_get_form_structure("123456")
    
    # Test 3: Complete form (uncomment and provide page_id and form_data)
    # await test_complete_form("123456", {
    #     "field1": "value1",
    #     "field2": "value2"
    # })
    
    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
