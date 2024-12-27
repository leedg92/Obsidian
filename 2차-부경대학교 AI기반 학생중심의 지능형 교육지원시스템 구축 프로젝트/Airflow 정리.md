
# Airflow 운영 가이드



## 1. 시스템 구성
- Oracle Linux 환경에서 Podman(Docker 호환)을 통해 운영
- Oracle Linux 계정
  - ID : ai-airflow 
  - PW : AIRFLOW!jsa@244

- Webserver Port: 8090
- 내부망 접속 주소: http://10.250.124.101:8090
- 기본 관리자 계정
  - ID: airflow
  - PW: airflow

## 2. Airflow 계정 관리
### 새 사용자 추가
```bash
# Webserver 컨테이너에 접속하여 사용자 생성
sudo docker exec -it docker-airflow-airflow-webserver-1 airflow users create \
    --username [새로운사용자명] \
    --firstname [이름] \
    --lastname [성] \
    --role Admin \
    --email [이메일] \
    --password [패스워드]
```

## 3. Docker 빌드 및 실행 가이드

### 일반 빌드 방식
```bash
# 1. 컨테이너 중지
sudo docker compose down

# 2. 일반 빌드
sudo docker compose build

# 3. 컨테이너 시작
sudo docker compose up -d
```

### No-cache 빌드 방식 (완전 새로운 빌드 필요시)
```bash
# 1. 컨테이너 중지
sudo docker compose down

# 2. 캐시없이 새로 빌드
sudo docker compose build --no-cache

# 3. 컨테이너 시작
sudo docker compose up -d
```

### 시스템 정리 (메모리/디스크 공간 확보)
```bash
# 1. 실행 중인 컨테이너 중지
sudo docker compose down

# 2. 사용하지 않는 컨테이너 삭제
sudo docker container prune

# 3. 사용하지 않는 이미지 삭제
sudo docker image prune -a

# 4. 사용하지 않는 볼륨 삭제
sudo docker volume prune

# 5. 전체 시스템 정리 (미사용 리소스 모두 삭제)
sudo docker system prune -a --volumes
```

## 4. 주의사항
- 시스템 정리 명령어는 사용하지 않는 모든 Docker 리소스를 삭제하므로 신중하게 사용
- 새로운 빌드 전에 시스템 정리를 실행하면 깔끔한 환경에서 시작 가능
- No-cache 빌드는 모든 레이어를 새로 생성하므로 일반 빌드보다 시간이 더 소요됨