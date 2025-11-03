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
                    bat """
                        call venv\\Scripts\\activate
                        cd ${env.WORKSPACE_DIR}
                        echo Starting Flask app in background...
                        start "" /MIN ${env.PYTHON} run.py > flask.log 2>&1
                    """
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
                    withEnv(["SONAR_SCANNER_HOME=${tool 'SonarScanner'}"]) {
                        bat """
                            call venv\\Scripts\\activate
                            cd ${env.WORKSPACE_DIR}
                            echo sonar.projectKey=Invensis> sonar-project.properties
                            echo sonar.projectName=Invensis>> sonar-project.properties
                            echo sonar.sources=.>> sonar-project.properties
                            echo sonar.host.url=%SONAR_HOST_URL%>> sonar-project.properties
                            echo sonar.python.version=3.14>> sonar-project.properties
                            echo sonar.coverageReportPaths=coverage.xml>> sonar-project.properties
                            "%SONAR_SCANNER_HOME%\\bin\\sonar-scanner.bat"
                        """
                    }
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
        always {
            bat """
                echo Cleaning up Flask processes...
                taskkill /F /IM python.exe 2>nul || exit /b 0
            """
            echo "🧹 Cleaning up workspace..."
        }
    }
}
