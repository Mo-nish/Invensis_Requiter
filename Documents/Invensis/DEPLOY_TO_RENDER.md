# ⚡ Quick Deploy to Render

## 🚀 **One-Click Deployment**

Your Invensis Hiring Portal is ready for Render deployment!

### **Repository**: https://github.com/Mo-nish/Invensis_Requiter

---

## 🎯 **Deployment Steps**

### **1. Go to Render**
👉 [render.com](https://render.com)

### **2. Create Web Service**
- Click **"New +"** → **"Web Service"**
- Connect: `Mo-nish/Invensis_Requiter`
- Name: `invensis-hiring-portal`

### **3. Configure Service**
```yaml
Environment: Python 3
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python run.py
Instance: Starter (Free)
```

### **4. Set Environment Variables**
```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/invensis
DEFAULT_ADMIN_EMAIL=admin@invensis.com
DEFAULT_ADMIN_PASSWORD=InvensisAdmin2025!
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
BASE_URL=https://invensis-hiring-portal.onrender.com
```

### **5. Deploy!**
- Click **"Create Web Service"**
- Wait 5-10 minutes
- Your app will be live!

---

## 🔗 **After Deployment**

### **Your App URLs**
- **Main**: `https://invensis-hiring-portal.onrender.com`
- **Admin**: `https://invensis-hiring-portal.onrender.com/admin/login`

### **Login Credentials**
- **Admin**: `admin@invensis.com` / `InvensisAdmin2025!`
- **HR**: `p.monishreddy19@gmail.com` / `Monish@007`

---

## 📚 **Detailed Guides**
- **Complete Guide**: `COMPLETE_RENDER_GUIDE.md`
- **MongoDB Setup**: `MONGODB_ATLAS_SETUP.md`
- **Render Config**: `RENDER_DEPLOYMENT.md`

---

**🎉 Ready to deploy! Your hiring portal will be live in minutes!**
