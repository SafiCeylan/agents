import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

class Brain:
    """
    Brain: Groq (birincil, hızlı/ücretsiz) veya OpenRouter (yedek) destekler.
    429 rate limit durumunda otomatik olarak yeniden dener.
    """
    def __init__(self, model_name="llama-3.3-70b-versatile", temperature=0.7, api_key=None, backend="groq"):
        self.model_name = model_name
        self.temperature = temperature
        self.backend = backend
        self.api_key = api_key or (
            os.getenv("GROQ_API_KEY") if backend == "groq" else os.getenv("OPENROUTER_API_KEY")
        )
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        if self.backend == "groq":
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=1000,
                openai_api_key=self.api_key,
                openai_api_base="https://api.groq.com/openai/v1",
            )
        else:
            # OpenRouter yedek
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=1000,
                openai_api_key=self.api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://localhost:3000",
                    "X-Title": "Synthic Agency",
                }
            )

    def get_llm(self):
        return self.llm

    def invoke_with_retry(self, messages, max_retries: int = 3):
        """429 rate limit durumunda otomatik bekleyip yeniden dener."""
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except Exception as e:
                err = str(e)
                if "429" in err:
                    wait = 15 * (attempt + 1)  # 15s, 30s, 45s
                    print(f"[Brain] Rate limit (429) — {wait}s bekleniyor... (deneme {attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    raise
        return self.llm.invoke(messages)

    def switch_model(self, model_name):
        self.model_name = model_name
        self.llm = self._initialize_llm()
        return self.llm
