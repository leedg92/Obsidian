# ChainPortal Control System - 민원관리 API

체인포털 관제시스템의 민원관리 API 서비스입니다. Spring Boot 기반으로 구축된 RESTful API로, 민원 접수, 처리 현황 관리, 시스템 모니터링, 보고서 생성 등의 기능을 제공합니다.

## 🛠 기술 스택

### Backend
- **Java 17**
- **Spring Boot 3.3.4**
- **MyBatis** - 데이터베이스 ORM
- **MariaDB** - 데이터베이스
- **Elasticsearch** - 검색 엔진
- **Swagger/OpenAPI 3** - API 문서화

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 멀티 컨테이너 관리
- **Maven** - 빌드 도구

## 📚 API 명세

### 기본 정보
- **Base URL**: `http://localhost:58080`
- **Content-Type**: `application/json`
- **Swagger UI**: http://localhost:58080/swagger-ui/index.html

### 공통 응답 형식
모든 API는 `ResponseFormat<T>` 형태로 응답합니다.

```json
{
  "success": true,
  "message": "성공 메시지",
  "data": <응답 데이터>
}
```

### 📋 1. 민원 분석 API (`/handles`)

#### 1.1 민원 분석 상세 조회
- **URL**: `GET /handles/detail`
- **설명**: 민원 분석 상세 정보를 조회합니다
- **Parameters**:
  - `complaintKey` (String, required): 민원 키

**Response**:
```json
{
  "success": true,
  "data": {
    "complaintKey": "string",
    "pinNo": "string",
    "systemKey": "string", 
    "faultKey": 1,
    "user": "string",
    "context": "string"
  }
}
```

#### 1.2 민원 분석 등록
- **URL**: `POST /handles/insert`
- **설명**: 새로운 민원 분석을 등록합니다

**Request Body**:
```json
{
  "complaintKey": "string",
  "pinNo": "string",
  "systemKey": "string",
  "faultKey": 1,
  "user": "string",
  "context": "string"
}
```

#### 1.3 민원 분석 수정
- **URL**: `POST /handles/update`
- **설명**: 기존 민원 분석을 수정합니다

**Request Body**:
```json
{
  "complaintKey": "string",
  "pinNo": "string",
  "systemKey": "string",
  "faultKey": 1,
  "user": "string",
  "context": "string"
}
```

#### 1.4 민원 분석 삭제
- **URL**: `POST /handles/delete`
- **설명**: 기존 민원 분석을 삭제합니다

**Request Body**:
```json
{
  "complaintKey": "string"
}
```

### ⚠️ 2. 주요 장애 사항 관리 API (`/faults`)

#### 2.1 장애사항 목록 조회
- **URL**: `GET /faults/list`
- **설명**: 주요 장애사항 목록을 조회합니다

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": 1,
      "label": "네트워크 장애"
    }
  ]
}
```

#### 2.2 장애사항 등록
- **URL**: `POST /faults/insert`
- **설명**: 새로운 장애사항을 등록합니다

**Request Body**:
```json
{
  "context": "장애 내용",
  "user": "등록자"
}
```

#### 2.3 장애사항 수정
- **URL**: `POST /faults/update`
- **설명**: 기존 장애사항을 수정합니다

**Request Body**:
```json
{
  "key": 1,
  "context": "수정된 장애 내용",
  "user": "수정자"
}
```

#### 2.4 장애사항 삭제
- **URL**: `POST /faults/delete`
- **설명**: 기존 장애사항을 삭제합니다 (논리삭제)

**Request Body**:
```json
{
  "key": 1,
  "user": "삭제자"
}
```

### 🔍 3. 시스템 조회 API (`/systems`)

#### 3.1 시스템 위치 목록 조회
- **URL**: `GET /systems/locationList`
- **설명**: 터미널 내/외부 시스템 위치 목록을 조회합니다

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": "I",
      "label": "내부"
    },
    {
      "value": "E", 
      "label": "외부"
    }
  ]
}
```

#### 3.2 시스템 상세 목록 조회
- **URL**: `GET /systems/detailList`
- **설명**: 터미널 내/외부 상세 시스템 목록을 조회합니다
- **Parameters**:
  - `systemLoc` (String, required): 시스템 위치 (I: 내부, E: 외부)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "value": "SYS001",
      "label": "게이트 시스템"
    }
  ]
}
```

### 📊 4. 민원 분석 기반 통계 관리 API (`/report`)

#### 4.1 통계 조회
- **URL**: `POST /report/getReport`
- **설명**: 민원 분석 기반으로 테이블 및 통계 데이터를 조회합니다

**Request Body**:
```json
{
  "fromDate": "2024-01-01",
  "toDate": "2024-12-31"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "total": {
      "장애": 10,
      "일반 문의": 5
    },
    "table": {
      "total": [
        {
          "systemLoc": "전체 시스템",
          "cnt": 15
        }
      ],
      "detail": [
        {
          "systemLoc": "내부시스템 장애",
          "systemDtl": "게이트 시스템",
          "fault": "네트워크 장애",
          "faultCnt": 3
        }
      ]
    }
  }
}
```

### 📌 5. PIN No 조회 API (`/pinNo`)

#### 5.1 Service Key 목록 조회
- **URL**: `GET /pinNo/list`
- **설명**: 민원 ID 기반으로 Service Key 목록을 조회합니다
- **Parameters**:
  - `complaintKey` (String, required): 민원 키

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "pinNo": "PIN001",
      "serviceKey": "SERVICE_KEY_001"
    }
  ]
}
```

---

### 공통 에러 응답

```json
{
  "success": false,
  "message": "에러 메시지",
  "data": null
}
```

#### 주요 에러 코드
- **400 Bad Request**: 잘못된 요청 파라미터
- **404 Not Found**: 요청한 리소스를 찾을 수 없음
- **500 Internal Server Error**: 서버 내부 오류


## 📁 프로젝트 구조

```
chainportal-control-complaint-handling/
├── src/
│   ├── main/
│   │   ├── java/kr/co/chainportal/allcone_control_system/
│   │   │   ├── handling/         # 민원 관리 패키지
│   │   │   │   ├── controller/   # REST Controllers
│   │   │   │   ├── service/      # 비즈니스 로직
│   │   │   │   ├── mapper/       # MyBatis Mappers
│   │   │   │   ├── dto/          # Data Transfer Objects
│   │   │   │   └── vo/           # Value Objects
│   │   │   └── config/           # 설정
│   │   └── resources/
│   │       ├── mapper/           # MyBatis XML
│   │       └── sql/              # 스키마/데이터
│   └── test/
├── docker-compose.yaml
├── dev-docker-compose.yaml
├── Dockerfile
├── deploy.sh
└── pom.xml
```

## 🚀 설치 및 실행

### 사전 요구사항
- Java 17 이상
- Docker & Docker Compose
- Maven 3.9.6 이상

### 실행 방법
```bash
# 개발 환경
./deploy.sh -p dev

# 프로덕션 환경
./deploy.sh -p prod
```

### 포트 설정
- **개발 환경**: 58080
- **프로덕션 환경**: 58080