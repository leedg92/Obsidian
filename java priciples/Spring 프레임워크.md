# Spring 프레임워크 핵심 개념

## IoC와 DI의 개념과 Spring에서의 구현 방식

### IoC(Inversion of Control, 제어의 역전)

- **개념**: 객체의 생성과 생명주기 관리를 개발자가 아닌 프레임워크가 담당
- **쉬운 설명**: 일반적으로 개발자가 직접 객체를 생성하고 관리하지만, IoC에서는 이 '제어권'이 프레임워크로 넘어감
- **장점**:
    - 코드의 결합도 감소
    - 유연성 및 테스트 용이성 향상
    - 코드 재사용성 증가

### DI(Dependency Injection, 의존성 주입)

- **개념**: 객체가 필요로 하는 의존 객체를 외부에서 주입
- **쉬운 설명**: 클래스 내부에서 다른 클래스의 객체를 직접 생성하지 않고, 외부에서 생성된 객체를 받아서 사용
- **유형**:
    1. **생성자 주입**: 생성자를 통한 의존성 주입
    2. **수정자(Setter) 주입**: 수정자 메서드를 통한 주입
    3. **필드 주입**: 필드에 직접 주입 (권장하지 않음)

### Spring에서의 구현 방식

#### IoC 컨테이너

- **BeanFactory**: 기본 IoC 컨테이너, 빈 관리 기능 제공
- **ApplicationContext**: BeanFactory를 확장한 컨테이너, 추가 기능 제공

#### DI 구현 방식

1. **XML 설정 방식**

```xml
<bean id="userService" class="com.example.UserService">
    <constructor-arg ref="userRepository" />
</bean>
<bean id="userRepository" class="com.example.UserRepository" />
```

2. **자바 설정 방식**

```java
@Configuration
public class AppConfig {
    @Bean
    public UserRepository userRepository() {
        return new UserRepository();
    }
    
    @Bean
    public UserService userService() {
        return new UserService(userRepository());
    }
}
```

3. **애노테이션 방식** (가장 일반적)

```java
@Service
public class UserService {
    private final UserRepository userRepository;
    
    // 생성자 주입 (권장)
    @Autowired
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
}

@Repository
public class UserRepository {
    // 구현
}
```

## Spring Bean의 스코프와 라이프사이클

### Bean 스코프

Bean의 스코프는 빈이 생성되고 존재하는 범위를 정의합니다.

#### 주요 스코프 종류

1. **singleton** (기본값)
    
    - 스프링 IoC 컨테이너당 하나의 인스턴스만 생성
    - 모든 요청이 동일한 객체 참조
    - 상태를 공유하므로 상태 변경에 주의
2. **prototype**
    
    - 요청할 때마다 새로운 인스턴스 생성
    - 독립적인 상태가 필요한 경우 사용
3. **request**
    
    - HTTP 요청마다 새로운 인스턴스 생성 (웹 애플리케이션)
    - 요청이 끝나면 소멸
4. **session**
    
    - HTTP 세션마다 하나의 인스턴스 (웹 애플리케이션)
    - 세션이 종료되면 소멸
5. **application**
    
    - ServletContext 라이프사이클 동안 유지 (웹 애플리케이션)

### Bean 라이프사이클

Spring 빈은 정해진 라이프사이클을 따라 생성, 초기화, 소멸됩니다.

#### 주요 단계

1. **인스턴스화**: 빈 객체 생성
2. **의존성 주입**: 필요한 의존성 설정
3. **초기화 콜백**: 빈의 초기화 메서드 호출
4. **사용**: 애플리케이션에서 빈 사용
5. **소멸 콜백**: 빈의 소멸 메서드 호출 (컨테이너 종료 시)

#### 라이프사이클 관리 방법

1. **인터페이스 구현 방식**

```java
public class MyBean implements InitializingBean, DisposableBean {
    @Override
    public void afterPropertiesSet() throws Exception {
        // 초기화 로직
    }
    
    @Override
    public void destroy() throws Exception {
        // 소멸 로직
    }
}
```

2. **애노테이션 방식**

```java
@Component
public class MyBean {
    @PostConstruct
    public void init() {
        // 초기화 로직
    }
    
    @PreDestroy
    public void cleanup() {
        // 소멸 로직
    }
}
```

3. **XML 또는 Java 설정 방식**

```java
@Configuration
public class AppConfig {
    @Bean(initMethod = "init", destroyMethod = "cleanup")
    public MyBean myBean() {
        return new MyBean();
    }
}
```

## AOP의 핵심 개념과 Spring에서의 구현 방법

### AOP(Aspect-Oriented Programming, 관점 지향 프로그래밍)

- **개념**: 애플리케이션의 여러 부분에 걸쳐 있는 공통 관심사(로깅, 트랜잭션, 보안 등)를 분리하여 모듈화
- **쉬운 설명**: 핵심 비즈니스 로직과 부가 기능을 분리하여 코드 중복을 줄이고 유지보수성 향상

### AOP 주요 용어

1. **Aspect**: 여러 클래스에 적용되는 공통 관심사의 모듈화 (로깅, 트랜잭션 등)
2. **Join Point**: 메서드 실행, 예외 처리 등 프로그램 실행 중의 특정 지점
3. **Advice**: 특정 Join Point에서 Aspect가 취하는 행동 (Before, After, Around 등)
4. **Pointcut**: Advice를 적용할 Join Point를 선별하는 표현식
5. **Target**: Advice가 적용되는 객체
6. **Weaving**: Aspect를 Target에 적용하여 새로운 프록시 객체를 생성하는 과정

### Spring AOP 구현 방법

#### 1. 애노테이션 기반 구현

```java
// Aspect 정의
@Aspect
@Component
public class LoggingAspect {
    
    // Pointcut 정의
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceMethods() {}
    
    // Before Advice
    @Before("serviceMethods()")
    public void logBefore(JoinPoint joinPoint) {
        System.out.println("Before method: " + joinPoint.getSignature().getName());
    }
    
    // After Advice
    @After("serviceMethods()")
    public void logAfter(JoinPoint joinPoint) {
        System.out.println("After method: " + joinPoint.getSignature().getName());
    }
    
    // Around Advice
    @Around("serviceMethods()")
    public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        
        Object result = joinPoint.proceed(); // 원래 메서드 실행
        
        long end = System.currentTimeMillis();
        System.out.println("Method execution time: " + (end - start) + "ms");
        
        return result;
    }
    
    // AfterReturning Advice
    @AfterReturning(pointcut = "serviceMethods()", returning = "result")
    public void logAfterReturning(JoinPoint joinPoint, Object result) {
        System.out.println("Method returned: " + result);
    }
    
    // AfterThrowing Advice
    @AfterThrowing(pointcut = "serviceMethods()", throwing = "ex")
    public void logAfterThrowing(JoinPoint joinPoint, Exception ex) {
        System.out.println("Exception in method: " + ex.getMessage());
    }
}
```

#### 2. AOP 활성화

```java
@Configuration
@EnableAspectJAutoProxy
public class AppConfig {
    // 설정
}
```

#### 주요 사용 사례

- **로깅**: 메서드 호출 및 실행 시간 로깅
- **트랜잭션 관리**: `@Transactional`
- **보안 검사**: 메서드 실행 전 권한 확인
- **캐싱**: `@Cacheable`
- **예외 처리**: 공통 예외 처리 로직

## @Component, @Service, @Repository, @Controller의 차이점

이 애노테이션들은 모두 클래스를 Spring Bean으로 등록하는 역할을 하지만, 의미와 사용 목적에 차이가 있습니다.

### @Component

- **기본 개념**: 스프링 관리 컴포넌트를 나타내는 일반적인 스테레오타입 애노테이션
- **사용 시점**: 특정 계층에 속하지 않는 일반적인 스프링 빈을 정의할 때
- **특징**: 다른 스테레오타입 애노테이션의 기본이 되는 애노테이션

### @Repository

- **계층**: 데이터 접근 계층(DAO)
- **추가 기능**: 데이터베이스 예외를 스프링의 통합 예외로 변환
- **사용 시점**: JPA Repository, JDBC 기반 DAO 등 데이터 접근 클래스에 사용
- **예시**:

```java
@Repository
public class UserRepository {
    public User findById(Long id) {
        // 데이터베이스 접근 로직
    }
}
```

### @Service

- **계층**: 서비스 계층, 비즈니스 로직
- **추가 기능**: 현재 특별한 추가 기능은 없으나, 비즈니스 로직임을 명시
- **사용 시점**: 비즈니스 서비스 로직을 구현한 클래스에 사용
- **예시**:

```java
@Service
public class UserService {
    private final UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public User getUserById(Long id) {
        return userRepository.findById(id);
    }
}
```

### @Controller

- **계층**: 프레젠테이션 계층, MVC 패턴의 컨트롤러
- **추가 기능**: 요청 매핑, 응답 처리 등 웹 MVC 특화 기능
- **사용 시점**: 웹 요청을 처리하는 클래스에 사용
- **예시**:

```java
@Controller
public class UserController {
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping("/users/{id}")
    public String getUser(@PathVariable Long id, Model model) {
        User user = userService.getUserById(id);
        model.addAttribute("user", user);
        return "user-details";
    }
}
```

### @RestController

- **특징**: `@Controller` + `@ResponseBody`의 조합
- **추가 기능**: 모든 메서드가 REST API 응답으로 직접 객체 반환 (JSON/XML)
- **사용 시점**: REST API 엔드포인트를 구현할 때
- **예시**:

```java
@RestController
@RequestMapping("/api")
public class UserApiController {
    private final UserService userService;
    
    public UserApiController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getUserById(id);  // 객체가 JSON으로 변환되어 반환
    }
}
```

### 주요 차이점 요약

1. **목적과 의미**:
    
    - 각 애노테이션은 애플리케이션의 다른 계층을 나타냄
    - 코드의 가독성과 의도 명확화에 도움
2. **기술적 차이**:
    
    - `@Repository`: 데이터 접근 예외 변환 기능
    - `@Controller`: 웹 요청 처리 및 뷰 반환 기능
    - `@RestController`: JSON/XML로 객체 직접 반환
3. **내부 동작**:
    
    - 모두 내부적으로 `@Component`를 포함하여 빈으로 등록됨
    - 스프링의 컴포넌트 스캔에 의해 감지되어 IoC 컨테이너에 등록

이러한 계층별 애노테이션을 사용하면 애플리케이션 구조를 더 명확하게 표현할 수 있고, 특정 계층에 맞는 추가 기능을 자동으로 활용할 수 있습니다.