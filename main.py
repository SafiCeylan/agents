import os
from dotenv import load_dotenv
from memory.vector_db import LongTermMemory
from core.multi_agent_system import MultiAgentSystem

# Load environment variables
load_dotenv()

def main():
    print("--- Otonom Agent Sistemi Başlatılıyor ---")
    
    # Check for API Key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("HATA: OPENROUTER_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.")
        return

    # Initialize Components
    memory = LongTermMemory()
    ns = MultiAgentSystem(memory)

    print("Şef Ajan Hazır! (Çıkmak için 'exit' yazın)")
    
    while True:
        user_input = input("\nSen: ")
        if user_input.lower() in ["exit", "quit", "çıkış"]:
            break
            
        print("\nŞef Ajan ve departmanı çalışıyor...")
        response = ns.run(user_input)
        print(f"\nŞef Ajan:\n{response}")

if __name__ == "__main__":
    main()
