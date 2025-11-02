pipeline {
    agent any

    environment {
        PYTHON = "python"
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
                pip install --upgrade pip
                pip install -r requirements.txt
                """
            }
        }

        stage('Run Flask and Tests') {
            steps {
                bat """
                call venv\\Scripts\\activate
                echo Starting Flask app...
                start /B ${env.PYTHON} run.py
                timeout /t 5 >nul
                echo Running pytest...
                pytest --maxfail=1 --disable-warnings -q
                """
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
            echo "🧹 Cleaning up workspace..."
        }
    }
}
