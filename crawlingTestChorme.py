from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.common.exceptions import NoSuchElementException


# from openpyxl import Workbook

chrome_options = Options()
chrome_options.add_argument("--disable-web-security")  # 웹 보안 비활성화
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")


# ChromeDriver 경로 설정
chrome_driver_path = "C:\\Users\\leedg\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# WebDriver 서비스 시작
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options) 

# 웹페이지 접속
url = 'https://shop.coupang.com/A01015774?platform=p&locale=ko_KR&source=brandstore_sdp_atf&pid=7809951769&viid=87075782691&ocid=17792877'
driver.get(url)

time.sleep(500)  

# # 페이지 끝까지 스크롤 다운
# last_height = driver.execute_script("return document.body.scrollHeight")


# 점진적으로 스크롤 다운
# scroll_pause_time = 1  # 스크롤 사이 대기 시간 (초)
# scroll_height = 600  # 한 번에 스크롤할 높이 (픽셀)

# # "contents" 섹션을 지날 때마다 정보를 로드하기 위해 점진적으로 스크롤
# for _ in range(20):  # 필요에 따라 반복 횟수 조정
#     # 페이지를 조금씩 여러 번 내림
#     driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_height)
#     time.sleep(scroll_pause_time)  # 동적 콘텐츠가 로드될 시간을 기다림

# AJAX로 로드된 모든 정보가 포함된 페이지의 특정 요소의 텍스트를 추출
# 예: 'product-wrap' 클래스를 가진 모든 'li' 태그 내의 'name' 클래스를 가진 'div' 태그
name_elements = driver.find_elements(By.CSS_SELECTOR, ".product-wrap .name")

for name_element in name_elements:
    print(name_element.text)

# 드라이버 종료 코드를 제거하거나 주석 처리
# driver.quit()