# Fix Jenkins Credential with Your GitHub Token

## ✅ What We Know:
- Repository exists: `https://github.com/Mo-nish/Invensis_Requiter`
- Your GitHub token: `YOUR_TOKEN_HERE` (replace with your actual token)
- Token has `repo` scope ✅
- Still getting connection error in Jenkins

## 🔧 Solution: Update Jenkins Credential

The issue is likely that Jenkins credential doesn't have the correct token, or there's a mismatch. Let's fix it:

---

### STEP 1: Copy Your Token

Your token should start with **`ghp_`** followed by your token characters

**Copy this entire token** (you'll need it in the next step)

---

### STEP 2: Update Jenkins Credential

1. **In Jenkins, go to:**
   - **Manage Jenkins** → **Credentials**
   - **System** → **Global credentials (unrestricted)**

2. **Find your GitHub credential:**
   - Look for: `Mo-nish/******` or `github-invensis`
   - **Click on it** to edit

3. **Update the credential:**
   - **Kind**: Should be `Username with password`
   - **Username**: `Mo-nish` (exact match)
   - **Password**: **Delete the old value** and paste your token (it should start with `ghp_`)
   - **ID**: `github-invensis` (or whatever you named it)
   - **Description**: `GitHub token for Invensis_Requiter`

4. **Click "Update"** (or "Save")

---

### STEP 3: Go Back to Pipeline Config

1. **Go to your pipeline job:**
   - **Jenkins Dashboard** → **Invensis-Pipeline** → **Configure**

2. **In the Pipeline section:**
   - **Repository URL**: Should be `https://github.com/Mo-nish/Invensis_Requiter.git`
   - **Credentials dropdown**: Select `Mo-nish/****** (github-invensis)` 
     - If it's not selected, select it from the dropdown
   - **Branch Specifier**: `*/main`
   - **Script Path**: `Documents/Invensis/Jenkinsfile`

3. **Wait 3-5 seconds** after selecting the credential
   - Jenkins will automatically test the connection
   - The red error should disappear ✅

4. **Click "Save"**

---

### STEP 4: Verify It Works

1. **After saving**, go back to your job page
2. **Click "Build Now"**
3. **Watch the Console Output:**
   - Should see "Checking out code..."
   - Should successfully clone the repository
   - No authentication errors ✅

---

## 🔍 Alternative: Create Fresh Credential

If updating doesn't work, create a completely new credential:

1. **Manage Jenkins** → **Credentials** → **System** → **Global**
2. **Click "Add Credentials"**
3. Fill in:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: `Mo-nish`
   - **Password**: `YOUR_TOKEN_HERE` (paste your actual GitHub token)
   - **ID**: `github-invensis-new`
   - **Description**: `GitHub token for Jenkins`
4. **Click "Create"**
5. **Go back to pipeline config** → Select `github-invensis-new` from dropdown
6. **Save**

---

## ⚠️ Common Issues

**Issue**: "Authentication failed" still appears
- **Fix**: Make sure you copied the ENTIRE token (all characters)
- **Fix**: Make sure there are no extra spaces before/after the token
- **Fix**: Token should start with `ghp_` and be about 40 characters long

**Issue**: Dropdown doesn't show the credential
- **Fix**: Refresh the page (F5) and try again
- **Fix**: Create a new credential with a different ID

**Issue**: Error persists even with correct token
- **Fix**: Check if repository is actually accessible:
  - Try accessing: `https://github.com/Mo-nish/Invensis_Requiter` (should load)
  - Make sure you're logged into GitHub with the account that owns the repo

---

## ✅ Quick Checklist

- [ ] Token copied from GitHub (starts with `ghp_`)
- [ ] Credential updated in Jenkins with this exact token
- [ ] Username is exactly: `Mo-nish`
- [ ] Credential selected in pipeline config
- [ ] Waited 3-5 seconds for connection test
- [ ] Clicked "Save"
- [ ] Error disappeared ✅

---

**Try updating the credential now with the token above and let me know if it works!**
