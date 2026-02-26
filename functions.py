import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("SECRET_KEY"))

def get_embedding(text):

    response = client.embeddings.create(
        input = text,
        model = "text-embedding-3-small"
    )

    return response.data[0].embedding