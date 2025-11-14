import os

import ollama
from django.conf import settings
from groq import Groq


class BaseAIAssistant:
    """
    Base class that describes what our AI assistant should be able to do
    """

    def get_city_guide(self, city_name, country_name):
        prompt = (
            f"You are a helpful travel assistant. "
            f"Write a short, engaging travel guide for {city_name}, {country_name}. "
            f"Include 3 top attractions and 1 local dish to try. "
            f"Keep it under 100 words."
        )
        try:
            return self._generate(prompt)
        except Exception as e:
            return f"AI Service is currently unavailable: {str(e)}"

    def _generate(self, prompt):
        """This must be implemented in child classes"""
        raise NotImplementedError("Subclasses must implement the _generate method.")


# OLLAMA (LOCAL)
class OllamaAssistant(BaseAIAssistant):
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=self.host)
        self.model = "llama3.2"  # Or gemma:2b, mistral

    def _generate(self, prompt):
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return response["message"]["content"]


# GROQ (PRODUCTION)
class GroqAssistant(BaseAIAssistant):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-20b"

    def _generate(self, prompt):
        completion = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.7,
            max_tokens=1024,
        )
        return completion.choices[0].message.content


def get_ai_assistant():
    """
    Decide wich version of AI use based on settings
    """
    if settings.DEBUG:
        # In debug mode use Ollama
        return OllamaAssistant()
    else:
        # On production use Groq
        return GroqAssistant()
