## Nest.js 백엔드 세팅 가이드

### 1. Nest CLI 설치 및 프로젝트 생성

```bash
# Nest CLI 전역 설치
npm install -g @nestjs/cli

# 프로젝트 루트 디렉토리로 이동
cd backend-node

# Nest.js 프로젝트 생성
nest new . --skip-git --package-manager npm
```

프로젝트 생성 중 패키지 매니저를 선택하라는 메시지가 나타나면 npm을 선택합니다.

### 2. 필요한 패키지 설치

```bash
# 기본 의존성 설치
npm install @nestjs/config @nestjs/jwt passport passport-jwt bcrypt class-validator class-transformer 

# PostgreSQL 관련 패키지
npm install @nestjs/typeorm typeorm pg

# Swagger 문서화
npm install @nestjs/swagger swagger-ui-express

# 개발 의존성 설치
npm install -D @types/passport-jwt @types/bcrypt
```

### 3. 포트 설정 변경

`src/main.ts` 파일을 수정하여 포트를 8089로 변경합니다.

### 4. 환경 설정 파일 생성

프로젝트 루트에 `.env` 파일 생성:

```
# 서버 설정
PORT=8089
NODE_ENV=development

# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_DATABASE=community_board

# JWT 설정
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRES_IN=7d
```

### 5. 모듈 구조 설정

Nest.js는 모듈 기반 구조를 사용합니다. 다음과 같은 모듈 구조를 생성합니다:

```
src/
├── main.ts                  # 애플리케이션 진입점
├── app.module.ts            # 루트 모듈
├── auth/                    # 인증 관련 모듈
│   ├── auth.module.ts
│   ├── auth.controller.ts
│   ├── auth.service.ts
│   ├── jwt.strategy.ts
│   └── dto/
│       ├── login.dto.ts
│       └── register.dto.ts
├── users/                   # 사용자 관련 모듈
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── user.entity.ts
│   └── dto/
│       ├── create-user.dto.ts
│       └── update-user.dto.ts
├── community/               # 커뮤니티 관련 모듈
│   ├── community.module.ts
│   ├── posts/               # 게시글 관련
│   │   ├── posts.controller.ts
│   │   ├── posts.service.ts
│   │   ├── post.entity.ts
│   │   └── dto/
│   │       ├── create-post.dto.ts
│   │       └── update-post.dto.ts
│   └── comments/            # 댓글 관련
│       ├── comments.controller.ts
│       ├── comments.service.ts
│       ├── comment.entity.ts
│       └── dto/
│           ├── create-comment.dto.ts
│           └── update-comment.dto.ts
└── common/                  # 공통 유틸리티
    ├── decorators/         # 커스텀 데코레이터
    ├── filters/            # 예외 필터
    ├── guards/             # 인증 가드
    └── interceptors/       # 인터셉터
```

### 6. TypeORM 설정

`app.module.ts`에서 TypeORM을 설정하여 PostgreSQL 데이터베이스에 연결합니다.

### 7. 기본 엔티티 생성

사용자, 게시글, 댓글 등의 기본 엔티티를 생성합니다.

### 8. 인증 시스템 구현

JWT 기반 인증 시스템을 구현합니다. 이는 로그인, 회원가입, 토큰 검증 등의 기능을 포함합니다.

### 9. API 엔드포인트 구현

REST API 엔드포인트를 구현합니다. 각 엔드포인트는 BFF 레이어에서 호출될 수 있도록 설계됩니다.

### 10. 데이터베이스 마이그레이션 설정 (선택사항)

TypeORM 마이그레이션을 설정하여 데이터베이스 스키마를 관리합니다.

### 11. API 문서화

Swagger를 사용하여 API 문서를 자동 생성합니다.

### 12. 테스트 설정

단위 테스트와 E2E 테스트를 위한 설정을 추가합니다.

### 13. 실행 및 빌드 스크립트 설정

`package.json`의 스크립트를 설정하여 개발, 테스트, 빌드, 배포 등의 작업을 간소화합니다.

### 14. 상태 확인 엔드포인트 추가

BFF에서 백엔드 상태를 확인할 수 있는 헬스 체크 엔드포인트를 추가합니다.

### 실행 방법

개발 모드로 실행:

```bash
npm run start:dev
```
