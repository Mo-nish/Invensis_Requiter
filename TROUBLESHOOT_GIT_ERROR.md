# Troubleshoot "Failed to connect to repository" Error

## 🔴 Current Status:
- ✅ Credential is selected: `Mo-nish/****** (GitHub credentials)`
- ❌ Still getting error: `Failed to connect to repository : Error performing git command: git.exe ls-remote -h https://github.com/Mo-nish/Invensis_Requiter.git HEAD`

---

## 🔍 Step-by-Step Troubleshooting

### TEST 1: Verify Repository Exists and is Accessible

1. **Open a new browser tab**
2. **Go to**: `https://github.com/Mo-nish/Invensis_Requiter`
3. **Check**:
   - ✅ Does the repository exist? (Does it load?)
   - ✅ Can you see the code/files?
   - ❌ If it says "404 Not Found" → Repository doesn't exist or wrong name
   - ❌ If it asks you to log in → Repository is private and needs credentials

**If repository doesn't exist:**
- Check the exact repository name (might be `Invensis_Recruiter` instead of `Invensis_Requiter`)
- Go to your GitHub profile → Repositories → Find the correct name

---

### TEST 2: Verify Your GitHub Token Works

1. **Test the token manually using Command Prompt/PowerShell:**

#### Windows PowerShell:
```powershell
# Replace YOUR_TOKEN with your actual GitHub token (ghp_xxxxx)
$token = "YOUR_TOKEN"
$repo = "Mo-nish/Invensis_Requiter"
$headers = @{Authorization = "token $token"}
$url = "https://api.github.com/repos/$repo"

# Test if token can access the repo
Invoke-RestMethod -Uri $url -Headers $headers
```

#### Or use Git command:
```powershell
# First, set up git with your token
git config --global credential.helper store

# Try to clone (it will ask for username/password)
git ls-remote https://github.com/Mo-nish/Invensis_Requiter.git HEAD
# When prompted:
# Username: Mo-nish
# Password: paste your token (ghp_xxxxx)
```

**Expected Result:**
- ✅ Success: You see commit hash and branch info
- ❌ Failure: "Authentication failed" or "Repository not found"

---

### TEST 3: Check Token Permissions

1. **Go to**: https://github.com/settings/tokens
2. **Find your token** (the one you created for Jenkins)
3. **Check**:
   - ✅ Does it have **"repo"** scope checked?
   - ❌ If not, you need a new token with `repo` permission

4. **If token is missing or wrong permissions:**
   - Create a NEW token:
     - Go to: https://github.com/settings/tokens/new
     - Name: `Jenkins-Invensis-New`
     - Expiration: Choose appropriate time
     - **Check ✅ `repo`** (this gives full access to repositories)
     - Click "Generate token"
     - **Copy the new token immediately** (starts with `ghp_`)

5. **Update credential in Jenkins:**
   - Go to: **Manage Jenkins** → **Credentials** → **System** → **Global**
   - Find your credential (`Mo-nish/******`)
   - Click on it → Click **Update** (or create new one)
   - Replace the Password with your NEW token
   - Click **Save**

---

### TEST 4: Verify Repository URL Spelling

**Check for typos in the repository name:**

- Current URL in Jenkins: `https://github.com/Mo-nish/Invensis_Requiter.git`
- Possible correct names:
  - `Invensis_Recruiter` (with 'c')
  - `Invensis_Requiter` (with 'q') ← Current one
  - `invensis_requiter` (lowercase)
  - `Invensis` (different name)

**To find the correct name:**
1. Go to: https://github.com/Mo-nish?tab=repositories
2. Look at your repository list
3. Copy the EXACT name (case-sensitive!)

---

### TEST 5: Test Git Command in Jenkins Machine

**If Jenkins is running on your local Windows machine:**

1. **Open Command Prompt or PowerShell**
2. **Navigate to a test folder:**
   ```powershell
   cd C:\temp
   mkdir jenkins-test
   cd jenkins-test
   ```

3. **Test the git command that Jenkins is trying:**
   ```powershell
   git.exe ls-remote -h https://github.com/Mo-nish/Invensis_Requiter.git HEAD
   ```

4. **If it prompts for credentials:**
   - Username: `Mo-nish`
   - Password: Your GitHub token (not your GitHub password!)

5. **Results:**
   - ✅ Success: Shows commit hash → The command works, issue is in Jenkins credential
   - ❌ "Authentication failed": Token is wrong or expired
   - ❌ "Repository not found": Wrong repository name or doesn't exist
   - ❌ "Could not resolve host": Network/firewall issue

---

### TEST 6: Update Jenkins Credential with Correct Information

**If you found issues in tests above, update the credential:**

1. **In Jenkins**: **Manage Jenkins** → **Credentials** → **System** → **Global**
2. **Find**: Your GitHub credential (`Mo-nish/******` or `github-invensis`)
3. **Click on it** → Click **Update** (or create a new one)

4. **Double-check:**
   - **Kind**: `Username with password`
   - **Username**: `Mo-nish` (exact match, case-sensitive)
   - **Password**: Your GitHub token (should start with `ghp_`)
     - ⚠️ **NOT your GitHub password!** Must be a Personal Access Token
   - **ID**: `github-invensis` (or any name)

5. **Click Save**

6. **Go back to pipeline config:**
   - Remove and re-add the credential (or select it again from dropdown)
   - Wait for Jenkins to re-test the connection

---

## 🔧 Common Fixes

### Fix 1: Token Expired or Wrong
- **Solution**: Create a new token and update the credential

### Fix 2: Token Missing "repo" Scope
- **Solution**: Create a new token with ✅ `repo` checkbox checked

### Fix 3: Wrong Repository Name
- **Solution**: Check GitHub and use the exact repository name (case-sensitive)

### Fix 4: Using GitHub Password Instead of Token
- **Solution**: Must use Personal Access Token (starts with `ghp_`), not your GitHub password

### Fix 5: Username Mismatch
- **Solution**: Username in credential must match exactly: `Mo-nish` (with hyphen)

---

## 📋 Action Items - Do These Now:

1. [ ] **Verify repository exists**: Visit `https://github.com/Mo-nish/Invensis_Requiter`
2. [ ] **Check token permissions**: Go to https://github.com/settings/tokens
3. [ ] **Test git command manually**: Run `git ls-remote` in PowerShell
4. [ ] **Create new token if needed**: With `repo` scope
5. [ ] **Update credential in Jenkins**: With correct token
6. [ ] **Retest in pipeline config**: Wait for error to clear

---

## 💡 Quick Test Command

**Run this in PowerShell to test everything at once:**

```powershell
# Replace with your actual token
$token = "ghp_YOUR_TOKEN_HERE"
$repo = "Mo-nish/Invensis_Requiter"

# Test API access
$headers = @{Authorization = "token $token"}
try {
    $result = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo" -Headers $headers
    Write-Host "✅ SUCCESS: Repository found!" -ForegroundColor Green
    Write-Host "Repository: $($result.full_name)"
    Write-Host "Private: $($result.private)"
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "→ Authentication failed - Check your token!" -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "→ Repository not found - Check repository name!" -ForegroundColor Yellow
    }
}
```

---

**Try these tests and let me know what you find!**
