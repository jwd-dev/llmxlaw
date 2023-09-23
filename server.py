from fastapi import FastAPI
from typing import Optional
from typing import Dict, List, Tuple, Optional
from haystack.schema import Document
from haystack.nodes.base import BaseComponent
from pypdf import PdfReader
from haystack import Pipeline
from haystack.nodes import MarkdownConverter, PreProcessor, PDFToTextConverter, TextConverter
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate
import os
from dotenv import load_dotenv
from document_logger import DocumentLogger
import uvicorn
from database import Database

load_dotenv()

app = FastAPI()
database = Database()

# Code from main.py to create index
document_store = WeaviateDocumentStore(host="http://localhost",
                                        port=8080,
                                        embedding_dim=768)

converter = TextConverter(remove_numeric_tables=True, valid_languages=["en"])
retriever = EmbeddingRetriever(
    document_store=document_store,
    batch_size=8,
    embedding_model="text-embedding-ada-002",
    api_key=os.getenv("OPENAI_API_KEY"),
    max_seq_len=1536
  )

@app.post("/create_index")
def create_index():
  timeline_finder = DocumentLogger()
  reader = PdfReader("filename.pdf")
  text = ""
  for page in reader.pages:
      text += page.extract_text() + "\n"
  with open('readme.txt', 'w') as f:
      f.write(text)
  
  preprocessor = PreProcessor()

  indexing_pipeline = Pipeline()
  indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
  indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
  indexing_pipeline.add_node(component=timeline_finder, name="DocumentLogger", inputs=["PreProcessor"])
  indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["DocumentLogger"])
  indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])

  indexing_pipeline.run(file_paths=['readme.txt'])
  return {"message": "Index created"}

# curl -X POST "http://0.0.0.0:8000/query_index" \
#      -H "Content-Type: application/json" \
#      -d '{"query": "DDOS", "top_k": 5}'
@app.post("/query_index")
def query_index(body: dict):
  query = body.get('query')
  top_k = body.get('top_k', 5)
  # Code from main.py to query index
  query_pipeline = Pipeline()

  prompt_template = PromptTemplate(prompt=""""Given the provided Documents, answer the Query. Make your answer detailed and long\n
                                              Query: {query}\n
                                              Documents: {join(documents)}
                                              Answer:
                                          """,
                                 output_parser=AnswerParser())
  prompt_node = PromptNode(model_name_or_path="gpt-4",
                         api_key=os.getenv("OPENAI_API_KEY"),
                         default_prompt_template=prompt_template)

  query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
  query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

  result = query_pipeline.run(query=query, params={"Retriever": {"top_k": top_k}})
  return result

@app.post("/list_timeline")
def query_index(body: dict):
  query = body.get('query')
  top_k = body.get('top_k', 5)
  # Code from main.py to query index
  query_pipeline = Pipeline()

  prompt_template = PromptTemplate(prompt=""""Given the provided Documents, answer the Query. Make your answer detailed and long\n
                                              Query: {query}\n
                                              Documents: {join(documents)}
                                              Answer:
                                          """,
                                 output_parser=AnswerParser())
  prompt_node = PromptNode(model_name_or_path="gpt-4",
                         api_key=os.getenv("OPENAI_API_KEY"),
                         default_prompt_template=prompt_template)

  query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
  query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])

  result = query_pipeline.run(query=query, params={"Retriever": {"top_k": top_k}})
  return result


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
