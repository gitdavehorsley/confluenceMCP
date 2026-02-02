"""
Inspect Confluence page to understand form structure
"""

import asyncio
import os
import sys
import json
from mcp_server import get_confluence_client

if len(sys.argv) >= 4:
    os.environ['CONFLUENCE_BASE_URL'] = sys.argv[1]
    os.environ['CONFLUENCE_USERNAME'] = sys.argv[2]
    os.environ['CONFLUENCE_API_TOKEN'] = sys.argv[3]
    page_id = sys.argv[4] if len(sys.argv) >= 5 else None
else:
    print("Usage: python inspect_page.py <base_url> <username> <api_token> [page_id]")
    print("\nExample:")
    print("  python inspect_page.py https://your-domain.atlassian.net user@example.com ATATT3x... 123456")
    sys.exit(1)

async def inspect_page():
    """Inspect the page content in detail"""
    confluence = get_confluence_client()
    
    # Get full page content
    page = confluence.get_page_by_id(page_id, expand="body.storage,version,space")
    
    print("="*80)
    print(f"Page: {page['title']}")
    print(f"Page ID: {page_id}")
    print(f"Space: {page.get('space', {}).get('key', 'Unknown')}")
    print("="*80)
    print("\nFull Content:")
    print("-"*80)
    print(page['body']['storage']['value'])
    print("-"*80)
    
    # Try to extract iframe URL
    import re
    iframe_pattern = r'<ri:url ri:value="([^"]+)"'
    matches = re.findall(iframe_pattern, page['body']['storage']['value'])
    if matches:
        print("\nFound iframe URLs:")
        for url in matches:
            print(f"  {url}")

if __name__ == "__main__":
    asyncio.run(inspect_page())
