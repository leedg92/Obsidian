### 파일 구조도
<sub>- 이하에서 말하는 [모듈명]이란 용어사전 혹은 네이밍 룰에 기반한 기능 구분명입니다. </sub>
##### 1. \*.java
	- [모듈명]Controller
	- [모듈명]Service (abstract)
	- [모듈명]ServiceImpl (implement)
	- [모듈명]Mapper (Data Access Object)
##### 2. \*.xml
	- [모듈명]SQL_Oracle


### Naming Rule
<sub>- 각 메뉴에 대한 파일이 이미 다수 존재하지만 새로 만들때 참고하시면 됩니다.</sub>

##### 1. 사용자화면 / 관리자화면 구분
	- 관리자화면용 모듈
		- java : [모듈명]+ADM+[기능].java 
			- (예: mainAdmController.java)
		- xml : [모듈명]_ADM_SQL_Oracle.xml
			- (예: main_ADM_SQL_Oracle.xml)
	- 사용자화면용 모듈
		- java : [모듈명]+[기능].java 
			- (예: mainController.java)
		- xml : [모듈명]_SQL_Oracle.xml
			- (예: main_SQL_Oracle.xml)


### 백엔드 API호출 URL 설정법
##### 1. 백엔드에서 alias를 선언 후 Model에 add
	- controller의 클래스 매서드인 setCommonPath()를 참고하시면 됩니다.
