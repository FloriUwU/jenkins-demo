pipeline {
    agent any

    stages {

        stage('Code prüfen') {
            steps {
                echo 'Code wurde von GitHub geladen.'
            }
        }

        stage('Docker Image bauen') {
            steps {
                sh 'docker build -t jenkins-demo .'
            }
        }

        stage('Container starten') {
            steps {
                sh 'docker stop jenkins-demo || true'
                sh 'docker rm jenkins-demo || true'
                sh 'docker run -d --name jenkins-demo -p 8081:80 jenkins-demo'
            }
        }
    }
}
