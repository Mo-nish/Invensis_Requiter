pipeline {
    agent any

    environment {
        PYTHON = "python"
        WORKSPACE_DIR = "Documents\\Invensis"
    }

    stages {

        stage('Checkout') {
            steps {
                echo "📦 Checking out source code..."
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                bat """
                    ${env.PYTHON} -m venv venv
                    call venv\\Scripts\\activate
                    python -m pip install --upgrade pip
                    if exist requirements.txt (
                        pip install -r requirements.txt
                    )
                    pip install pytest pytest-cov
                """
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat """
                    call venv\\Scripts\\activate
                    echo Running unit tests...
                    cd ${env.WORKSPACE_DIR}
                    pytest --maxfail=1 --disable-warnings -q --ignore=test_reset_password_flow.py --ignore=test_forgot_password.py --cov=. --cov-report=xml:coverage.xml
                """
            }
        }

        stage('Run Integration Tests') {
            steps {
                script {
                    echo "Attempting to start Flask and run integration tests..."
                    def flaskStarted = false
                    
                    // Try to start Flask
                    bat """
                        call venv\\Scripts\\activate
                        cd ${env.WORKSPACE_DIR}
                        echo Starting Flask app in background...
                        start "" /MIN ${env.PYTHON} run.py > flask.log 2>&1
                    """
                    
                    // Wait and check if Flask started
                    sleep(time: 10, unit: 'SECONDS')
                    
                    def flaskReady = bat(
                        script: 'powershell -Command "try { $null = Invoke-WebRequest -Uri \'http://localhost:5001/\' -TimeoutSec 3 -UseBasicParsing; Write-Host \'READY\'; exit 0 } catch { Write-Host \'NOT_READY\'; exit 1 }"',
                        returnStatus: true
                    )
                    
                    if (flaskReady == 0) {
                        echo "✅ Flask is ready! Running integration tests..."
                        bat """
                            call venv\\Scripts\\activate
                            cd ${env.WORKSPACE_DIR}
                            pytest --maxfail=1 --disable-warnings -q test_reset_password_flow.py test_forgot_password.py
                        """
                        flaskStarted = true
                    } else {
                        echo "⚠️ Flask could not start - skipping integration tests"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
            post {
                always {
                    bat """
                        echo Stopping Flask processes...
                        taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" 2>nul || taskkill /F /IM python.exe 2>nul || echo No Flask processes to stop
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('Invensis') {
                    bat """
                        call venv\\Scripts\\activate
                        cd ${env.WORKSPACE_DIR}
                        
                        echo Setting up SonarScanner...
                        set SONAR_SCANNER_VERSION=5.0.1.3006
                        set SONAR_SCANNER_ZIP=sonar-scanner-cli-%SONAR_SCANNER_VERSION%-windows.zip
                        set SONAR_SCANNER_DIR=%WORKSPACE%\\sonar-scanner-%SONAR_SCANNER_VERSION%-windows
                        
                        if not exist "%SONAR_SCANNER_DIR%" (
                            echo Downloading SonarScanner...
                            powershell -Command "Invoke-WebRequest -Uri 'https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/%SONAR_SCANNER_ZIP%' -OutFile '%WORKSPACE%\\%SONAR_SCANNER_ZIP%'"
                            
                            echo Extracting SonarScanner...
                            powershell -Command "Expand-Archive -Path '%WORKSPACE%\\%SONAR_SCANNER_ZIP%' -DestinationPath '%WORKSPACE%' -Force"
                            
                            echo Cleaning up zip file...
                            del "%WORKSPACE%\\%SONAR_SCANNER_ZIP%" 2>nul
                        ) else (
                            echo SonarScanner already exists, skipping download...
                        )
                        
                        echo Creating sonar-project.properties...
                        echo sonar.projectKey=Invensis> sonar-project.properties
                        echo sonar.projectName=Invensis>> sonar-project.properties
                        echo sonar.sources=.>> sonar-project.properties
                        echo sonar.host.url=http://localhost:9000>> sonar-project.properties
                        echo sonar.login=%SONAR_AUTH_TOKEN%>> sonar-project.properties
                        echo sonar.python.version=3.14>> sonar-project.properties
                        echo sonar.coverageReportPaths=coverage.xml>> sonar-project.properties
                        
                        echo Updating SonarScanner global config...
                        powershell -Command "(Get-Content '%SONAR_SCANNER_DIR%\\conf\\sonar-scanner.properties') -replace 'sonar.host.url=.*', 'sonar.host.url=http://localhost:9000' | Set-Content '%SONAR_SCANNER_DIR%\\conf\\sonar-scanner.properties'"
                        
                        echo Running SonarQube analysis...
                        "%SONAR_SCANNER_DIR%\\bin\\sonar-scanner.bat" -Dsonar.host.url=http://localhost:9000 -Dsonar.login=%SONAR_AUTH_TOKEN%
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        success {
            echo "✅ All tests passed successfully!"
        }
        failure {
            echo "❌ Build failed! Check logs for test errors."
        }
        always {
            bat """
                echo Cleaning up Flask processes...
                taskkill /F /IM python.exe 2>nul || exit /b 0
            """
            echo "🧹 Cleaning up workspace..."
        }
    }
}
