# Docker 환경 설정 가이드

## 디렉토리 구조
```
docker/
├── postgresql/
│   ├── Dockerfile         # PostgreSQL 컨테이너 설정
│   ├── init.sql          # 초기 데이터베이스 스키마 및 데이터
│   └── postgresql.conf   # PostgreSQL 설정 파일
├── kafka/
│   ├── Dockerfile        # Kafka 컨테이너 설정
│   └── server.properties # Kafka 브로커 설정
├── spark/
│   ├── Dockerfile        # Spark 컨테이너 설정
│   └── spark-defaults.conf # Spark 설정 파일
├── airflow/
│   ├── Dockerfile        # Airflow 컨테이너 설정
│   ├── requirements.txt  # Python 패키지 의존성
│   └── dags/            # Airflow DAG 파일 디렉토리
└── docker-compose.yml    # 전체 서비스 구성 파일
```

## 서비스 구성

### 1. PostgreSQL (포트: 5432)
- 메인 데이터베이스 서버
- 환경 변수:
  - POSTGRES_DB: coindb
  - POSTGRES_USER: postgres
  - POSTGRES_PASSWORD: postgres
- 볼륨: postgres_data (데이터 영속성)
- 초기화 스크립트: init.sql을 통해 기본 테이블 생성

### 2. Kafka & Zookeeper (포트: 9092, 2181)
- 실시간 데이터 스트리밍 처리
- Kafka 브로커 설정:
  - KAFKA_BROKER_ID: 1
  - KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
- Zookeeper 설정:
  - ZOOKEEPER_CLIENT_PORT: 2181
  - ZOOKEEPER_TICK_TIME: 2000

### 3. Spark (포트: 8080, 7077)
- 분산 데이터 처리 엔진
- 구성:
  - Master 노드: 작업 조율 및 리소스 관리
  - Worker 노드: 실제 데이터 처리 수행
- 설정:
  - SPARK_WORKER_MEMORY: 1G
  - SPARK_WORKER_CORES: 1
- 볼륨: spark_data (작업 데이터 저장)

### 4. Airflow (포트: 8081)
- 워크플로우 관리 및 스케줄링
- 구성:
  - Webserver: UI 제공 및 작업 모니터링
  - Scheduler: DAG 실행 및 관리
- 볼륨:
  - airflow_logs: 로그 저장
  - dags: DAG 파일 관리

## 네트워크 구성
- 네트워크 이름: coin_network
- 타입: bridge
- 모든 서비스가 동일 네트워크에서 통신

## 볼륨 구성
- postgres_data: PostgreSQL 데이터 저장
- spark_data: Spark 작업 데이터 저장
- airflow_logs: Airflow 로그 저장

## 실행 방법

1. 전체 서비스 실행:
```bash
docker-compose up -d
```

2. 개별 서비스 실행:
```bash
docker-compose up -d postgres  # PostgreSQL만 실행
docker-compose up -d kafka    # Kafka와 Zookeeper 실행
docker-compose up -d spark-master spark-worker  # Spark 실행
docker-compose up -d airflow-webserver airflow-scheduler  # Airflow 실행
```

3. 서비스 상태 확인:
```bash
docker-compose ps
```

4. 로그 확인:
```bash
docker-compose logs [서비스명]
```

## 접속 정보

1. PostgreSQL:
- Host: localhost
- Port: 5432
- Database: coindb
- Username: postgres
- Password: postgres

2. Kafka:
- Bootstrap Servers: localhost:9092

3. Spark UI:
- URL: http://localhost:8080

4. Airflow UI:
- URL: http://localhost:8081
- Username: airflow
- Password: airflow

## 주의사항

1. 메모리 사용량
- 전체 서비스 실행 시 최소 8GB RAM 권장
- 리소스 부족 시 Spark Worker 메모리 조정 필요

2. 포트 충돌
- 사용되는 포트가 이미 사용 중인 경우 docker-compose.yml에서 포트 매핑 수정 필요

3. 데이터 영속성
- 컨테이너 삭제 시에도 볼륨 데이터는 유지됨
- 완전한 초기화를 위해서는 볼륨도 함께 삭제 필요:
```bash
docker-compose down -v
```