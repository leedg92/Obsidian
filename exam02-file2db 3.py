import os
import sys
import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'exam02-file2db'
default_args = {
    'owner': 'aaron',
    'start_date': datetime(2023, 8, 4, tzinfo=KST),
    'catchup': False,
}
path = "/opt/airflow/dags/"

# DAG CREATE
dag = DAG(dag_id=dag_id,
          default_args=default_args,
          schedule_interval='@once',
          tags=['pythonOperator', 'oracleHook', 'example'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)


def rename_for_file(**kwargs):
    filelist = os.listdir(path)

    for name in filelist:
        if name.find('.') < 0:
            if name.find('_') < 0:
                replaced = name + ".txt"
                print(replaced)
                os.rename(path+'/'+name, path+'/'+replaced)


def read_file_and_insert_to_db(**kwargs):
    filelist = os.listdir(path)

    for f in filelist:
        if f.find('.txt') > 0:
            file_path = path + f

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file does not exist at {file_path}")

            with open(file_path, 'r') as file:
                print(file)
                lines = file.readlines()

            # Split lines into data (assuming data is in CSV format)
            data = [line.strip().split('|') for line in lines]

            hook = OracleHook(oracle_conn_id='oracle-target-conn')
            conn = hook.get_conn()

            insert_query = "INSERT INTO FCT_DEPT (SEQ, DEPT_CD, DEPT_NM, CREATED_DTM) VALUES (:seq, :dept_cd, :dept_nm, TO_DATE(:created_dtm, 'YYYY-MM-DD HH24:MI:SS'))"
            cursor = conn.cursor()

            cursor.executemany(insert_query, [{'SEQ': seq, 'DEPT_CD': dept_cd, 'DEPT_NM': dept_nm, 'CREATED_DTM':created_dtm } for seq, dept_cd, dept_nm, created_dtm in data])
            conn.commit()

            cursor.close()
            conn.close()


t_rename_for_file = PythonOperator(
    task_id='t_rename_for_file',
    python_callable=rename_for_file,
    dag=dag,
)


t_file_to_db_insert = PythonOperator(
    task_id='t_file_to_db_insert',
    python_callable=read_file_and_insert_to_db,
    provide_context=True,
    dag=dag,
)

t_start >> t_rename_for_file >> t_file_to_db_insert >> t_end