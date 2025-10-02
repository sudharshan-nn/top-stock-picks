#!/bin/bash
# Build script for Lambda deployment package

set -e  # Exit on error

echo "🚀 Building Lambda deployment package..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf boto3 botocore s3transfer requests urllib3 certifi charset_normalizer \
       idna jmespath dateutil numpy pandas pytz lxml html5lib webencodings \
       bs4 beautifulsoup4-4.14.2.dist-info soupsieve multitasking yfinance \
       frozendict bin six.py appdirs.py typing_extensions.py peewee.py \
       *.dist-info __pycache__ *.zip

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -t . -r requirements.txt --upgrade

# Clean up unnecessary files
echo "🧹 Cleaning up unnecessary files..."
find . -type d -name "tests" -o -name "test" -o -name "*.dist-info" | xargs rm -rf 2>/dev/null || true
find . -type d -name "tzdata" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Create deployment package
echo "📦 Creating deployment package..."
zip -r lambda_deployment.zip . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.dist-info*" \
  -x "*.md" \
  -x "build.sh" \
  -x ".gitignore"

# Check size
SIZE=$(du -h lambda_deployment.zip | cut -f1)
echo "✅ Package created: lambda_deployment.zip ($SIZE)"

if [ -f lambda_deployment.zip ]; then
    echo ""
    echo "📤 To deploy to AWS Lambda:"
    echo "   aws s3 cp lambda_deployment.zip s3://sudhan-stock-analysis/"
    echo "   aws lambda update-function-code \\"
    echo "     --function-name stock-analysis-function \\"
    echo "     --s3-bucket sudhan-stock-analysis \\"
    echo "     --s3-key lambda_deployment.zip"
fi
