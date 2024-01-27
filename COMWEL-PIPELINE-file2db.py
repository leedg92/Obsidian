import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import cx_Oracle
import os
import csv
import logging


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'COMWEL-PIPELINE'
default_args = {
    'owner': 'LDG',
    'start_date': datetime(2023, 10, 6, tzinfo=KST),
    #'retries': 1,
    #'retry_delay': timedelta(minutes=5),
    'catchup': False,
}


# CREATE DAG
dag = DAG(dag_id=dag_id,
          default_args=default_args,
          #run daily at 8AM
          schedule_interval='0 8 * * *',
          #run once
          #schedule_interval='@once',  
          tags=['file2db', 'comwelFile_to_hrdDoctor_REAL', 'INSERT'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)


def read_from_source_file(**kwargs):
    execute_date_range = ''
    source_data_rows = 0
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    query = "SELECT MAX(exec_date) from HRD_BSK_PRC_LOG where proc_id = 'COMWEL' and proc_success_yn = 'Y'"
    last_exec_date = hrdDoctor_DEV_hook.get_first(query)[0]
    print(".....")
    print(last_exec_date)
    print(".....")
    # exec_date( data from logtable) -> not plus 1 day due to reading last day file 
    if last_exec_date != None:
        last_exec_date
    else:
        last_exec_date = datetime.now()- timedelta(1)
        
    # today
    file_drop_date = datetime.now()        
    
    
    if last_exec_date != None and last_exec_date.strftime("%y%m%d") != (file_drop_date - timedelta(1)).strftime("%y%m%d"):
        execute_date_range = f'{last_exec_date.strftime("%y%m%d")}~{file_drop_date.strftime("%y%m%d")}'
        # looping from last_exec_date to today
        date_range = [last_exec_date + timedelta(days=x) for x in range(0, (file_drop_date-last_exec_date).days)]
    else:
        execute_date_range = f'{file_drop_date.strftime("%y%m%d")}'
        date_range = [last_exec_date]
    
    print((file_drop_date-last_exec_date).days)
    

     
   
    print(date_range)
    file_prefixes = ["KAA001MT_IFS_", "KAB048MT_IFS_", "KAB055MT_IFS_"]       
    file_dir = "/LMS"   

    aggregated_data = {prefix: [] for prefix in file_prefixes}

    for date in date_range:
        date_str = date.strftime("%Y%m%d")
        print(date_str)

        for file_prefix in file_prefixes:
            target_file_name = file_prefix + date_str
            for file_name in os.listdir(file_dir):                
                if target_file_name in file_name:
                    print(f"filename ::: {file_name}")
                    
                    file_path = os.path.join(file_dir, file_name)
                    with open(file_path, 'r', encoding='ms949', errors='replace') as file:
                        reader = csv.reader(file, delimiter='|',quoting=csv.QUOTE_NONE)
                        rows = [row + [f'{date_str}'] for row in reader]

                        # add data to aggregated_data
                        aggregated_data[file_prefix].extend(rows)

    # XCom push
    for file_prefix, rows in aggregated_data.items():
        source_data_rows += len(rows)
                      
        print(f"Sending {len(rows)} rows for prefix {file_prefix}")
        kwargs['ti'].xcom_push(key=f'{file_prefix}data', value=rows)
        
    print(f'source_data_rows ::: {source_data_rows}')
    kwargs['ti'].xcom_push(key='execute_date_range', value=execute_date_range)
    kwargs['ti'].xcom_push(key='source_data_rows', value=source_data_rows)

 
  
  

def insert_into_target_db(**kwargs):

        
    inserted_data_rows = 0
    KAA001MT_IFS_data = kwargs['ti'].xcom_pull(key='KAA001MT_IFS_data', task_ids='t_read_from_source_file')
    KAB048MT_IFS_data = kwargs['ti'].xcom_pull(key='KAB048MT_IFS_data', task_ids='t_read_from_source_file')
    KAB055MT_IFS_data = kwargs['ti'].xcom_pull(key='KAB055MT_IFS_data', task_ids='t_read_from_source_file')
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    connection = hrdDoctor_DEV_hook.get_conn()
    cursor = connection.cursor()    
    

    # insert original data to temp table 
    for row in KAA001MT_IFS_data:
        try:              
            connection.commit()                  
            cursor.execute(
                    """   INSERT INTO IFS_CM_CORP
                         VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,
                          	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32, :33) """, row                                                        
                )
            
                        
            inserted_data_rows += 1
        except Exception as e:
            print("error found at KAA001MT_IFS_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")
            continue   
    print(inserted_data_rows)  
    
          
    for row in KAB048MT_IFS_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_CM_PRI_SUP
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at KAB048MT_IFS_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)
        
    
    for row in KAB055MT_IFS_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_CM_SELF_EMP
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6, :7, :8, :9, :10, :11, :12) """, row                                                        
                )
            inserted_data_rows += 1
        except Exception as e:
            print("error found at KAB055MT_IFS_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")
            continue             
    print(inserted_data_rows)            
    connection.commit()
    
    
    execute_date_range = kwargs['ti'].xcom_pull(key='execute_date_range', task_ids='t_read_from_source_file')
    source_data_rows = kwargs['ti'].xcom_pull(key='source_data_rows', task_ids='t_read_from_source_file')
    
    
    log_query = f"""insert into 
                    HRD_BSK_CRAWLING_LOG
                    (CRAWLING_DATA_ROW,INSERTED_DATA_ROW,CRAWLING_DATA_RANGE,LOGFILE_PATH,TARGET) 
                    values 
                    ({source_data_rows},{inserted_data_rows},'{execute_date_range}','/home/saltlux/airflow/logs/dag_id=COMWEL-PIPELINE/','COMWEL')"""
    print(log_query)
    hrdDoctor_DEV_hook.run(log_query)


def call_proc(**kwargs):
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    conn = hrdDoctor_DEV_hook.get_conn()
    cursor = conn.cursor()        
    
    cursor.callproc("BSK_PRC_CM_DATA_OGNZ") 
    conn.close()
    cursor.close()


# Python Operator
# TASK : CALL PROC
t_call_proc = PythonOperator(
    task_id='t_call_proc',
    python_callable=call_proc,
    provide_context=True, 
    dag=dag,
)


# Python Operator
# TASK : READ FILE  
t_read_from_source_file = PythonOperator(
    task_id='t_read_from_source_file',
    python_callable=read_from_source_file,
    provide_context=True, 
    dag=dag,
)


# Python Operator
# TASK : CREATE AND INSERT INTO TEMP TABLE IN TARGET DB
t_insert_into_target_db = PythonOperator(
    task_id='t_insert_into_target_db',
    python_callable=insert_into_target_db,
    provide_context=True, 
    dag=dag,
)



# task flow
t_start >> t_read_from_source_file  >> t_insert_into_target_db >> t_call_proc  >> t_end
