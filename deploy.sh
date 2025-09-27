#!/bin/bash

# AWS Lambda Deployment Script for Stock Analysis Function
set -e

echo "🚀 Starting Lambda deployment package creation..."

# Clean up previous builds
rm -rf package/
rm -f lambda_deploy.zip

# Create package directory
mkdir -p package

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -t package/

# Copy lambda function
echo "📋 Copying lambda function..."
cp lambda_function.py package/

# Create deployment zip
echo "🗜️ Creating deployment package..."
cd package
zip -r ../lambda_deploy.zip .
cd ..

# Check package size
PACKAGE_SIZE=$(du -h lambda_deploy.zip | cut -f1)
echo "📊 Package size: $PACKAGE_SIZE"

if [ $(stat -f%z lambda_deploy.zip) -gt 52428800 ]; then
    echo "⚠️  Warning: Package size exceeds 50MB. Consider using Lambda layers for large dependencies."
fi

echo "✅ Deployment package created: lambda_deploy.zip"
echo ""
echo "Next steps:"
echo "1. Upload lambda_deploy.zip to AWS Lambda"
echo "2. Set handler to: lambda_function.lambda_handler"
echo "3. Configure environment variables"
echo "4. Set up IAM roles and SES permissions"