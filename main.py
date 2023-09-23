from pathlib import Path

from haystack import Pipeline
from haystack.nodes import MarkdownConverter, PreProcessor, PDFToTextConverter, TextConverter
from haystack.document_stores import WeaviateDocumentStore
from haystack.nodes import AnswerParser, EmbeddingRetriever, PromptNode, PromptTemplate
import logging
from typing import Dict, List, Tuple, Optional
from haystack.schema import Document
from haystack.nodes.base import BaseComponent
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentLogger(BaseComponent):
    """
    Custom node that logs the content of documents to the console.
    """

    outgoing_edges = 1

    def run(
            self,
            documents: Optional[List[Document]] = None,
            **kwargs
    ) -> Tuple[Dict, str]:
        """
        Log the content of each document to the console.

        :param documents: List of documents to log.
        :return: The same list of documents without any modification.
        """
        if documents:
            for doc in documents:
                print(f"Document ID: {doc.id}, Content: {doc.content}")

        return {"documents": documents}, "output_1"

    def run_batch(self, **kwargs):
        return self.run(**kwargs)


document_store = WeaviateDocumentStore(host="http://localhost",
                                       port=8080,
                                       embedding_dim=768)

timeline_finder = DocumentLogger()
reader = PdfReader("filename.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"
with open('readme.txt', 'w') as f:
    f.write(text)
converter = TextConverter(remove_numeric_tables=True, valid_languages=["en"])
preprocessor = PreProcessor()
retriever = EmbeddingRetriever(
    document_store=document_store,
    batch_size=8,
    embedding_model="text-embedding-ada-002",
    api_key="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",
    max_seq_len=1536
)
indexing_pipeline = Pipeline()
indexing_pipeline.add_node(component=converter, name="PDFConverter", inputs=["File"])
indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["PDFConverter"])
indexing_pipeline.add_node(component=timeline_finder, name="DocumentLogger", inputs=["PreProcessor"])
indexing_pipeline.add_node(component=retriever, name="Retriever", inputs=["DocumentLogger"])
indexing_pipeline.add_node(component=document_store, name="DocumentStore", inputs=["Retriever"])

indexing_pipeline.run(file_paths=['readme.txt'])

#
# prompt_template = PromptTemplate(prompt=""""Given the provided Documents, answer the Query. Make your answer detailed and long\n
#                                               Query: {query}\n
#                                               Documents: {join(documents)}
#                                               Answer:
#                                           """,
#                                  output_parser=AnswerParser())
# prompt_node = PromptNode(model_name_or_path="gpt-4",
#                          api_key="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",
#                          default_prompt_template=prompt_template)
#
# query_pipeline = Pipeline()
# query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
# query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
#
# query_pipeline.run(query="What is Weaviate", params={"Retriever": {"top_k": 5}})
