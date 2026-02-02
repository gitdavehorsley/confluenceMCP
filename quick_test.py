"""
Quick test script for Confluence MCP Server
Usage: python quick_test.py <base_url> <username> <api_token> [page_id]
"""

import asyncio
import os
import sys
from mcp_server import list_tools, call_tool, get_confluence_client

# Set credentials from command line or environment
if len(sys.argv) >= 4:
    os.environ['CONFLUENCE_BASE_URL'] = sys.argv[1]
    os.environ['CONFLUENCE_USERNAME'] = sys.argv[2]
    os.environ['CONFLUENCE_API_TOKEN'] = sys.argv[3]
    page_id = sys.argv[4] if len(sys.argv) >= 5 else None
else:
    print("Usage: python quick_test.py <base_url> <username> <api_token> [page_id]")
    print("\nExample:")
    print("  python quick_test.py https://your-domain.atlassian.net user@example.com ATATT3x... 123456")
    sys.exit(1)


async def test_connection():
    """Test basic connection to Confluence"""
    print("Testing Confluence connection...")
    try:
        confluence = get_confluence_client()
        # Try to get spaces to verify connection
        spaces = confluence.get_all_spaces(start=0, limit=1)
        print(f"✓ Connected successfully!")
        print(f"  Confluence URL: {confluence.url}")
        if spaces and 'results' in spaces and len(spaces['results']) > 0:
            space = spaces['results'][0]
            print(f"  Test Space: {space.get('name', 'Unknown')} ({space.get('key', 'Unknown')})")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_list_tools():
    """Test listing available tools"""
    print("\n" + "="*60)
    print("Testing list_tools...")
    try:
        tools = await list_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"\n  Tool: {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Required params: {tool.inputSchema.get('required', [])}")
        return tools
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


async def test_get_form_structure(page_id: str):
    """Test getting form structure"""
    print("\n" + "="*60)
    print(f"Testing get_form_structure for page {page_id}...")
    try:
        result = await call_tool("get_form_structure", {"page_id": page_id})
        print("✓ Success!")
        for content in result:
            print("\nResult:")
            print(content.text)
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("="*60)
    print("Confluence MCP Server - Quick Test")
    print("="*60)
    
    # Test 1: Connection
    if not await test_connection():
        print("\n⚠️  Cannot proceed without connection. Please check your credentials.")
        return
    
    # Test 2: List tools
    tools = await test_list_tools()
    if not tools:
        print("\n⚠️  Cannot list tools. Check the MCP server implementation.")
        return
    
    # Test 3: Get form structure (if page_id provided)
    if page_id:
        await test_get_form_structure(page_id)
    else:
        print("\n" + "="*60)
        print("ℹ️  No page_id provided. Skipping form structure test.")
        print("   To test form operations, provide a page_id as the 4th argument.")
        print("   Example: python quick_test.py <url> <user> <token> 123456")
    
    print("\n" + "="*60)
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
