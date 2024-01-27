import pendulum
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import cx_Oracle
import requests
from xml.etree import ElementTree
from airflow.hooks.dbapi_hook import DbApiHook
import math
import time


KST = pendulum.timezone("Asia/Seoul")

# INIT DAG
dag_id = 'WORKNET-PIPELINE'
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
          tags=['file2db', 'comwelFile_to_hrdDoctor_REAL', 'IFS_CM_CORP', 'MERGE'],
         )

t_start = DummyOperator(task_id='start', dag=dag)
t_end = DummyOperator(task_id='end', dag=dag)

        

def fetch_and_insert_returned_data(**kwargs):

    execute_date_range = ''
    source_data_rows = 0
    inserted_data_rows = 0
    
    authKey =  'WNLK0DII9UFHNQEPNG4692VR1HK'
      
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    connection = hrdDoctor_DEV_hook.get_conn()
    cursor = connection.cursor()
    
    query = "SELECT MAX(exec_date) from HRD_BSK_PRC_LOG where proc_id = 'WORKNET' and proc_success_yn = 'Y'"
    last_exec_date = hrdDoctor_DEV_hook.get_first(query)[0]    

    # exec_date( data from logtable)
    if last_exec_date != None:
        last_exec_date = last_exec_date
    else:
        last_exec_date = datetime.now() - timedelta(1)
        
    kwargs['ti'].xcom_push(key='last_exec_date', value=last_exec_date)
        
    print(".....")
    print(last_exec_date)
    print(".....")

    today = datetime.now()

    print(today)
    print(last_exec_date)
    
    
        
    print(execute_date_range)
    
    if last_exec_date != None and last_exec_date.strftime("%y%m%d") != (today).strftime("%y%m%d"):
        execute_date_range = f'{last_exec_date.strftime("%y%m%d")}~{today.strftime("%y%m%d")}'
                
        # looping from last_exec_date to today
        date_range = [last_exec_date + timedelta(days=x) for x in range(0, (today-last_exec_date).days)]           
    else:
        execute_date_range = f'{today.strftime("%Y%m%d")}'
        date_range = [today]    

    
    for date in date_range:
        print("in loop")
        print(date)
        minWantedAuthDt = date.strftime("%Y%m%d")
        print(minWantedAuthDt)
        print(date + timedelta(1))
        maxWantedAuthDt = (date + timedelta(1)).strftime("%Y%m%d")
        print(maxWantedAuthDt)
    
        #http://openapi.work.go.kr/opi/opi/opia/wantedApi.do?authKey=WNLK0DII9UFHNQEPNG4692VR1HK&callTp=L&returnType=XML&startPage=1&display=100
       
        recruit_list_url = "http://openapi.work.go.kr/opi/opi/opia/wantedApi.do"
        recruit_detail_url = "http://openapi.work.go.kr/opi/opi/opia/wantedApi.do"
        

        
        
        response = requests.get(f"""http://openapi.work.go.kr/opi/opi/opia/wantedApi.do?authKey=WNLK0DII9UFHNQEPNG4692VR1HK&callTp=L&returnType=XML&startPage=1&display=1&minWantedAuthDt={minWantedAuthDt + "07"}&maxWantedAuthDt={maxWantedAuthDt + "07"}""")
        
        if response.status_code != 200:
            raise Exception(f"Initial API request failed with status code {response.status_code}")
    
    
        root = ElementTree.fromstring(response.content)
        total = int(root.find('total').text)
        iterations = math.ceil(total / 100.0)
        count = 0;
        wanted_list = []
        wantedDtl_list = []
        recruit_data_list = []
    
        source_data_rows += total
        print(f"iterations ::: {iterations}")
        
    
        for i in range(iterations):
            if i in [200,400,600,800]:
                print("sleep 10 seconds")
                time.sleep(120)
            #recruit list API call
            params = {
                "callTp" : "L", 
                "returnType" : "XML", 
                "display" : "100", 
                "authKey" : authKey, 
                "startPage" : i+1,
                "minWantedAuthDt" : minWantedAuthDt + "07",
                "maxWantedAuthDt" : maxWantedAuthDt + "07"
            }
            response = requests.get(recruit_list_url, params=params)
            if response.status_code != 200:
                raise Exception(f"API request for iteration {i+1} failed with status code {response.status_code}")
            
            wanted_root = ElementTree.fromstring(response.content)
            #wanted   
            print(f"index ::: {i}")
            for wantedItem in wanted_root.findall('wanted'):            
                wantedAuthNo = wantedItem.find('wantedAuthNo').text if wantedItem.find('wantedAuthNo') is not None else None
                company = wantedItem.find('company').text if wantedItem.find('company') is not None else None
                busino = wantedItem.find('busino').text if wantedItem.find('busino') is not None else None
                title = wantedItem.find('title').text if wantedItem.find('title') is not None else None
                salTp = wantedItem.find('salTpNm').text if wantedItem.find('salTpNm') is not None else None
                sal = wantedItem.find('sal').text if wantedItem.find('sal') is not None else None
                minSal = wantedItem.find('minSal').text if wantedItem.find('minSal') is not None else None
                maxSal = wantedItem.find('maxSal').text if wantedItem.find('maxSal') is not None else None
                region = wantedItem.find('region').text if wantedItem.find('region') is not None else None
                holidayTpNm = wantedItem.find('holidayTpNm').text if wantedItem.find('holidayTpNm') is not None else None
                minEdubg = wantedItem.find('minEdubg').text if wantedItem.find('minEdubg') is not None else None
                maxEdubg = wantedItem.find('maxEdubg').text if wantedItem.find('maxEdubg') is not None else None
                career = wantedItem.find('career').text if wantedItem.find('career') is not None else None
                regDt = wantedItem.find('regDt').text if wantedItem.find('regDt') is not None else None
                closeDt = wantedItem.find('closeDt').text if wantedItem.find('closeDt') is not None else None
                infoSvc = wantedItem.find('infoSvc').text if wantedItem.find('infoSvc') is not None else None
                wantedInfoUrl = wantedItem.find('wantedInfoUrl').text.replace("&","&\\") if wantedItem.find('wantedInfoUrl') is not None else None
                wantedMobileInfoUrl = wantedItem.find('wantedMobileInfoUrl').text.replace("&","&\\") if wantedItem.find('wantedMobileInfoUrl') is not None else None
                zipCd = wantedItem.find('zipCd').text if wantedItem.find('zipCd') is not None else None
                strtnmCd = wantedItem.find('strtnmCd').text if wantedItem.find('strtnmCd') is not None else None
                basicAddr = wantedItem.find('basicAddr').text if wantedItem.find('basicAddr') is not None else None
                detailAddr = wantedItem.find('detailAddr').text if wantedItem.find('detailAddr') is not None else None
                jobsCd = wantedItem.find('jobsCd').text if wantedItem.find('jobsCd') is not None else None
                smodifyDtm = wantedItem.find('smodifyDtm').text if wantedItem.find('smodifyDtm') is not None else None
                prefCd = wantedItem.find('prefCd').text if wantedItem.find('prefCd') is not None else None
    
                
                #recruit detail API call
                params = {
                    "callTp" : "D", 
                    "returnType" : "XML",                  
                    "authKey" : authKey,
                    "wantedAuthNo" : wantedAuthNo,
                    "infoSvc" : "VALIDATION"              
                } 
                #init variable to Errors from API      
                reperNm = None
                totPsncnt = ""
                capitalAmt = None
                yrSalesAmt = None
                indTpCdNm = None
                busiCont = None
                homePg = None
                busiSize = None
                jobsNm = None
                wantedTitle = None
                relJobsNm = None
                jobCont = None
                receiptCloseDt = None
                empTpNm = None
                collectPsncnt = None
                salTpNm = None
                enterTpNm = None
                eduNm = None
                forLang = None
                major = None
                certificate = None
                mltsvcExcHope = None
                compAbl = None
                pfCond = None
                etcPfCond = None
                selMthd = None
                rcptMthd = None
                submitDoc = None
                etcHopeCont = None
                workRegion = None
                nearLine = None
                workdayWorkhrCont = None
                fourIns = None
                retirepay = None
                etcWelfare = None
                disableCvntl = None
                attachFileInfo = None
                corpAttachList = None
                srchKeywordNm = None
                dtlRecrContUrl = None
                minEdubgIcd = None
                maxEdubgIcd = None
                regionCd = None
                empTpCd = None
                enterTpCd = None
                salTpCd = None
                staAreaRegionCd = None
                lineCd = None
                staNmCd = None
                exitNoCd = None
                walkDistCd = None
                empChargerDpt = None
                contactTelno = None
                chargerFaxNo = None                 
                detail_response = requests.get(recruit_detail_url, params=params)
                try:                
                
                    detail_root = ElementTree.fromstring(detail_response.content)            
                    if detail_response.status_code == 200:                                
                        
                        detail_root = ElementTree.fromstring(detail_response.content)
                        print("//////////////////////////////////////////////////")
                        print(total)
                        print(count)
                        print("wantedAuthNo ::: " + wantedAuthNo)
                        print("//////////////////////////////////////////////////")
                        
                        #corpInfo
                        for corpInfoItem in detail_root.findall('corpInfo'):
                            
                            reperNm = corpInfoItem.find('reperNm').text if corpInfoItem.find('reperNm') is not None else None
                            totPsncnt = corpInfoItem.find('totPsncnt').text if corpInfoItem.find('totPsncnt') is not None else None
                            capitalAmt = corpInfoItem.find('capitalAmt').text if corpInfoItem.find('capitalAmt') is not None else None
                            yrSalesAmt = corpInfoItem.find('yrSalesAmt').text if corpInfoItem.find('yrSalesAmt') is not None else None
                            indTpCdNm = corpInfoItem.find('indTpCdNm').text if corpInfoItem.find('indTpCdNm') is not None else None
                            busiCont = corpInfoItem.find('busiCont').text if corpInfoItem.find('busiCont') is not None else None
                            homePg = corpInfoItem.find('homePg').text if corpInfoItem.find('homePg') is not None else None
                            busiSize = corpInfoItem.find('busiSize').text if corpInfoItem.find('busiSize') is not None else None
        
                            
                        #wantedInfo    
                        for wantedInfoItem in detail_root.findall('wantedInfo'): 
                            jobsNm = wantedInfoItem.find('jobsNm').text if wantedInfoItem.find('jobsNm') is not None else None
                            wantedTitle = wantedInfoItem.find('wantedTitle').text if wantedInfoItem.find('wantedTitle') is not None else None
                            relJobsNm = wantedInfoItem.find('relJobsNm').text if wantedInfoItem.find('relJobsNm') is not None else None
                            jobCont = wantedInfoItem.find('jobCont').text if wantedInfoItem.find('jobCont') is not None else None
                            receiptCloseDt = wantedInfoItem.find('receiptCloseDt').text if wantedInfoItem.find('receiptCloseDt') is not None else None
                            empTpNm = wantedInfoItem.find('empTpNm').text if wantedInfoItem.find('empTpNm') is not None else None
                            collectPsncnt = wantedInfoItem.find('collectPsncnt').text if wantedInfoItem.find('collectPsncnt') is not None else None
                            salTpNm = wantedInfoItem.find('salTpNm').text if wantedInfoItem.find('salTpNm') is not None else None
                            enterTpNm = wantedInfoItem.find('enterTpNm').text if wantedInfoItem.find('enterTpNm') is not None else None
                            eduNm = wantedInfoItem.find('eduNm').text if wantedInfoItem.find('eduNm') is not None else None
                            forLang = wantedInfoItem.find('forLang').text if wantedInfoItem.find('forLang') is not None else None
                            major = wantedInfoItem.find('major').text if wantedInfoItem.find('major') is not None else None
                            certificate = wantedInfoItem.find('certificate').text if wantedInfoItem.find('certificate') is not None else None
                            mltsvcExcHope = wantedInfoItem.find('mltsvcExcHope').text if wantedInfoItem.find('mltsvcExcHope') is not None else None
                            compAbl = wantedInfoItem.find('compAbl').text if wantedInfoItem.find('compAbl') is not None else None
                            pfCond = wantedInfoItem.find('pfCond').text if wantedInfoItem.find('pfCond') is not None else None
                            etcPfCond = wantedInfoItem.find('etcPfCond').text if wantedInfoItem.find('etcPfCond') is not None else None
                            selMthd = wantedInfoItem.find('selMthd').text if wantedInfoItem.find('selMthd') is not None else None
                            rcptMthd = wantedInfoItem.find('rcptMthd').text if wantedInfoItem.find('rcptMthd') is not None else None
                            submitDoc = wantedInfoItem.find('submitDoc').text if wantedInfoItem.find('submitDoc') is not None else None
                            etcHopeCont = wantedInfoItem.find('etcHopeCont').text if wantedInfoItem.find('etcHopeCont') is not None else None
                            workRegion = wantedInfoItem.find('workRegion').text if wantedInfoItem.find('workRegion') is not None else None
                            nearLine = wantedInfoItem.find('nearLine').text if wantedInfoItem.find('nearLine') is not None else None
                            workdayWorkhrCont = wantedInfoItem.find('workdayWorkhrCont').text if wantedInfoItem.find('workdayWorkhrCont') is not None else None
                            fourIns = wantedInfoItem.find('fourIns').text if wantedInfoItem.find('fourIns') is not None else None
                            retirepay = wantedInfoItem.find('retirepay').text if wantedInfoItem.find('retirepay') is not None else None
                            etcWelfare = wantedInfoItem.find('etcWelfare').text if wantedInfoItem.find('etcWelfare') is not None else None
                            disableCvntl = wantedInfoItem.find('disableCvntl').text if wantedInfoItem.find('disableCvntl') is not None else None
                            attachFileInfo = wantedInfoItem.find('attachFileInfo').text if wantedInfoItem.find('attachFileInfo') is not None else None
                            corpAttachList = wantedInfoItem.find('corpAttachList').text if wantedInfoItem.find('corpAttachList') is not None else None
                            srchKeywordNm = ", ".join([srchKeywordNm.find('srchKeywordNm').text for srchKeywordNm in wantedInfoItem.findall('keywordList') if srchKeywordNm.find('srchKeywordNm').text ])
                            dtlRecrContUrl = wantedInfoItem.find('dtlRecrContUrl').text.replace("&","&\\") if wantedInfoItem.find('dtlRecrContUrl') is not None else None
                            minEdubgIcd = wantedInfoItem.find('minEdubgIcd').text if wantedInfoItem.find('minEdubgIcd') is not None else None
                            maxEdubgIcd = wantedInfoItem.find('maxEdubgIcd').text if wantedInfoItem.find('maxEdubgIcd') is not None else None
                            regionCd = wantedInfoItem.find('regionCd').text if wantedInfoItem.find('regionCd') is not None else None
                            empTpCd = wantedInfoItem.find('empTpCd').text if wantedInfoItem.find('empTpCd') is not None else None
                            enterTpCd = wantedInfoItem.find('enterTpCd').text if wantedInfoItem.find('enterTpCd') is not None else None
                            salTpCd = wantedInfoItem.find('salTpCd').text if wantedInfoItem.find('salTpCd') is not None else None
                            staAreaRegionCd = wantedInfoItem.find('staAreaRegionCd').text if wantedInfoItem.find('staAreaRegionCd') is not None else None
                            lineCd = wantedInfoItem.find('lineCd').text if wantedInfoItem.find('lineCd') is not None else None
                            staNmCd = wantedInfoItem.find('staNmCd').text if wantedInfoItem.find('staNmCd') is not None else None
                            exitNoCd = wantedInfoItem.find('exitNoCd').text if wantedInfoItem.find('exitNoCd') is not None else None
                            walkDistCd = wantedInfoItem.find('walkDistCd').text if wantedInfoItem.find('walkDistCd') is not None else None                                                          
    
                                
                        for empchargeInfoItem in detail_root.findall('empchargeInfo'):  
                            empChargerDpt = empchargeInfoItem.find('empChargerDpt').text if empchargeInfoItem.find('empChargerDpt') is not None else None
                            contactTelno = empchargeInfoItem.find('contactTelno').text if empchargeInfoItem.find('contactTelno') is not None else None
                            chargerFaxNo = empchargeInfoItem.find('chargerFaxNo').text if empchargeInfoItem.find('chargerFaxNo') is not None else None
                                                                                      
                    else:
                        raise Exception(f"Second API request for wantedAuthNo {wantedAuthNo} failed with status code {second_response.status_code}")
             
                except ElementTree.ParseError:  
                        print("error =====> insert init variable")
                        print( reperNm, wantedAuthNo)
                #recruit detail append
                recruit_data_list.append((wantedAuthNo,busino,company,title,salTp,sal,minSal,maxSal,region,holidayTpNm,minEdubg,maxEdubg,career,
                                                regDt,closeDt,infoSvc,wantedInfoUrl,wantedMobileInfoUrl,zipCd,strtnmCd,basicAddr,detailAddr,jobsCd,smodifyDtm,
                                                prefCd,reperNm,totPsncnt,capitalAmt,yrSalesAmt,indTpCdNm,busiCont,
                                                homePg,busiSize,jobsNm,wantedTitle,relJobsNm,receiptCloseDt,empTpNm,collectPsncnt,salTpNm,enterTpNm,eduNm,forLang,major,
                                                certificate,mltsvcExcHope,compAbl,pfCond,etcPfCond,selMthd,rcptMthd,submitDoc,etcHopeCont,workRegion,nearLine,
                                                workdayWorkhrCont,fourIns,retirepay,etcWelfare,disableCvntl,attachFileInfo,corpAttachList,srchKeywordNm,dtlRecrContUrl,
                                                minEdubgIcd,maxEdubgIcd,regionCd,empTpCd,enterTpCd,salTpCd,staAreaRegionCd,lineCd,staNmCd,exitNoCd,walkDistCd,empChargerDpt,
                                                contactTelno,chargerFaxNo,jobCont,maxWantedAuthDt))
                                
                    
                recruit_data_list[0] = tuple(val.replace(":",":\\") if val is not None else val for val in recruit_data_list[0])
                
                print(maxWantedAuthDt)  
                print("???")
                
                cursor.execute(
                        """   INSERT INTO IFS_WORK_REC
                                  (WANTED_AUTH_NO,BIZR_NO,CORP_NM,TITLE,SAL_TYPE,SALARY,MIN_SALARY,MAX_SALARY,REGION,HOLIDAY_TYPE,MIN_EDU,MAX_EDU,CAREER,REG_DT,CLOSE_DT,INFO_SVC,WANTED_INFO,WANTED_MOBILE,BPL_POST,STRTNM_CODE,BPL_ADDR,BPL_ADDR_DTL,JOBS_CODE,MODIFY_DT,PREF_CODE,REPER_NM,PSN_CNT,CAPITAL_AMT,YR_SALES_AMT,MAIN_INDUTY,MAIN_SERVICE,HOMEPAGE,BIZ_SIZE,JOBS_NM,WANTED_TITLE,REL_JOBS_NM,RECEIPT_CLS_DT,EMP_TYPE,COLLECT_PSN,SAL_TYPE_NM,ENTER_TYPE,EDU_NM,FOR_LANG,MAJOR,CERTIFICATE,MLT_SVC_EXC,COMP_ABL,PF_COND,ETC_PF_COND,SEL_MTHD,RCPT_MTHD,SUBMIT_DOC,ETC_HOPE_CONT,WORK_REGION,NEAR_LINE,WORKDAY,FOURLNS,RETIREPAY,ETC_WELFARE,DISABLE_CVNTL,ATTACH_FILE,CORP_ATTACH_LIST,SRCH_KEYWORD,DTL_RECR_CONT,MIN_EDUBGLCD,MAX_EDUBGLCD,REGION_CD,EMP_TYPE_CD,ENTER_TYPE_CD,SAL_TYPE_CD,STA_AREA_REGION,LINE_CD,STA_NM_CD,EXIT_NO_CD,WALK_DIST_CD,EMP_CHARGER,CONTACT_TEL,CHARGER_FAX,JOB_CONT, WRT_DATE)
                              VALUES (:1,	:2,	:3,	:4,	:5,	:6,	:7,	:8,	:9,	:10,	:11,	:12,	:13,	:14,	:15,	:16,	:17,	:18,	:19,	:20,	:21,	:22,	:23,	:24,	:25,	:26,	:27,	:28,	:29,	:30,	:31,	:32,	:33,	:34,	:35,	:36,	:37,	:38,	:39,	:40,	:41,	:42,	:43,	:44,	:45, :46,	:47,	:48,	:49,	:50,	:51,	:52,	:53,	:54,	:55,	:56,	:57,	:58,	:59,	:60,	:61,	:62,	:63,	:64,	:65,	:66,	:67,	:68,	:69,	:70,	:71,	:72,	:73,	:74,	:75,	:76,	:77,	:78,	TO_CLOB(:79), TO_DATE(:80)) """,
                              recruit_data_list[0]                                                        
                    )
                inserted_data_rows += 1
                connection.commit() 
                recruit_data_list.clear()
                                                   
                count += 1                    
    cursor.close()
    connection.close()

#----------------------------------------------------------smallGiantYoung---------------------------------------------------------------------------    
    
    smallGiants_young_list_url = "http://openapi.work.go.kr/opi/smallGiants/smallGiantsYoung.do"
    
    response = requests.get("http://openapi.work.go.kr/opi/smallGiants/smallGiantsYoung.do?authKey=WNLK0DII9UFHNQEPNG4692VR1HK&returnType=XML")
    if response.status_code != 200:
        raise Exception(f"Initial API request failed with status code {response.status_code}")

    root = ElementTree.fromstring(response.content)

    count = 0;
    smallGiants_young_data_list = []

    #recruit list API call
    params = {
        "returnType" : "XML", 
        "authKey" : authKey
    }
    response = requests.get(smallGiants_young_list_url, params=params)
    if response.status_code != 200:
        raise Exception(f"API request for iteration {i+1} failed with status code {response.status_code}")
    
    smallGiants_young_list_root = ElementTree.fromstring(response.content)
    #wanted   
    for smallGiantYoungItem in smallGiants_young_list_root.findall('smallGiant'):     
        
        coNm = smallGiantYoungItem.find('coNm').text if smallGiantYoungItem.find('coNm') is not None else None
        busiNo = smallGiantYoungItem.find('busiNo').text if smallGiantYoungItem.find('busiNo') is not None else None
        reperNm = smallGiantYoungItem.find('reperNm').text if smallGiantYoungItem.find('reperNm') is not None else None
        superIndTpCd = smallGiantYoungItem.find('superIndTpCd').text if smallGiantYoungItem.find('superIndTpCd') is not None else None
        superIndTpNm = smallGiantYoungItem.find('superIndTpNm').text if smallGiantYoungItem.find('superIndTpNm') is not None else None
        indTpCd = smallGiantYoungItem.find('indTpCd').text if smallGiantYoungItem.find('indTpCd') is not None else None
        indTpNm = smallGiantYoungItem.find('indTpNm').text if smallGiantYoungItem.find('indTpNm') is not None else None
        regionCd = smallGiantYoungItem.find('regionCd').text if smallGiantYoungItem.find('regionCd') is not None else None
        regionNm = smallGiantYoungItem.find('regionNm').text if smallGiantYoungItem.find('regionNm') is not None else None
        alwaysWorkerCnt = smallGiantYoungItem.find('alwaysWorkerCnt').text if smallGiantYoungItem.find('alwaysWorkerCnt') is not None else None
        print(coNm)                                             

        #smallGiantYoungItem.append(ElementTree.SubElement(smallGiantYoungItem, "additionalData", text=additional_data))
        smallGiants_young_data_list.append((busiNo,coNm	,reperNm	,superIndTpCd	,superIndTpNm	,indTpCd	,indTpNm	,regionCd	,regionNm	,alwaysWorkerCnt	))
        #print(len(smallGiants_data_list[i]))
        #print(smallGiants_data_list[i])            
        count += 1
    print("------------------------------------------------")
    kwargs['ti'].xcom_push(key='smallGiants_young_data_list', value=smallGiants_young_data_list)    
    source_data_rows += count
    
    hrdDoctor_DEV_hook.insert_rows(table="IFS_WORK_YF", rows=smallGiants_young_data_list, target_fields=['BIZR_NO','CORP_NM','REPER_NM',	'BKIND_LCLS_CD','BKIND_LCLS_NM','BKIND_MCLS_CD',	'BKIND_MCLS_NM',	'REGION_CD',	'REGION_NM',	'TOT_WORK_CNT'])
    inserted_data_rows += count
    
    
    
#----------------------------------------------------------smallGiant---------------------------------------------------------------------------    

    #https://openapi.work.go.kr/opi/smallGiants/smallGiants.do?authKey=WNLK0DII9UFHNQEPNG4692VR1HK&returnType=XML&startPage=1&display=1
    authKey =  'WNLK0DII9UFHNQEPNG4692VR1HK'
    smallGiants_list_url = "https://openapi.work.go.kr/opi/smallGiants/smallGiants.do"
    
    response = requests.get("https://openapi.work.go.kr/opi/smallGiants/smallGiants.do?authKey=WNLK0DII9UFHNQEPNG4692VR1HK&returnType=XML&startPage=1&display=1")
    if response.status_code != 200:
        raise Exception(f"Initial API request failed with status code {response.status_code}")

    root = ElementTree.fromstring(response.content)
    total = int(root.find('total').text)
    iterations = math.ceil(total / 100.0)
    count = 0;
    smallGiants_data_list = []
    source_data_rows += total
    print(f"iterations ::: {iterations}")
    for i in range(iterations):
        #recruit list API call
        params = {
            "returnType" : "XML", 
            "display" : "100", 
            "authKey" : authKey, 
            "startPage" : i+1
        }
        response = requests.get(smallGiants_list_url, params=params)
        if response.status_code != 200:
            raise Exception(f"API request for iteration {i+1} failed with status code {response.status_code}")
        
        smallGiants_list_root = ElementTree.fromstring(response.content)
        #wanted   
        print(f"index ::: {i+1}")
        for smallGiantItem in smallGiants_list_root.findall('smallGiant'):     
            print(count)
            selYear = smallGiantItem.find('selYear').text if smallGiantItem.find('selYear') is not None else None
            sgBrandNm = smallGiantItem.find('sgBrandNm').text if smallGiantItem.find('sgBrandNm') is not None else None
            coNm = smallGiantItem.find('coNm').text if smallGiantItem.find('coNm') is not None else None
            busiNo = smallGiantItem.find('busiNo').text if smallGiantItem.find('busiNo') is not None else None
            reperNm = smallGiantItem.find('reperNm').text if smallGiantItem.find('reperNm') is not None else None
            superIndTpCd = smallGiantItem.find('superIndTpCd').text if smallGiantItem.find('superIndTpCd') is not None else None
            superIndTpNm = smallGiantItem.find('superIndTpNm').text if smallGiantItem.find('superIndTpNm') is not None else None
            indTpCd = smallGiantItem.find('indTpCd').text if smallGiantItem.find('indTpCd') is not None else None
            indTpNm = smallGiantItem.find('indTpNm').text if smallGiantItem.find('indTpNm') is not None else None
            coTelNo = smallGiantItem.find('coTelNo').text if smallGiantItem.find('coTelNo') is not None else None
            regionCd = smallGiantItem.find('regionCd').text if smallGiantItem.find('regionCd') is not None else None
            regionNm = smallGiantItem.find('regionNm').text if smallGiantItem.find('regionNm') is not None else None
            coAddr = smallGiantItem.find('coAddr').text if smallGiantItem.find('coAddr') is not None else None
            coMainProd = smallGiantItem.find('coMainProd').text if smallGiantItem.find('coMainProd') is not None else None
            coHomePage = smallGiantItem.find('coHomePage').text if smallGiantItem.find('coHomePage') is not None else None
            alwaysWorkerCnt = smallGiantItem.find('alwaysWorkerCnt').text if smallGiantItem.find('alwaysWorkerCnt') is not None else None
            smlgntCoClcd = smallGiantItem.find('smlgntCoClcd').text if smallGiantItem.find('smlgntCoClcd') is not None else None                                                             
            print(coNm)
            #smallGiantItem.append(ElementTree.SubElement(smallGiantItem, "additionalData", text=additional_data))
            smallGiants_data_list.append((busiNo,selYear,sgBrandNm,coNm,reperNm,superIndTpCd,superIndTpNm,indTpCd,indTpNm,coTelNo,regionCd,regionNm,coAddr,coMainProd,coHomePage,alwaysWorkerCnt,smlgntCoClcd))
            #print(len(smallGiants_data_list[i]))
            #print(smallGiants_data_list[i])            
            count += 1
        
    hrdDoctor_DEV_hook.insert_rows(table="IFS_WORK_SG", rows=smallGiants_data_list, target_fields=['BIZR_NO'	,'REQUEST_YEAR'	,'SG_BRAND_NM'	,
                                                                                            'CORP_NM'	,'REPER_NM'	,'BKIND_LCLS_CD'	,'BKIND_LCLS_NM',	
                                                                                            'BKIND_MCLS_CD'	,'BKIND_MCLS_NM'	,'CONTACT'	,'REGION_CD'	,
                                                                                            'REGION_NM'	,'BPL_ADDR'	,'PRODUCT'	,'HOMEPAGE'	,'TOT_WORK_CNT'	,'SG_BRAND_CD'	,
])
    inserted_data_rows += count
    

    
#-----------------------------------------------------------------log data---------------------------------------------------------------    
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(source_data_rows)
    print(inserted_data_rows)
    print(execute_date_range)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    log_query = f"""insert into 
                    HRD_BSK_CRAWLING_LOG
                    (CRAWLING_DATA_ROW,INSERTED_DATA_ROW,CRAWLING_DATA_RANGE,LOGFILE_PATH,TARGET) 
                    values 
                    ({source_data_rows},{inserted_data_rows},'{execute_date_range}','/home/saltlux/airflow/logs/dag_id=WORKNET-PIPELINE/','WORKNET')"""
    print(log_query)
    hrdDoctor_DEV_hook.run(log_query) 
    

    

 
def call_proc(**kwargs):
    hrdDoctor_DEV_hook = OracleHook(oracle_conn_id='hrdDoctor_REAL')
    conn = hrdDoctor_DEV_hook.get_conn()
    cursor = conn.cursor()        
    
    cursor.callproc("BSK_PRC_WORK_DATA_OGNZ") 
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
# TASK : fetch_and_insert_returned_data
t_fetch_and_insert_returned_data = PythonOperator(
    task_id='t_fetch_and_insert_returned_data',
    python_callable=fetch_and_insert_returned_data,
    provide_context=True, 
    dag=dag,
)





t_start >> t_fetch_and_insert_returned_data >> t_call_proc >> t_end
