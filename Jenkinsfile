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
          pip3 install pytest-cov --user
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

    /* 👇 ADD THIS NEW STAGE HERE 👇 */
    stage('Push All Docker Versions') {
      steps {
        withCredentials([string(credentialsId: 'docker-hub-password', variable: 'DOCKERHUB_TOKEN')]) {
          sh '''
            echo "🔹 Logging in to Docker Hub for multi-version push..."
            echo "$DOCKERHUB_TOKEN" | docker login -u "srilakshmikalaga" --password-stdin

            echo "🔹 Running push_all_versions.sh ..."
            chmod +x push_all_versions.sh
            ./push_all_versions.sh

            echo "✅ All tagged versions pushed to Docker Hub successfully!"
          '''
        }
      }
    }
    /* 👆 END OF NEW STAGE 👆 */

    stage('Deploy to Kubernetes (TEST)') {
      steps {
        sh '''
          echo "Applying Kubernetes manifests (Rolling Update enabled)..."
          kubectl apply -f k8s/blue-deployment.yaml --validate=false
          kubectl apply -f k8s/service.yaml --validate=false

          echo "Verifying deployment rollout..."
          if ! kubectl rollout status deployment/aceest-fitness-deployment-blue --timeout=120s; then
            echo "❌ Rollout failed! Initiating rollback..."
            kubectl rollout undo deployment/aceest-fitness-deployment-blue
            exit 1
          fi

          kubectl get pods -l version=blue || echo "⚠️ Unable to fetch pods"
        '''
      }
    }

    stage('A/B Testing Deployments') {
      steps {
        sh '''
          echo "Deploying Version A and Version B (RollingUpdate strategy)..."
          kubectl apply -f k8s/ab/deployment-a.yaml --validate=false
          kubectl apply -f k8s/ab/service-a.yaml --validate=false
          kubectl apply -f k8s/ab/deployment-b.yaml --validate=false
          kubectl apply -f k8s/ab/service-b.yaml --validate=false

          echo "Checking rollout status..."
          kubectl rollout status deployment/aceest-fitness-a --timeout=120s || kubectl rollout undo deployment/aceest-fitness-a
          kubectl rollout status deployment/aceest-fitness-b --timeout=120s || kubectl rollout undo deployment/aceest-fitness-b
          echo "✅ All A/B Testing deployments successful!"
        '''
      }
    }

    stage('Canary Deployment (Progressive Rollout)') {
      steps {
        sh '''
          echo "🚀 Starting Canary deployment..."
          kubectl apply -f k8s/canary-deployment.yaml --validate=false
          kubectl apply -f k8s/service-canary.yaml --validate=false
          kubectl rollout status deployment/aceest-fitness-canary || echo "⚠️ Canary rollout check skipped"
          kubectl get pods -l version=canary
          echo "✅ Canary deployment allows controlled rollout (10-20% traffic) before full release."
        '''
      }
    }

    stage('Shadow Deployment (Traffic Mirroring)') {
      steps {
        sh '''
          echo "👥 Starting Shadow deployment..."
          kubectl apply -f k8s/shadow-deployment.yaml --validate=false
          kubectl apply -f k8s/ingress-shadow.yaml --validate=false
          kubectl get pods -l version=shadow
          echo "✅ Shadow deployments receive mirrored live traffic for testing without affecting users."
        '''
      }
    }

  }
}
