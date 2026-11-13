
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing")

client = OpenAI(api_key=api_key)

try:
    response = client.responses.create(
        model="gpt-5.5",
        input="Reply with exactly: DBA Agent API Connection Successful"
    )

    print(response.output_text)

except Exception as error:
    print(f"OpenAI API test failed: {type(error).__name__}")
    print(str(error))
