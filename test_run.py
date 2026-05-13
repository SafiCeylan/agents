import os
import sys
from dotenv import load_dotenv
from memory.vector_db import LongTermMemory
from core.multi_agent_system import MultiAgentSystem

load_dotenv()

def run_single_test(question):
    print(f"\n--- TEST BAŞLATILIYOR ---")
    print(f"Soru: {question}")
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("HATA: OPENROUTER_API_KEY eksik! Lütfen .env dosyasını kontrol edin.")
        return

    memory = LongTermMemory()
    ns = MultiAgentSystem(memory)

    print("Şef Ajan analiz ediyor...")
    response = ns.run(question)
    print(f"\nAsistan Yanıtı:\n{response}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "BTC-USD fiyatı nedir ve benim için uygun mu?"
    run_single_test(query)
