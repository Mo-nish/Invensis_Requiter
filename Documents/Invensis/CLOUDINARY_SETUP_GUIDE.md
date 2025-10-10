# Cloudinary Setup Guide - Simple & Free!

## 🎉 Why Cloudinary?
- ✅ **100% FREE** for your use case (25GB storage, 25GB bandwidth)
- ✅ **Super easy** to set up (5 minutes!)
- ✅ **No credit card** required for free tier
- ✅ **Perfect for resumes and images**

---

## 📝 Step-by-Step Setup (5 Minutes)

### **Step 1: Create Cloudinary Account**

1. **Go to**: https://cloudinary.com/users/register_free
2. Fill in the form:
   - **Email**: `p.monishreddy99@gmail.com` (or your email)
   - **Password**: Create a password
   - **Cloud name**: `invensis-portal` (or any name you like)
     - ⚠️ **Write this down - you'll need it!**
   - Check "I agree to the Terms of Service"
3. Click **"Create account"**
4. Check your email and verify your account

### **Step 2: Get Your API Credentials**

1. After email verification, you'll be taken to the dashboard
2. Look for **"Account Details"** or **"Dashboard"** section
3. You'll see these 3 values:

```
Cloud name: invensis-portal
API Key: 123456789012345
API Secret: AbCdEfGhIjKlMnOpQrStUvWxYz
```

**⚠️ SAVE THESE!** Copy them to a text file.

**Alternative way to find them:**
- Click your profile icon (top right)
- Click **"Settings"**
- Click **"Access Keys"** tab
- You'll see all your credentials there

### **Step 3: Add to Render Environment Variables**

1. Go to: https://dashboard.render.com/
2. Click on your service: **"invensis-requiter"**
3. Click **"Environment"** tab
4. Click **"Add Environment Variable"**
5. Add these 3 variables:

```
CLOUDINARY_CLOUD_NAME=invensis-portal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=AbCdEfGhIjKlMnOpQrStUvWxYz
```

6. Click **"Save Changes"**

### **Step 4: Add to Local .env File**

Open your `.env` file and add:

```bash
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=invensis-portal
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=AbCdEfGhIjKlMnOpQrStUvWxYz
```

---

## ✅ That's It!

**What you get FREE:**
- 25 GB storage
- 25 GB bandwidth per month
- 25,000 transformations per month
- Unlimited uploads

**Perfect for your hiring portal!**

---

## 📋 What to Send Me

Once you complete the signup, send me your 3 credentials:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**Or just tell me**: "Done! Cloud name is `invensis-portal`" and confirm you added them to Render.

Then I'll integrate Cloudinary into your app immediately! 🚀

---

## 🆘 Need Help?

**Can't find your credentials?**
- Go to: https://cloudinary.com/console
- Click **"Settings"** (gear icon)
- Click **"Access Keys"** tab

**Forgot your cloud name?**
- It's in the URL: `https://console.cloudinary.com/console/{cloud_name}/`
- Or in Settings → Account → Cloud name

Ready to start? The signup takes only 2-3 minutes! 🎉

