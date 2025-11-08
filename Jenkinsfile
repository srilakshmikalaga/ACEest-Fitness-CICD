pipeline {
  agent any

  environment {
    PATH = "${env.PATH}:/var/lib/jenkins/.local/bin"
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
        sh 'pip3 install -r requirements.txt --user'
      }
    }

    stage('Run Tests') {
      steps {
        echo "Running unit tests..."
        sh '''
          echo "Setting up environment..."
          export PATH=$PATH:/var/lib/jenkins/.local/bin
          echo "Running pytest..."
          python3 -m pytest -q --disable-warnings --cache-clear
        '''
      }
    }
 stage('SonarQube Analysis') {
  environment {
    SCANNER_HOME = tool 'SonarScanner'
  }
  steps {
    withSonarQubeEnv('sonar-cloud') {
      sh '''
        $SCANNER_HOME/bin/sonar-scanner \
        -Dsonar.projectKey=ACEest-Fitness-CICD \
        -Dsonar.organization=srilakshmikalaga \
        -Dsonar.sources=. \
        -Dsonar.python.version=3.8 \
        -Dsonar.host.url=https://sonarcloud.io
      '''
    }
  }
}




    stage('Build Docker Image') {
      steps {
        sh 'docker build -t aceest-fitness-app .'
      }
    }

    stage('Push to Docker Hub') {
  steps {
    withCredentials([string(credentialsId: 'docker-hub-password', variable: 'DOCKERHUB_TOKEN')]) {
      sh '''
        echo "🔹 Logging in to Docker Hub..."
        echo "$DOCKERHUB_TOKEN" | docker login -u "srilakshmikalaga" --password-stdin

        echo "🔹 Tagging image..."
        docker tag aceest-fitness-app srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}

        echo "🔹 Pushing image..."
        docker push srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
      '''
    }
  }
}
stage('Deploy to Kubernetes (TEST)') {
  steps {
    sh '''
      echo "Applying Kubernetes manifests..."
      kubectl apply -f k8s/blue-deployment.yaml
      kubectl apply -f k8s/service.yaml

      echo "Verifying deployment..."
      kubectl rollout status deployment/aceest-fitness-deployment-blue
      kubectl get pods -l version=blue
    '''
  }
}




  }
}
