from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.common.exceptions import NoSuchElementException

#pip install beautifulsoup4 lxml
#pip install pandas openpyxl
# pip install requests
# pip install requests beautifulsoup4
# pip install selenium


# from openpyxl import Workbook

chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # 웹 보안 비활성화
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--user-data-dir=~/.e2e-chrome-profile")
chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
chrome_options.add_argument("--headless")  # 헤드리스
chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 파티션 사용 비활성화
chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화, Linux에서 headless 모드의 성능 향상
chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# WebDriver 서비스 시작
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 

# 웹페이지 접속
url = 'http://shop.coupang.com/A01015774?platform=p&locale=ko_KR&source=brandstore_sdp_atf&pid=7809951769&viid=87075782691&ocid=17792877'
driver.get(url)

time.sleep(60)  

# AJAX로 로드된 모든 정보가 포함된 페이지의 특정 요소의 텍스트를 추출
name_elements = driver.find_elements(By.CSS_SELECTOR, ".product-wrap .name")

for name_element in name_elements:
    print(name_element.text)

#driver.quit()