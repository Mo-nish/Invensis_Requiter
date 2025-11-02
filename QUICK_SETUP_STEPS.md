# Quick Setup Steps - Invensis CI/CD

## ✅ STEP-BY-STEP CHECKLIST

### 1. SonarQube Webhook (Do This NOW)
- [ ] Open SonarQube → Administration → Configuration → Webhooks
- [ ] Click "Create"
- [ ] Name: `Invensis`
- [ ] URL: `http://localhost:8080/sonarqube-webhook/` (or your Jenkins URL)
- [ ] Secret: Leave blank
- [ ] Click "Create" button at bottom
- [ ] ✅ Webhook created successfully

---

### 2. Jenkins Pipeline Job
- [ ] Go to Jenkins Dashboard
- [ ] Click "New Item"
- [ ] Name: `Invensis-Pipeline`
- [ ] Select "Pipeline" → Click "OK"
- [ ] Pipeline section:
  - [ ] Definition: "Pipeline script from SCM"
  - [ ] SCM: "Git"
  - [ ] Repository URL: Your GitHub repo URL (e.g., `https://github.com/username/Invensis.git`)
  - [ ] Credentials: Select if private repo, leave blank if public
  - [ ] Branch: `*/main` or `*/master`
  - [ ] Script Path: `Jenkinsfile`
- [ ] Click "Save"

---

### 3. First Build
- [ ] Go to your job: `Invensis-Pipeline`
- [ ] Click "Build Now"
- [ ] Click on build #1
- [ ] Click "Console Output"
- [ ] Wait for completion (watch for these stages):
  - [ ] ✅ Checkout
  - [ ] ✅ Set up Python and deps
  - [ ] ✅ Run tests with coverage
  - [ ] ✅ SonarQube Analysis
  - [ ] ✅ Quality Gate

---

### 4. Verify Results
- [ ] Open SonarQube
- [ ] Go to Projects → "Invensis"
- [ ] Check:
  - [ ] Code metrics displayed
  - [ ] Coverage percentage shown
  - [ ] Quality Gate status (Pass/Fail)

---

## 🔧 TROUBLESHOOTING

**If webhook creation fails:**
- Make sure Jenkins is running
- Check Jenkins URL is correct
- Try: `http://localhost:8080/sonarqube-webhook/`

**If build fails:**
- Check console output for errors
- Make sure GitHub repo URL is correct
- Verify `Jenkinsfile` exists in your repo root

**If SonarQube analysis fails:**
- Check SonarQube server is running
- Verify webhook was created successfully
- Check token credential exists in Jenkins

---

## 📞 CURRENT STATUS

**Right now, you should:**
1. ✅ Create the webhook in SonarQube (you're doing this)
2. ⏭️ Next: Create Jenkins Pipeline job
3. ⏭️ Then: Run first build
4. ⏭️ Finally: Verify in SonarQube
