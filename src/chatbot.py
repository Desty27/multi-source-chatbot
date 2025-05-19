from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from src.file_processor import process_uploaded_file
from src.web_search import search_web

class ChatBot:
    def __init__(self):
        self.context = ""
        self.llm = OpenAI(temperature=0.7)
        
    def add_context(self, content):
        self.context += content + "\n"
            
    def generate_response(self, question):
        # First try with context
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="Context: {context}\n\nQuestion: {question}\nAnswer:"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        answer = chain.run({"context": self.context, "question": question})
        
        # Fallback to web search
        if any(phrase in answer.lower() for phrase in ["i don't know", "not in the context"]):
            web_results = search_web(question)
            answer = self._process_web_results(web_results, question)
        
        return answer
    
    def _process_web_results(self, results, question):
        # Process web search results
        snippets = [result.get("snippet", "") for result in results.get("organic", [])[:3]]
        web_context = "\n".join(snippets)
        
        prompt_template = PromptTemplate(
            input_variables=["web_context", "question"],
            template="Web Context: {web_context}\n\nQuestion: {question}\nAnswer:"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run({"web_context": web_context, "question": question})