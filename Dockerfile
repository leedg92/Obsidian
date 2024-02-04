FROM apache/airflow:2.2.4

USER root

RUN apt-get update
RUN apt-get install wget -y
RUN apt-get install zip -y
WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/215000/instantclient-basic-linux.x64-21.5.0.0.0dbru.zip
RUN unzip -o /opt/oracle/instantclient-basic-linux.x64-21.5.0.0.0dbru.zip
RUN apt-get install libaio1
RUN sh -c "echo /opt/oracle/instantclient_21_5 > /etc/ld.so.conf.d/oracle-instantclient.conf"
RUN ldconfig

USER airflow
