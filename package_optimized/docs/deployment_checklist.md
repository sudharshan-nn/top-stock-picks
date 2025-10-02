# Production Deployment Checklist

## ✅ Pre-Deployment Validation

- [x] **Distributed processing logic implemented**
  - Automatic switching between sequential (≤100 stocks) and distributed (>100 stocks) processing
  - Chunking mechanism with configurable chunk size
  - Parallel processing within chunks using ThreadPoolExecutor

- [x] **All tests passing**
  - Sequential processing test: ✅ PASSED
  - Distributed processing logic: ✅ PASSED
  - Chunk processing logic: ✅ PASSED

- [x] **Performance optimizations**
  - Reduced API timeouts (5s vs 10s)
  - Essential fundamentals only for faster processing
  - Optimized JSON parsing and response handling
  - Rate limiting with jitter for API calls

## 🚀 Deployment Steps

### 1. Lambda Function Update

```bash
# Backup existing function
aws lambda get-function --function-name stock-analysis-function \
  --query 'Code.Location' --output text | xargs curl -o backup.zip

# Update function code
zip -r function.zip lambda_function.py
aws lambda update-function-code \
  --function-name stock-analysis-function \
  --zip-file fileb://function.zip
```

### 2. Environment Variables

Add/update these environment variables in AWS Lambda Console:

```
CHUNK_SIZE=50
MAX_WORKERS=5
S3_BUCKET=sudhan-stock-analysis
AWS_LAMBDA_FUNCTION_NAME=stock-analysis-function
EMAIL_RECIPIENT=your-email@domain.com
ALPHA_VANTAGE_API_KEY=your-api-key
OPENAI_API_KEY=your-openai-key
```

### 3. IAM Permissions

Update Lambda execution role with these additional permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": "arn:aws:lambda:us-east-1:*:function:stock-analysis-function"
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
                "arn:aws:s3:::sudhan-stock-analysis",
                "arn:aws:s3:::sudhan-stock-analysis/*"
            ]
        }
    ]
}
```

### 4. S3 Bucket Setup

```bash
# Create bucket if not exists
aws s3 mb s3://sudhan-stock-analysis --region us-east-1

# Set lifecycle policy for automatic cleanup
aws s3api put-bucket-lifecycle-configuration \
  --bucket sudhan-stock-analysis \
  --lifecycle-configuration file://s3-lifecycle.json
```

### 5. Lambda Configuration Update

```bash
# Increase memory and timeout for better performance
aws lambda update-function-configuration \
  --function-name stock-analysis-function \
  --memory-size 1024 \
  --timeout 900
```

## 🧪 Testing Protocol

### Phase 1: Small Dataset Test
```bash
# Test with existing payload (15 stocks - sequential processing)
aws lambda invoke \
  --function-name stock-analysis-function \
  --payload file://test_payload.json \
  response.json

# Expected: Sequential processing, email delivered
```

### Phase 2: Medium Dataset Test
```bash
# Test with 150 stocks (distributed processing)
python generate_test_payload.py --size 150 > medium_test.json
aws lambda invoke \
  --function-name stock-analysis-function \
  --payload file://medium_test.json \
  response.json

# Expected: Distributed processing triggered, multiple chunks
```

### Phase 3: Full S&P 500 Test
```bash
# Test with full S&P 500 dataset (500 stocks)
aws lambda invoke \
  --function-name stock-analysis-function \
  --payload file://sp500_full_payload.json \
  response.json

# Expected: ~10 chunks, completion in 10-15 minutes
```

## 📊 Monitoring Setup

### CloudWatch Dashboards
Create dashboard with these metrics:
- Lambda invocation count and duration
- Error rates by chunk
- S3 object count in chunks folder
- SES email delivery status

### CloudWatch Alarms
Set up alarms for:
- Lambda function errors > 5%
- Individual chunk timeout (> 10 minutes)
- S3 storage costs > expected threshold
- Email delivery failures

### Log Analysis
Monitor these log patterns:
- `"chunks_launched"` - Distributed processing triggered
- `"Chunk.*complete"` - Individual chunk completion
- `"Analysis complete"` - Final aggregation
- `"S3 chunks cleaned up"` - Cleanup confirmation

## 🔧 Performance Tuning

### Expected Performance Metrics

**Sequential Processing (≤100 stocks):**
- Duration: 8-12 minutes
- Memory usage: 200-400 MB
- API calls: 100-150 (including retries)
- Cost: ~$0.05 per execution

**Distributed Processing (500 stocks):**
- Total duration: 10-15 minutes
- Parallel chunks: 10 (50 stocks each)
- Memory usage per chunk: 200-300 MB
- Total API calls: 500-750
- Cost: ~$0.15 per execution

### Optimization Opportunities

1. **API Rate Limiting**
   - Monitor Alpha Vantage quota usage
   - Adjust delays based on actual rate limits
   - Implement exponential backoff for errors

2. **Memory Optimization**
   - Profile memory usage in production
   - Adjust based on actual data size
   - Consider streaming for very large datasets

3. **Cost Optimization**
   - Use provisioned concurrency for consistent performance
   - Optimize chunk size based on processing time
   - Implement intelligent caching for repeated analysis

## 🚨 Rollback Plan

If issues occur:

```bash
# Quick rollback to previous version
aws lambda update-function-code \
  --function-name stock-analysis-function \
  --zip-file fileb://backup.zip

# Revert environment variables if needed
aws lambda update-function-configuration \
  --function-name stock-analysis-function \
  --environment Variables='{...previous_vars...}'
```

## ✅ Post-Deployment Validation

- [ ] Test email delivery with small dataset
- [ ] Verify distributed processing with medium dataset
- [ ] Monitor first full S&P 500 execution
- [ ] Check S3 cleanup after completion
- [ ] Validate CloudWatch metrics and alarms
- [ ] Confirm EventBridge scheduling still works

## 📈 Success Criteria

**Deployment is successful when:**
1. ✅ All test payloads process without errors
2. ✅ Emails are delivered with correct top 25 stocks
3. ✅ Distributed processing completes within 15 minutes
4. ✅ S3 temporary files are cleaned up automatically
5. ✅ No increase in error rates or timeouts
6. ✅ Weekly scheduled execution works as expected

The system is now ready to handle the full S&P 500 dataset with distributed processing while maintaining backward compatibility for smaller datasets.