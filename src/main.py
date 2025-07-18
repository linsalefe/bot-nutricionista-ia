from dotenv import load_dotenv
import os

load_dotenv()
print("OpenAI API Key:", os.getenv("OPENAI_API_KEY"))

