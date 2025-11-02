# Fix GitHub Repository Connection Error in Jenkins

## ❌ Error You're Seeing:
```
Failed to connect to repository : Error performing git command: git.exe ls-remote -h https://github.com/Mo-nish/Invensis_Requiter.git HEAD
```

## ✅ Solution: Add GitHub Credentials

Your repository likely requires authentication. Follow these steps:

---

## STEP 1: Create GitHub Personal Access Token (PAT)

### 1.1 Generate Token on GitHub:
1. Go to GitHub.com and log in
2. Click your profile picture (top right) → **Settings**
3. Scroll down → Click **Developer settings** (bottom left)
4. Click **Personal access tokens** → **Tokens (classic)**
5. Click **Generate new token** → **Generate new token (classic)**
6. Fill in:
   - **Note**: `Jenkins-Invensis` (any name)
   - **Expiration**: Choose 90 days or No expiration
   - **Select scopes**: Check ✅ **repo** (this gives full access to repositories)
7. Click **Generate token** (at bottom)
8. **IMPORTANT**: Copy the token immediately (it starts with `ghp_` and you won't see it again!)
   - Example: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## STEP 2: Add Credentials in Jenkins

### 2.1 Create GitHub Credential:
1. In Jenkins, go to: **Manage Jenkins** → **Credentials**
2. Click **System** → **Global credentials (unrestricted)**
3. Click **Add Credentials**
4. Fill in the form:
   - **Kind**: Select `Username with password`
   - **Username**: Enter your GitHub username: `Mo-nish`
   - **Password**: Paste your GitHub token (the `ghp_xxxxxxxx` token you just created)
   - **ID**: `github-invensis` (lowercase with hyphens)
   - **Description**: `GitHub credentials for Invensis_Requiter repository`
5. Click **Create**

---

## STEP 3: Use Credentials in Pipeline Job

### 3.1 Go Back to Your Pipeline Configuration:
1. Go to your **Invensis-Pipeline** job
2. Click **Configure** (left sidebar)
3. Scroll to **Pipeline** section
4. In **Repository URL** field:
   - URL: `https://github.com/Mo-nish/Invensis_Requiter.git` ✅ (you already have this)
5. In **Credentials** dropdown:
   - Select: `github-invensis` (the credential you just created)
6. In **Branch Specifier**:
   - Enter: `*/main` or `*/master`
7. In **Script Path**:
   - Enter: `Documents/Invensis/Jenkinsfile` (because your Jenkinsfile is in the Documents/Invensis folder)
8. Click **Save**

---

## STEP 4: Test the Connection

### 4.1 Verify Connection:
1. After clicking **Save**, Jenkins will automatically test the connection
2. The red ❌ error should disappear
3. You should see a ✅ checkmark or no error

### 4.2 Run Build:
1. Click **Build Now** to test
2. Check **Console Output** to see if it successfully checks out the code

---

## 🔍 Alternative: If Repository is Public

If your repository is **public** and you still get this error:

### Check 1: Verify Repository Visibility
1. Go to: https://github.com/Mo-nish/Invensis_Requiter
2. Click **Settings** tab (if you see it, repo is private)
3. If repo is private, you MUST use credentials (follow steps above)

### Check 2: Test Git Access
1. Open Command Prompt or PowerShell
2. Try: `git ls-remote https://github.com/Mo-nish/Invensis_Requiter.git HEAD`
3. If this fails on your computer, it will fail in Jenkins too

---

## 📋 Quick Checklist

- [ ] Created GitHub Personal Access Token (PAT) with `repo` scope
- [ ] Added credential in Jenkins (Username: `Mo-nish`, Password: your PAT token)
- [ ] Credential ID: `github-invensis`
- [ ] Selected credential in Pipeline job configuration
- [ ] Script Path: `Documents/Invensis/Jenkinsfile`
- [ ] Clicked Save and verified no error

---

## ⚠️ Common Issues

**Issue**: "Invalid credentials"
- **Fix**: Make sure you pasted the entire token (starts with `ghp_`)

**Issue**: "Repository not found"
- **Fix**: Verify the repository name is correct: `Invensis_Requiter` (not `Invensis_Recruiter`)

**Issue**: Still seeing error after adding credentials
- **Fix**: Make sure you selected the credential in the dropdown (not "- none -")

---

**Need Help?** 
- If still having issues, check the Jenkins Console Output for more detailed error messages
