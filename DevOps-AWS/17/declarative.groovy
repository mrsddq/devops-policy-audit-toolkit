pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    stages {
        stage('SCM-Checkout') {
            steps {
                echo 'SCM-Checkout stage'
            }
        }
        stage('Build') {
            steps {
                echo 'build stage'
            }
        }
        stage('test') {
            steps {
                echo 'test stage'
            }
        }
        stage('deploy') {
            steps {
                echo 'deploy stage'
            }
        }
        stage('archive') {
            steps {
                echo 'archive stage'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml'
        }
    }
}
