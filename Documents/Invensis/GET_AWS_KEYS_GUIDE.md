# How to Get AWS S3 Keys - Step-by-Step Guide

## 🎯 Quick Overview
You need 4 things:
1. AWS Access Key ID
2. AWS Secret Access Key
3. S3 Bucket Name
4. AWS Region

**Time needed**: 10-15 minutes

---

## Step 1: Create AWS Account (If You Don't Have One)

### 1.1 Go to AWS
- Open: https://aws.amazon.com/
- Click **"Create an AWS Account"** (orange button in top right)

### 1.2 Fill in Account Details
- **Email address**: Your email
- **Password**: Create a strong password
- **AWS account name**: `Invensis Hiring Portal` (or any name)
- Click **"Continue"**

### 1.3 Contact Information
- **Account type**: Select **"Personal"**
- Fill in your name, phone number, and address
- Click **"Continue"**

### 1.4 Payment Information
- Enter credit card details (required, but we'll use free tier)
- AWS won't charge you unless you exceed free tier limits
- Click **"Verify and Continue"**

### 1.5 Identity Verification
- Choose phone verification
- Enter code sent to your phone
- Click **"Continue"**

### 1.6 Select Support Plan
- Choose **"Basic support - Free"**
- Click **"Complete sign up"**

✅ **Account created!** You'll receive a confirmation email.

---

## Step 2: Create S3 Bucket

### 2.1 Login to AWS Console
- Go to: https://console.aws.amazon.com/
- Login with your email and password

### 2.2 Navigate to S3
- In the search bar at the top, type **"S3"**
- Click on **"S3"** (Scalable Storage in the Cloud)

### 2.3 Create Bucket
- Click the orange **"Create bucket"** button

### 2.4 Configure Bucket
Fill in these settings:

**General Configuration:**
- **Bucket name**: `invensis-hiring-portal-YOUR-NAME` 
  - Example: `invensis-hiring-portal-monish`
  - Must be globally unique (add your name if taken)
  - **Write down this name - you'll need it!**

- **AWS Region**: Select **"US East (N. Virginia) us-east-1"**
  - Or choose closest to your users
  - **Write down this region - you'll need it!**

**Object Ownership:**
- Keep default: **"ACLs disabled"**

**Block Public Access settings:**
- ⚠️ **IMPORTANT**: UNCHECK **"Block all public access"**
- Check the box that says "I acknowledge that the current settings might result in this bucket and the objects within becoming public"
- This allows people to view resumes

**Bucket Versioning:**
- Keep **"Disable"** (saves money)

**Default encryption:**
- Keep **"Enable"** with **"Amazon S3 managed keys (SSE-S3)"**

- Click orange **"Create bucket"** button at bottom

✅ **Bucket created!**

### 2.5 Configure Bucket Policy (Make Files Publicly Readable)

- Click on your bucket name (e.g., `invensis-hiring-portal-monish`)
- Click **"Permissions"** tab
- Scroll down to **"Bucket policy"** section
- Click **"Edit"** button
- Paste this policy (replace `YOUR-BUCKET-NAME` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

**Example** (if your bucket is `invensis-hiring-portal-monish`):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::invensis-hiring-portal-monish/*"
        }
    ]
}
```

- Click **"Save changes"**

✅ **Bucket is now configured!**

---

## Step 3: Create IAM User and Get Access Keys

### 3.1 Navigate to IAM
- In the AWS Console search bar, type **"IAM"**
- Click on **"IAM"** (Manage access to AWS resources)

### 3.2 Create User
- In left sidebar, click **"Users"**
- Click orange **"Create user"** button

### 3.3 User Details
- **User name**: `invensis-s3-uploader`
- Click **"Next"**

### 3.4 Set Permissions
- Select **"Attach policies directly"**
- In the search box, type: **"AmazonS3FullAccess"**
- Check the box next to **"AmazonS3FullAccess"**
- Click **"Next"**

### 3.5 Review and Create
- Review the settings
- Click **"Create user"**

### 3.6 Create Access Keys
- Click on the user name **"invensis-s3-uploader"**
- Click **"Security credentials"** tab
- Scroll to **"Access keys"** section
- Click **"Create access key"**

### 3.7 Select Use Case
- Select **"Application running outside AWS"**
- Check the confirmation box at bottom
- Click **"Next"**

### 3.8 Description (Optional)
- Description tag: `Invensis Hiring Portal`
- Click **"Create access key"**

### 3.9 **SAVE YOUR KEYS!** ⚠️
You'll see a screen with:

```
Access key ID: AKIA2XXXXXXXXXX
Secret access key: wJalrXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ CRITICAL**: Copy both keys NOW! The secret key is only shown once!

**Option 1**: Click **"Download .csv file"** (recommended)
**Option 2**: Copy and paste both keys to a safe place

✅ **Keys obtained!**

---

## Step 4: Add Keys to Render

### 4.1 Go to Render Dashboard
- Open: https://dashboard.render.com/
- Login to your account

### 4.2 Select Your Service
- Click on your web service: **"invensis-requiter"** (or your service name)

### 4.3 Add Environment Variables
- Click **"Environment"** in the left sidebar
- Click **"Add Environment Variable"** button
- Add these 4 variables one by one:

**Variable 1:**
- Key: `AWS_ACCESS_KEY_ID`
- Value: `AKIA2XXXXXXXXXX` (your actual Access Key ID)

**Variable 2:**
- Key: `AWS_SECRET_ACCESS_KEY`
- Value: `wJalrXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` (your actual Secret Access Key)

**Variable 3:**
- Key: `AWS_S3_BUCKET_NAME`
- Value: `invensis-hiring-portal-monish` (your actual bucket name)

**Variable 4:**
- Key: `AWS_S3_REGION`
- Value: `us-east-1` (or your chosen region)

- Click **"Save Changes"** button

⚠️ **Note**: Render will automatically redeploy after saving environment variables

✅ **Environment variables configured!**

---

## Step 5: Add Keys to Local .env File

Open your `.env` file and add these lines:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=AKIA2XXXXXXXXXX
AWS_SECRET_ACCESS_KEY=wJalrXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
AWS_S3_BUCKET_NAME=invensis-hiring-portal-monish
AWS_S3_REGION=us-east-1
```

Replace with your actual values!

---

## ✅ Verification Checklist

Before proceeding, make sure you have:

- [ ] AWS account created
- [ ] S3 bucket created (name: `invensis-hiring-portal-XXXX`)
- [ ] Bucket policy configured (files are publicly readable)
- [ ] IAM user created (`invensis-s3-uploader`)
- [ ] Access keys generated and saved
- [ ] Environment variables added to Render
- [ ] Keys added to local `.env` file

---

## 🆘 Common Issues

### "Bucket name already exists"
- Bucket names must be globally unique
- Add your name or company name: `invensis-hiring-portal-monish`

### "Access Denied" errors
- Make sure bucket policy is configured correctly
- Check that IAM user has `AmazonS3FullAccess` policy

### "Can't find IAM in console"
- Use the search bar at top: type "IAM"
- Or go directly to: https://console.aws.amazon.com/iam/

### "Lost my secret access key"
- You can't retrieve it again
- Delete the old access key and create a new one
- Go to IAM → Users → invensis-s3-uploader → Security credentials → Create access key

---

## 📞 Need Help?

If you get stuck at any step, tell me:
1. Which step you're on
2. What error message you see (if any)
3. Screenshot of the issue (if possible)

And I'll help you through it!

---

## ⏭️ Next Steps

Once you complete all steps above, tell me:
1. ✅ "AWS setup complete"
2. Share your bucket name (e.g., `invensis-hiring-portal-monish`)
3. Confirm environment variables are in Render

Then I'll integrate S3 into your application and all resume uploads will work permanently! 🚀

