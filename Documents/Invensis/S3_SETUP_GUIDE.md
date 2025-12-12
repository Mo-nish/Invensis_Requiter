# 🚀 AWS S3 Setup Guide for Invensis Hiring Portal

## Overview
This guide will help you set up AWS S3 for persistent file storage (resumes and images) on Render.

## Why S3?
- **Persistent Storage**: Files survive server restarts and redeployments
- **Scalable**: Handle unlimited file uploads
- **Reliable**: 99.999999999% (11 9's) durability
- **Cost-Effective**: Pay only for what you use

## Step 1: Create AWS Account

1. Go to [AWS Console](https://aws.amazon.com/console/)
2. Sign up for a free account (12 months free tier available)
3. Complete the registration process

## Step 2: Create S3 Bucket

1. **Navigate to S3**:
   - Go to AWS Console → Services → S3
   - Click "Create bucket"

2. **Configure Bucket**:
   - **Bucket name**: `invensis-hiring-portal` (must be globally unique)
   - **AWS Region**: Choose closest to your users (e.g., `us-east-1`)
   - **Object Ownership**: ACLs enabled (recommended)
   - **Block Public Access**: **Uncheck** "Block all public access" (we need public read access for resumes)
   - **Bucket Versioning**: Disable (optional)
   - **Default encryption**: Enable (recommended)
   - Click "Create bucket"

3. **Configure Bucket Policy** (for public read access):
   - Go to your bucket → Permissions → Bucket Policy
   - Add this policy (replace `YOUR_BUCKET_NAME` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
        }
    ]
}
```

4. **Configure CORS** (if needed):
   - Go to Permissions → CORS
   - Add this configuration:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## Step 3: Create IAM User for S3 Access

1. **Navigate to IAM**:
   - Go to AWS Console → Services → IAM
   - Click "Users" → "Create user"

2. **Create User**:
   - **User name**: `invensis-s3-user`
   - **Access type**: Programmatic access
   - Click "Next"

3. **Set Permissions**:
   - Click "Attach policies directly"
   - Search for and select: **AmazonS3FullAccess** (or create a custom policy with only necessary permissions)
   - Click "Next" → "Create user"

4. **Save Credentials**:
   - **Access Key ID**: Copy this (you'll need it)
   - **Secret Access Key**: Click "Show" and copy this (you'll only see it once!)
   - Save these credentials securely

## Step 4: Configure Environment Variables on Render

1. **Go to Render Dashboard**:
   - Select your service
   - Go to "Environment" tab

2. **Add Environment Variables**:
   ```
   S3_BUCKET_NAME=invensis-hiring-portal
   S3_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your-access-key-id-here
   AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
   ```

3. **Save and Redeploy**:
   - Click "Save Changes"
   - Render will automatically redeploy

## Step 5: Verify Setup

1. **Check Logs**:
   - After redeploy, check Render logs
   - You should see: `✅ S3 client initialized successfully for bucket: invensis-hiring-portal`

2. **Test Upload**:
   - Upload a candidate with a resume
   - Check logs for: `✅ Resume uploaded to S3: https://...`
   - Try viewing the resume - it should work!

## Troubleshooting

### Error: "S3 not configured"
- **Solution**: Check that all 4 environment variables are set in Render

### Error: "Access Denied"
- **Solution**: 
  - Verify IAM user has S3 permissions
  - Check bucket policy allows public read access
  - Verify bucket name matches `S3_BUCKET_NAME`

### Error: "Bucket not found"
- **Solution**: 
  - Verify bucket name is correct
  - Check region matches `S3_REGION`
  - Ensure bucket exists in your AWS account

### Files not accessible
- **Solution**: 
  - Check bucket policy allows public read
  - Verify CORS is configured
  - Check file URL in database (should be full S3 URL)

## Cost Estimation

**AWS S3 Free Tier** (first 12 months):
- 5 GB storage
- 20,000 GET requests
- 2,000 PUT requests

**After Free Tier**:
- Storage: ~$0.023 per GB/month
- Requests: ~$0.0004 per 1,000 GET requests

For a small hiring portal, costs are typically **$1-5/month**.

## Security Best Practices

1. **Use IAM Roles** (instead of access keys) if possible
2. **Limit Permissions**: Create custom IAM policy with only necessary S3 permissions
3. **Enable Encryption**: Use S3 server-side encryption
4. **Monitor Access**: Enable CloudTrail for audit logs
5. **Rotate Keys**: Regularly rotate access keys

## Migration from Local Storage

Existing candidates with local file paths will continue to work. New uploads will automatically use S3 if configured.

To migrate existing files:
1. Download files from local storage
2. Re-upload them (they'll go to S3)
3. Or create a migration script to upload existing files to S3

## Support

If you encounter issues:
1. Check Render logs for detailed error messages
2. Verify AWS credentials in AWS Console
3. Test S3 access using AWS CLI
4. Contact support with specific error messages

