pipeline {
    agent any

    environment {
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        PREVIOUS_IMAGE = ""
    }

    options {
        disableConcurrentBuilds()
    }

    stages {
        stage('Environment Check') {
            steps {
                sh '''
                    echo "===== 환경 확인 ====="
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

        stage('Save Current Version') {
            steps {
                script {
                    env.PREVIOUS_IMAGE = sh(
                        script: '''
                            docker inspect jenkins-ci-demo \
                                --format='{{.Config.Image}}' 2>/dev/null || true
                        ''',
                        returnStdout: true
                    ).trim()

                    if (env.PREVIOUS_IMAGE) {
                        echo "현재 실행 이미지: ${env.PREVIOUS_IMAGE}"
                    } else {
                        echo "현재 실행 중인 기존 이미지가 없습니다."
                    }

                    echo "새 배포 이미지: jenkins-ci-demo:${env.IMAGE_TAG}"
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "===== 컨테이너 배포 ====="

                    docker rm -f jenkins-ci-demo 2>/dev/null || true

                    IMAGE_TAG=${IMAGE_TAG} docker-compose up -d

                    docker-compose ps
                '''
            }
        }

        stage('Health Check') {
            steps {
                script {
                    int healthStatus = sh(
                        script: '''
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
                        ''',
                        returnStatus: true
                    )

                    if (healthStatus != 0) {
                        echo "새 버전 Health Check 실패"
                        echo "자동 롤백을 시작합니다."

                        if (!env.PREVIOUS_IMAGE?.trim()) {
                            error(
                                "이전 이미지가 없어 롤백할 수 없습니다."
                            )
                        }

                        def previousTag = env.PREVIOUS_IMAGE.replace(
                            'jenkins-ci-demo:',
                            ''
                        )

                        sh """
                            echo "===== 자동 롤백 ====="
                            echo "롤백 대상 이미지: ${env.PREVIOUS_IMAGE}"

                            docker rm -f jenkins-ci-demo \
                                2>/dev/null || true

                            IMAGE_TAG=${previousTag} \
                                docker-compose up -d

                            docker-compose ps
                        """

                        int rollbackStatus = sh(
                            script: '''
                                for i in 1 2 3 4 5
                                do
                                    echo "Rollback Health Check: ${i}/5"

                                    if curl -fsS \
                                        http://127.0.0.1:18080/health
                                    then
                                        echo
                                        echo "롤백 Health Check 성공"
                                        exit 0
                                    fi

                                    sleep 2
                                done

                                echo "롤백 Health Check 실패"
                                docker logs jenkins-ci-demo || true

                                exit 1
                            ''',
                            returnStatus: true
                        )

                        if (rollbackStatus != 0) {
                            error(
                                "새 버전 배포와 롤백이 모두 실패했습니다."
                            )
                        }

                        error(
                            "새 버전 배포 실패. " +
                            "${env.PREVIOUS_IMAGE}로 롤백했습니다."
                        )
                    }

                    echo "새 버전 배포가 정상 완료되었습니다."
                }
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

        always {
            sh '''
                echo "===== 최종 실행 상태 ====="

                docker inspect jenkins-ci-demo \
                    --format='현재 이미지: {{.Config.Image}}' \
                    2>/dev/null || true

                docker-compose ps || true
            '''
        }
    }
}
