from typing import Dict, List, Tuple, Optional
from haystack.nodes.base import BaseComponent
from haystack.schema import Document

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