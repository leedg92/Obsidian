
#### TODO
1. CMS 자체  스키마 생성 및 디비 테이블 생성 
2. 인천대학교 프로젝트 소스 이관(테이블 에러 나도록 ? 혹은 테이블 에러부분 주석 처리?)(디비 - 정채우 주임(01045681778) , 소스 - 이주호 주임)
3. 부경대학교 erd있으면 요청하고 그에 맞춰서 얼추 맞춰놓기
4. .....지금 이클립스에 있는 소스 이거 뭐여

#### DONE
 1. aipknu 데이터베이스에 적재 및 서치스튜디오 설정에 디비 세팅 이분화(aipknu, aisearch)
     -  192.168.110.121(root/salt01!) 푸티 접속 후 /home/aisearch/searchstudio로 경로 이동
       ![[Pasted image 20240206122704.png]]
         이 세개 폴더의 conf 폴더 안의 database.properties를 vi로 열고 주석을 해제하면 db를 바꿀 수 있다. 
         이후 startup-unix 폴더로 이동해 .sh파일을 모두 restart한다 (파일명 restart)
         