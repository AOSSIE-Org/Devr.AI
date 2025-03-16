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
