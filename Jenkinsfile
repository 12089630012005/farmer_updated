pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t farmer-app .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                set -e
                # Network for app and DB (no docker-compose required)
                docker network create farmer-net 2>/dev/null || true

                # Stop and remove existing containers
                docker stop farmer-mysql farmer-app 2>/dev/null || true
                docker rm farmer-mysql farmer-app 2>/dev/null || true

                # Start MySQL (schema.sql runs on first start via init volume)
                docker run -d --name farmer-mysql --network farmer-net \\
                  -e MYSQL_ROOT_PASSWORD='Nikki@3001' \\
                  -e MYSQL_DATABASE=farmer_updated \\
                  -v farmer-mysql-data:/var/lib/mysql \\
                  -v $(pwd)/schema.sql:/docker-entrypoint-initdb.d/schema.sql:ro \\
                  -p 3306:3306 \\
                  mysql:8.0

                # Wait for MySQL to accept connections
                echo "Waiting for MySQL..."
                for i in $(seq 1 30); do
                  if docker exec farmer-mysql mysqladmin ping -h localhost -uroot -p'Nikki@3001' --silent 2>/dev/null; then
                    echo "MySQL ready."
                    break
                  fi
                  sleep 2
                done

                # Start app (connects to farmer-mysql via farmer-net)
                docker run -d --name farmer-app --network farmer-net \\
                  -p 80:3000 \\
                  -e MYSQL_HOST=farmer-mysql \\
                  -e MYSQL_USER=root \\
                  -e MYSQL_PASSWORD='Nikki@3001' \\
                  -e MYSQL_DATABASE=farmer_updated \\
                  farmer-app:latest
                '''
            }
        }
    }
}

