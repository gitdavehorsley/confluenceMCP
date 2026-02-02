"""
Test form completion with sample data
"""

import asyncio
import os
import sys
from mcp_server import call_tool

if len(sys.argv) >= 4:
    os.environ['CONFLUENCE_BASE_URL'] = sys.argv[1]
    os.environ['CONFLUENCE_USERNAME'] = sys.argv[2]
    os.environ['CONFLUENCE_API_TOKEN'] = sys.argv[3]
    page_id = sys.argv[4] if len(sys.argv) >= 5 else None
else:
    print("Usage: python test_form_completion.py <base_url> <username> <api_token> <page_id>")
    print("\nExample:")
    print("  python test_form_completion.py https://your-domain.atlassian.net user@example.com ATATT3x... 123456")
    sys.exit(1)

if not page_id:
    print("Error: page_id is required")
    sys.exit(1)

# Sample form data - adjust based on your actual form fields
sample_form_data = {
    "project_name": "AI Integration Project",
    "description": "Integrating AI capabilities into our workflow",
    "requestor": "Test User",
    "priority": "High",
    "estimated_budget": "$50,000",
    "timeline": "Q2 2024",
    "department": "IT",
    "status": "Submitted"
}

async def test_complete_form():
    """Test completing the form"""
    print("="*80)
    print("Testing form completion...")
    print("="*80)
    print(f"\nPage ID: {page_id}")
    print(f"Form Data:")
    for key, value in sample_form_data.items():
        print(f"  {key}: {value}")
    print("\n" + "-"*80)
    
    try:
        result = await call_tool("complete_confluence_form", {
            "page_id": page_id,
            "form_data": sample_form_data,
            "create_summary_page": True
        })
        
        print("\n✓ Form completion successful!")
        print("\nResult:")
        for content in result:
            print(content.text)
        
        # Parse result to get the new page ID
        import json
        result_data = json.loads(result[0].text)
        if "summary_page_id" in result_data:
            base_url = os.environ.get('CONFLUENCE_BASE_URL', '').replace('/wiki', '')
            space_key = result_data.get('space_key', 'SI')
            page_id = result_data['summary_page_id']
            print(f"\n📄 Summary page created: {result_data['summary_page_id']}")
            if base_url:
                print(f"   View at: {base_url}/wiki/spaces/{space_key}/pages/{page_id}")
            else:
                print(f"   Space: {space_key}, Page ID: {page_id}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_form())
