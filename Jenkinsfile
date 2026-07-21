pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.BUILD_NUMBER}" 
    }
    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Environment Check') {
            steps {
                sh '''
                    echo "Jenkins Build Number: ${BUILD_NUMBER}"
                    echo "Docker Image Tag: ${IMAGE_TAG}"
		    docker --version
                    docker-compose --version
                '''
            }
        }

        stage('Syntax Check') {
            steps {
                sh '''
                    echo "===== Python 문법 검사 ====="
                    python3 -m py_compile app.py logic.py test_logic.py
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    echo "===== 단위 테스트 ====="
                    python3 -m unittest -v
                '''
            }
        }

        stage('Compose Check') {
            steps {
                sh '''
                    echo "===== Compose 설정 검사 ====="
                    docker-compose config
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                    echo "===== Docker 이미지 빌드 ====="
                    docker-compose build
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                   echo "===== 컨테이너 배포 ====="
		   docker-compose up -d
             	   docker-compose ps 
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    for i in 1 2 3 4 5
                    do
                        echo "Health Check: ${i}/5"

                        if curl -fsS http://127.0.0.1:18080/health
                        then
                            echo
                            echo "Health Check 성공"
                            exit 0
                        fi

                        sleep 2
                    done

                    echo "Health Check 실패"
                    docker logs jenkins-ci-demo || true
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline 성공'
        }

        failure {
            echo 'CI/CD Pipeline 실패'
        }
    }
}
