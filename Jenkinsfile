pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t farmer-app .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                docker stop farmer-app || true
                docker rm farmer-app || true
                docker run -d -p 80:80 --name farmer-app farmer-app
                '''
            }
        }
    }
}

