import logging

logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[
        logging.FileHandler("agent.log"),  
        logging.StreamHandler()            
    ]
)

from fastapi import FastAPI
from pydantic import BaseModel
from .query_processor import QueryProcessor

app = FastAPI()
processor = QueryProcessor()

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    response = processor.generate_response(request.query)
    return {"response": response}