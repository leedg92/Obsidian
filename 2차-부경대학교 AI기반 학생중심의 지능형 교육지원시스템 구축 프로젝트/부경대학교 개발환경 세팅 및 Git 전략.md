
***
## 1. 초기 설정

### 이클립스에서 Git 프로젝트 가져오기
- JDK1.8
- Apache Tomcat 8.5
- Maven
  
1. eGovFramework로 변경

2. 이클립스 Git Repositories 뷰 열기
   - Window -> Show View -> Other -> Git -> Git Repositories

3.  GitLab 계정 활성화
   - http://192.168.110.121:40080 접속
   - \*별첨에서 본인에 해당하는 초기 ID / PW 입력 -> 패스워드 변경
   

4. Git Repositories 뷰에서 'Clone a Git repository' 클릭
   - URI: http://192.168.110.121/pknu-project-group/pknu-project.git
   - Port: 40080
   - Authentication
     * User: [GitLab 사용자명]
     * Password: [GitLab 비밀번호]
   - Next -> main 브렌치 선택 -> Next
   - Import all existing Eclispse projects after clone finishes 체크
   - Finish

5. 프로젝트 Import
   - Git Repositories 뷰에서 Working Directory 우클릭
   - Import Projects 선택
   - Import as general project -> Next -> Finish

6. Java Version Setting
   - 프로젝트(Source) 우클릭 -> Build Path -> Libraris탭
   - JRE Stsrem Library 선택 -> 우측 Edit 버튼 클릭
   - Alternate JRE 체크 -> Installed JREs... 클릭
   - Add.. 클릭 -> 설치된 Java(Jdk1.8) 폴더 선택
   - Apply -> Apply and Close -> Finish

7. Maven Setting
   - PKNU_MAVEN 폴더 settings.xml의 경로 수정(동일 경로의 repository) 
   - 이클립스 Window -> Preference -> Maven 검색 -> User Settings 선택
   - Global Settings, User Settings를 수정한 settings.xml로 변경
   - Apply -> Applt and Close

8. Apache Tomcat Setting
   - 이클립스 하단의 Servers 탭 클릭
   - No servers are available. Click 뭐시기 클릭
   - Apache -> Tomcat v8.5 Server 선택 -> Next -> Browse
   - 설치된 Tomcat 경로 선택
   - JRE : jdk1.8 선택(Build Path설정에서 추가한 자바 버전) -> Next
   - Source(rbis4-4.0.0) 선택 -> Add -> Finish

9. DB Connection Setting
   - server.xml 파일 열기
   - server.xml 하단부의 Context 태그를 README.md \*별첨의 Context로 변경

10. globals.properties 설정
   - `globals.properties_dev` 파일 복사 ->  `globals.properties`로 동일 경로에 붙여넣기
   - `/home/aipknu/apache-tomcat-8.5.98/webapps/Source/` 검색 -> 로컬PC의 Source(git clone 한) 위치의 경로로 수정
   - `Globals.server.license.key` 검색 -> 할당받은 로컬PC용 라이센스키로 변경
   - 저장

11. 테스트
   - 서버 기동(Tomcat)
   - 서버 실행 후 http://127.0.0.1:8080/web 접속(or localhost)
     - 포트는 자유롭게 변경하셔도 됩니다.
   - 부경대 종합정보시스템 화면 나오면 성공
   - http://127.0.0.1:8080/RBISADM 접속
   - 부경대AI 시스템 관리자 화면 나오면 성공
   - ID : egovadmin3 / PW : test1234! 로그인 시도
   - 로그인 되면 DB도 접속 성공
   
### Git 사용자 정보 설정(선택)
- 이클립스 우측 상단 Git Perspective에서 우클릭 -> Configure
- user.name "이름"
- user.email "이메일"

***
## 2. 브랜치 전략

### 브랜치 구조
- main: 배포용 브랜치
- feature/*: 기능 개발 브랜치 (예: feature/login, feature/board)

### 새로운 기능 개발 시작
1. main 브랜치에서 새 브랜치 생성
   - 프로젝트 우클릭 -> Team -> Switch To -> New Branch
   - Branch name: feature/[기능명]
   - 'Checkout new branch' 체크
   - Finish

2. 기능 개발 및 커밋
   - 코드 수정
   - Git Staging 뷰에서 변경된 파일 스테이징(+)
   - Commit message 작성
   - "Commit and Push" 클릭

### 메인 브랜치로 병합(Merge)
1. 기능 개발 완료 후
   - 프로젝트 우클릭 -> Team -> Switch To -> main

2. feature 브랜치 병합
   - 프로젝트 우클릭 -> Team -> Merge
   - 병합할 feature 브랜치 선택
   - 충돌 발생 시 해결

3. 배포를 위한 푸시
   - 프로젝트 우클릭 -> Team -> Push to Upstream
   - main 브랜치로 푸시되면 자동 배포 시작

***
## 3. 주요 작업 가이드

### 코드 업데이트
1. main 브랜치 최신화
   - 프로젝트 우클릭 -> Team -> Pull
   - 최신 코드 가져오기

2. feature 브랜치 최신화
   - feature 브랜치로 전환
   - main 브랜치 내용 병합
   - Team -> Merge -> main 선택

### 충돌 해결
1. 충돌 발생 시
   - 충돌 파일 더블클릭
   - 병합 에디터에서 충돌 부분 확인
   - 적절한 코드 선택 또는 수정
   - 저장 후 커밋

### 커밋 메시지 규칙 
- 형식: 
```
  \[YYYYMMDD\] - \[이름\]
  (둘째 줄 공백)
  [유형] 종류 - 내용 (같은 종류이더라도 다른 내용이면 다음 줄에 추가)
```
- 유형:
  * ADD: 새로운 기능 추가
  * FIX: 버그 수정
  * MOD: 코드 수정
  * DOC: 문서 작업
  * CLEAN: 코드 정리
- 예시 :
```
  2024110617 - 이동근
  
  1. [ADD] 비교과상세보기 - 신청 기능 추가
  2. [MOD] 메인 - 로그인 기능 SSO 방식으로 수정
  3. [FIX] 비교과검색 - 검색결과 화면 페이징 버그 수정
  4. [DOC] 설정 - globals.properties의 학생설계전공 알림 메세지 변경
  5. [CLEAN] 전공검색 - 검색기능 코드 리펙토링
  6. [CLEAN] 전공검색 - 불필요한 주석 및 console출력 제거
```

***
## 4. 배포 프로세스

### 자동 배포
- main 브랜치에 push하면 자동으로 Jenkins 파이프라인 실행
- 컴파일된 파일과 리소스가 개발 서버에 자동 배포
  - class, jsp, xml, properties, json 파일들만 배포됨
- globals.properties와 bk/\*.json는 배포에서 제외됨
- 서버 재기동 기능은 추후 내부 협의 후 추가 예정

### 배포 확인
- 개발서버소스 경로: /home/aipknu/apache-tomcat-8.5.98/webapps/Source
- 배포된 파일 확인:
  * WEB-INF/classes: 컴파일된 클래스 파일
  * 루트 디렉토리: jsp, xml, properties 등 리소스 파일
    
### 서버 재기동(변경 가능성 있음)
- 개발서버 재기동 경로:  sudo systemctl tomcat restart
## 5. 주의사항

### 브랜치 관리
- 기능 개발은 반드시 feature 브랜치에서 진행
- main 브랜치는 안정적인 배포 코드만 유지

### 코드 품질
- 각 브랜치에서 충분한 테스트 후 병합
- 이미 이 프로젝트 소스코드는 주석이 이상하게 달렸거나 안달렸지만 앞으로라도 주석 많이 달아주세요.

### 배포 주의
- main 브랜치 푸시 시 자동 배포됨
- 소스 대변경 시 충분한 테스트 후 배포
- 병합 후 소스코드(일부만이라도)가 최신본으로 올라가있는지 확인(저도 제가 구축한 파이프라인을 못 믿겠습니다..)


***

## 별첨


### - 계정목록

|  이름  |    ID     |    PW    |
| :--: | :-------: | :------: |
| 곽홍근  |  hg_kwak  | 1qw2#ER$ |
| 이동근  |  dg_lee   | 1qw2#ER$ |
| 웨일비  |  whalebe  | 1qw2#ER$ |
| 퍼블리셔 | publisher | 1qw2#ER$ |

### - Context 태그 변경

```
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
