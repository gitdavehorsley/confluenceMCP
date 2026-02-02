"""
MCP Server for Atlassian Confluence Form Completion
Handles form completion for AI intake process
"""

import json
import os
import logging
import re
from typing import Any, Dict, List, Optional
from atlassian import Confluence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize MCP server
server = Server("confluence-form-mcp")

# Register handlers for stdio mode (for local testing)
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return await list_tools()

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    return await call_tool(name, arguments)

# Confluence client (will be initialized on first use)
confluence_client: Optional[Confluence] = None


def get_confluence_client() -> Confluence:
    """Initialize and return Confluence client"""
    global confluence_client
    if confluence_client is None:
        base_url = os.environ.get("CONFLUENCE_BASE_URL")
        username = os.environ.get("CONFLUENCE_USERNAME")
        api_token = os.environ.get("CONFLUENCE_API_TOKEN")
        
        if not all([base_url, username, api_token]):
            raise ValueError("Missing required Confluence environment variables")
        
        confluence_client = Confluence(
            url=base_url,
            username=username,
            password=api_token
        )
    return confluence_client


async def list_tools() -> List[Tool]:
    """List available tools for Confluence form completion"""
    return [
        Tool(
            name="complete_confluence_form",
            description="Complete a Confluence form for AI intake process. Requires form page ID and form data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "The Confluence page ID containing the form"
                    },
                    "form_data": {
                        "type": "object",
                        "description": "Key-value pairs of form field names and their values",
                        "additionalProperties": True
                    },
                    "space_key": {
                        "type": "string",
                        "description": "The Confluence space key (optional, will be inferred from page if not provided)"
                    }
                },
                "required": ["page_id", "form_data"]
            }
        ),
        Tool(
            name="get_form_structure",
            description="Get the structure of a Confluence form to understand available fields",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_id": {
                        "type": "string",
                        "description": "The Confluence page ID containing the form"
                    }
                },
                "required": ["page_id"]
            }
        )
    ]


async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "complete_confluence_form":
            return await complete_form(arguments)
        elif name == "get_form_structure":
            return await get_form_structure(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def complete_form(arguments: Dict[str, Any]) -> List[TextContent]:
    """Complete a Confluence form with provided data"""
    page_id = arguments.get("page_id")
    form_data = arguments.get("form_data", {})
    space_key = arguments.get("space_key")
    
    if not page_id:
        raise ValueError("page_id is required")
    
    if not form_data:
        raise ValueError("form_data is required")
    
    try:
        confluence = get_confluence_client()
        
        # Get the current page content
        page = confluence.get_page_by_id(page_id, expand="body.storage,version")
        
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        # Get space key if not provided
        if not space_key:
            space_key = page.get("space", {}).get("key")
        
        # Extract current content
        current_content = page["body"]["storage"]["value"]
        
        # Update form fields in the content
        # This assumes the form uses Confluence macros or custom fields
        # Adjust this logic based on your specific form structure
        updated_content = update_form_fields(current_content, form_data)
        
        # Update the page
        confluence.update_page(
            page_id=page_id,
            title=page["title"],
            body=updated_content,
            version=page["version"]["number"] + 1
        )
        
        result = {
            "success": True,
            "page_id": page_id,
            "page_title": page["title"],
            "updated_fields": list(form_data.keys()),
            "message": "Form completed successfully"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error completing form: {str(e)}", exc_info=True)
        raise


async def get_form_structure(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get the structure of a Confluence form"""
    page_id = arguments.get("page_id")
    
    if not page_id:
        raise ValueError("page_id is required")
    
    try:
        confluence = get_confluence_client()
        
        # Get the page content
        page = confluence.get_page_by_id(page_id, expand="body.storage")
        
        if not page:
            raise ValueError(f"Page {page_id} not found")
        
        # Extract form structure from the content
        # This is a simplified version - adjust based on your form structure
        content = page["body"]["storage"]["value"]
        form_fields = extract_form_fields(content)
        
        result = {
            "page_id": page_id,
            "page_title": page["title"],
            "form_fields": form_fields,
            "raw_content_preview": content[:500] if len(content) > 500 else content
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting form structure: {str(e)}", exc_info=True)
        raise


def update_form_fields(content: str, form_data: Dict[str, Any]) -> str:
    """
    Update form fields in Confluence content.
    This is a template function - customize based on your form structure.
    
    Common approaches:
    1. If using Confluence Forms macro: Update macro parameters
    2. If using custom fields: Update field values
    3. If using structured content: Update specific sections
    """
    updated_content = content
    
    # Example: Replace placeholder patterns like {{field_name}} with actual values
    for field_name, field_value in form_data.items():
        # Pattern 1: Replace {{field_name}} placeholders
        placeholder = f"{{{{{field_name}}}}}"
        if placeholder in updated_content:
            updated_content = updated_content.replace(placeholder, str(field_value))
        
        # Pattern 2: Update form macro parameters (adjust based on your macro format)
        # This is a simplified example - adjust regex patterns based on your form structure
        pattern = f'name="{re.escape(field_name)}"[^>]*value="[^"]*"'
        replacement = f'name="{field_name}" value="{field_value}"'
        updated_content = re.sub(pattern, replacement, updated_content)
    
    return updated_content


def extract_form_fields(content: str) -> List[Dict[str, str]]:
    """
    Extract form field information from Confluence content.
    Customize this based on your form structure.
    """
    fields = []
    
    # Example: Extract fields from form macros or structured content
    # This is a simplified version - adjust based on your form structure
    
    # Pattern 1: Extract {{field_name}} placeholders
    placeholder_pattern = r'\{\{(\w+)\}\}'
    placeholders = re.findall(placeholder_pattern, content)
    for field_name in placeholders:
        fields.append({
            "name": field_name,
            "type": "text",
            "source": "placeholder"
        })
    
    # Pattern 2: Extract form input fields
    input_pattern = r'name="(\w+)"[^>]*(?:type="(\w+)")?'
    inputs = re.finditer(input_pattern, content)
    for match in inputs:
        fields.append({
            "name": match.group(1),
            "type": match.group(2) or "text",
            "source": "form_input"
        })
    
    return fields


async def main():
    """Main entry point for MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
