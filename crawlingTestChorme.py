from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import re
import cx_Oracle

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 이미지 로딩 비활성화
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,  # 이미지 로딩 비활성화
})

caps = DesiredCapabilities.CHROME.copy()
caps['pageLoadStrategy'] = 'eager'  # 'normal', 'eager', 'none'

chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# 로컬에 설치된 크롬 드라이버의 경로
driver_path = "C:\\Users\\sli004\\Downloads\\chromedriver-win32\\chromedriver.exe"

# WebDriver 서비스 시작
driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)

# 웹페이지 접속
url = 'https://www.pknu.ac.kr/main/163?pageIndex=1&bbsId=2&searchCondition=title&searchKeyword=&cd=10001'
driver.get(url)
time.sleep(1)

time.sleep(60)  

try:
    current_page = 0
    #while True:
    while current_page < 3:
        current_page += 1

        posts = driver.find_elements(By.CSS_SELECTOR, "tr" + (":not(.noti)" if current_page > 1 else ""))
        for post in posts:
            try:
                title_element = post.find_element(By.CLASS_NAME, "bdlTitle")
                title_text = title_element.text
                title_link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                # Extracting number from the link
                no_match = re.search(r"&no=(\d+)", title_link)
                no = no_match.group(1) if no_match else None

                regi_date = post.find_element(By.CLASS_NAME, "bdlDate").text
                regi_name = post.find_element(By.CLASS_NAME, "bdlUser").text
                
                data_list.append((no, title_text, regi_date, regi_name))
            except NoSuchElementException:
                continue

        # Moving to the next page
        pagination_links = driver.find_elements(By.CSS_SELECTOR, "li.paginate a")
        next_page_found = False
        for link in pagination_links:
            if link.text == str(current_page + 1):
                next_page_found = True
                link.click()
                time.sleep(1)
                break

        if not next_page_found:
            break

except Exception as e:
    print(f"An exception occurred: {e}")

finally:
    print(data_list)
    print("data_list")
    driver.quit()

# Oracle DB 접속 정보 설정
dsnStr = cx_Oracle.makedsn("YourDBHost", YourDBPort, sid="YourDBSID")
connection = cx_Oracle.connect(user="YourUsername", password="YourPassword", dsn=dsnStr)

cursor = connection.cursor()

# 데이터 삽입 쿼리
insert_query = """
INSERT INTO your_table_name (no, title, regi_date, regi_name)
VALUES (:1, :2, :3, :4)
"""

# 데이터를 데이터베이스에 삽입하는 루프
for item in data_list:
    cursor.execute(insert_query, item)

# 커밋으로 변경사항 적용
connection.commit()

# 자원 정리
cursor.close()
connection.close()
