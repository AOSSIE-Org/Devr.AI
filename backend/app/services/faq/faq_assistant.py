from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

class FaqAssistant:
    def __init__(self, groq_api_key=None, groq_model=None):        
        # Initialize the LLM
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model=groq_model,
            streaming=False
        )
        
        # Set up the FAQ prompt template
        self.faq_prompt = PromptTemplate.from_template(
            """You are a helpful AI assistant that answers questions based only on the provided context.
            
            Instructions:
            1. Do not include phrases like "Based on the context" or "According to the provided information"
            2. Do not repeat or include the instructions in your answer
            3. Do not make up information
            
            Context:
            {context}
            
            Question:
            {question}
            
            Answer:"""
        )
        
        # Create the FAQ chain
        self.faq_chain = self.faq_prompt | self.llm | StrOutputParser()
    
    def generate_faq_response(self, question: str, retrieved_documents: List[Dict[str, Any]]) -> str:
        """Generates a response to a question using the LLM model."""
        # Extract the content of the retrieved documents
        documents = [doc['content'] for doc in retrieved_documents]
        
        print("docs", documents)

        # Generate a response from the LLM model
        response = self.faq_chain.invoke({'context': "\n".join(documents), 'question': question})
        return response
