currentBuild.displayName = 'tomcat-build - ' + currentBuild.number

pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 45, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        TOMCAT_HOST = credentials('tomcat-host')
    }

    tools {
        maven 'MVN_HOME'
    }
    stages {
        stage('SCM-checkout') {
            steps {
                git branch: 'main', credentialsId: 'git-credentials', url: 'https://github.com/mrsddq/my-app-demo.git'
            }
        }
        stage('sonar') {
            steps {
                withSonarQubeEnv('sonar') {
                    sh 'mvn sonar:sonar'
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('maven-package') {
            steps {
                sh 'mvn clean compile package'
            }
        }
        stage('Tomcat-Deployment') {
            steps {
                sshagent(['tomcat-credentials']) {
                    sh '''
                        scp target/my-app-demo.war ec2-user@$TOMCAT_HOST:/opt/tomcat/webapps/
                        ssh ec2-user@$TOMCAT_HOST /opt/tomcat/bin/shutdown.sh
                        ssh ec2-user@$TOMCAT_HOST /opt/tomcat/bin/startup.sh
                    '''
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml'
        }
    }
}
