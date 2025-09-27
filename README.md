# 🚀 AI-Powered Stock Analysis Lambda

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An intelligent stock analysis system that uses OpenAI GPT to evaluate S&P 500 stocks based on fundamental indicators and automatically emails the top-ranked picks.

## ✨ Features

- 🤖 **AI-Powered Analysis** - Uses OpenAI GPT-3.5 to analyze 15 fundamental indicators
- 📊 **Multiple Data Sources** - Alpha Vantage, Financial Modeling Prep, Yahoo Finance, and smart fallbacks
- 📧 **Automated Email Reports** - Sends CSV reports via AWS SES
- 🚀 **Production Ready** - Optimized Lambda package without dependency conflicts
- 🛡️ **Robust Error Handling** - Graceful fallbacks for data and API failures
- 💰 **Cost Effective** - ~$4-6/month for daily analysis

## 🎯 Quick Start

### Prerequisites
- AWS Account with Lambda and SES access
- OpenAI API key
- Verified email address in AWS SES

### 1. Deploy to AWS Lambda
```bash
# Download the production package (17.1MB)
# Upload lambda_production_with_email.zip to AWS Lambda

# Or via AWS CLI
aws lambda create-function \
  --function-name stock-analysis \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_production_with_email.zip \
  --timeout 900 \
  --memory-size 1024
```

### 2. Configure Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ Required | Your OpenAI API key |
| `EMAIL_RECIPIENT` | ✅ Required | Email address to receive reports |
| `ALPHA_VANTAGE_API_KEY` | Optional | For real stock data |
| `FMP_API_KEY` | Optional | For real stock data |

### 3. Test the Function
```json
{
  "sp500_data": [
    {"Symbol": "AAPL", "Sector": "Technology"},
    {"Symbol": "MSFT", "Sector": "Technology"},
    {"Symbol": "GOOGL", "Sector": "Technology"}
  ]
}
```

### 4. Expected Output
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Analysis completed successfully\", \"results_count\": 3, \"openai_used\": true}"
}
```

You'll receive an email with a CSV attachment containing the AI-ranked stock picks! 📧

## 🏗️ Architecture

### Data Flow
```
S&P 500 Data → Stock APIs → AI Analysis → Email Report
     ↓              ↓           ↓            ↓
Lambda Event → Fundamentals → OpenAI GPT → AWS SES
```

### Stock Data Sources (Priority Order)
1. **Alpha Vantage API** - Professional financial data
2. **Financial Modeling Prep** - Comprehensive ratios
3. **Yahoo Finance** - Free fallback option
4. **Smart Dummy Data** - Realistic test data

### AI Analysis Process
1. **Fetch Fundamentals** - 15 key indicators per stock
2. **Batch Processing** - 20 stocks per OpenAI call
3. **AI Scoring** - GPT assigns buy scores (1-10) and reasons
4. **Ranking** - Top 25 stocks by AI buy score
5. **Email Delivery** - CSV attachment via SES

## 📁 Project Structure

```
lambda_openai_clean/
├── lambda_production_with_email.zip    # 🚀 Production deployment package
├── lambda_function.py                   # Source code (minimal version)
├── lambda_function_original.py          # Original full-featured version
├── requirements.txt                     # Full dependencies
├── requirements_no_pandas.txt           # Lightweight dependencies
├── DEPLOYMENT_GUIDE.md                  # 📖 Detailed deployment instructions
├── cloudformation-template.yaml        # Infrastructure as code
├── deploy.sh                           # Deployment script
├── Dockerfile                          # Container support
└── README.md                           # This file
```

## 🔧 Configuration

### Lambda Settings
- **Runtime**: Python 3.9+
- **Memory**: 1024MB (recommended)
- **Timeout**: 15 minutes
- **Handler**: `lambda_function.lambda_handler`

### IAM Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🚀 Production Package Highlights

### ✅ What's Included
- **Real OpenAI Integration** - Direct HTTP API calls
- **Multiple Stock APIs** - Alpha Vantage, FMP, Yahoo Finance
- **Email Functionality** - AWS SES with CSV attachments
- **Error Handling** - Graceful fallbacks for all failures
- **Performance Optimized** - 17.1MB package, 30-60s execution

### ❌ Dependency Issues Solved
- **No `async_timeout` errors** - Removed aiohttp dependencies
- **No `pydantic_core` conflicts** - No OpenAI library used
- **No `numpy` architecture issues** - Pure Python approach
- **No pandas dependencies** - Custom CSV generation

## 📊 Sample Output

### Email Subject
"Top 25 Stock Buy Picks (AI Analysis)"

### CSV Content
```csv
Symbol,Industry,BuyScore,ReasonsToBuy
AAPL,Technology,9,"Strong revenue growth; Healthy profit margins; Low debt ratio"
MSFT,Technology,8,"Consistent earnings; High ROE; Market leadership"
GOOGL,Technology,7,"Innovation leader; Strong cash flow; Stable growth"
```

## 💰 Cost Breakdown

### Monthly Costs (1 execution/day, 25 stocks)
- **AWS Lambda**: ~$2-3 (compute time)
- **OpenAI API**: ~$1-2 (GPT calls)
- **AWS SES**: ~$0.10 (email sending)
- **Data Transfer**: ~$0.50
- **Total**: ~$4-6/month

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
**Fixed** ✅ - Production package avoids all problematic dependencies

#### Email Not Received
1. Check SES email verification
2. Verify IAM permissions include SES
3. Check CloudWatch logs for errors

#### OpenAI API Errors
1. Verify API key is correct
2. Check OpenAI account credits
3. Monitor rate limiting

### Debug Commands
```bash
# View logs
aws logs tail /aws/lambda/stock-analysis --follow

# Test function
aws lambda invoke --function-name stock-analysis \
  --payload file://test-event.json response.json
```

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python lambda_function.py
```

### Building New Package
```bash
# Install to package directory
pip install -r requirements.txt -t package/

# Create deployment zip
cd package && zip -r ../lambda-new.zip .
```

### API Keys for Real Data
- **Alpha Vantage**: Free at [alphavantage.co](https://alphavantage.co)
- **Financial Modeling Prep**: Free tier at [financialmodelingprep.com](https://financialmodelingprep.com)

## 🔐 Security

### Best Practices Implemented
- ✅ Environment variables for API keys
- ✅ HTTPS-only API calls
- ✅ No hardcoded credentials
- ✅ Least privilege IAM permissions

### Recommendations
- Store API keys in AWS Secrets Manager
- Enable Lambda function encryption
- Regular API key rotation

## 📈 Performance

### Current Performance
- **Cold Start**: ~2-3 seconds
- **Warm Execution**: ~30-60 seconds (3 stocks)
- **Package Size**: 17.1MB
- **Memory Usage**: ~512MB peak

### Optimization Tips
1. Increase memory to 1536MB for faster execution
2. Add real API keys for better data quality
3. Use provisioned concurrency for consistent performance

## 🎯 Future Enhancements

### Immediate
- [x] Make email recipient configurable
- [ ] Add CloudWatch alarms for monitoring
- [ ] Implement EventBridge scheduling

### Advanced
- [ ] Support full S&P 500 analysis
- [ ] Add technical indicators
- [ ] Multi-format reports (PDF, HTML)
- [ ] Real-time market data integration

## 📚 Documentation

- [**Deployment Guide**](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [**CloudFormation Template**](cloudformation-template.yaml) - Infrastructure as code
- [**AWS Lambda Docs**](https://docs.aws.amazon.com/lambda/) - Official AWS documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the GPT API
- **AWS** for Lambda and SES services
- **Alpha Vantage** for financial data APIs
- **Financial Modeling Prep** for comprehensive stock data

---

## 🚀 Ready to Deploy?

1. **Download**: `lambda_production_with_email.zip`
2. **Upload**: To AWS Lambda
3. **Configure**: Environment variables and permissions
4. **Test**: With sample S&P 500 data
5. **Enjoy**: AI-powered stock analysis emails! 📧

**Questions?** Check the [Deployment Guide](DEPLOYMENT_GUIDE.md) or open an issue.

---

*Built with ❤️ for intelligent investing*