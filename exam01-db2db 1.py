import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'exam01-db2db'
default_args = {
    'owner': 'aaron',
    'start_date': datetime(2023, 8, 4, tzinfo=KST),
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    'catchup': False,
}


# CREATE DAG
dag = DAG(dag_id=dag_id,
          default_args=default_args,
          schedule_interval='@once',
          tags=['pythonOperator', 'oracleHook', 'example'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)


def select_from_source_db(**kwargs):
    hook = OracleHook(oracle_conn_id='hrd4u_DEV')
    conn = hook.get_conn()

    qry = """
            SELECT SEQ, DEPT_CD, DEPT_NM, CREATED_DTM
            FROM DIM_DEPARTMENT
            WHERE TO_CHAR(CREATED_DTM, 'YYYY-MM-DD') = TO_CHAR(SYSDATE-3, 'YYYY-MM-DD')
            ORDER BY SEQ, CREATED_DTM
          """
    cursor = conn.cursor()
    cursor.execute(qry)
    result = cursor.fetchall()

    # XCom push
    kwargs['ti'].xcom_push(key='source_data', value=result)


def insert_to_target_db(**kwargs):
    # XCom pull
    source_data = kwargs['ti'].xcom_pull(key='source_data', task_ids='t_select_from_source_db')
    hook = OracleHook(oracle_conn_id='oracle-target-conn')
    conn = hook.get_conn()

    hook.insert_rows(table='FCT_DEPT', rows=source_data, target_fields=['SEQ', 'DEPT_CD', 'DEPT_NM', 'CREATED_DTM'])


# Python Operator
# TASK : SELECT SOURCE DB
t_select_from_source_db = PythonOperator(
    task_id='t_select_from_source_db',
    python_callable=select_from_source_db,
    provide_context=True, 
    dag=dag,
)


# Python Operator
# TASK : INSERT TARGET DB
t_insert_to_target_db = PythonOperator(
    task_id='t_insert_to_target_db',
    python_callable=insert_to_target_db,
    provide_context=True, 
    dag=dag,
)


t_start >> t_select_from_source_db >> t_insert_to_target_db >> t_end
