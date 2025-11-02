pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo "🔹 Checking out source code..."
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "🔹 Setting up Python virtual environment..."
                bat '''
                python -m venv venv
                call venv\\Scripts\\activate
                pip install --upgrade pip
                pip install -r requirements.txt
                pytest
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "🔹 Running pytest..."
                bat '''
                call venv\\Scripts\\activate
                pytest
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Build and tests completed successfully!"
        }
        failure {
            echo "❌ Build failed! Check logs for errors."
        }
    }
}
