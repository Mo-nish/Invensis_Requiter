# Complete Jenkins + SonarQube Setup Guide for Invensis Project

## ✅ Step 1: Add SonarQube Token Credential in Jenkins

### Problem Fix:
The ID field shows "Unacceptable characters" because Jenkins credential IDs must be:
- **Lowercase letters only**
- **Hyphens (-) or underscores (_) allowed**
- **No spaces, uppercase, or special characters**

### Solution:
1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **Credentials**
2. Click **System** → **Global credentials (unrestricted)**
3. Click **Add Credentials**
4. Fill in the form:
   - **Kind**: Select `Secret text`
   - **Secret**: Paste your SonarQube token: `sqp_3c0a4d26d7baadb4b3d6540b8aa01f4682e3312a`
   - **ID**: `sonarqube-token` (⚠️ **MUST be lowercase with hyphens**)
   - **Description**: `SonarQube PAT for Invensis project`
5. Click **Create**

---

## ✅ Step 2: Configure SonarQube Server in Jenkins

1. Go to **Jenkins Dashboard** → **Manage Jenkins** → **System**
2. Scroll down to **SonarQube servers** section
3. Click **Add SonarQube**
4. Fill in:
   - **Name**: `SonarQubeServer` (⚠️ **Must match exactly**)
   - **Server URL**: `http://localhost:9000` (or your SonarQube URL)
   - **Server authentication token**: Select `sonarqube-token` from dropdown
5. Click **Apply** → **Save**

---

## ✅ Step 3: Configure SonarQube Webhook (IMPORTANT!)

This is required for Quality Gate to work in Jenkins.

1. Open your **SonarQube** instance
2. Go to **Administration** (top menu) → **Configuration** → **Webhooks**
3. Click **Create**
4. Fill in:
   - **Name**: `Jenkins`
   - **URL**: `http://localhost:8080/sonarqube-webhook/` 
     - ⚠️ Replace `localhost:8080` with your Jenkins server URL
     - ⚠️ Must end with `/sonarqube-webhook/`
5. Click **Create**

---

## ✅ Step 4: Add GitHub Credential (For Private Repos)

**If your GitHub repo is private**, you need to add credentials:

### Option A: HTTPS (Easier)
1. Go to **Jenkins** → **Manage Jenkins** → **Credentials** → **System** → **Global**
2. Click **Add Credentials**
3. Fill in:
   - **Kind**: `Username with password`
   - **Username**: Your GitHub username
   - **Password**: Your GitHub Personal Access Token (PAT)
     - Generate at: https://github.com/settings/tokens
     - Required scopes: `repo` (full control of private repositories)
   - **ID**: `github-credentials` (lowercase with hyphens)
   - **Description**: `GitHub credentials for Invensis repo`
4. Click **Create**

### Option B: SSH (Alternative)
- Use **SSH Username with private key** kind instead
- Paste your private SSH key

---

## ✅ Step 5: Create Jenkins Pipeline Job

1. Go to **Jenkins Dashboard** → **New Item**
2. Enter item name: `Invensis-Pipeline`
3. Select **Pipeline** → Click **OK**
4. In **Pipeline** section:
   - **Definition**: Select `Pipeline script from SCM`
   - **SCM**: Select `Git`
   - **Repository URL**: Your GitHub repo URL
     - HTTPS: `https://github.com/yourusername/Invensis.git`
     - SSH: `git@github.com:yourusername/Invensis.git`
   - **Credentials**: Select your GitHub credential (if private repo)
   - **Branches to build**: `*/main` or `*/master` (your default branch)
   - **Script Path**: `Jenkinsfile` (must match your file name)
5. Click **Save**

---

## ✅ Step 6: Configure GitHub Webhook (Optional - Auto Build on Push)

1. Go to your **GitHub repository** → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Fill in:
   - **Payload URL**: `http://your-jenkins-url/github-webhook/`
     - Example: `http://localhost:8080/github-webhook/`
   - **Content type**: `application/json`
   - **Which events**: Select `Just the push event`
4. Click **Add webhook**

---

## ✅ Step 7: Run Your First Build

1. In Jenkins, go to your **Invensis-Pipeline** job
2. Click **Build Now**
3. Click on the build number (#1) in the left sidebar
4. Click **Console Output** to watch the build progress

### Expected Stages:
1. ✅ **Checkout** - Downloads code from GitHub
2. ✅ **Set up Python and deps** - Creates virtual environment, installs packages
3. ✅ **Run tests with coverage** - Runs pytest, generates `coverage.xml`
4. ✅ **SonarQube Analysis** - Runs `pysonar` scanner
5. ✅ **Quality Gate** - Waits for SonarQube to finish and check Quality Gate

---

## 🔍 Troubleshooting

### Issue: "Unacceptable characters" error
- **Solution**: Use lowercase with hyphens only in credential IDs
- ✅ Good: `sonarqube-token`, `github-credentials`, `invensis-project`
- ❌ Bad: `Invensis`, `sonar token`, `token_123!`

### Issue: "pysonar: command not found"
- **Solution**: The Jenkinsfile now installs `pysonar` automatically in the setup stage
- Check console output - it should show: `pip install pytest pytest-cov pysonar`

### Issue: "Quality Gate timeout" or "waitForQualityGate" hangs
- **Solution**: Make sure you created the SonarQube webhook (Step 3)
- Verify webhook URL is correct: `http://your-jenkins-url/sonarqube-webhook/`

### Issue: "SonarQubeServer not found"
- **Solution**: Verify the server name in Jenkins System settings matches exactly: `SonarQubeServer`
- Check that you added the SonarQube server in Step 2

### Issue: "Access denied" or "Authentication failed"
- **Solution**: Verify your SonarQube token is correct
- Check that token credential ID is `sonarqube-token`
- Verify token hasn't expired in SonarQube

### Issue: No coverage shown in SonarQube
- **Solution**: Check that `coverage.xml` is generated
- Verify `sonar-project.properties` has: `sonar.python.coverage.reportPaths=coverage.xml`
- Check that tests actually run and produce coverage

---

## 📋 Quick Checklist

- [ ] SonarQube token credential created (ID: `sonarqube-token`)
- [ ] SonarQube server added in Jenkins (Name: `SonarQubeServer`)
- [ ] SonarQube webhook created (URL: `http://jenkins-url/sonarqube-webhook/`)
- [ ] GitHub credential added (if private repo)
- [ ] Jenkins pipeline job created
- [ ] GitHub webhook added (optional, for auto-builds)
- [ ] First build executed successfully
- [ ] Quality Gate passed in SonarQube

---

## 🎯 Test Locally (Optional)

To test the scanner locally before running in Jenkins:

### Windows PowerShell:
```powershell
# Navigate to project
cd C:\Users\Monish\Downloads\Invensis

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pysonar

# Run tests with coverage
pytest -q --cov=. --cov-report=xml:coverage.xml

# Run SonarQube scanner
pysonar --sonar-host-url=http://localhost:9000 --sonar-token=sqp_3c0a4d26d7baadb4b3d6540b8aa01f4682e3312a --sonar-project-key=Invensis
```

### Linux/Mac:
```bash
# Navigate to project
cd /path/to/Invensis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pysonar

# Run tests with coverage
pytest -q --cov=. --cov-report=xml:coverage.xml

# Run SonarQube scanner
pysonar --sonar-host-url=http://localhost:9000 --sonar-token=sqp_3c0a4d26d7baadb4b3d6540b8aa01f4682e3312a --sonar-project-key=Invensis
```

---

## 📞 Next Steps After First Successful Build

1. **Review SonarQube Dashboard**: Go to your project in SonarQube to see code quality metrics
2. **Fix Issues**: Address any bugs, vulnerabilities, or code smells found
3. **Adjust Quality Gate**: Customize quality gate rules in SonarQube if needed
4. **Monitor Builds**: Set up email notifications or integrate with Slack/Teams
5. **Add More Tests**: Increase code coverage by adding more test cases

---

**Need Help?** Check the Jenkins console output and SonarQube logs for detailed error messages.
