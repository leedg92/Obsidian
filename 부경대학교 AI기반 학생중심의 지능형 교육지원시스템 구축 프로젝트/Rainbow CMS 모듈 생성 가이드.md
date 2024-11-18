
## 1. Java 소스 설정
### 위치: `src/main/java/rbs/modules`
- sample 패키지를 복사하여 새로운 모듈명으로 변경
- 폴더명, controller, impl, mapper 모두 변경
- impl 수정사항:
  - `KEY_IDX`를 `IDX`로 변경
  - implements 수정

### 다중 기능 모듈 설정
1. fnIdx 사용 시: 위 내용 그대로 적용
2. confModule 사용 시:
   - 위 내용 적용 + confModule 지정된 모듈 추가 생성
   - 예) clinic 모듈과 clinicDct 모듈(confModule이 clinic)이 있을 경우:
     - clinic 폴더 내 `ClinicController`와 `ClinicDctController` 모두 필요

## 2. XML 설정
### 위치: `src/main/resources/egovframework/sqlmap/mapper/rbs/modules`
1. `모듈이름_SQL_Oracle.xml` 수정:
   - `[<include refid="SAMPLE_TABLE_NAME"/>]` A 제거 및 SAMPLE을 새 모듈명으로 변경
   - selectList, deleteList 쿼리: `SELECT A.*` 형식으로 변경
   - 기본정렬쿼리를 `A.IDX`로 변경
   - `[KEY_IDX_COLUMN]`을 `IDX`로 변경
   - `KEY_IDX`를 `IDX`로 변경

2. `모듈이름File_SQL_Oracle.xml` 수정:
   - `SAMPLE_${fnIdx}_FILE_INFO`를 `모듈이름_${fnIdx}_FILE_INFO`로 변경
   - 나머지 수정사항은 위와 동일

3. `모듈이름Multi_SQL_Oracle.xml` 수정도 동일한 방식 적용

## 3. JSON 설정
### 위치: `WEB-INF/data/rbs/conf/module`
- setting_info.json 수정:
  - idx_name, idx_column 설정
- 항목 수정: items, order, list_search
- format_type, object_type은 RBS_OPTION_INFO 참고

## 4. JSP 설정
### 위치: `WEB-INF/jsp/rbs/modules`
1. 기본 설정:
   - sample 폴더 복사 후 이름 변경
   - 디자인 생성: webapp/resource/rbs에서 busi 복사
   - admDesign과 usrDesign에 default 폴더 복사

2. confModule 사용 시:
   - 디자인 템플릿별로 폴더 구조 생성
   - 자바스크립트 경로 수정
   ```jsp
   <c:if test="${!empty TOP_PAGE}">
     <jsp:include page="${TOP_PAGE}" flush="false">
       <jsp:param name="javascript_page" value="${moduleJspRPath}/[디자인폴더]/view.jsp"/>
     </jsp:include>
   </c:if>
   ```

## 5. 데이터베이스 설정
1. 테이블 생성:
   - board_info, board_file_info, board_multi_info 복사
   - 이름 및 IDX 수정

2. 필수 쿼리 실행:
   ```sql
   -- 모듈 정보 등록
   INSERT INTO RBS_MODULE_INFO (
     MODULE_ID, CONF_MODULE, MODULE_NAME, 
     AN_URL, AN_URL2, UR_URL, UR_URL2, 
     -- 기타 필드...
   ) VALUES (...);

   -- 기능 정보 등록
   INSERT INTO RBS_FN_INFO(
     FN_IDX, MODULE_ID, FN_NAME, ISAPPLY
   ) VALUES (...);
   ```

## 6. 외부 모듈 연동
- ~SearchController.java 생성 (implements ModuleSearchController)
- RequestMapping 설정:
  ```java
  @RequestMapping({
    "/{admSiteId}/menuContents/{usrSiteId}/모듈명",
    "/{admSiteId}/moduleFn/모듈명",
    "/{siteId}/모듈명"
  })
  ```
- ModuleAuth 설정:
  ```java
  @ModuleAuth(name="권한", accessModule="접근할모듈")
  ```