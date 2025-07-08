

## 1. 도커 레지스트리 로그인
```
docker login registry.smartm2m.co.kr
Username: m2m
Password: rootPass
```
## 2. BUILD 
```
docker build -t registry.smartm2m.co.kr/bpahealth/chainportal-healthcheck-backend_api:latest .
```
## 3. PUSH
```
docker push registry.smartm2m.co.kr/bpahealth/chainportal-healthcheck-backend_api:latest
```
