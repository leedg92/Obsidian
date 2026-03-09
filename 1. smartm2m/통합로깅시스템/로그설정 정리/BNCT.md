### BNCT

### 1. 로그 라이브러리

**Logback**

- Spring Boot 2.2.2에 기본 내장 (`spring-boot-starter` 포함)
- SQL 로깅용 **log4jdbc-log4j2-jdbc4.1** 추가 사용

### 2. 버전

|라이브러리|버전|
|---|---|
|Logback|Spring Boot 2.2.2 내장 (1.2.3)|
|log4jdbc-log4j2-jdbc4.1|**1.16**|

### 3. logback-spring.xml

Plain Text

```
<?xml version="1.0" encoding="UTF-8"?><configuration>    <include resource="org/springframework/boot/logging/logback/defaults.xml" />    <include resource="org/springframework/boot/logging/logback/console-appender.xml" />    <property name="LOG_PATH_NAME" value="data.log" />    <!-- SQL Debugger 변수 지정 -->    <logger name="jdbc.sqlonly" level="OFF" />    <logger name="jdbc.sqltiming" level="info" />    <logger name="jdbc.resultsettable" level="info" />    <logger name="jdbc.audit" level="OFF" />    <logger name="jdbc.resultset" level="OFF" />    <logger name="jdbc.connection" level="OFF" />    <springProperty scope="context" name="DB_DRIVER" source="remote-db.datasource.driver-class-name" />    <springProperty scope="context" name="DB_URL" source="remote-db.datasource.url" />    <springProperty scope="context" name="DB_USER" source="remote-db.datasource.username" />    <springProperty scope="context" name="DB_PASSWORD" source="remote-db.datasource.password" />    <!-- FILE Appender -->    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppen
