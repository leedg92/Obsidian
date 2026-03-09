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

- 변경 전
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <include resource="org/springframework/boot/logging/logback/defaults.xml" />
    <include resource="org/springframework/boot/logging/logback/console-appender.xml" />

    <property name="LOG_PATH_NAME" value="data.log" />

    <!-- SQL Debugger 변수 지정 -->
    <logger name="jdbc.sqlonly" level="OFF" />
    <logger name="jdbc.sqltiming" level="info" />
    <logger name="jdbc.resultsettable" level="info" />
    <logger name="jdbc.audit" level="OFF" />
    <logger name="jdbc.resultset" level="OFF" />
    <logger name="jdbc.connection" level="OFF" />

    <springProperty scope="context" name="DB_DRIVER" source="remote-db.datasource.driver-class-name" />
    <springProperty scope="context" name="DB_URL" source="remote-db.datasource.url" />
    <springProperty scope="context" name="DB_USER" source="remote-db.datasource.username" />
    <springProperty scope="context" name="DB_PASSWORD" source="remote-db.datasource.password" />

    <!-- FILE Appender -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH_NAME}</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_PATH_NAME}.%d{yyyyMMdd}</fileNamePattern>
            <maxHistory>60</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%-5p] [%F] : %m%n</pattern>
        </encoder>
    </appender>

    <!-- JDBC Appender (커스텀) -->
    <appender name="JDBC" class="com.bnctkorea.bcitt.api.common.CustomJDBCAppender">
        <connectionSource class="ch.qos.logback.core.db.DriverManagerConnectionSource">
            <driverClass>${DB_DRIVER}</driverClass>
            <url>${DB_URL}</url>
            <user>${DB_USER}</user>
            <password>${DB_PASSWORD}</password>
        </connectionSource>
    </appender>

    <!-- Async Appender -->
    <appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="JDBC" />
        <queueSize>500</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <neverBlock>true</neverBlock>
    </appender>

    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <layout class="ch.qos.logback.classic.PatternLayout">
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%-5p] [%F] %M \(%L\) : %m%n</pattern>
        </layout>
    </appender>

    <root level="INFO">
        <appender-ref ref="FILE" />
        <appender-ref ref="STDOUT" />
        <!-- <appender-ref ref="JDBC" /> -->
        <appender-ref ref="ASYNC" />
    </root>
</configuration>
```

- 변경 후
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="30 seconds">

    <property name="SERVICE_NAME" value="BNCT"/>
    <property name="LOG_DIR"      value="/app/logs/BNCT"/>
    <property name="LOG_FILENAME" value="BNCT.log"/>

    <logger name="jdbc.sqlonly"        level="OFF" />
    <logger name="jdbc.sqltiming"      level="INFO" />
    <logger name="jdbc.resultsettable" level="INFO" />
    <logger name="jdbc.audit"          level="OFF" />
    <logger name="jdbc.resultset"      level="OFF" />
    <logger name="jdbc.connection"     level="OFF" />

    <springProperty scope="context" name="DB_DRIVER"   source="remote-db.datasource.driver-class-name" />
    <springProperty scope="context" name="DB_URL"      source="remote-db.datasource.url" />
    <springProperty scope="context" name="DB_USER"     source="remote-db.datasource.username" />
    <springProperty scope="context" name="DB_PASSWORD" source="remote-db.datasource.password" />

    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS}|${SERVICE_NAME}|%5p|%c{1}|%m%n</pattern>
        </encoder>
    </appender>

    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/${LOG_FILENAME}</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/${LOG_FILENAME}.%d{yyyy-MM-dd}.%i</fileNamePattern>
            <maxHistory>7</maxHistory>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS}|${SERVICE_NAME}|%5p|%C|%M|%L|%m%n</pattern>
        </encoder>
    </appender>

    <appender name="JDBC" class="com.bnctkorea.bcitt.api.common.CustomJDBCAppender">
        <connectionSource class="ch.qos.logback.core.db.DriverManagerConnectionSource">
            <driverClass>${DB_DRIVER}</driverClass>
            <url>${DB_URL}</url>
            <user>${DB_USER}</user>
            <password>${DB_PASSWORD}</password>
        </connectionSource>
    </appender>

    <appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <appender-ref ref="JDBC" />
        <queueSize>500</queueSize>
        <discardingThreshold>0</discardingThreshold>
        <neverBlock>true</neverBlock>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT"/>
        <appender-ref ref="FILE"/>
        <appender-ref ref="ASYNC"/>
    </root>

</configuration>
```