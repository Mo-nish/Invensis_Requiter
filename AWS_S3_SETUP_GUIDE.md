# AWS S3 Setup Guide for Invensis Hiring Portal

## Why AWS S3?
Render uses ephemeral storage - uploaded files are deleted on every deployment or restart. AWS S3 provides permanent, reliable cloud storage for your resume and image files.

## Step 1: Create AWS Account
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process (requires credit card, but S3 is very cheap)
4. **Free Tier**: 5GB storage, 20,000 GET requests, 2,000 PUT requests per month for 12 months

## Step 2: Create S3 Bucket
1. Log into AWS Console: https://console.aws.amazon.com/
2. Search for "S3" in the services search bar
3. Click "Create bucket"
4. **Bucket settings:**
   - **Bucket name**: `invensis-hiring-portal` (must be globally unique)
   - **Region**: Choose closest to your users (e.g., `us-east-1`)
   - **Block Public Access**: UNCHECK "Block all public access"
   - **Bucket Versioning**: Disabled (to save costs)
   - **Encryption**: Enable (recommended)
5. Click "Create bucket"

## Step 3: Configure Bucket Policy
1. Click on your bucket name
2. Go to "Permissions" tab
3. Scroll to "Bucket policy"
4. Click "Edit" and paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::invensis-hiring-portal/*"
        }
    ]
}
```

**Note**: Replace `invensis-hiring-portal` with your actual bucket name

5. Click "Save changes"

## Step 4: Create IAM User for API Access
1. Go to IAM service: https://console.aws.amazon.com/iam/
2. Click "Users" in left sidebar
3. Click "Create user"
4. **User details:**
   - **User name**: `invensis-s3-uploader`
   - **Access type**: Programmatic access
5. Click "Next"
6. **Set permissions:**
   - Click "Attach policies directly"
   - Search for "AmazonS3FullAccess"
   - Check the box next to it
7. Click "Next" → "Create user"
8. **IMPORTANT**: Copy and save these credentials:
   - **Access Key ID**: `AKIA...`
   - **Secret Access Key**: `wJalr...` (only shown once!)

## Step 5: Add AWS Credentials to Render
1. Go to your Render dashboard
2. Click on your web service
3. Go to "Environment" tab
4. Add these environment variables:

```
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_S3_BUCKET_NAME=invensis-hiring-portal
AWS_S3_REGION=us-east-1
```

5. Click "Save Changes"

## Step 6: Add to Local .env File
Add these lines to your local `.env` file:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_S3_BUCKET_NAME=invensis-hiring-portal
AWS_S3_REGION=us-east-1
```

## Step 7: Test S3 Connection
After I integrate the code and you deploy:

1. Go to: `https://invensis-requiter.onrender.com/recruiter/test-s3`
2. You should see: `{"configured": true, "bucket": "invensis-hiring-portal", ...}`

## Cost Estimate
**Very affordable for your use case:**
- **Storage**: $0.023 per GB/month (~$0.23 for 10GB)
- **Requests**: $0.0004 per 1,000 PUT requests, $0.0004 per 10,000 GET requests
- **Data Transfer**: First 100GB free per month

**Example monthly cost for 100 candidates:**
- Storage (500MB): ~$0.01
- Uploads (100 files): ~$0.00004
- Downloads (1,000 views): ~$0.00004
- **Total**: ~$0.01 per month

## Security Best Practices
✅ Files are publicly readable (needed for viewing resumes)
✅ Only your application can upload/delete files (via IAM credentials)
✅ Credentials stored securely in environment variables
✅ Files have unique UUIDs to prevent conflicts

## Next Steps
Once you complete Steps 1-6 above, let me know and I'll:
1. Integrate S3 into all upload routes
2. Update templates to use S3 URLs
3. Create a migration script to move existing files
4. Test the complete flow

Ready to proceed? Complete the AWS setup steps above and share your:
- ✅ Bucket name (if different from `invensis-hiring-portal`)
- ✅ Region (if different from `us-east-1`)
- ✅ Confirmation that environment variables are added to Render

Then I'll complete the integration! 🚀

