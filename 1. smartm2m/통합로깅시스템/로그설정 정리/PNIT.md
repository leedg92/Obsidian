### PNIT

### 1. 로그 라이브러리

**Log4j 1.2** (실제 구현체) + **SLF4J** (추상화 레이어)

- 코드에서는 SLF4J API를 통해 로깅 → 실제 출력은 Log4j 1.2가 처리

### 2. 버전

|라이브러리|버전|
|---|---|
|`slf4j-api`|1.6.6|
|`jcl-over-slf4j`|1.6.6|
|`slf4j-log4j12`|1.6.6|
|`log4j`|**1.2.15**|

### 3. log4j.xml

Plain Text

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE log4j:configuration PUBLIC "-//APACHE//DTD LOG4J 1.2//EN" "https://logging.apache.org/log4j/1.2/apidocs/org/apache/log4j/xml/doc-files/log4j.dtd">
<log4j:configuration xmlns:log4j="http://jakarta.apache.org/log4j/">

    <!-- Appenders -->
    <appender name="console" class="org.apache.log4j.ConsoleAppender">
        <param name="Target" value="System.out" />
        <layout class="org.apache.log4j.PatternLayout">
            <param name="ConversionPattern" value="%d{yyyy-MM-dd HH:mm:ss.SSS} %-5p: %c - %m%n" />
        </layout>
    </appender>

    <appender name="file" class="org.apache.log4j.DailyRollingFileAppender">
        <param name="Threshold" value="INFO" />
        <param name="file" value="/data/log/waslog/bctrans/bctrans.log" />
        <param name="append" value="true" />
        <param name="DatePattern" value="'.'yyyy-MM-dd" />
        <layout class="org.apache.log4j.PatternLayout">
            <param name="ConversionPattern" value="%d{yyyy-MM-dd HH:mm:ss.SSS} %-5p: %c - %m%n" />
        </layout>
    </appender>

    <appender name="jdbc" class="com.huni.ittblockchain.common.CustomJDBCAppender">
        <param name="URL" value="jdbc:mysql://133.186.229.131:13306/BPA_TA_LOG?connectionTimeout=10000" />
        <param name="driver" value="com.mysql.jdbc.Driver" />
        <param name="user" value="pnit-logger" />
        <param name="password" value="bpaPNIT01" />
    </appender>

    <appender name="ASYNC" class="org.apache.log4j.AsyncAppender">
        <param name="BufferSize" value="500"/>
        <param name="Blocking" value="false"/>
        <appender-ref ref="jdbc"/>
    </appender>

    <!-- Application Loggers -->
    <logger name="com.huni">
        <level value="info" />
    </logger>

    <!-- 3rdparty Loggers -->
    <logger name="org.springframework">
        <level value="info" />
    </logger>

    <!-- Root Logger -->
    <root>
        <priority value="info" />
        <appender-ref ref="file" />
        <!-- <appender-ref ref="jdbc" /> -->
        <appender-ref ref="ASYNC"/>
    </root>

</log4j:configuration>
```
