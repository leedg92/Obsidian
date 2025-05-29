### 체리픽 가져오기
```
git cherry-pick <commit-hash>

*** merge인거 가져올때
git cherry-pick -m 1 <merge-commit-hash>
```

### 브랜치 히스토리
```
*** 10개씩
git log -10 bctrans-prod/containus/develop

*** 한줄로 보기
git log --oneline bctrans-prod/containus/develop

*** 한줄로 10개 보기
git log --oneline -10 bctrans-prod/containus/develop
```