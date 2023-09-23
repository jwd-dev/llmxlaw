import json
import os
from typing import Dict, List, Tuple, Optional

import openai
from haystack import Document
from haystack.nodes.base import BaseComponent

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
                response = openai.ChatCompletion.create(
                    model = "gpt-4",
                    api_key = os.getenv("OPENAI_API_KEY"),
                    messages=[
                        {"role": "system",
                         "content": "Extract timeline events from this paragraph, use the following format. Write N/A if the line does not have an event associated with it. "+"""
                         {
	"event_name": "event name",
	"event_description": "event description",
	"time": "mm-dd-yyyy mm-dd-yyyy"
}
                         """},
                        {"role": "user",
                         "content": "In or about July 2016, Jha wrote and implemented computer code with his co-conspirators that enabled them to control and direct devices infected with the Mirai malware. Over 300,000 devices ultimately became part of the Mirai botnet and were used by Jha and others to unlawfully participate in DDOS attacks and other criminal activity. Some of these devices were located in the District of Alaska."},
                        {"role": "assistant",
                         "content": """
                         {
	"event_name": "Imposition of Sentence on Paras Jha",
	"event_description": "The court hearing for the imposition of sentence on Paras Jha took place",
	"time": "09-18-2018 09-18-2018"
}
                         """},
                        {"role": "user",
                         "content": str(doc.content.replace("\'","\""))}
                    ]
                )
                try:
                    print(json.loads(response.choices[0].message.content))
                except:
                    pass

        return {"documents": documents}, "output_1"

    def run_batch(self, **kwargs):
        return self.run(**kwargs)


