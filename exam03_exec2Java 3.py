import os
import sys
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator  import BashOperator


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'exam03-exec2Java'
default_args = {
    'owner': 'aaron',
    'start_date': datetime(2023, 8, 4, tzinfo=KST),
    'catchup': False,
}

# DAG CREATE
dag = DAG(dag_id=dag_id,
          default_args=default_args,
          schedule_interval='@once',
          tags=['BashOperator', 'example'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)


t_exec_to_java = BashOperator(
    task_id='t_exec_to_java',
    bash_command='java -version',
    dag=dag,
)


t_start >> t_exec_to_java >> t_end