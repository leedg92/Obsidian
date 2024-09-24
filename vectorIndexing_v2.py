# 필요한 프로그램:
# 1. Elasticsearch (http://localhost:9200에서 실행 중이어야 함)
# 2. SQLite (amazon_reviews.db 파일이 필요함)

# 필요한 라이브러리:
# pip install pandas elasticsearch sentence-transformers spacy fastapi pydantic textblob uvicorn
# python -m spacy download ko_core_news_sm

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
from elasticsearch import Elasticsearch, helpers
from sentence_transformers import SentenceTransformer
import spacy
from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel
from textblob import TextBlob
import sys  
import time  
from elasticsearch.helpers import bulk
from argostranslate import package, translate
import argostranslate.package
import argostranslate.translate

import os

# SQLite 연결 설정
conn = sqlite3.connect('C:\\Users\\inno\\Downloads\\sqlite-tools-win-x64-3460100\\amazon_reviews.db')

# 번역 모델 설치 (프로그램 최초 실행 시 한 번만 실행)
def install_translation_model():
    # 이미 설치된 언어 확인
    installed_languages = argostranslate.translate.get_installed_languages()
    from_code = "en"
    to_code = "ko"
    
    # 영어에서 한국어로의 번역이 가능한지 확인
    if not any(lang for lang in installed_languages if lang.code == from_code) or \
       not any(lang for lang in installed_languages if lang.code == to_code):
        print("번역 모델 다운로드 및 설치 중...")
        # 사용 가능한 패키지 목록 업데이트
        argostranslate.package.update_package_index()
        # 사용 가능한 패키지 가져오기
        available_packages = argostranslate.package.get_available_packages()
        # 영어에서 한국어로의 번역 패키지 찾기
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages
            )
        )
        # 패키지 다운로드 및 설치
        argostranslate.package.install_from_path(package_to_install.download())
        print("번역 모델 설치 완료")
    else:
        print("번역 모델이 이미 설치되어 있습니다.")

# 번역 함수
def translate_text(text, from_code='en', to_code='ko'):
    installed_languages = argostranslate.translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == from_code), None)
    to_lang = next((lang for lang in installed_languages if lang.code == to_code), None)
    
    if not from_lang or not to_lang:
        raise ValueError("지원되지 않는 언어 코드입니다.")
    
    translation = from_lang.get_translation(to_lang)
    return translation.translate(text)

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
                "review_text_kor": {"type": "text"},
                "summary": {"type": "text"},
                "summary_kor": {"type": "text"},
                "score": {"type": "float"},  
                "star_rating": {"type": "integer"},
                "helpful_votes": {"type": "integer"},
                "total_votes": {"type": "integer"},
                "verified_purchase": {"type": "boolean"},
                "review_headline": {"type": "text"},
                "review_date": {"type": "date"},
                "embedding": {"type": "dense_vector", "dims": 512}
            }
        }
    }
    
    try:
        es.indices.create(index=index_name, body=settings)
        print(f"인덱스 '{index_name}' 생성.")
    except Exception as e:
        print(f"인덱스 생성 중 오류 발생: {e}")

def index_data():
    print("데이터 색인 시작...")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM amazon_fine_food_reviews")
    max_id = cursor.fetchone()[0]
    
    batch_size = 20
    total_indexed = 0
    last_indexed_id = 0

    while last_indexed_id < max_id:
        try:
            for start_id in range(last_indexed_id + 1, max_id + 1, batch_size):
                end_id = min(start_id + batch_size - 1, max_id)
                
                cursor.execute(f"SELECT id, text, summary, score FROM amazon_fine_food_reviews WHERE id BETWEEN {start_id} AND {end_id}")
                rows = cursor.fetchall()

                actions = []
                for row in rows:
                    id, text, summary, score = row
                    
                    # Argos Translate를 사용한 번역
                    translated_text = translate_text(text)
                    translated_summary = translate_text(summary)

                    # 임베딩 생성
                    embedding = model.encode(text).tolist()

                    doc = {
                        'id': id,
                        'text': text,
                        'translated_text': translated_text,
                        'summary': summary,                        
                        'summary_kor': translated_summary,
                        'score': float(score),
                        'embedding': embedding
                    }
                    action = {
                        "_index": "amazon_reviews",
                        "_id": id,
                        "_source": doc
                    }
                    actions.append(action)

                if actions:
                    # 새로운 방식으로 bulk 작업 수행
                    with es.options(request_timeout=300):
                        success, failed = helpers.bulk(es, actions)
                    
                    if failed:
                        print(f'문서 색인 실패: {len(failed)} 건')
                    total_indexed += success
                    last_indexed_id = end_id
                    print(f"진행 상황: {total_indexed} / {max_id} 문서 색인 완료")
                else:
                    print(f"ID 범위 {start_id}-{end_id}에 데이터가 없습니다.")

        except Exception as e:
            print(f"오류 발생: {e}")
            retry = input("다시 시작하시겠습니까? (y: 예, n: 아니오, c: 계속): ").lower()
            if retry == 'y':
                continue
            elif retry == 'c':
                continue_option = input("마지막으로 색인된 ID를 유지하고 계속하시겠습니까? (y/n): ").lower()
                if continue_option == 'y':
                    continue
                else:
                    es.delete(index="amazon_reviews", id=last_indexed_id)
                    last_indexed_id -= 1
                    total_indexed -= 1
                    continue
            else:
                break

    print(f"데이터 색인 완료. 총 {total_indexed}개 문서 처리.")

@app.get("/search")
async def search(query: str):
    query_embedding = model.encode(query).tolist()
    
    # TextBlob을 사용하여 쿼리의 감성 분석
    query_sentiment = TextBlob(query).sentiment.polarity

    search_body = {
        "_source": {"excludes": ["embedding"]},
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["text^3", "summary^2"],
                            "fuzziness": "AUTO",
                            "minimum_should_match": "70%"
                        }
                    }
                ],
                "should": [
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                                "params": {"query_vector": query_embedding}
                            }
                        }
                    }
                ],
                "filter": [
                    {
                        "range": {
                            "score": {
                                "gte": 0,
                                "lte": 5 if query_sentiment >= 0 else 2.5
                            }
                        }
                    }
                ]
            }
        },
        "min_score": 2.0
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

def delete_index():
    index_name = "amazon_reviews"
    try:
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
            print(f"인덱스 '{index_name}' 삭제.")
        else:
            print(f"인덱스 '{index_name}'가 존재하지 않음.")
    except Exception as e:
        print(f"인덱스 삭제 중 오류 발생: {e}")

def main():
    print("프로그램 시작")
    install_translation_model()  # 번역 모델 설치
    try:
        if index_exists():
            delete_option = input("기존 인덱스 삭제 ? (y/n): ")
            if delete_option.lower() == 'y':
                delete_index()
                create_index()
                index_data()
            else:
                print("기존 인덱스 유지.")
                continue_option = input("색인을 계속하시겠습니까? (y/n): ")
                if continue_option.lower() == 'y':
                    index_data()
        else:
            print("인덱스 없음. 새로 생성")
            create_index()
            index_data()

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()  # 데이터베이스 연결 종료

if __name__ == "__main__":
    main()
