pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-credentials',
                    url: 'https://github.com/<your-username>/<your-repo>.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t two-tier-app .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                docker stop two-tier-app || true
                docker rm two-tier-app || true
                docker run -d -p 80:80 --name two-tier-app two-tier-app
                '''
            }
        }
    }
}
