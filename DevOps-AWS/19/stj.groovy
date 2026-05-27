currentBuild.displayName = 'tomcat-build - ' + currentBuild.number

pipeline {
    agent any

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
                        scp -o StrictHostKeyChecking=no target/my-app-demo.war ec2-user@13.60.253.80:/opt/tomcat/webapps/
                        ssh ec2-user@13.60.253.80 /opt/tomcat/bin/shutdown.sh
                        ssh ec2-user@13.60.253.80 /opt/tomcat/bin/startup.sh
                    '''
                }
            }
        }
    }
}
