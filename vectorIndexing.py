# 필요한 프로그램:
# 1. Elasticsearch (http://localhost:9200에서 실행 중이어야 함)
# 2. SQLite (amazon_reviews.db 파일이 필요함)

# 필요한 라이브러리:
# pip install pandas elasticsearch sentence-transformers spacy fastapi pydantic textblob uvicorn
# python -m spacy download ko_core_news_sm

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import spacy
from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from textblob import TextBlob

# SQLite 연결 설정
conn = sqlite3.connect('C:\\Users\\inno\\Downloads\\sqlite-tools-win-x64-3460100\\amazon_reviews.db')

# Elasticsearch 클라이언트 생성 부분을 수정
try:
    es = Elasticsearch(["http://localhost:9200"])
    es.info()  # Elasticsearch 연결 테스트
except Exception as e:
    print(f"Elasticsearch 연결 오류: {e}")
    exit(1)

# spaCy 모델 로드
nlp = spacy.load("ko_core_news_sm")

# Sentence Transformer 모델 로드
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

# FastAPI 앱 생성
app = FastAPI()

# 검색 요청을 위한 Pydantic 모델
class SearchRequest(BaseModel):
    query: str

def create_index():
    index_name = "amazon_reviews"
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "review_id": {"type": "keyword"},
                "product_id": {"type": "keyword"},
                "review_text": {"type": "text"},
                "star_rating": {"type": "integer"},
                "helpful_votes": {"type": "integer"},
                "total_votes": {"type": "integer"},
                "verified_purchase": {"type": "boolean"},
                "review_headline": {"type": "text"},
                "review_date": {"type": "date"}
            }
        }
    }
    
    try:
        es.indices.create(index=index_name, body=settings)
        print(f"인덱스 '{index_name}'가 생성.")
    except Exception as e:
        print(f"인덱스 생성 중 오류 발생: {e}")

def index_data():
    print("데이터 색인 시작...")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM amazon_fine_food_reviews")
    total_rows = cursor.fetchone()[0]
    
    cursor.execute("SELECT * FROM amazon_fine_food_reviews")
    rows = cursor.fetchall()
    
    existing_count = get_index_count()
    print(f"기존 문서 수: {existing_count}")
    
    for i, row in enumerate(rows, 1):
        doc = {
            'id': row[0],
            'text': row[9],
            'embedding': model.encode(row[9]).tolist()
        }
        es.index(index='amazon_reviews', body=doc)
        if i % 10 == 0:
            current_count = existing_count + i
            progress = (current_count / total_rows) * 100
            print(f"{current_count}/{total_rows} 색인 완료 ({progress:.2f}%)")
    
    final_count = get_index_count()
    print(f"데이터 색인 완료. 최종 문서 수: {final_count}")

@app.get("/search")
async def search(query: str):
    query_embedding = model.encode(query).tolist()
    query_sentiment = TextBlob(query).sentiment.polarity

    search_body = {
        "_source": {"excludes": ["embedding"]},
        "query": {
            "function_score": {
                "query": {
                    "match": {
                        "text": query
                    }
                },
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_embedding}
                            }
                        }
                    },
                    {
                        "script_score": {
                            "script": {
                                "source": "1.0 / (1.0 + Math.abs(params.query_sentiment - doc['sentiment'].value))",
                                "params": {"query_sentiment": query_sentiment}
                            }
                        }
                    }
                ],
                "score_mode": "sum"
            }
        }
    }

    results = es.search(index='amazon_reviews', body=search_body)
    return results['hits']['hits']

@app.post("/api/search")
async def api_search(request: SearchRequest):
    # 쿼리 임베딩 생성
    query_embedding = model.encode(request.query).tolist()
    
    # Elasticsearch에서 의미 기반 검색
    search_body = {
        "_source": {"excludes": ["embedding"]},  # embedding 필드 제외
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
    }
    
    results = es.search(index='amazon_reviews', body=search_body)
    return {"results": results['hits']['hits']}

def index_exists():
    return es.indices.exists(index="amazon_reviews")

def get_index_count():
    try:
        return es.count(index="amazon_reviews")['count']
    except Exception as e:
        print(f"인덱스 카운트 확인 오류: {e}")
        return 0

def main():
    print("프로그램 시작")
    try:
        if not index_exists():
            print("인덱스 없음. 새로 생성")
            create_index()
            index_data()
        else:
            doc_count = get_index_count()
            print(f"인덱스 존재. 현재 문서 수: {doc_count}")
            
            expected_count = 20000  # 예상 전체 문서 수
            if doc_count < expected_count * 0.9:
                print("문서 수 부족. 추가 색인 진행")
                index_data()
            else:
                print("충분한 문서 색인됨. 기존 데이터 사용")
        
        print("서버 시작")
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()  # 데이터베이스 연결 종료

if __name__ == "__main__":
    main()
