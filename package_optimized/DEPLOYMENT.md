# Lambda Deployment Package - Quick Reference

## 📦 Current Deployment

**Package**: `lambda_yahoo_primary.zip` (46MB)
**S3**: `s3://sudhan-stock-analysis/lambda_yahoo_primary.zip`
**Lambda**: `stock-analysis-function`
**Status**: ✅ Production Ready

## 🚀 Redeploy After Changes

```bash
cd package_optimized

# Create new package
zip -r lambda_updated.zip . \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.dist-info*" \
  -x "*.md"

# Upload to S3
aws s3 cp lambda_updated.zip s3://sudhan-stock-analysis/

# Update Lambda
aws lambda update-function-code \
  --function-name stock-analysis-function \
  --s3-bucket sudhan-stock-analysis \
  --s3-key lambda_updated.zip
```

## 📝 Key Files

- **lambda_function.py** (27KB) - Main Lambda handler
- **requirements.txt** - Python dependencies
- **lambda_yahoo_primary.zip** (46MB) - Deployed package
- **step_functions_definition.json** - Step Functions workflow

## 🔧 Dependencies

All dependencies are installed directly in this directory:
- boto3, botocore, s3transfer (AWS SDK)
- yfinance, pandas, numpy (Data fetching)
- lxml, html5lib (HTML parsing)
- requests, urllib3 (HTTP)

## ⚙️ Environment Variables

Required in Lambda:
```
ALPHA_VANTAGE_API_KEY=SIEYBT4M9BD3CDTN
OPENAI_API_KEY=sk-proj-***
EMAIL_RECIPIENT=sudharshan.nn@gmail.com
S3_BUCKET=sudhan-stock-analysis
MAX_WORKERS=10
CHUNK_SIZE=50
```

## ✅ Last Successful Test

- **Stocks**: 50 S&P 500 companies
- **Success**: 44 stocks (88% real data)
- **Duration**: 8.5 minutes
- **Memory**: 90 MB
- **Email**: Top 25 delivered

## 📊 Data Sources

1. Yahoo Finance → ❌ Import fails (numpy issue)
2. Alpha Vantage → ✅ Primary (88% success)
3. Mock Data → ✅ Fallback (12%)
