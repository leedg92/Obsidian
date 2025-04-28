## SOLID 원칙

### 1. 단일 책임 원칙 (Single Responsibility Principle)

- **개념**: 하나의 클래스는 하나의 책임만 가져야 함
- **쉬운 설명**: 클래스는 한 가지 일만 해야 합니다
- **예시**: 사용자 정보를 저장하는 `UserRepository` 클래스와 비밀번호 암호화를 담당하는 `PasswordEncoder` 클래스를 분리

```java
// 나쁜 예
public class User {
    private String username;
    private String password;
    
    public void saveToDatabase() { /* DB 저장 로직 */ }
    public void encryptPassword() { /* 암호화 로직 */ }
}

// 좋은 예
public class User {
    private String username;
    private String password;
}

public class UserRepository {
    public void save(User user) { /* DB 저장 로직 */ }
}

public class PasswordEncoder {
    public String encrypt(String password) { /* 암호화 로직 */ }
}
```

### 2. 개방-폐쇄 원칙 (Open-Closed Principle)

- **개념**: 확장에는 열려 있고, 수정에는 닫혀 있어야 함
- **쉬운 설명**: 기존 코드를 변경하지 않고 기능을 추가할 수 있어야 함
- **예시**: 결제 시스템에서 새로운 결제 방식 추가

```java
// 인터페이스 사용으로 확장 가능
public interface PaymentProcessor {
    void processPayment(double amount);
}

public class CreditCardProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        // 신용카드 결제 처리
    }
}

// 나중에 새로운 결제 방식 추가 가능 (기존 코드 수정 없이)
public class PayPalProcessor implements PaymentProcessor {
    @Override
    public void processPayment(double amount) {
        // PayPal 결제 처리
    }
}
```

### 3. 리스코프 치환 원칙 (Liskov Substitution Principle)

- **개념**: 상위 타입 객체를 하위 타입 객체로 치환해도 프로그램이 올바르게 동작해야 함
- **쉬운 설명**: 부모 클래스의 자리에 자식 클래스가 들어가도 문제없이 작동해야 함
- **예시**: 도형의 면적 계산

```java
public class Rectangle {
    protected int width;
    protected int height;
    
    public void setWidth(int width) { this.width = width; }
    public void setHeight(int height) { this.height = height; }
    public int area() { return width * height; }
}

// 잘못된 예 - 정사각형은 가로와 세로가 항상 같아야 함
public class Square extends Rectangle {
    @Override
    public void setWidth(int width) {
        super.setWidth(width);
        super.setHeight(width); // 리스코프 위반
    }
    
    @Override
    public void setHeight(int height) {
        super.setHeight(height);
        super.setWidth(height); // 리스코프 위반
    }
}

// 올바른 접근 - 별도의 인터페이스 사용
public interface Shape {
    int area();
}

public class Rectangle implements Shape {
    // 구현
}

public class Square implements Shape {
    // 구현
}
```

### 4. 인터페이스 분리 원칙 (Interface Segregation Principle)

- **개념**: 클라이언트가 자신이 사용하지 않는 메서드에 의존하지 않아야 함
- **쉬운 설명**: 큰 인터페이스보다 작고 구체적인 여러 인터페이스가 낫다
- **예시**: 프린터 기능 분리

```java
// 나쁜 예 - 너무 많은 기능을 가진 인터페이스
public interface MultiFunctionPrinter {
    void print();
    void scan();
    void fax();
    void copy();
}

// 좋은 예 - 기능별로 분리된 인터페이스
public interface Printer {
    void print();
}

public interface Scanner {
    void scan();
}

public interface Fax {
    void fax();
}

// 필요한 기능만 구현
public class SimplePrinter implements Printer {
    @Override
    public void print() { /* 구현 */ }
}

public class AllInOnePrinter implements Printer, Scanner, Fax {
    @Override
    public void print() { /* 구현 */ }
    @Override
    public void scan() { /* 구현 */ }
    @Override
    public void fax() { /* 구현 */ }
}
```

### 5. 의존관계 역전 원칙 (Dependency Inversion Principle)

- **개념**: 고수준 모듈은 저수준 모듈에 의존하지 않아야 함. 둘 다 추상화에 의존해야 함
- **쉬운 설명**: 구체적인 클래스보다 인터페이스나 추상 클래스에 의존해야 함
- **예시**: 이메일 발송 서비스

```java
// 나쁜 예 - 구체 클래스에 직접 의존
public class NotificationService {
    private EmailSender emailSender = new EmailSender();
    
    public void notify(String message) {
        emailSender.sendEmail(message);
    }
}

// 좋은 예 - 추상화에 의존
public interface MessageSender {
    void sendMessage(String message);
}

public class EmailSender implements MessageSender {
    @Override
    public void sendMessage(String message) {
        // 이메일 전송 로직
    }
}

public class SMSSender implements MessageSender {
    @Override
    public void sendMessage(String message) {
        // SMS 전송 로직
    }
}

public class NotificationService {
    private MessageSender messageSender;
    
    // 의존성 주입
    public NotificationService(MessageSender messageSender) {
        this.messageSender = messageSender;
    }
    
    public void notify(String message) {
        messageSender.sendMessage(message);
    }
}
```

## 그 외 객체지향 원칙

### 1. DRY (Don't Repeat Yourself)

- **개념**: 코드 중복을 피하고 재사용성을 높여야 함
- **쉬운 설명**: 같은 코드를 여러 번 작성하지 말고 한 번만 작성하여 재사용
- **예시**: 공통 유틸리티 메서드 사용

```java
// 나쁜 예
public class OrderService {
    public void processOrder(Order order) {
        // 주문 처리 로직
        String formattedDate = String.format("%d-%02d-%02d", 
            order.getDate().getYear(), 
            order.getDate().getMonthValue(), 
            order.getDate().getDayOfMonth());
        // ...
    }
}

public class InvoiceService {
    public void generateInvoice(Invoice invoice) {
        // 인보이스 생성 로직
        String formattedDate = String.format("%d-%02d-%02d", 
            invoice.getDate().getYear(), 
            invoice.getDate().getMonthValue(), 
            invoice.getDate().getDayOfMonth());
        // ...
    }
}

// 좋은 예
public class DateUtils {
    public static String formatDate(LocalDate date) {
        return String.format("%d-%02d-%02d", 
            date.getYear(), 
            date.getMonthValue(), 
            date.getDayOfMonth());
    }
}

public class OrderService {
    public void processOrder(Order order) {
        String formattedDate = DateUtils.formatDate(order.getDate());
        // ...
    }
}

public class InvoiceService {
    public void generateInvoice(Invoice invoice) {
        String formattedDate = DateUtils.formatDate(invoice.getDate());
        // ...
    }
}
```

### 2. KISS (Keep It Simple, Stupid)

- **개념**: 복잡하게 만들지 말고 간단하게 설계해야 함
- **쉬운 설명**: 필요 이상으로 복잡한 코드를 작성하지 말고 단순하게 유지
- **예시**: 날짜 검증

```java
// 복잡한 코드
public boolean isValidDate(int year, int month, int day) {
    if (month < 1 || month > 12) return false;
    
    boolean isLeapYear = (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
    int[] daysInMonth = {0, 31, isLeapYear ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    return day >= 1 && day <= daysInMonth[month];
}

// 더 단순한 접근
public boolean isValidDate(int year, int month, int day) {
    try {
        LocalDate.of(year, month, day);
        return true;
    } catch (DateTimeException e) {
        return false;
    }
}
```

### 3. 객체지향의 기본 개념

#### 캡슐화

- **개념**: 데이터와 관련 기능을 하나로 묶고, 외부에서 직접 접근하지 못하게 제한
- **쉬운 설명**: 객체의 내부 상태를 보호하고 제어된 방법으로만 접근 허용
- **예시**: 계좌 클래스

```java
public class BankAccount {
    // 내부 데이터는 private으로 캡슐화
    private int accountNumber;
    private double balance;
    
    public BankAccount(int accountNumber) {
        this.accountNumber = accountNumber;
        this.balance = 0;
    }
    
    // 외부에서는 메서드를 통해서만 접근 가능
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
        }
    }
    
    public boolean withdraw(double amount) {
        if (amount > 0 && balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }
    
    public double getBalance() {
        return balance;
    }
    
    public int getAccountNumber() {
        return accountNumber;
    }
}
```

#### 상속

- **개념**: 기존 클래스의 특성을 물려받아 새로운 클래스를 정의
- **쉬운 설명**: 부모 클래스의 기능을 자식 클래스가 재사용하거나 확장함
- **예시**: 직원 클래스 상속

```java
public class Employee {
    protected String name;
    protected double salary;
    
    public Employee(String name, double salary) {
        this.name = name;
        this.salary = salary;
    }
    
    public void work() {
        System.out.println(name + " is working");
    }
    
    public double calculateMonthlyPay() {
        return salary / 12;
    }
}

public class Manager extends Employee {
    private double bonus;
    
    public Manager(String name, double salary, double bonus) {
        super(name, salary);
        this.bonus = bonus;
    }
    
    @Override
    public void work() {
        System.out.println(name + " is managing the team");
    }
    
    @Override
    public double calculateMonthlyPay() {
        return (salary + bonus) / 12;
    }
}
```

#### 다형성

- **개념**: 같은 인터페이스나 메서드가 다른 클래스에서 다르게 동작
- **쉬운 설명**: 같은 메서드 호출이 객체에 따라 다르게 동작하는 것
- **예시**: 도형 클래스

```java
public abstract class Shape {
    public abstract double area();
}

public class Circle extends Shape {
    private double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    public double area() {
        return Math.PI * radius * radius;
    }
}

public class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double area() {
        return width * height;
    }
}

// 다형성 활용
public class ShapeCalculator {
    public double calculateTotalArea(Shape[] shapes) {
        double totalArea = 0;
        for (Shape shape : shapes) {
            // 같은 메서드 호출이지만 객체에 따라 다르게 동작
            totalArea += shape.area();
        }
        return totalArea;
    }
}
```

#### 추상화

- **개념**: 공통적인 속성과 기능을 추출하여 정의
- **쉬운 설명**: 복잡한 시스템에서 핵심적인 개념만 추출하여 간략화
- **예시**: 결제 시스템

```java
// 결제 처리 추상화
public abstract class Payment {
    protected double amount;
    
    public Payment(double amount) {
        this.amount = amount;
    }
    
    // 추상 메서드 - 어떻게 결제할지는 하위 클래스에서 구현
    public abstract boolean processPayment();
    
    // 공통 기능
    public void validateAmount() {
        if (amount <= 0) {
            throw new IllegalArgumentException("결제 금액은 0보다 커야 합니다");
        }
    }
}

public class CreditCardPayment extends Payment {
    private String cardNumber;
    private String expiryDate;
    
    public CreditCardPayment(double amount, String cardNumber, String expiryDate) {
        super(amount);
        this.cardNumber = cardNumber;
        this.expiryDate = expiryDate;
    }
    
    @Override
    public boolean processPayment() {
        validateAmount();
        System.out.println("신용카드 " + cardNumber + "로 " + amount + "원 결제");
        // 결제 처리 로직
        return true;
    }
}

public class BankTransferPayment extends Payment {
    private String accountNumber;
    
    public BankTransferPayment(double amount, String accountNumber) {
        super(amount);
        this.accountNumber = accountNumber;
    }
    
    @Override
    public boolean processPayment() {
        validateAmount();
        System.out.println("계좌 " + accountNumber + "로 " + amount + "원 이체");
        // 이체 처리 로직
        return true;
    }
}
```

이상이 객체지향 프로그래밍의 핵심 원칙들입니다. 이러한 원칙들을 잘 적용하면 유지보수가 쉽고, 확장성이 높은 코드를 작성할 수 있습니다. 면접에서는 이러한 원칙들을 실제 프로젝트에서 어떻게 적용했는지 예시를 들어 설명하면 좋을 것 같습니다.