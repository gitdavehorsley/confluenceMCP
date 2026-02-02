# Confluence MCP Server for AWS Lambda

An MCP (Model Context Protocol) server for completing Atlassian Confluence forms, designed to run as an AWS Lambda function. This server is specifically built for automating the AI intake process by completing Confluence forms.

## Features

- **Complete Confluence Forms**: Automatically fill out Confluence forms with provided data
- **Form Structure Discovery**: Retrieve form structure to understand available fields
- **AWS Lambda Integration**: Runs serverlessly on AWS Lambda
- **CloudFormation Deployment**: Infrastructure as code for easy deployment
- **Secure Credential Management**: Uses AWS Secrets Manager for Confluence credentials

## Architecture

```
MCP Client → AWS Lambda → Confluence API
                ↓
         Secrets Manager (credentials)
```

## Prerequisites

- AWS Account with appropriate permissions
- Python 3.11+
- AWS CLI configured
- Confluence instance with API access
- Confluence API token

## Setup

### 1. Get Confluence API Token

1. Go to your Atlassian account settings
2. Navigate to Security → API tokens
3. Create a new API token
4. Save the token securely

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Deploy with CloudFormation

#### Option A: Using the deployment script

```bash
chmod +x deploy.sh
./deploy.sh
```

Then create the CloudFormation stack:

```bash
aws cloudformation create-stack \
  --stack-name confluence-mcp-server \
  --template-body file://cloudformation.yaml \
  --parameters \
    ParameterKey=ConfluenceBaseUrl,ParameterValue=https://your-domain.atlassian.net \
    ParameterKey=ConfluenceUsername,ParameterValue=your-email@example.com \
    ParameterKey=ConfluenceApiToken,ParameterValue=your-api-token \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

After the stack is created, update the Lambda function code:

```bash
aws lambda update-function-code \
  --function-name confluence-form-mcp-server \
  --zip-file fileb://lambda-deployment.zip \
  --region us-east-1
```

#### Option B: Manual deployment

1. Create a deployment package:

```bash
mkdir deployment
pip install -r requirements.txt -t deployment/
cp lambda_handler.py deployment/
cp mcp_server.py deployment/
cd deployment
zip -r ../lambda-deployment.zip .
cd ..
```

2. Create the CloudFormation stack (same as Option A)
3. Upload the deployment package to Lambda

## Configuration

### CloudFormation Parameters

- `ConfluenceBaseUrl`: Your Confluence instance URL (e.g., `https://your-domain.atlassian.net`)
- `ConfluenceUsername`: Your Confluence username or email
- `ConfluenceApiToken`: Your Confluence API token
- `LambdaFunctionName`: Name for the Lambda function (default: `confluence-form-mcp-server`)
- `LambdaMemorySize`: Memory size in MB (default: 256)
- `LambdaTimeout`: Timeout in seconds (default: 30)

### Environment Variables

The Lambda function automatically loads credentials from AWS Secrets Manager. The secret is created by the CloudFormation template.

## Usage

### MCP Protocol Methods

#### Initialize

```json
{
  "method": "initialize",
  "params": {}
}
```

#### List Tools

```json
{
  "method": "tools/list",
  "params": {}
}
```

#### Complete Form

```json
{
  "method": "tools/call",
  "params": {
    "name": "complete_confluence_form",
    "arguments": {
      "page_id": "123456",
      "form_data": {
        "field_name_1": "value1",
        "field_name_2": "value2"
      }
    }
  }
}
```

#### Get Form Structure

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_form_structure",
    "arguments": {
      "page_id": "123456"
    }
  }
}
```

### Testing Locally

You can test the MCP server locally using stdio mode:

```bash
python mcp_server.py
```

## Customization

### Form Field Update Logic

The `update_form_fields()` function in `mcp_server.py` handles how form fields are updated. You'll need to customize this based on your specific Confluence form structure:

1. **Confluence Forms Macro**: Update macro parameters
2. **Custom Fields**: Update field values directly
3. **Structured Content**: Update specific sections

Example customization:

```python
def update_form_fields(content: str, form_data: Dict[str, Any]) -> str:
    # Your custom logic here
    # For example, if using Confluence Forms macro:
    # - Parse macro parameters
    # - Update field values
    # - Reconstruct macro
    pass
```

### Form Field Extraction

Similarly, customize `extract_form_fields()` to match your form structure:

```python
def extract_form_fields(content: str) -> List[Dict[str, str]]:
    # Your custom logic to extract form fields
    # Return list of field definitions
    pass
```

## Troubleshooting

### Lambda Function Errors

Check CloudWatch Logs:

```bash
aws logs tail /aws/lambda/confluence-form-mcp-server --follow
```

### Common Issues

1. **Missing Credentials**: Ensure the Secrets Manager secret is created and accessible
2. **Permission Errors**: Check IAM role permissions for Secrets Manager access
3. **Confluence API Errors**: Verify API token and base URL are correct
4. **Form Update Failures**: Review form structure and customize update logic

## Security Considerations

- API tokens are stored in AWS Secrets Manager
- Lambda execution role has minimal required permissions
- Consider adding VPC configuration if Confluence is in a private network
- Enable CloudWatch logging for audit trails

## Monitoring

The CloudFormation template creates a CloudWatch Log Group for monitoring. You can:

- View logs in AWS Console
- Set up CloudWatch Alarms for errors
- Monitor Lambda metrics (invocations, errors, duration)

## License

This project is provided as-is for your use case.

## Support

For issues or questions:
1. Check CloudWatch Logs for error details
2. Verify Confluence API credentials
3. Review form structure customization
4. Ensure Lambda has proper IAM permissions
