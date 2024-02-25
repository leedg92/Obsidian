from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
import time

# Firefox 실행 파일의 위치를 지정
firefox_binary_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"

options = FirefoxOptions()
options.accept_insecure_certs = True
options.binary_location = firefox_binary_path

# GeckoDriver 경로 설정
gecko_driver_path = "C:\\Users\\leedg\\Downloads\\geckodriver-v0.34.0-win32\\geckodriver.exe"

# WebDriver 서비스 시작 (Firefox) 및 옵션 적용
service = Service(executable_path=gecko_driver_path)
driver = webdriver.Firefox(service=service, options=options)

# 웹페이지 접속
url = 'https://shop.coupang.com/A01015774?platform=p&locale=ko_KR&source=brandstore_sdp_atf&pid=7809951769&viid=87075782691&ocid=17792877'
# url = 'https://coupang.com'
driver.get(url)

# 페이지 로드 대기
time.sleep(2)

# 페이지 맨 아래로 스크롤하고 조금 올리기를 300번 반복
for _ in range(300):
    # 페이지 맨 아래로 스크롤
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)  # 스크롤 사이에 적당한 대기 시간 추가
    # 페이지를 조금 올림 (여기서는 100px만큼 올림)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)

# 작업 완료 후 드라이버 종료
#driver.quit()
