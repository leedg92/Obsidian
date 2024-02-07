
#### TODO
1. CMS 자체  스키마 생성 및 디비 테이블 생성 
2. 인천대학교 프로젝트 소스 이관(테이블 에러 나도록 ? 혹은 테이블 에러부분 주석 처리?)(디비 - 정채우 주임(01045681778) , 소스 - 이주호 주임)
3. 개발서버에 깡통 CMS 개발환경 세팅
4. 

#### DONE
 1. aipknu 데이터베이스에 적재 및 서치스튜디오 설정에 디비 세팅 이분화(aipknu, aisearch)
 2. 이주호주임에게 받은 인천대 소스 세팅
	 - 이 과정에서 학사디비(INUDB, STARINUDB)의 디비커넥션은 주석처리함(이동근 주석 으로 통일)
3. 인천대 학생의 정보와 관련되어서 돌아가는 비즈니스 로직은 우선 메인화면으로 보내줄때만 주석 처리해놨음(추후에 어떻게 처리할지 정해야할듯)......씹 절대 메이븐 업데이트 하지말자.... 절대로 하지말자..
4. 개발 리눅스 서버에 깡통 CMS 개발환경 세팅 - user : aipknu / pw : aipknu1!
	- server.xml에 connector(8009)부분에 secretRequired="false"를 추가함



#### 정리
 - 개발환경과 인천대학교 참고 디비 변경 법
	 - 192.168.110.121(root/salt01!) 푸티 접속 후 /home/aisearch/searchstudio로 경로 이동
	       ![[Pasted image 20240206122704.png]]
	     이 세개 폴더의 conf 폴더 안의 database.properties를 vi로 열고 주석을 해제하면 db를 바꿀 수 있다. 
	     이후 startup-unix 폴더로 이동해 .sh파일을 모두 restart한다 (파일명 restart)

- 리눅스 가동 포트 확인법 : sudo lsof -i :\[포트번호]
- 리눅스 가동 포트 죽이기: sudo kill -9 \[포트번호]

- 리눅스 서버 톰캣 8088포트 열기
	 1. sudo firewall-cmd --zone=public --add-port=8088/tcp --permanent (방화벽 영구적으로 열기)
	 2. sudo firewall-cmd --reload (방화벽 규칙 리로드)
	 3. sudo firewall-cmd --list-all (변경사항 확인)




자바버전
톰캣
마리아디비버전
오라클디비버전

api호출방법 명시