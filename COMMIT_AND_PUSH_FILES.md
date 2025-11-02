# How to Commit and Push Jenkinsfile to GitHub

## 📁 Current Situation:
- ✅ `Jenkinsfile` exists in: `C:\Users\Monish\Downloads\Invensis`
- ✅ `sonar-project.properties` exists in: `C:\Users\Monish\Downloads\Invensis`
- ❌ This folder is NOT a git repository
- ⚠️ Jenkins expects `Jenkinsfile` at: `Documents/Invensis/Jenkinsfile` in the repo

---

## 🎯 Method 1: Using GitHub Web Interface (Easiest - No Git Needed!)

### Step 1: Upload Files Directly to GitHub
1. **Go to your repository**: https://github.com/Mo-nish/Invensis_Requiter
2. **Navigate to the correct folder**: Click on `Documents` → `Invensis`
3. **Click "Add file"** → **"Upload files"**
4. **Drag and drop** both files:
   - `Jenkinsfile`
   - `sonar-project.properties`
5. **Scroll down** → Enter commit message:
   ```
   Add Jenkinsfile and SonarQube config for CI/CD pipeline
   ```
6. **Click "Commit changes"** (green button)

✅ **Done!** Files are now in your repository.

---

## 🎯 Method 2: Clone Repository, Copy Files, Then Push

### Step 1: Find Your Repository Location
If you already have the repository cloned somewhere:
- It might be in: `C:\Users\Monish\Documents\GitHub\Invensis_Requiter`
- Or check: GitHub Desktop → Repository → Show in Explorer

### Step 2: Copy Files to Repository
1. **Copy these files:**
   - From: `C:\Users\Monish\Downloads\Invensis\Jenkinsfile`
   - To: `[Your Repo Path]\Documents\Invensis\Jenkinsfile`
   
   - From: `C:\Users\Monish\Downloads\Invensis\sonar-project.properties`
   - To: `[Your Repo Path]\Documents\Invensis\sonar-project.properties`

### Step 3: Commit and Push
**Using GitHub Desktop:**
1. Open GitHub Desktop
2. Select `Invensis_Requiter` repository
3. You should see the new files in "Changes"
4. Enter commit message: `Add Jenkinsfile and SonarQube config for CI/CD pipeline`
5. Click "Commit to main"
6. Click "Push origin"

**OR Using VS Code:**
1. Open VS Code in your repository folder
2. Open Source Control (Ctrl+Shift+G)
3. Stage the files
4. Commit with message: `Add Jenkinsfile and SonarQube config for CI/CD pipeline`
5. Click "Push"

---

## 🎯 Method 3: Clone Fresh, Add Files, Push

### Step 1: Clone Repository (if not already cloned)
**If you have Git installed:**
```powershell
cd C:\Users\Monish\Documents
git clone https://github.com/Mo-nish/Invensis_Requiter.git
cd Invensis_Requiter
```

**OR using GitHub Desktop:**
1. Open GitHub Desktop
2. File → Clone repository
3. Select `Invensis_Requiter`
4. Choose location and clone

### Step 2: Copy Files
1. **Copy** `Jenkinsfile` from `C:\Users\Monish\Downloads\Invensis\`
2. **Paste** to: `[Clone Location]\Documents\Invensis\Jenkinsfile`

3. **Copy** `sonar-project.properties` from `C:\Users\Monish\Downloads\Invensis\`
4. **Paste** to: `[Clone Location]\Documents\Invensis\sonar-project.properties`

### Step 3: Commit and Push
Use GitHub Desktop or VS Code as described in Method 2.

---

## ⚠️ Important Notes:

### File Location in Repository:
- ✅ **Correct location**: `Documents/Invensis/Jenkinsfile`
- ✅ **Correct location**: `Documents/Invensis/sonar-project.properties`
- ❌ **Wrong location**: Root folder `/Jenkinsfile`

This matches your Jenkins pipeline configuration where Script Path is set to: `Documents/Invensis/Jenkinsfile`

---

## ✅ After Pushing - Verify:

1. **Go to GitHub**: https://github.com/Mo-nish/Invensis_Requiter
2. **Navigate to**: `Documents` → `Invensis`
3. **Verify files exist**:
   - ✅ `Jenkinsfile`
   - ✅ `sonar-project.properties`

4. **Go back to Jenkins** → Your pipeline job → **Build Now**
5. **Check Console Output**:
   - Should successfully checkout code
   - Should find `Documents/Invensis/Jenkinsfile`
   - Should start running the pipeline!

---

## 🚀 Quick Summary:

**Recommended: Method 1 (GitHub Web Interface)**
- Fastest and easiest
- No Git installation needed
- No command line needed
- Just upload the files directly

**If you prefer desktop tools:**
- Use GitHub Desktop (easiest GUI)
- Or VS Code Git integration

---

**Which method would you like to use? Let me know when the files are pushed, and we can test the Jenkins pipeline!**
