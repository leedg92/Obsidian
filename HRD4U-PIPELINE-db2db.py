import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'HRD4U-PIPELINE'
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
    
    hrd4u_REAL_hook = OracleHook(oracle_conn_id='hrd4u_REAL')    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    conn = hrdDoctor_DEV_hook.get_conn()
    cursor = conn.cursor()        
    
    query = "SELECT MAX(exec_date) from HRD_BSK_PRC_LOG where proc_id = 'HRD4U' and proc_success_yn = 'Y'"
    last_exec_date = hrdDoctor_DEV_hook.get_first(query)[0]    

    # exec_date( data from logtable)
    if last_exec_date != None:
        last_exec_date = last_exec_date + timedelta(1)
    else:
        last_exec_date = datetime.now()
    
    kwargs['ti'].xcom_push(key='last_exec_date', value=last_exec_date)    
    print(".....")
    print(last_exec_date)
    print(".....")
    
    # today
    today = datetime.now()
    print(today)
    
    if last_exec_date != None and last_exec_date.strftime("%y%m%d") != (today).strftime("%y%m%d"):
        execute_date_range = f'{last_exec_date.strftime("%y%m%d")}~{today.strftime("%y%m%d")}'
                
        # looping from last_exec_date to today
        date_range = [last_exec_date + timedelta(days=x) for x in range(0, (today-last_exec_date).days + 1)]           
    else:
        execute_date_range = f'{today.strftime("%Y%m%d")}'
        date_range = [today]
        
    print(date_range)
    kwargs['ti'].xcom_push(key='date_range', value=date_range)      
     
    
    TBL_SOJT_PROGRAM_data = []
    THR_EG_APPLY_data = []
    BEST_COM_CERT_APPLY_data = []
    
    source_data_rows = 0
    
    for i in range(len(date_range)):
        date = date_range[i].strftime('%Y%m%d')
        task_date = date_range[i].strftime('%Y%m%d')                
        date_yyyymmddForm = date[:4] + "-" + date[4:6] + "-"+date[6:]
        print(date)
        print(date_yyyymmddForm)
        # select original data(IFS_4U_SOJT(hrd4u_DEV)) 

        TBL_SOJT_PROGRAM_data += hrd4u_REAL_hook.get_records(f"""SELECT 
        SEQ, CORP_NM,REPVE_NM,BUSINESS_TYPE,CORP_RGST_NUM,BIZ_NUM,IND_LOCATIONNUM,BUSINESS_POST,BUSINESS_ADDR1,BUSINESS_ADDR2,CHRGR_PHONE1,CHRGR_PHONE2,CHRGR_PHONE3,TRAIN_POSTCODE,TRAIN_ADDRESS,TRAIN_ADDRESS2,CHRGR_NM,CHRGR_MBL_PHON_NUM,BUSINESS_ORG,CHRGR_WIRE_PHON_NUM,BRANCH,CHRGR_WIRE_PHON_NUM2,PM_NAME,PM_BELONG,PM_POSIT,PM_MOBILE,CONT_EXPERT_NAME,CONT_EXPERT_BELONG,CONT_EXPERT_POSIT,CONT_EXPERT_MOBILE,INNER_EXPERT_NAME,INNER_EXPERT_BELONG,INNER_EXPERT_POSIT,INNER_EXPERT_MOBILE,PM_HRD4U_ID,PM_HRD4UYN,PM_EDU_END_YN,CONT_EXPERT_HRD4U_ID,CONT_EXPERT_HRD4U,CONT_EXPERT_EDU_END,CONT_EXPERT_LIMIT,CONSULT_START_DATE,CONSULT_END_DATE,TRNN1,TRNN2,TRNN3,TRAINING_NM,NCS,REGI_ID,REGI_DATE,STATUS,FILE_ID,ISDELETE,BUSINESS_YEAR,APPLY_TYPE,TURN,REASON,FILE_ID2,FILE_ID3,FILE_ID4,FILE_ID5,FILE_ID6,FILE_ID7,UPI_DATE,PARENT_ID,PM_BIZ_LIMIT,REQ_CHANGE,APPLY_DATE,TRAINING_PRG_DEV,PRG_COST_YN,APPLY_CLASS,NCS_PRICE,CHRGR_CFC_LVL,FILE_ID8,FILE_ID9,FILE_ID10,FILE_ID11,ADMIN_ID,TMP_REGIDT,TMP_APPLYDT,TMP_UPIDT
         FROM TBL_SOJT_PROGRAM WHERE
         TO_CHAR(NVL(UPI_DATE,REGI_DATE),'YYYYMMDD') = '{date}'
                                                            """)
                                                                    
                                                            
        print("TBL_SOJT_PROGRAM_data length :::")
        print(len(TBL_SOJT_PROGRAM_data))
    
        # select original data(IFS_4U_EG(hrd4u_DEV)) 
        THR_EG_APPLY_data += hrd4u_REAL_hook.get_records(f"""SELECT * FROM THR_EG_APPLY WHERE 
                                                          ( TO_CHAR(AUDIT_DTM,'YYYYMMDD') = '{date}'
                                                          or ASSESS_DTM = '{date_yyyymmddForm}')""")
        #print(THR_EG_APPLY_data)
        print("THR_EG_APPLY_data length :::")     
        print(len(THR_EG_APPLY_data))                                                 
        # select original data(IFS_4U_CERT(hrd4u_DEV))         
        BEST_COM_CERT_APPLY_data += hrd4u_REAL_hook.get_records(f"""SELECT * FROM BEST_COM_CERT_APPLY WHERE 
                                                          ( TO_CHAR(NVL(UPDATE_DATE,WRITE_DATE),'YYYYMMDD') = '{date}'
                                                          or CERT_DATE = '{date_yyyymmddForm}')""")   
        print("BEST_COM_CERT_APPLY_data length :::")     
        print(len(BEST_COM_CERT_APPLY_data))                                                               

    
    
    source_data_rows = len(TBL_SOJT_PROGRAM_data) + len(THR_EG_APPLY_data) + len(BEST_COM_CERT_APPLY_data)
    print("source_data_rows1!!!")
    print(source_data_rows)
    # XCom push
    kwargs['ti'].xcom_push(key='TBL_SOJT_PROGRAM_data', value=TBL_SOJT_PROGRAM_data)
    kwargs['ti'].xcom_push(key='THR_EG_APPLY_data', value=THR_EG_APPLY_data)
    kwargs['ti'].xcom_push(key='BEST_COM_CERT_APPLY_data', value=BEST_COM_CERT_APPLY_data)
    
    kwargs['ti'].xcom_push(key='source_data_rows', value=source_data_rows)
    kwargs['ti'].xcom_push(key='execute_date_range', value=execute_date_range)
 
 
def drop_temp_table_if_exists(**kwargs):    
    common_table_names = ["IFS_4U_SOJT", "IFS_4U_EG", "IFS_4U_CERT"]
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    
    for table_name in common_table_names:
        temp_table_name = table_name + "_TEMP"  
        check_table_query = f"""
        SELECT COUNT(*)
        FROM user_tables
        WHERE table_name = '{temp_table_name}'
        """
        
        table_exists = hrdDoctor_DEV_hook.get_first(check_table_query)[0]
        if table_exists:
            print(f"{temp_table_name} TABLE EXISTS => WILL DELETE")
            hrdDoctor_DEV_hook.run(f"DROP TABLE {temp_table_name}")   
  
  
def insert_into_target_db(**kwargs):    
        
    inserted_data_rows = 0
    TBL_SOJT_PROGRAM_data = kwargs['ti'].xcom_pull(key='TBL_SOJT_PROGRAM_data', task_ids='t_select_from_source_db')
    THR_EG_APPLY_data = kwargs['ti'].xcom_pull(key='THR_EG_APPLY_data', task_ids='t_select_from_source_db')
    BEST_COM_CERT_APPLY_data = kwargs['ti'].xcom_pull(key='BEST_COM_CERT_APPLY_data', task_ids='t_select_from_source_db')
    
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    connection = hrdDoctor_DEV_hook.get_conn()
    cursor = connection.cursor()
    


    # insert original data to temp table 
    for row in TBL_SOJT_PROGRAM_data:
        try:              
            connection.commit()                  
            cursor.execute(
                    """   INSERT INTO IFS_4U_SOJT
                         VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63,	:64,	:65,	:66,	:67,	:68,	:69,	:70,	:71,	:72,	:73,	:74,	:75,	:76,	:77,	:78,	:79,	:80,	:81
) """, row                                                        
                )
            
                        
            inserted_data_rows += 1
        except Exception as e:
            print("error found at TBL_SOJT_PROGRAM_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")
            continue   
    print(inserted_data_rows)  
    
          
    for row in THR_EG_APPLY_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_4U_EG
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63,	:64,	:65,	:66,	:67,	:68,	:69,	:70,	:71,	:72,	:73,	:74,	:75,	:76,	:77,	:78,	:79,	:80,	:81,	:82,	:83,	:84,	:85,	:86,	:87,	:88,	:89,	:90,	:91,	:92,	:93,	:94,	:95,	:96,	:97,	:98,	:99,	:100,	:101,	:102,	:103
) """, row                                                        
                )

            inserted_data_rows += 1
        except Exception as e:
            print("error found at THR_EG_APPLY_data")
            print(row)
            print(e)
            connection = hrdDoctor_DEV_hook.get_conn()
            cursor = connection.cursor()
            print("get new cursor")           
            continue 
    print(inserted_data_rows)
        
    
    for row in BEST_COM_CERT_APPLY_data:
        try:
            connection.commit()
            cursor.execute(
                    """   INSERT INTO IFS_4U_CERT
                          VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45,	:46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63, :64
) """, row                                                        
                )
            inserted_data_rows += 1
        except Exception as e:
            print("error found at BEST_COM_CERT_APPLY_data")
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
                    ({source_data_rows},{inserted_data_rows},'{execute_date_range}','/home/saltlux/airflow/logs/dag_id=HRD4U-PIPELINE/','HRD4U')"""
    print(log_query)
    hrdDoctor_DEV_hook.run(log_query)      
    
    
def call_proc(**kwargs):
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    conn = hrdDoctor_DEV_hook.get_conn()
    cursor = conn.cursor()        
    
    cursor.callproc("BSK_PRC_4U_DATA_OGNZ") 
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
