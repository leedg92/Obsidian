

## 1. 도커 레지스트리 로그인
```
docker login registry.smartm2m.co.kr
Username: m2m
Password: rootPass
```
## 2. BUILD 
```
docker build -t registry.smartm2m.co.kr/chainportal/ccs-complaint-handling:260109-01 .
```

## 2.1 BUILD(자바 Maven go)

## 3. PUSH
```
docker push registry.smartm2m.co.kr/chainportal/ccs-complaint-handling:260109-01
```
