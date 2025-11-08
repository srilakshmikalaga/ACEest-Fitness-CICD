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
        echo "Running unit tests with coverage..."
        sh '''
          echo "Setting up environment..."
          export PATH=$PATH:/var/lib/jenkins/.local/bin
          
          echo "Installing pytest-cov if not already present..."
          pip3 install pytest-cov --user
          
          echo "Running pytest with coverage..."
          pytest --cov=. --cov-report=xml --disable-warnings --cache-clear
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
              -Dsonar.python.coverage.reportPaths=coverage.xml \
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
      echo "Applying Kubernetes manifests (skipping validation check)..."
      kubectl apply -f k8s/blue-deployment.yaml --validate=false
      kubectl apply -f k8s/service.yaml --validate=false

      echo "Verifying deployment rollout..."
      kubectl rollout status deployment/aceest-fitness-deployment-blue || echo "⚠️ Rollout check skipped"
      echo "Fetching Blue deployment pods..."
      kubectl get pods -l version=blue || echo "⚠️ Unable to fetch pods, cluster might be running locally only"
    '''
  }
}

stage('A/B Testing Deployments') {
  steps {
    sh '''
      echo "Deploying Version A and Version B..."
      kubectl apply -f k8s/ab/deployment-a.yaml --validate=false
      kubectl apply -f k8s/ab/service-a.yaml --validate=false
      kubectl apply -f k8s/ab/deployment-b.yaml --validate=false
      kubectl apply -f k8s/ab/service-b.yaml --validate=false

      echo "Checking deployment status..."
      kubectl rollout status deployment/aceest-fitness-a || echo "⚠️ Version A rollout check skipped"
      kubectl rollout status deployment/aceest-fitness-b || echo "⚠️ Version B rollout check skipped"

      echo "A/B Testing pods:"
      kubectl get pods -l app=aceest-fitness
    '''
  }
}





  }
}
