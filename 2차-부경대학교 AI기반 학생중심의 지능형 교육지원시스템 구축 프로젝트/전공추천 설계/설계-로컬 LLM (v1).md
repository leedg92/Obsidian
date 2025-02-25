# 전공 추천 시스템 설계

## 1. 개요
- Ollama의 deepseek R1 모델 사용
- 일반 추천과 시뮬레이션 기반 추천
- 동일 입력 데이터에 대한 추천 결과 재사용
- 전공별 교육과정 기반 정확도 향상

## 2. 데이터베이스
```sql
-- 일반 추천용 테이블
CREATE TABLE uni_mj_recom_standard (
    std_no VARCHAR(20) PRIMARY KEY,
    input_data CLOB,          -- 추천에 사용된 데이터 (JSON)
    recommended_majors CLOB,   -- 추천된 전공 코드들 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 시뮬레이션용 테이블
CREATE TABLE uni_mj_recom_simmulation (
    std_no VARCHAR(20) PRIMARY KEY,
    input_data CLOB,                         -- 시뮬레이션에 사용된 데이터 (JSON)
    recommended_majors CLOB,                 -- 추천된 전공 코드들 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### JSON 구조
```json
// input_data
{
    "courses": [수강과목 코드(분반같은건 다 빼고 distinct)],
    "majors": [호출했던 당시의 전공코드] 
}

// recommended_majors
[LLM으로 부터 받았던 전공코드들]
```

## 3. 추천 프로세스
- 테이블만 다르고 결국 두 방식은 같은 프롬프트를 사용
### 일반 추천
1. 현재 데이터 수집
   - 학생의 수강 과목 목록
   - 현재 선택 가능한 전공 목록
   - 각 전공별 교육과정 정보

2. DB 조회
   - std_no로 이전 추천 기록 검색
   - input_data 비교하여 동일하면 저장된 추천 결과 반환
   - 다르면 새로운 추천 프로세스 진행

3. 새로운 추천 생성 시
   - 이전 데이터와 현재 데이터를 포함한 프롬프트 생성
   - LLM 호출 및 결과 upsert
   - 전공 코드 리턴

### 시뮬레이션 기반 추천
1. 데이터 준비
   - 현재 수강 과목 + 관심 과목 목록
   - 현재 선택 가능한 전공 목록
   - 각 전공별 교육과정 정보

2. DB 조회
   - std_no로 시뮬레이션 결과 검색
   - input_data 비교하여 동일하면 저장된 결과 반환
   - 다르면 새로운 시뮬레이션 진행

3. 새로운 시뮬레이션 시
   - 이전 데이터와 현재 데이터를 포함한 프롬프트 생성
   - 결과를 시뮬레이션 테이블에 upsert
   - 전공 코드 리턴

## 4. 프롬프트 구성

### 한글 버전
```
당신은 전공 추천 컨설턴트입니다. 학생들의 수강 이력을 분석하여 가장 적합한 전공을 추천해주세요.

[Rule]
1. 유사한 성격의 교과목이 많을수록 해당 전공 분야의 가중치가 높아집니다
2. 각 전공의 교육과정과 학생의 수강 과목을 비교하여 매칭률이 높은 전공의 가중치가 높아집니다
3. 이전 추천 정보가 있는 경우:
    - 이전 추천 전공의 연관 교과목이 계속 수강되고 있다면 해당 전공의 가중치가 유지됩니다
    - 새로운 교과목들의 성격을 고려하여 추천 전공을 조정합니다
    - 현재 주어진 전공들이 이전과 다른 경우, 유사한 성격의 새로운 전공들로 조정하여 추천합니다
4. 이전 추천 정보가 없는 경우:
    - 현재 수강 과목들의 성격과 전공 교육과정 매칭을 기준으로 추천합니다
5. 아무런 설명 없이 상위 5개 전공 코드만 json 배열 형태로 응답해주세요
   응답 형식 예시: ["MAJOR_CODE1","MAJOR_CODE2","MAJOR_CODE3","MAJOR_CODE4","MAJOR_CODE5"]

[이전 추천 정보]
이전 수강 과목: [
   {"course_code": [교과목코드], "course_nm": [교과목명], "course_description": [교과목 소개]},
]
이전 추천 전공: [전공 코드들]

[현재 데이터]
현재 수강 과목: [
   {"course_code": [교과목코드], "course_nm": [교과목명], "course_description": [교과목 소개]},
]

[전공 정보]
[
   {
      "major_code": [전공코드],
      "major_nm": [전공명],
      "major_description": [전공소개],
      "curriculum": [
         {"course_code": [교과목코드], "course_nm": [교과목명]},
      ]
   }
]
```

### 영문 버전
```
You are a major recommendation consultant. Please analyze students' course history and recommend the most suitable majors.

[Rule]
1. The more similar courses taken, the higher the weight for related majors
2. Higher weights are given to majors with better matches between their curriculum and student's taken courses
3. When previous recommendation exists:
    - Maintain weight for previous majors if related courses continue to be taken
    - Adjust recommendations considering newly added courses
    - When current majors differ from previous ones, adjust recommendations to similar new majors
4. When no previous recommendation:
    - Recommend based on current course characteristics and curriculum matching
5. Return only json array with top 5 major codes without any explanation
   Response Format Example: ["MAJOR_CODE1","MAJOR_CODE2","MAJOR_CODE3","MAJOR_CODE4","MAJOR_CODE5"]

[Previous Recommendation]
Previous Courses: [
   {"course_code": [교과목코드], "course_nm": [교과목명], "course_description": [교과목 소개]},
]
Previous Majors: [전공 코드들]

[Current Data]
Current Courses: [
   {"course_code": [교과목코드], "course_nm": [교과목명], "course_description": [교과목 소개]},
]

[Major Information]
[
   {
      "major_code": [전공코드],
      "major_nm": [전공명],
      "major_description": [전공소개],
      "curriculum": [
         {"course_code": [교과목코드], "course_nm": [교과목명]},
      ]
   }
]
```

## 5. 사용자 인터페이스
1. 일반 추천 탭
   - 현재 수강중인 과목 목록 표시
   - 신규 학생 경우 안내 문구 표시
   - 추천된 전공 코드 표시

2. 시뮬레이션 탭
   - 현재 수강 과목 목록 표시
   - 관심 과목 추가/제거 기능
   - 시뮬레이션 결과 표시

3. 공통 UI 요소
   - 선택 가능한 전공 목록 표시
   - 교과목 검색 및 필터링
   - 결과 표시 영역
   - 전공별 교육과정 조회 기능