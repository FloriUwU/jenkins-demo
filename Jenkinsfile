pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh 'python3 -m py_compile app.py'
                sh 'python3 -m py_compile webapp.py'
		sh 'exit 1'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t netwatch_app:latest .'
            }
        }

        stage('Deploy') {
            steps {
                sh 'docker rm -f netwatch-app || true'

                sh '''
                    docker run -d \
                      --name netwatch-app \
                      --network netwatch_netwatch \
                      -p 5000:5000 \
                      -e DB_HOST=netwatch-db \
                      -e DB_NAME=netwatch \
                      -e DB_USER=netwatch \
                      -e DB_PASSWORD=netwatchpass \
                      netwatch_app:latest
                '''
            }
        }

        stage('Check') {
            steps {
                sh 'sleep 5'
                sh 'docker ps --filter name=netwatch-app'
                sh 'curl -f http://localhost:5000'
            }
        }
    }

    post {
        success {
            echo 'NetWatch wurde erfolgreich gebaut und deployed.'
        }

        failure {
            echo 'Pipeline fehlgeschlagen.'
        }
    }
}
