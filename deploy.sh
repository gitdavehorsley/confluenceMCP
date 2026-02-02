#!/bin/bash
# Deployment script for Confluence MCP Server Lambda function

set -e

FUNCTION_NAME="${1:-confluence-form-mcp-server}"
REGION="${2:-us-east-1}"
STACK_NAME="${3:-confluence-mcp-server}"

echo "Building deployment package..."

# Create deployment directory
rm -rf deployment
mkdir -p deployment

# Install dependencies
pip install -r requirements.txt -t deployment/

# Copy source files
cp lambda_handler.py deployment/
cp mcp_server.py deployment/

# Create deployment package
cd deployment
zip -r ../lambda-deployment.zip .
cd ..

echo "Deployment package created: lambda-deployment.zip"
echo ""
echo "To deploy with CloudFormation:"
echo "  aws cloudformation create-stack \\"
echo "    --stack-name $STACK_NAME \\"
echo "    --template-body file://cloudformation.yaml \\"
echo "    --parameters \\"
echo "      ParameterKey=ConfluenceBaseUrl,ParameterValue=YOUR_CONFLUENCE_URL \\"
echo "      ParameterKey=ConfluenceUsername,ParameterValue=YOUR_USERNAME \\"
echo "      ParameterKey=ConfluenceApiToken,ParameterValue=YOUR_API_TOKEN \\"
echo "    --capabilities CAPABILITY_NAMED_IAM \\"
echo "    --region $REGION"
echo ""
echo "After stack creation, update Lambda function code:"
echo "  aws lambda update-function-code \\"
echo "    --function-name $FUNCTION_NAME \\"
echo "    --zip-file fileb://lambda-deployment.zip \\"
echo "    --region $REGION"
