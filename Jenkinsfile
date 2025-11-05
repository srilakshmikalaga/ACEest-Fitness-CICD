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

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t aceest-fitness-app .'
      }
    }

    stage('Tag & Push to Docker Hub') {
      steps {
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
        sh '''
          docker rm -f aceest-container || true
          docker pull srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
          docker run -d -p 5000:5000 --name aceest-container srilakshmikalaga/aceest-fitness-app:v${BUILD_NUMBER}
        '''
      }
    }
  }
}
