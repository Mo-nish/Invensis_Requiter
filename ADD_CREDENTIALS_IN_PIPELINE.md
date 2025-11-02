# Add GitHub Credentials Directly in Pipeline Form

## 🔴 Current Problem:
- Repository URL is correct: `https://github.com/Mo-nish/Invensis_Requiter.git`
- Credentials dropdown shows: `- none -`
- Error: "Failed to connect to repository"

## ✅ Solution: Add Credential Right in This Form

### STEP 1: Click the "+ Add" Button
1. **Look at the "Credentials" section** in your pipeline configuration
2. You should see a dropdown that says "- none -"
3. **To the RIGHT of that dropdown**, you'll see a button: **"+ Add"**
4. **Click that "+ Add" button**

---

### STEP 2: Fill in the Credential Form

After clicking "+ Add", a small form will appear. Fill it in:

1. **Kind**: Select `Username with password` from dropdown

2. **Username**: 
   - Enter: `Mo-nish` (your GitHub username)

3. **Password**: 
   - **This is your GitHub Personal Access Token (PAT)**
   - If you don't have one yet:
     - Go to: https://github.com/settings/tokens
     - Click "Generate new token" → "Generate new token (classic)"
     - Name: `Jenkins`
     - Check ✅ **repo** checkbox
     - Click "Generate token"
     - Copy the token (starts with `ghp_`)
   - Paste the token in the Password field

4. **ID**: 
   - Enter: `github-invensis` (lowercase, with hyphen)

5. **Description**: 
   - Enter: `GitHub token for Invensis_Requiter`

6. **Click "Add"** (or "Create" button at bottom)

---

### STEP 3: Select the Credential

1. **After adding the credential**, you'll be back at the main form
2. **Click on the "Credentials" dropdown** (where it says "- none -")
3. **Select**: `github-invensis` (the credential you just created)
4. **Wait 2-3 seconds** - Jenkins will automatically test the connection
5. **The red error should disappear** ✅

---

### STEP 4: Complete the Form

1. **Branch Specifier**: 
   - Enter: `*/main` (or `*/master` if that's your branch)

2. **Script Path**: 
   - Enter: `Documents/Invensis/Jenkinsfile`

3. **Click "Save"** at the bottom

---

## 🔍 Troubleshooting

### If you don't see the "+ Add" button:
- Scroll the page to make sure you can see the entire "Credentials" section
- The button should be to the RIGHT of the dropdown

### If the error persists after adding credentials:
1. **Double-check your GitHub token**:
   - Go to: https://github.com/settings/tokens
   - Make sure the token exists and has `repo` scope
   - If expired or missing, create a new one

2. **Verify repository access**:
   - Open a new browser tab
   - Try: https://github.com/Mo-nish/Invensis_Requiter
   - If it asks you to log in, the repo is private and needs credentials
   - If it opens without login, repo is public (might not need credentials, but try anyway)

3. **Test git command manually**:
   - Open Command Prompt or PowerShell
   - Try: `git ls-remote https://github.com/Mo-nish/Invensis_Requiter.git HEAD`
   - If this fails, Jenkins will fail too

### If the dropdown doesn't show your credential:
1. Make sure you clicked "Add" (or "Create") after filling the credential form
2. Try refreshing the page (F5)
3. Go to: **Manage Jenkins** → **Credentials** → **System** → **Global**
4. Check if `github-invensis` appears there
5. If not, create it there first, then go back to pipeline config

---

## 📋 Quick Visual Guide

```
┌─────────────────────────────────────────┐
│ Repository URL                          │
│ [https://github.com/Mo-nish/...] ✅     │
│                                         │
│ ❌ Error: Failed to connect...          │
│                                         │
│ Credentials ?                           │
│ [- none - ▼] [+ Add]  ← CLICK THIS!    │
└─────────────────────────────────────────┘
```

After clicking "+ Add", you'll see a form:

```
┌─────────────────────────────────────────┐
│ Add Credentials                         │
│                                         │
│ Kind: [Username with password ▼]       │
│ Username: [Mo-nish]                    │
│ Password: [ghp_xxxxxxxxxxxxx]          │
│ ID: [github-invensis]                  │
│ Description: [GitHub token...]         │
│                                         │
│ [Add] [Cancel]                         │
└─────────────────────────────────────────┘
```

---

**Try this now and let me know if the error disappears after selecting the credential!**
