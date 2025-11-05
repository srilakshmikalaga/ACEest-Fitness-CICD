pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}"
        PATH = "/var/lib/jenkins/.local/bin:${env.PATH}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/srilakshmikalaga/ACEest-Fitness-CICD.git',
                        credentialsId: 'github-token'
                    ]]
                ])
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "Installing Python dependencies..."
                sh 'pip3 install -r requirements.txt --user'
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running Pytest..."
                sh '''
                    cd $WORKSPACE
                    export PYTHONPATH=$WORKSPACE
                    pytest -q
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t aceest-fitness-app .'
            }
        }

        stage('Tag & Push to Docker Hub') {
            steps {
                echo "Tagging and pushing Docker image..."
                withCredentials([string(credentialsId: 'docker-hub-password', variable: 'DOCKERHUB_TOKEN')]) {
                    sh '''
                        docker tag aceest-fitness-app srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
                        echo "$DOCKERHUB_TOKEN" | docker login -u "srilakshmikalaga" --password-stdin
                        docker push srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying the container..."
                sh '''
                    docker rm -f aceest-container || true
                    docker pull srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
                    docker run -d -p 5000:5000 --name aceest-container srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Build and Deployment successful! App running on port 5000."
        }
        failure {
            echo "❌ Build failed. Check logs in Jenkins console output."
        }
    }
}
