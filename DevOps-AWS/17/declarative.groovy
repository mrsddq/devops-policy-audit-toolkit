pipeline {
    agent any

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
}
