

## 1. 도커 레지스트리 로그인
```
docker login registry.smartm2m.co.kr
Username: m2m
Password: rootPass
```
## 2. BUILD 
```
docker build -t registry.smartm2m.co.kr/chainportal/ccs-history-db:260109-01 .
```

## 2.1 BUILD(자바 Maven GOAL 세팅 시)
```
docker build --build-arg MAVEN_GOAL="package" --build-arg MAVEN_OPTS="-DskipTests" -t registry.smartm2m.co.kr/chainportal/ccs-history-db:260109-01 .
```

## 3. PUSH
```
docker push registry.smartm2m.co.kr/chainportal/ccs-history-db:260109-01
```
