pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/srilakshmikalaga/ACEest-Fitness-CICD.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest -q || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness-app .'
            }
        }
    }
}
