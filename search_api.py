from fastapi import FastAPI
from pydantic import BaseModel
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from textblob import TextBlob

app = FastAPI()

# Elasticsearch 클라이언트 생성
es = Elasticsearch(["http://localhost:9200"])

# Sentence Transformer 모델 로드
model = SentenceTransformer('distiluse-base-multilingual-cased-v1')

class SearchRequest(BaseModel):
    query: str

@app.post("/search")
async def search(request: SearchRequest):
    query = request.query
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)