import csv
import sqlite3
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# SQLite 데이터베이스 연결
conn = sqlite3.connect('C:\\Users\\inno\\Downloads\\sqlite-tools-win-x64-3460100\\amazon_reviews.db')
cursor = conn.cursor()

# 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS amazon_fine_food_reviews (
    Id INTEGER PRIMARY KEY,
    ProductId TEXT,
    UserId TEXT,
    ProfileName TEXT,
    HelpfulnessNumerator INTEGER,
    HelpfulnessDenominator INTEGER,
    Score INTEGER,
    Time INTEGER,
    Summary TEXT,
    Text TEXT
)
''')

# CSV 파일을 청크로 읽어 SQLite에 삽입
chunksize = 10000  # 한 번에 처리할 행의 수
with open('C:\\Users\\inno\\Downloads\\archive\\Reviews.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)  # 헤더 건너뛰기
    
    chunk = []
    for row in csvreader:        
        chunk.append(row)
        if len(chunk) == chunksize:
            cursor.executemany('''
                INSERT INTO amazon_fine_food_reviews 
                (Id, ProductId, UserId, ProfileName, HelpfulnessNumerator, 
                HelpfulnessDenominator, Score, Time, Summary, Text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', chunk)
            chunk = []
    
    # 남은 데이터 처리
    if chunk:
        cursor.executemany('''
            INSERT INTO amazon_fine_food_reviews 
            (Id, ProductId, UserId, ProfileName, HelpfulnessNumerator, 
            HelpfulnessDenominator, Score, Time, Summary, Text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', chunk)

# 변경사항 저장 및 연결 종료
conn.commit()
conn.close()

print("데이터 가져오기 완료")