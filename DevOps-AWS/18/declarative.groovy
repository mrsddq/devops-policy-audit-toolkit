pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    tools {
        maven 'MVN_HOME'
    }

    stages {
        stage('SCM-Checkout') {
            steps {
                git branch: 'master', credentialsID: 'git-credentials', url: 'https://github.com/mrsddq/my-tomcat-app.git'
            }
        }
        stage('Build') {
            steps {
                sh 'mvn compile'
            }
        }
        stage('test') {
            steps {
                sh 'mvn compile'
            }
        }
        stage('Package') {
            steps {
                sh 'mvn compile'
            }
        }
        stage('archive') {
            steps {
                sh 'mvn compile'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml'
        }
    }
}
