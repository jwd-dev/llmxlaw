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
database_fake = [["Conspiracy to Cause Damage to Protected Computers","Paras Jha and other individuals conspired to knowingly cause damage to protected computers","07-01-2016","10-04-2016","2a0d34ff25586b6f1a17d474da5e3c0"],["Operation and Advertising of Mirai Botnet","Paras Jha used monikers like 'ogmemes' and 'Anna Senpai' to advertise the botnet and discuss its capabilities on cyber criminal discussion boards. Jha and his co-conspirators actively sought criminal clients for Mirai, serving as a point of contact for leasing the botnet and negotiating with prospective customers to generate illicit proceeds.","08-01-2016","09-30-2016","ad1df510958ef711da23e40cd26f9202"]]
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

@app.get("/create_index")
def create_index():
  timeline_finder = DocumentLogger(database_fake)
  reader = PdfReader("f2.pdf")
  text = ""
  for page in reader.pages:
      text += page.extract_text() + "\n"
  with open('readme.txt', 'w') as f:
      f.write(text)
  
  preprocessor = PreProcessor(split_length=100)

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
@app.get("/query_index")
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

@app.get("/list_timeline")
def query_index():
  return database_fake


if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000)
