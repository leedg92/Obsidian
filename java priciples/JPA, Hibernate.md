# JPA/Hibernate 핵심 개념

## JPA와 Hibernate 개요

### JPA(Java Persistence API)

- **정의**: 자바 애플리케이션에서 관계형 데이터베이스를 사용하는 방식을 정의한 인터페이스
- **목적**: 객체 지향 프로그래밍과 관계형 데이터베이스 간의 패러다임 불일치 해결
- **특징**: 자바 ORM 기술 표준, 인터페이스 모음(명세)으로 구현체가 필요

### Hibernate

- **정의**: JPA 명세의 구현체(implementation)
- **특징**:
    - JPA 인터페이스를 구현한 ORM(Object-Relational Mapping) 프레임워크
    - 가장 널리 사용되는 JPA 구현체
    - JPA보다 더 많은 기능 제공
- **관계**: 모든 Hibernate 기능은 JPA를 포함하지만, 모든 JPA 기능이 Hibernate인 것은 아님

## 영속성 컨텍스트(Persistence Context)

### 개념

- **정의**: 엔티티를 영구 저장하는 환경
- **쉬운 설명**: 애플리케이션과 데이터베이스 사이에서 엔티티를 관리하는 메모리 영역
- **생명주기**: EntityManager를 통해 관리되며, 트랜잭션 범위에서 동작

### 엔티티 상태

1. **비영속(New/Transient)**: 영속성 컨텍스트와 관련 없는 상태
2. **영속(Managed)**: 영속성 컨텍스트에 저장된 상태
3. **준영속(Detached)**: 영속성 컨텍스트에 있다가 분리된 상태
4. **삭제(Removed)**: 삭제된 상태

### 영속성 컨텍스트의 이점

1. **1차 캐시**
    
    - 동일 트랜잭션 내에서 중복 데이터베이스 조회 방지
    - 예시:
    
    ```java
    // 첫 번째 조회: DB에서 가져옴
    User user1 = entityManager.find(User.class, 1L);
    // 두 번째 조회: 캐시에서 가져옴 (DB 접근 없음)
    User user2 = entityManager.find(User.class, 1L);
    ```
    
2. **동일성(Identity) 보장**
    
    - 같은 엔티티 인스턴스 반환 보장
    - 예시: `user1 == user2` (같은 객체 참조)
3. **트랜잭션을 지원하는 쓰기 지연(Transactional Write-Behind)**
    
    - SQL을 바로 실행하지 않고 모았다가 트랜잭션 커밋 시점에 실행
    - 예시:
    
    ```java
    entityManager.persist(user1); // SQL 실행 안 함
    entityManager.persist(user2); // SQL 실행 안 함
    transaction.commit(); // 이 시점에 모든 SQL 실행
    ```
    
4. **변경 감지(Dirty Checking)**
    
    - 엔티티 수정 시 자동으로 변경 감지
    - 예시:
    
    ```java
    User user = entityManager.find(User.class, 1L);
    user.setName("New Name"); // 직접 update 호출 불필요
    transaction.commit(); // 변경 감지 후 update SQL 실행
    ```
    
5. **지연 로딩(Lazy Loading)**
    
    - 연관된 엔티티를 실제 사용 시점에 로딩
    - 예시: `user.getOrders()`를 호출할 때 orders 테이블 조회

## N+1 문제

### 개념

- **정의**: 연관 관계가 있는 엔티티를 조회할 때 1번의 쿼리로 N개의 레코드를 가져온 후, 각 레코드마다 연관된 엔티티를 조회하기 위해 N번의 추가 쿼리가 발생하는 문제

### 발생 원인

1. **기본적으로 지연 로딩 사용**: 연관 엔티티를 실제 사용할 때 추가 쿼리 발생
2. **즉시 로딩에서도 발생 가능**: JPQL 사용 시 일대다 관계에서 발생

### 예시

```java
// N+1 문제 발생 예시
@Entity
public class Team {
    @Id @GeneratedValue
    private Long id;
    
    private String name;
    
    @OneToMany(mappedBy = "team", fetch = FetchType.LAZY)
    private List<Member> members = new ArrayList<>();
}

@Entity
public class Member {
    @Id @GeneratedValue
    private Long id;
    
    private String name;
    
    @ManyToOne
    private Team team;
}

// 다음 코드 실행 시:
List<Team> teams = em.createQuery("select t from Team t", Team.class)
    .getResultList();

// 1. 우선 "select t from Team t" 쿼리 1번 실행
// 2. 팀 목록 순회하면서 members 접근 시 추가 쿼리 발생
for (Team team : teams) {
    System.out.println("Team: " + team.getName());
    // 여기서 추가 쿼리 발생 (N번)
    for (Member member : team.getMembers()) {
        System.out.println("Member: " + member.getName());
    }
}
```

### 해결 방법

1. **페치 조인(Fetch Join)**
    
    - JPQL에서 연관 엔티티를 함께 조회
    
    ```java
    List<Team> teams = em.createQuery(
        "select t from Team t join fetch t.members", Team.class)
        .getResultList();
    ```
    
2. **EntityGraph**
    
    - 엔티티 그래프로 함께 조회할 속성 지정
    
    ```java
    @EntityGraph(attributePaths = {"members"})
    @Query("select t from Team t")
    List<Team> findAllWithMembers();
    ```
    
3. **BatchSize 설정**
    
    - 여러 엔티티를 한번에 조회하도록 설정
    
    ```java
    @OneToMany(mappedBy = "team")
    @BatchSize(size = 100)
    private List<Member> members;
    
    // 또는 글로벌 설정
    // hibernate.default_batch_fetch_size=100
    ```
    
4. **DTO로 직접 조회**
    
    - 필요한 데이터만 조회하여 DTO로 변환
    
    ```java
    @Query("select new com.example.TeamDto(t.id, t.name) from Team t")
    List<TeamDto> findAllDto();
    ```
    
5. **@Fetch(FetchMode.SUBSELECT)**
    
    - 서브 쿼리를 사용하여 컬렉션 로딩
    
    ```java
    @OneToMany(mappedBy = "team")
    @Fetch(FetchMode.SUBSELECT)
    private List<Member> members;
    ```
    

## 지연 로딩(Lazy Loading)과 즉시 로딩(Eager Loading)

### 지연 로딩(Lazy Loading)

- **개념**: 연관된 엔티티를 실제 사용 시점에 로딩
- **설정 방법**: `fetch = FetchType.LAZY`
- **장점**:
    - 초기 로딩 시간 단축
    - 메모리 사용량 최적화
    - 필요한 데이터만 로딩
- **단점**:
    - N+1 문제 발생 가능
    - 세션 종료 후 사용 시 LazyInitializationException 발생

```java
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.LAZY)
    private Team team;
}
```

### 즉시 로딩(Eager Loading)

- **개념**: 엔티티 조회 시 연관된 엔티티도 함께 로딩
- **설정 방법**: `fetch = FetchType.EAGER`
- **장점**:
    - 연관 엔티티를 바로 사용 가능
    - 프록시 관련 문제 없음
- **단점**:
    - 불필요한 데이터도 함께 로딩되어 성능 저하
    - 조인으로 인한 쿼리 복잡성 증가
    - JPQL 사용 시 N+1 문제 여전히 발생 가능

```java
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.EAGER)
    private Team team;
}
```

### 적절한 사용 상황

#### 지연 로딩이 적합한 경우

- **대부분의 상황에서 기본 전략으로 사용**
- 자주 함께 사용되지 않는 연관 관계
- 대용량 데이터나 컬렉션(일대다, 다대다)
- 필요에 따라 페치 조인으로 최적화

```java
@OneToMany(mappedBy = "member", fetch = FetchType.LAZY)
private List<Order> orders; // 사용자 정보만 보는 경우가 많다면 지연 로딩이 좋음
```

#### 즉시 로딩이 적합한 경우

- 항상 함께 사용되는 연관 관계
- 작은 크기의 데이터(참조 테이블 등)
- 변경 가능성이 낮은 데이터

```java
@ManyToOne(fetch = FetchType.EAGER)
private Address address; // 사용자를 조회할 때 항상 주소가 필요한 경우
```

### 실무 권장 사항

- **모든 연관 관계에 지연 로딩 설정을 기본으로 사용**
- 필요한 경우에만 페치 조인 등으로 최적화
- `@ManyToOne`, `@OneToOne`의 기본값은 EAGER이므로 LAZY로 명시적 변경 권장
- `@OneToMany`, `@ManyToMany`의 기본값은 LAZY이므로 그대로 사용

```java
// 권장 패턴
@Entity
public class Member {
    @ManyToOne(fetch = FetchType.LAZY)  // 명시적으로 LAZY 설정
    private Team team;
    
    @OneToMany(mappedBy = "member")  // 기본값 LAZY 사용
    private List<Order> orders;
}
```

JPA와 Hibernate를 적절히 활용하면 객체 지향적인 설계를 유지하면서도 데이터베이스와의 효율적인 상호작용이 가능합니다. 특히 영속성 컨텍스트의 다양한 이점을 활용하고, N+1 문제를 해결하며, 적절한 로딩 전략을 선택하는 것이 중요합니다.