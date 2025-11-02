pipeline {
  agent any

  options {
    timestamps()
    skipDefaultCheckout(true)
  }

  environment {
    VENV = 'venv'
    SONAR_PROJECT_KEY = 'Invensis'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Set up Python and deps') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
              $PY -V
              $PY -m venv ${VENV}
              . ${VENV}/bin/activate
              pip install --upgrade pip
            if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
            pip install pytest pytest-cov pysonar
            '''
          } else {
            bat '''
              where python
              python -V
              python -m venv %VENV%
              call %VENV%\Scripts\activate
              python -m pip install --upgrade pip
            if exist requirements.txt ( pip install -r requirements.txt )
            pip install pytest pytest-cov pysonar
            '''
          }
        }
      }
    }

    stage('Run tests with coverage') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -e
              . ${VENV}/bin/activate
              pytest -q --maxfail=1 --disable-warnings --cov=. --cov-report=xml:coverage.xml
            '''
          } else {
            bat '''
              call %VENV%\Scripts\activate
              pytest -q --maxfail=1 --disable-warnings --cov=. --cov-report=xml:coverage.xml
            '''
          }
        }
      }
    }

    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQubeServer') {
          script {
            if (isUnix()) {
              sh '''
                set -e
                . ${VENV}/bin/activate
                pysonar \
                  --sonar-project-key=${SONAR_PROJECT_KEY}
              '''
            } else {
              bat '''
                call %VENV%\Scripts\activate
                pysonar --sonar-project-key=%SONAR_PROJECT_KEY%
              '''
            }
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
}


