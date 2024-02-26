import pandas as pd
from bs4 import BeautifulSoup

# HTML 파일 열기
with open('C:\\Users\\leedg\\Documents\\ajax_loaded_page.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Beautiful Soup 객체 생성
soup = BeautifulSoup(html_content, 'lxml')

# CSS 선택자를 사용하여 특정 요소의 텍스트 추출
elements = soup.select(".product-wrap .name")

# 텍스트 데이터를 리스트로 저장
data = [element.text for element in elements]

# pandas DataFrame 생성
df = pd.DataFrame(data, columns=['Product Name'])

# Excel 파일로 저장
# df.to_excel('products.xlsx', index=False, engine='openpyxl')
df.to_excel('C:\\Users\\leedg\\Documents\\products.xlsx', index=False, engine='openpyxl')
