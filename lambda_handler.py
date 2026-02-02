"""
AWS Lambda handler for Confluence MCP Server
Wraps the MCP server to work with Lambda's request/response model
"""

import json
import logging
import os
import boto3
from typing import Any, Dict
from mcp_server import list_tools, call_tool

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')


def load_confluence_credentials():
    """Load Confluence credentials from Secrets Manager"""
    secret_name = os.environ.get('CONFLUENCE_SECRET_NAME')
    if not secret_name:
        raise ValueError("CONFLUENCE_SECRET_NAME environment variable not set")
    
    try:
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # Set environment variables for the MCP server
        os.environ['CONFLUENCE_BASE_URL'] = secret['base_url']
        os.environ['CONFLUENCE_USERNAME'] = secret['username']
        os.environ['CONFLUENCE_API_TOKEN'] = secret['api_token']
        
    except Exception as e:
        logger.error(f"Error loading secrets: {str(e)}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for MCP server requests
    
    Expected event format:
    {
        "method": "tools/list" | "tools/call" | "initialize",
        "params": {
            "name": "tool_name",      # Only for tools/call
            "arguments": {...}        # Only for tools/call
        }
    }
    """
    try:
        # Load credentials on first invocation (Lambda container reuse)
        if not os.environ.get('CONFLUENCE_BASE_URL'):
            load_confluence_credentials()
        
        method = event.get("method", "")
        params = event.get("params", {})
        
        logger.info(f"Processing MCP request: {method}")
        
        if method == "tools/list":
            # List available tools
            import asyncio
            tools = asyncio.run(list_tools())
            
            # Convert tools to JSON-serializable format
            tools_dict = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
            ]
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "tools": tools_dict
                })
            }
        
        elif method == "tools/call":
            # Call a specific tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "error": "Tool name is required"
                    })
                }
            
            import asyncio
            result = asyncio.run(call_tool(tool_name, arguments))
            
            # Convert TextContent to JSON-serializable format
            result_text = "\n".join([content.text for content in result])
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                })
            }
        
        elif method == "initialize":
            # MCP initialization
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "confluence-form-mcp",
                        "version": "1.0.0"
                    }
                })
            }
        
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "error": f"Unknown method: {method}"
                })
            }
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
