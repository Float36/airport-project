import os
import ollama
from django.conf import settings


class AI_Assistant:
    def __init__(self):
        self.host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.client = ollama.Client(host=self.host)
        self.model = "llama3.2"

    def get_city_guide(self, city_name, country_name):
        """
        Generate info about your city
        """
        prompt = (
            f"You are a helpful traval assistant. "
            f"Write a short, engaging travel guid for {city_name}, {country_name}"
            f"Include 3 top attraction and 1 local dish to try. "
            f"Keep it under 100 words."
        )

        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            return f"AI Services unavailable: {str(e)}"

