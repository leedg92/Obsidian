
# 포트폴리오 페이지 배포 가이드

이 문서는 채용 담당자가 포트폴리오 페이지에 접속할 수 있도록 AWS에서 서버를 설정하고, Docker, PostgreSQL 및 CI/CD를 통해 서비스를 자동화하는 과정에 대한 자세한 안내입니다.

## 1. AWS EC2 서버 대여

### 1.1 EC2 인스턴스 생성
1. **AWS 관리 콘솔**에 로그인 후, **EC2 서비스**로 이동합니다.
2. 인스턴스 생성 방법:
   - 인스턴스 시작 클릭.
   - 운영체제 선택: **Ubuntu 20.04** 또는 **Amazon Linux 2** 추천.
   - 인스턴스 유형 선택: **t3.micro** 또는 **t3.small**.
   - 키 페어 생성 후 다운로드.
   - 보안 그룹 설정: HTTP(80), HTTPS(443), SSH(22) 포트를 열어줍니다.
   - 인스턴스 시작.

### 1.2 Elastic IP 설정
1. EC2 인스턴스에 **Elastic IP**를 할당.
2. **AWS EC2 대시보드**에서 **Elastic IP** 메뉴로 이동 후, 새 IP 할당 및 인스턴스에 연결.

### 1.3 SSH 접속
```bash
ssh -i /path/to/your-key.pem ubuntu@your-elastic-ip
```

## 2. 도메인 및 SSL 설정

### 2.1 도메인 구입 및 설정
1. **Google Domains, Namecheap, GoDaddy** 등에서 도메인 구입.
2. **AWS Route 53**을 사용해 도메인 연결.

### 2.2 SSL 인증서 설정
1. **Let’s Encrypt**를 사용해 SSL 인증서 발급:
```bash
sudo apt install certbot
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 3. 필수 소프트웨어 설치 (Java, Python, Docker)

### 3.1 Docker 설치
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

### 3.2 Java 설치
```bash
sudo apt install openjdk-11-jdk -y
```

### 3.3 Python 설치
```bash
sudo apt install python3 python3-pip -y
```

## 4. DB 설정 (PostgreSQL)

### 4.1 PostgreSQL 설치
```bash
sudo apt install postgresql postgresql-contrib -y
```

### 4.2 PostgreSQL 데이터베이스 및 사용자 생성
```bash
sudo -i -u postgres
psql

CREATE DATABASE myportfolio;
CREATE USER myuser WITH ENCRYPTED PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE myportfolio TO myuser;
```

## 5. Docker 컨테이너 설정

### 5.1 Python 기반 컨테이너 (API 서버)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Java 기반 컨테이너 (Spring Boot 내장 서버 사용)
```dockerfile
FROM openjdk:11-jre-slim

WORKDIR /app
COPY target/myapp.jar /app/myapp.jar
CMD ["java", "-jar", "myapp.jar"]
```

## 6. CI/CD 설정 (GitHub Actions or Jenkins)

### 6.1 GitHub Actions 예시
```yaml
name: Deploy to AWS
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    - name: Build Docker image
      run: |
        docker build -t my-python-api .
        docker build -t my-java-app .
    - name: Push Docker image to Docker Hub
      run: |
        docker push your-dockerhub-repo/my-python-api
        docker push your-dockerhub-repo/my-java-app
```

## 7. 프론트엔드 및 백엔드 배포

### 7.1 React 빌드 및 배포
```bash
npm run build
```

### 7.2 Docker Compose 설정
```yaml
version: '3'
services:
  python-api:
    image: my-python-api
    ports:
      - "8000:8000"
  java-app:
    image: my-java-app
    ports:
      - "8080:8080"
```

## 8. 네트워크 설정 및 보안

### 8.1 Nginx 리버스 프록시 설정
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
    }

    location / {
        proxy_pass http://localhost:8080/;
    }
}
```
