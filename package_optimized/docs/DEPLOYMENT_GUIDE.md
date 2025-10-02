# Distributed S&P 500 Stock Analysis - Deployment Guide

This guide explains how to deploy the distributed processing solution that can handle the full S&P 500 dataset (500+ stocks) within AWS Lambda's constraints.

## Architecture Overview

The solution uses a distributed architecture to overcome Lambda's 15-minute timeout:

- **Sequential Processing**: For datasets ≤ 100 stocks (existing behavior)
- **Distributed Processing**: For datasets > 100 stocks (new capability)
  - Splits dataset into chunks of 50 stocks each
  - Processes chunks in parallel using async Lambda invocations
  - Uses S3 for intermediate result storage
  - Aggregates results and sends final email

## Deployment Steps

### 1. Update Lambda Function

Replace your existing `lambda_function.py` with the new distributed version:

```bash
# In your package_optimized directory
cp lambda_function.py lambda_function_backup.py  # Backup existing
# Then deploy the new lambda_function.py
```

### 2. Configure Environment Variables

Add these new environment variables to your Lambda function:

```bash
CHUNK_SIZE=50                    # Stocks per chunk (recommended: 50)
MAX_WORKERS=5                    # Parallel API calls per chunk
S3_BUCKET=your-bucket-name       # S3 bucket for temporary storage
AWS_LAMBDA_FUNCTION_NAME=stock-analysis-function  # Your function name
```

### 3. Update IAM Permissions

Add these permissions to your Lambda's IAM role:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "arn:aws:lambda:*:*:function:stock-analysis-function"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### 4. Create S3 Bucket

Create an S3 bucket for storing intermediate results:

```bash
aws s3 mb s3://your-bucket-name --region us-east-1
```

### 5. Increase Lambda Configuration

Update your Lambda function configuration:

```bash
# Increase memory for better performance
aws lambda update-function-configuration \
    --function-name stock-analysis-function \
    --memory-size 1024 \
    --timeout 900  # 15 minutes max
```

## Testing the Solution

### Test with Small Dataset (Sequential)

```python
# Use test_payload.json (15 stocks) - will use sequential processing
aws lambda invoke \
    --function-name stock-analysis-function \
    --payload file://test_payload.json \
    response.json
```

### Test with Large Dataset (Distributed)

```python
# Create a larger test dataset with 150+ stocks
python test_distributed.py
```

## Step Functions Integration (Optional)

For production use with full S&P 500, deploy the Step Functions workflow:

### 1. Create Step Functions State Machine

```bash
aws stepfunctions create-state-machine \
    --name sp500-stock-analysis \
    --definition file://step_functions_definition.json \
    --role-arn arn:aws:iam::ACCOUNT:role/StepFunctionsExecutionRole
```

### 2. Update EventBridge Rule

Update your weekly trigger to call Step Functions instead of Lambda directly:

```bash
aws events put-targets \
    --rule weekly-stock-analysis \
    --targets "Id"="1","Arn"="arn:aws:states:us-east-1:ACCOUNT:stateMachine:sp500-stock-analysis"
```

## Performance Characteristics

### Sequential Processing (≤ 100 stocks)
- **Time**: ~10-15 minutes for 100 stocks
- **Cost**: Standard Lambda pricing
- **Reliability**: High (single execution)

### Distributed Processing (> 100 stocks)
- **Time**: ~10-15 minutes for 500 stocks (parallel processing)
- **Cost**: Multiple Lambda invocations + S3 storage
- **Reliability**: Built-in retry logic and error handling

## Monitoring

### CloudWatch Logs
Each chunk creates separate log streams:
- Main orchestrator: `/aws/lambda/stock-analysis-function`
- Individual chunks: Look for `chunk_X_` in log messages

### S3 Monitoring
Monitor intermediate files in S3:
```bash
aws s3 ls s3://your-bucket-name/stock-analysis/chunks/
```

### Key Metrics to Watch
- **Chunk Success Rate**: Number of successful vs. total chunks
- **API Rate Limiting**: Alpha Vantage API call failures
- **Memory Usage**: Optimize based on CloudWatch metrics

## Troubleshooting

### Common Issues

1. **"Missing sp500_data in event"**
   - Ensure your input payload has the correct structure
   - Use `test_payload.json` as a reference

2. **S3 Access Denied**
   - Verify IAM permissions for S3 bucket
   - Ensure bucket name matches environment variable

3. **Lambda Invoke Errors**
   - Check IAM permissions for lambda:InvokeFunction
   - Verify function name in environment variables

4. **API Rate Limiting**
   - Increase delays between API calls if needed
   - Monitor Alpha Vantage quota usage

### Debug Mode

Enable debug logging by adding this to your Lambda:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Cost Optimization

### For Regular Use (Weekly)
- Use the distributed approach only when needed (> 100 stocks)
- Clean up S3 chunks automatically (implemented)
- Consider using Lambda provisioned concurrency for consistent performance

### For Development/Testing
- Use smaller test datasets
- Use mock data for testing (set ALPHA_VANTAGE_API_KEY to empty)

## Next Steps

1. **Deploy and Test**: Start with the distributed Lambda function
2. **Monitor Performance**: Watch first few executions closely
3. **Consider Step Functions**: For production reliability with full S&P 500
4. **Scale Further**: Add more sophisticated error handling and retry logic

The solution is designed to handle the full S&P 500 dataset efficiently while maintaining the existing functionality for smaller datasets.