pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                bat """
                python -m venv venv
                """
            }
        }

        stage('Activate Virtual Environment') {
            steps {
                bat """
                call venv\\Scripts\\activate
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                bat """
                call venv\\Scripts\\activate
                pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                bat """
                call venv\\Scripts\\activate
                pytest
                """
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
