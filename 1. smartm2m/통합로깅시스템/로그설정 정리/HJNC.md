
- 변경 전
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="30 seconds">
    <property name="SERVICE_NAME" value="tssgateout"/>
    <property name="LOG_FILENAME" value="tssgateout.json.log"/>
    <property name="SPRING_PROFILE" value="prod"/>
    <property name="LOG_DIR" value="/app/logs/tssgateout"/>

    <contextListener class="ch.qos.logback.classic.jul.LevelChangePropagator">
        <resetJUL>true</resetJUL>
    </contextListener>

    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS}|%5p|%X{traceId}|%c{1}|%m%n</pattern>
        </encoder>
    </appender>

    <appender name="File" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/${LOG_FILENAME}</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/${LOG_FILENAME}.%d{yyyy-MM-dd}.%i</fileNamePattern>
            <maxHistory>7</maxHistory>
            <timeBasedFileNamingAndTriggeringPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedFNATP">
                <maxFileSize>100MB</maxFileSize>
            </timeBasedFileNamingAndTriggeringPolicy>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%-5p] [%F] : %m%n</pattern>
        </encoder>
    </appender>

    <root level="INFO">
        <appender-ref ref="STDOUT" />
        <appender-ref ref="File" />
    </root>
</configuration>

```

- 변경 후
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration scan="true" scanPeriod="30 seconds">

    <springProperty name="SERVICE_NAME" source="spring.application.name" defaultValue="None"/>
    <property name="LOG_DIR"      value="/app/logs/${SERVICE_NAME}"/>
    <property name="LOG_FILENAME" value="${SERVICE_NAME}.log"/>

    <contextListener class="ch.qos.logback.classic.jul.LevelChangePropagator">
        <resetJUL>true</resetJUL>
    </contextListener>

    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS}|${SERVICE_NAME}|%5p|%X{traceId}|%c{1}|%m%n</pattern>
        </encoder>
    </appender>

    <appender name="File" class="ch.qos.logback.core.rolling.RollingFileAppender">
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

    <root level="INFO">
        <appender-ref ref="STDOUT"/>
        <appender-ref ref="File"/>
    </root>
</configuration>
```


