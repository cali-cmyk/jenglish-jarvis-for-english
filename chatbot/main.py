from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate




template = """
You are an English tutor to help develop your Students english skills. 
Youre multilingual which means that you always respond the language the user uses!!!!!

Always do the following:

Step 1: Greet the user warmly, in their language

Step 2: ask for a piece of writing to assess 

Step 3: grade the uploaded document very detailed on the following aspects: 

        Academic English
        Vocabulary
        Grammar
        Sentence Structure
        Linking Phrases

    
Step 4: explain to the student whats good and what can be worked on and suggest activities they can do to level up their language skills,
        in the

    
Conversation history: {context}

Student input: {question}

Answer:

"""


model = OllamaLLM(model="gemma3:1b",streaming=False)
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model




class ChatSession:
    def __init__(self):
        self.context = ""
        self.file_knowledge = ""

    def load_file_content(self, text):
        # Append the file's content to background knowledge
        self.file_knowledge += f"\n[FILE CONTENT START]\n{text}\n[FILE CONTENT END]\n"

    def reply(self, user_input):
        # Combine file knowledge + previous context + user input
        prompt_context = f"{self.file_knowledge}\n{self.context}"
        result = chain.invoke({"context": prompt_context, "question": user_input})
        self.context += f"\nUser: {user_input}\nAI: {result}"
        return result

        