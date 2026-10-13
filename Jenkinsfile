// Deklarative Pipeline: Jenkins führt die Stages der Reihe nach aus
// und bricht beim ersten Fehler ab (dann laufen die späteren Stages nicht)
pipeline {
    // Läuft auf jedem verfügbaren Jenkins-Agent (hier: der Ubuntu-Host selbst)
    agent any

    stages {

        // Stage 1: Quellcode aus GitHub holen
        // (checkout scm nutzt das Repository, aus dem das Jenkinsfile stammt)
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // Stage 2: Python-Syntaxprüfung
        // py_compile bricht mit Fehler ab, wenn eine Datei Syntaxfehler enthält.
        // Dadurch erreicht fehlerhafter Code nie Docker Build oder Deploy
        stage('Test') {
            steps {
                sh 'python3 -m py_compile app.py'
                sh 'python3 -m py_compile webapp.py'
            }
        }

        // Stage 3: Docker-Image aus dem Dockerfile bauen und als netwatch_app:latest taggen
        stage('Docker Build') {
            steps {
                sh 'docker build -t netwatch_app:latest .'
            }
        }

        // Stage 4: Alten App-Container entfernen und neuen starten
        stage('Deploy') {
          steps {
            // Holt das DB-Passwort aus dem Jenkins-Credential-Speicher (Typ "Secret text").
            // Es steht nur in der Variable DB_PASSWORD und wird im Build-Log mit **** maskiert,
            // im Repository steht es nicht
            withCredentials([string(credentialsId: 'netwatch-db-password', variable: 'DB_PASSWORD')]) {

              // Alten Container löschen; "|| true" verhindert einen Fehler,
              // falls noch keiner existiert (z. B. beim allerersten Deploy)
              sh 'docker rm -f netwatch-app || true'

              // Neuen Container starten. Der Block steht in ''' (einfache Anführungszeichen),
              // damit die Shell $DB_PASSWORD einsetzt und nicht Groovy (sonst könnte das
              // Passwort im Log auftauchen)
              sh '''
                 docker run -d \
                  --name netwatch-app \
                  --network netwatch_netwatch \
                  --restart unless-stopped \
                  -p 5000:5000 \
                  -e DB_HOST=netwatch-db \
                  -e DB_NAME=netwatch \
                  -e DB_USER=netwatch \
                  -e DB_PASSWORD="$DB_PASSWORD" \
                  netwatch_app:latest
              '''
              // -d                   im Hintergrund starten
              // --name               fester Name, damit der alte Container ersetzt werden kann
              // --network            gleiches Netzwerk wie die Datenbank (aus compose.yaml),
              //                      dort ist die DB unter dem Namen netwatch-db erreichbar
              // --restart            startet den Container nach Absturz oder VM-Neustart neu
              // -p 5000:5000         Dashboard von außen auf Port 5000 erreichbar
              // -e DB_...            Zugangsdaten für die Datenbank als Umgebungsvariablen
            }
          }
        }

        // Stage 5: Prüfen, ob die neue Version wirklich läuft
        stage('Check') {
            steps {
                // Dem Container Zeit zum Starten geben
                sh 'sleep 5'
                // Zeigt Status und Port des App-Containers im Log
                sh 'docker ps --filter name=netwatch-app'
                // Ruft das Dashboard auf; -f lässt curl bei HTTP-Fehlern (z. B. 500)
                // mit Fehler enden, sodass die Stage rot wird
                sh 'curl -f http://localhost:5000'
            }
        }
    }

    // Wird nach allen Stages ausgeführt, je nach Ergebnis des Builds
    post {
        success {
            echo 'NetWatch wurde erfolgreich gebaut und deployed.'
        }

        failure {
            echo 'Pipeline fehlgeschlagen.'
        }
    }
}
