import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import cx_Oracle


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'HRDNET-PIPELINE'
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
          #run daily at 7AM
          schedule_interval='0 7 * * *',
          #run once
          #schedule_interval='@once',  
          tags=['hrd4U_DEV_to_hrdDoctor_REAL', 'IFS_4U_SOJT', 'MERGE', 'db2db'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)



def select_from_source_db(**kwargs): 
    execute_date_range = ''
    source_data_rows = 0
    
    dsn = cx_Oracle.makedsn('165.213.105.97', '1521', sid='HRDC')    
    conn = cx_Oracle.connect(user='mega', password='@mega97!@#', dsn=dsn)
    cursor = conn.cursor()
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    
    query = "SELECT MAX(exec_date) from HRD_BSK_PRC_LOG where proc_id = 'HRDNET' and proc_success_yn = 'Y'"
    last_exec_date = hrdDoctor_DEV_hook.get_first(query)[0]    

    # exec_date( data from logtable)
    if last_exec_date != None:
        last_exec_date = last_exec_date + timedelta(1)
    else:
        last_exec_date = datetime.now()
        
    print(".....")
    print(last_exec_date)
    print(".....")
    
    # today
    today = datetime.now()
    print(today)
    
    if last_exec_date != None and last_exec_date.strftime("%y%m%d") != (today).strftime("%y%m%d"):
        execute_date_range = f'{last_exec_date.strftime("%y%m%d")}~{today.strftime("%y%m%d")}'
        
        print((today-last_exec_date).days + 1)
        # looping from last_exec_date to today
        date_range = [last_exec_date + timedelta(days=x) for x in range(0, (today-last_exec_date).days + 1)]
        print(date_range)
        # date to string
        date_strs = [d.strftime("%y/%m/%d") for d in date_range]
        date_str_in_rrmmddform = ",".join(f"TO_DATE('{d}','RR/MM/DD')" for d in date_strs)
        date_str_in_yyyymmddform = ",".join(f"TO_DATE('{d}','YYYY-MM-DD')" for d in date_strs)        
    else:
        execute_date_range = f'{today.strftime("%Y%m%d")}'
        date_range = [today]
        
    print(date_range)
          
     
    print("asdasdasdsasd")
    print(date_range[0].strftime("%Y%m%d"))
    
    IF_HRD_KHRD_001_data = []
    IF_HRD_KHRD_002_data = []
    IF_HRD_KHRD_003_data = []
    IF_HRD_KHRD_004_data = []
    IF_HRD_KHRD_008_data = []
    IF_HRD_KHRD_009_data = []
    
    source_data_rows = 0
    
    for i in range(len(date_range)):
        date = date_range[i].strftime("%Y%m%d")        
        date_yyyymmddForm = date[:4] + "-" + date[4:6] + "-"+date[6:]
        print(date)
        print(date_yyyymmddForm)        

        # select original data(IF_HRD_KHRD_001(megaware)) 
        cursor.execute(f"SELECT * FROM IF_HRD_KHRD_001 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_001_data += cursor.fetchall()
                                                                                                                                
        print("IF_HRD_KHRD_001_data length :::")
        print(len(IF_HRD_KHRD_001_data))
        
        # select original data(IF_HRD_KHRD_002(megaware)) 
        cursor.execute(f"SELECT * FROM IF_HRD_KHRD_002 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_002_data += cursor.fetchall()
                                                                                                                                
        print("IF_HRD_KHRD_002_data length :::")
        print(len(IF_HRD_KHRD_002_data))        
        
        
        
        # select original data(IF_HRD_KHRD_003(megaware)) 
        cursor.execute("SELECT * FROM IF_HRD_KHRD_003 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_003_data += cursor.fetchall() 
        print("IF_HRD_KHRD_003_data length :::")     
        print(len(IF_HRD_KHRD_003_data))  
    
    
        # select original data(IF_HRD_KHRD_004(megaware)) 
        cursor.execute("SELECT * FROM IF_HRD_KHRD_004 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_004_data += cursor.fetchall()
        
        print("IF_HRD_KHRD_004_data length :::")     
        print(len(IF_HRD_KHRD_004_data))                  

        

        
        # select original data(IF_HRD_KHRD_008(megaware)) 
        cursor.execute("SELECT * FROM IF_HRD_KHRD_008 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_008_data += cursor.fetchall()  
        print("IF_HRD_KHRD_008_data length :::")     
        print(len(IF_HRD_KHRD_008_data))   

        # select original data(IF_HRD_KHRD_009(megaware)) 
        cursor.execute("SELECT * FROM IF_HRD_KHRD_009 WHERE IF_DEAL_DT like '{date}%'")
        IF_HRD_KHRD_009_data += cursor.fetchall()       
        print("IF_HRD_KHRD_009_data length :::")     
        print(len(IF_HRD_KHRD_009_data))   

       

    
    
    source_data_rows = len(IF_HRD_KHRD_001_data) + len(IF_HRD_KHRD_002_data) + len(IF_HRD_KHRD_003_data) + len(IF_HRD_KHRD_004_data) + len(IF_HRD_KHRD_008_data) + len(IF_HRD_KHRD_009_data) 
    print("source_data_rows!!!")
    print(source_data_rows)
    # XCom push
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_001_data', value=IF_HRD_KHRD_001_data)
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_002_data', value=IF_HRD_KHRD_002_data)
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_003_data', value=IF_HRD_KHRD_003_data)
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_004_data', value=IF_HRD_KHRD_004_data)
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_008_data', value=IF_HRD_KHRD_008_data)
    kwargs['ti'].xcom_push(key='IF_HRD_KHRD_009_data', value=IF_HRD_KHRD_009_data)
    
    
    kwargs['ti'].xcom_push(key='source_data_rows', value=source_data_rows)
    kwargs['ti'].xcom_push(key='execute_date_range', value=execute_date_range)
 
 
  
def insert_into_target_db(**kwargs):    
        
    inserted_data_rows = 0
    IF_HRD_KHRD_001_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_001_data', task_ids='t_select_from_source_db')
    IF_HRD_KHRD_002_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_002_data', task_ids='t_select_from_source_db')
    IF_HRD_KHRD_003_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_003_data', task_ids='t_select_from_source_db')
    IF_HRD_KHRD_004_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_004_data', task_ids='t_select_from_source_db')
    IF_HRD_KHRD_008_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_008_data', task_ids='t_select_from_source_db')
    IF_HRD_KHRD_009_data = kwargs['ti'].xcom_pull(key='IF_HRD_KHRD_009_data', task_ids='t_select_from_source_db')
    
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    connection = hrdDoctor_DEV_hook.get_conn()
    cursor = connection.cursor()


    # insert original data to temp table 
    for row in IF_HRD_KHRD_001_data:
        try:              
            connection.commit()                  
            cursor.execute(
                    """   INSERT INTO IFS_NET_BPR_TR
                         VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63,	:64,	:65,	:66,	:67,	:68,	:69,	:70,	:71,	:72,	:73,	:74,	:75,	:76,	:77,	:78,	:79,	:80,	:81,	:82,	:83,	:84,	:85,	:86,	:87,	:88
) """, row                                                        
                )
            
                        
            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_001_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")
            continue   
    print(inserted_data_rows)  
    
          
    for row in IF_HRD_KHRD_002_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_NET_BPR_TRA
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_002_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)
        
    
    for row in IF_HRD_KHRD_003_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_NET_CON_TR
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_003_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)

    for row in IF_HRD_KHRD_004_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_NET_CON_TRA
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_004_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)

    for row in IF_HRD_KHRD_008_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_NET_REG_TR
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_008_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)

    for row in IF_HRD_KHRD_009_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_NET_REG_TRA
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at IF_HRD_KHRD_009_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)    
    connection.commit()
    
    execute_date_range = kwargs['ti'].xcom_pull(key='execute_date_range', task_ids='t_select_from_source_db')
    source_data_rows = kwargs['ti'].xcom_pull(key='source_data_rows', task_ids='t_select_from_source_db')
    
    log_query = f"""insert into 
                    HRD_BSK_CRAWLING_LOG
                    (CRAWLING_DATA_ROW,INSERTED_DATA_ROW,CRAWLING_DATA_RANGE,LOGFILE_PATH,TARGET) 
                    values 
                    ({source_data_rows},{inserted_data_rows},'{execute_date_range}','/home/saltlux/airflow/logs/dag_id=HRDNET-PIPELINE/','HRDNET')"""
    print(log_query)
    hrdDoctor_DEV_hook.run(log_query)       
           

def call_proc(**kwargs):
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    conn = hrdDoctor_DEV_hook.get_conn()
    cursor = conn.cursor()        
    
    cursor.callproc("BSK_PRC_NET_DATA_OGNZ") 
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
# TASK : SELECT SOURCE DB
t_select_from_source_db = PythonOperator(
    task_id='t_select_from_source_db',
    python_callable=select_from_source_db,
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
t_start >> t_select_from_source_db >> t_insert_into_target_db >> t_call_proc >> t_end
