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
	
	stage('Save Current Version') {
    		steps {
        		sh '''
            			echo "===== 현재 버전 저장 ====="

            			PREVIOUS_IMAGE=$(docker inspect jenkins-ci-demo \
                			--format='{{.Config.Image}}')

            			if [ -z "$PREVIOUS_IMAGE" ]; then
                			echo "기존 이미지 정보를 가져오지 못했습니다."
                			exit 1
            			fi

            			echo "$PREVIOUS_IMAGE" > .previous_image

            			echo "롤백용 이미지 저장 완료: $PREVIOUS_IMAGE"
            			echo "저장 파일 내용:"
            			cat .previous_image
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

                			sh '''
                   				echo "===== 자동 롤백 ====="
	
                    				if [ ! -f .previous_image ]; then
                        				echo "이전 이미지 기록 파일이 없습니다."
                       			 		exit 1
                    				fi

                    			PREVIOUS_IMAGE=$(cat .previous_image)
                    			PREVIOUS_TAG=${PREVIOUS_IMAGE#jenkins-ci-demo:}

                    			if [ -z "$PREVIOUS_TAG" ]; then
                        			echo "이전 이미지 태그를 추출하지 못했습니다."
                        			exit 1
                    			fi

                    			echo "롤백 대상 이미지: $PREVIOUS_IMAGE"
                    			echo "롤백 대상 태그: $PREVIOUS_TAG"

                    			docker rm -f jenkins-ci-demo \
                        			2>/dev/null || true

                    			IMAGE_TAG=$PREVIOUS_TAG \
                        		docker-compose up -d

                    			docker-compose ps
                			'''

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
                    				"새 버전 배포에 실패하여 이전 버전으로 롤백했습니다."
               				)
            		}

            		echo "새 버전 배포가 정상 완료되었습니다."
        	}
    	}
}
