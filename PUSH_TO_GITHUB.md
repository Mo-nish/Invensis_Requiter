# Push Changes to GitHub - Step by Step

## 📝 Files to Commit:

### Main Files (Must Push):
1. ✅ **Jenkinsfile** (root directory) - Fixed CI/CD pipeline
2. ✅ **Documents/Invensis/Jenkinsfile** (if different) - Ensure this one is correct
3. ✅ **sonar-project.properties** - SonarQube configuration
4. ✅ **verify_imports.py** - Fixed to use assertions
5. ✅ **test_reset_password_flow.py** - Fixed to use assertions
6. ✅ **test_forgot_password.py** - Fixed to use assertions

### Documentation Files (Optional):
- JENKINS_FIXES.md
- FIXED_TEST_FILES.md
- JENKINS_SONARQUBE_SETUP.md

---

## 🚀 Method 1: Using GitHub Desktop (Easiest)

### Steps:

1. **Open GitHub Desktop**
2. **Select your repository**: `Invensis_Requiter`
3. **Check the changes**:
   - You should see modified files listed
   - Look for `Jenkinsfile` and test files

4. **Stage files**:
   - Check the boxes next to:
     - `Jenkinsfile`
     - `test_reset_password_flow.py`
     - `test_forgot_password.py`
     - `verify_imports.py`
     - `sonar-project.properties`
   - Or click "Select All" if you want to push everything

5. **Write commit message**:
   ```
   Fix CI/CD pipeline: Update Jenkinsfile and fix pytest warnings
   
   - Fix Flask startup in Jenkins pipeline
   - Separate unit and integration tests
   - Fix test functions to use assertions instead of return values
   - Add SonarQube integration
   - Improve error handling for Flask-dependent tests
   ```

6. **Click "Commit to main"** (bottom left)

7. **Click "Push origin"** (top right, or in the toolbar)

8. **Done!** ✅ Changes are now on GitHub

---

## 🚀 Method 2: Using VS Code

### Steps:

1. **Open VS Code** in your project folder: `C:\Users\Monish\Downloads\Invensis`

2. **Open Source Control** (Ctrl+Shift+G)

3. **Stage files**:
   - Click the "+" next to files you want to commit:
     - `Jenkinsfile`
     - `test_reset_password_flow.py`
     - `test_forgot_password.py`
     - `verify_imports.py`
     - `sonar-project.properties`

4. **Write commit message** in the box at the top:
   ```
   Fix CI/CD pipeline: Update Jenkinsfile and fix pytest warnings
   
   - Fix Flask startup in Jenkins pipeline
   - Separate unit and integration tests
   - Fix test functions to use assertions instead of return values
   - Add SonarQube integration
   ```

5. **Click the checkmark** (✓) to commit

6. **Click "Sync Changes"** or the up arrow (↑) to push

7. **Done!** ✅

---

## 🚀 Method 3: Using GitHub Web Interface

If you can't use desktop tools, upload files directly:

### Steps:

1. **Go to your repository**: https://github.com/Mo-nish/Invensis_Requiter

2. **For each file you need to update**:
   - Navigate to the file location
   - Click the **pencil icon** (✏️) to edit
   - Copy the entire content from your local file
   - Paste it in GitHub's editor
   - Click **"Commit changes"**
   - Write commit message: `Fix CI/CD pipeline and pytest warnings`

3. **Important files to update**:
   - If `Jenkinsfile` is in root → Update it
   - If `Jenkinsfile` should be in `Documents/Invensis/` → Navigate there and update
   - Update test files in `Documents/Invensis/`

---

## ✅ Verify Push Was Successful:

1. **Go to GitHub**: https://github.com/Mo-nish/Invensis_Requiter
2. **Check latest commit** - should see your commit message
3. **Open Jenkinsfile** - verify it has the updated content
4. **Go to Jenkins** - trigger a new build

---

## 🎯 What Happens After Push:

1. **Jenkins will detect the change** (if webhook is set up)
2. **Or manually trigger build** in Jenkins:
   - Go to your pipeline job
   - Click "Build Now"
3. **Build should now**:
   - ✅ Run unit tests successfully
   - ⚠️ Handle Flask startup gracefully
   - ✅ Generate coverage report
   - ✅ Run SonarQube analysis

---

## 📋 Quick Checklist:

- [ ] Jenkinsfile updated and in correct location
- [ ] Test files fixed (using assertions)
- [ ] Files committed with descriptive message
- [ ] Changes pushed to GitHub
- [ ] Verify on GitHub that files are updated
- [ ] Trigger new Jenkins build

---

**Need Help?** If you're having trouble, tell me which method you're using and I can guide you through it!
