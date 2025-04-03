
# 부경대학교 프로젝트 세팅 가이드

이 문서는 부경대학교 프로젝트(pknu_ai, pknu_search)의 이클립스 기준 세팅방법 및 SVN 연결방법을 설명합니다.

## 개발 환경 사전 요구사항

- JDK 1.8
- Apache Tomcat 8.5
- Maven
- SVN 클라이언트 (이클립스용 SVN 플러그인 - Subversive 또는 Subclipse)

## pknu_ai 프로젝트 세팅 방법

1. eGovFramework로 변경
    
2. 이클립스에 SVN 플러그인 설치(이미 설치 시 skip)
    - `Help -> Eclipse Marketplace` 메뉴 선택
    - 'SVN' 검색 후 Subversive 또는 Subclipse 설치
    - 설치 후 이클립스 재시작

3. SVN Repository 연결 설정
    - `Window -> Show View -> Other -> SVN -> SVN Repositories` 선택
    - SVN Repositories 뷰에서 오른쪽 클릭 후 `New -> Repository Location` 선택
    - URL: `svn://10.250.124.102/pknu/trunk/pknu_ai`
    - Authentication
        - User: pknu1 (pknu1~pknu8 중 할당받은 계정)
        - Password: pknu1! (pknu1!~pknu8! 중 할당받은 계정의 비밀번호)
    - OK 클릭

4. 프로젝트 체크아웃
    - SVN Repositories 뷰에서 연결된 저장소 확장
    - `trunk/pknu_ai` 폴더 오른쪽 클릭
    - `Checkout...` 선택
    - "Check out as a project in the workspace" 선택 후 Next
    - 프로젝트 이름 확인 후 Finish

5. Java Version 설정
    - 프로젝트(pknu_ai) 우클릭 -> `Build Path -> Configure Build Path`
    - Libraries 탭 선택
    - JRE System Library 선택 -> 우측 Edit 버튼 클릭
    - Alternate JRE 체크 -> Installed JREs... 클릭
    - Add... 클릭 -> 설치된 Java(JDK 1.8) 폴더 선택
    - Apply -> Apply and Close -> Finish

6. Maven 설정
	- 사전 전달받은 PKNU_MAVEN 폴더 경로 확인
    - PKNU_MAVEN 폴더 -> settings.xml 파일 열기
    - settings.xml의 경로 수정(동일 경로의 repository)
    - settings.xml의 `<profiles>`, `<activeProfiles>` 태그 전부 제거
    - 이클립스 Window -> Preference -> Maven 검색 -> User Settings 선택
    - Global Settings, User Settings를 수정한 settings.xml로 변경
    - Apply -> Apply and Close

7. Apache Tomcat 설정
    - 이클립스 하단의 Servers 탭 클릭
    - "No servers are available. Click this link to create a new server..." 클릭
    - Apache -> Tomcat v8.5 Server 선택 -> Next -> Browse
    - 설치된 Tomcat 경로 선택
    - JRE: jdk1.8 선택(Build Path 설정에서 추가한 자바 버전) -> Next
    - pknu_ai 프로젝트 선택 -> Add -> Finish

8. DB Connection 설정
    - server.xml 파일 열기
    - server.xml 하단부의 Context 태그를 README.md *별첨의 Context로 변경

9. globals.properties 설정
    - `globals.properties_dev` 파일 복사 -> `globals.properties`로 동일 경로에 붙여넣기
    - `/home/aipknu/apache-tomcat-8.5.98/webapps/Source/` 검색 -> 로컬PC의 pknu_ai 위치의 경로로 수정
    - `Globals.server.license.key` 검색 -> 할당받은 로컬PC용 라이센스키로 변경
    - 저장

10. 테스트
    - 서버 기동(Tomcat)
        - Tomcat 리소스 경고가 나타나면 context.xml에 `<Resources cachingAllowed="true" cacheMaxSize="100000"/>` 추가
    - 서버 실행 후 http://127.0.0.1:8080/web 접속(또는 localhost)
        - 포트는 자유롭게 변경 가능
    - 부경대 종합정보시스템 화면이 나오면 성공
    - http://127.0.0.1:8080/RBISADM 접속
    - 부경대AI 시스템 관리자 화면이 나오면 성공
    - ID: egovadmin3 / PW: test1234! 로그인 시도
    - 로그인 되면 DB 접속도 성공

## SVN Ignored Resources 설정

SVN에서 버전 관리가 필요 없는 파일들을 제외하려면:

1. `Window -> Preferences -> Team -> Ignored Resources` 메뉴로 이동
2. 기본 설정에 추가로 다음 항목을 추가:
    - `.metadata` (이클립스 워크스페이스 메타데이터)
    - `target/` (빌드 결과물 폴더)
    - `.gitignore` (Git 무시 설정 파일)
    - `*/upload/*.*` (upload 폴더 내 모든 파일)
3. Apply and Close 클릭

## pknu_search(검색) 프로젝트 세팅 방법

1. pknu_search 프로젝트 체크아웃
    - SVN Repositories 뷰에서 오른쪽 클릭 후 `New -> Repository Location` 선택
    - URL: `svn://10.250.124.102/pknu/trunk/pknu_search`
    - Authentication
        - User: pknu1 (pknu1~pknu8 중 할당받은 계정)
        - Password: pknu1! (pknu1!~pknu8! 중 할당받은 계정의 비밀번호)
    - OK 클릭
    - 저장소 확장 후 `trunk/pknu_search` 폴더 오른쪽 클릭
    - `Checkout...` 선택
    - "Check out as a project in the workspace" 선택 후 Next
    - 프로젝트 이름 확인 후 Finish

2. Spring Boot 프로젝트 실행 방법
    - 프로젝트 우클릭 -> `Run As -> Spring Boot App` 선택
    - 또는 프로젝트의 메인 클래스(Application.java 또는 *Application.java) 우클릭 -> `Run As -> Spring Boot App` 선택
    - 콘솔에서 Spring Boot가 시작되는 로그를 확인
    - 기본적으로 8080 포트를 사용하므로, pknu_ai와 동시에 실행하려면 포트 충돌을 피하기 위해 `application.properties` 또는 `application.yml` 파일에서 `server.port=8081`과 같이 포트 설정 필요
    - 브라우저에서 http://localhost:8081 (또는 설정한 포트)로 접속하여 확인

## 참고 사항

1. 두 프로젝트를 동시에 개발할 경우:
    
    - pknu_ai는 Tomcat 서버에서 실행
    - pknu_search는 Spring Boot 내장 서버로 실행
    - 포트 설정이 충돌하지 않도록 주의
2. SVN 커밋 시 불필요한 파일 제외:
    
    - 커밋 대화상자에서 target 폴더, .metadata 등의 파일은 제외
    - Ignored Resources 설정을 통해 자동으로 제외 가능

## 별첨

### 계정 목록
| ID    | PW     |
| ----- | ------ |
| pknu1 | pknu1! |
| pknu2 | pknu2! |
| pknu3 | pknu3! |
| pknu4 | pknu4! |
| pknu5 | pknu5! |
| pknu6 | pknu6! |
| pknu7 | pknu7! |
| pknu8 | pknu8! |

### Context 태그 변경
```xml
<Context docBase="Source" path="/" reloadable="false" source="org.eclipse.jst.jee.server:Source">
    <!-- DEV -->
    <!-- searchadmin -->
    <Resource auth="Container" driverClassName="com.mysql.cj.jdbc.Driver" logAbandoned="true" maxIdle="10" maxTotal="100" maxWaitMillis="10000" minEvictableIdleTimeMillis="60000" name="jdbc/SEARCHDB" password="aisearch" removeAbandonedOnMaintenance="true" removeAbandonedTimeout="300" testOnBorrow="true" testWhileIdle="true" timeBetweenEvictionRunsMillis="10000" type="javax.sql.DataSource" url="jdbc:mysql://192.168.110.121:3306/searchadmin?autoReconnect=true&amp;useUnicode=true&amp;characterEncoding=utf8" username="aisearch" validationQuery="SELECT 1"/>
    <!-- 부경대학교 학사 DB -->
    <Resource auth="Container" driverClassName="oracle.jdbc.driver.OracleDriver" factory="oracle.jdbc.pool.OracleDataSourceFactory" logAbandoned="true" maxActive="100" maxIdle="10" maxWait="10000" minEvictableIdleTimeMillis="60000" name="jdbc/PKNUDB" password="devs1234" removeAbandoned="true" removeAbandonedTimeout="300" timeBetweenEvictionRunsMillis="10000" type="oracle.jdbc.pool.OracleDataSource" url="jdbc:oracle:thin:@203.250.124.177:1521/dev01" user="uni"/>					
    <!-- 부경대학교 ai기반 학사지원 시스템 DB(가칭) -->
    <Resource auth="Container" driverClassName="oracle.jdbc.driver.OracleDriver" factory="oracle.jdbc.pool.OracleDataSourceFactory" logAbandoned="true" maxActive="100" maxIdle="10" maxWait="10000" minEvictableIdleTimeMillis="60000" name="jdbc/RBISDB" password="aiedu24!" removeAbandoned="true" removeAbandonedTimeout="300" timeBetweenEvictionRunsMillis="10000" type="oracle.jdbc.pool.OracleDataSource" url="jdbc:oracle:thin:@203.250.124.177:1521/dev01" user="aiedu"/>
</Context>
```

### SVN에 추적되는 파일 제외하기

Ignored Resources에 선언이 되어있음에도 불구하고 추적되는 파일이 존재할 경우:

- SVN 저장소를 제거하고 다시 체크아웃
- Eclipse 재실행
- 특정 파일만 제외하려면 파일/폴더 우클릭 -> Team -> Add to svn:ignore

### 부경AI 학생 로그인 방법

1. 시스템 접속
    
    - 접속 URL: 루프백 주소(localhost or 127.0.0.1):포트(8080)/RBISADM
    - http://localhost:8080/RBISADM
    - http://127.0.0.1:8080/RBISADM
2. 로그인 정보
    
    - ID: egovadmin3
    - PW: test1234!
3. 학생 검색 및 로그인
    
    1. '서비스관리 > 학사정보조회' 메뉴로 이동
    2. 검색창에 학번 입력 (예: 202312342)
    3. 검색 결과 행의 가장 오른쪽 [로그인] 버튼 클릭
4. 다른 계정으로 전환
    
    4. 헤더의 가장 오른쪽 '권한 새로고침' 버튼 클릭
    5. 새로운 학번 검색 후 로그인 과정 반복

