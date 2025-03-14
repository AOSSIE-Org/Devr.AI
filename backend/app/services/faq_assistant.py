from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class FaqAssistant:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # Set up the FAQ prompt template
        self.faq_prompt = PromptTemplate.from_template("""You are an AI assistant that answers questions based only on the provided context.  
                                                        If the context does not contain the required information, respond with: "I do not know."  

                                                        Context:  
                                                        {context}  

                                                        Question:  
                                                        {question}  

                                                        Answer:
                                                        """)
        
        # Create the FAQ chain
        self.faq_chain = self.faq_prompt | self.llm | StrOutputParser()
    
    def generate_faq_response(self, question: str, retrieved_documents: List[Dict[str, Any]]) -> str:
        """Generates a response to a question using the LLM model."""
        # Extract the content of the retrieved documents
        documents = [doc['content'] for doc in retrieved_documents]
        
        # Generate a response from the LLM model
        response = self.faq_chain.invoke({'context': "\n".join(documents), 'question': question})
        return response
