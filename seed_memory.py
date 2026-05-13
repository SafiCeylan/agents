import os
from dotenv import load_dotenv
from memory.vector_db import LongTermMemory

load_dotenv()

def seed():
    print("--- Hafıza Tohumlanıyor ---")
    memory = LongTermMemory()
    
    # Simüle edilmiş kullanıcı profili
    profile_data = [
        "Kullanıcı Adı: Mehmet",
        "Risk Profili: Düşük riskli yatırımları tercih eder, volatiliteden hoşlanmaz.",
        "İlgi Alanları: Kripto paralar (özellikle BTC) ve Teknoloji hisseleri.",
        "Önceki konuşmalarda Mehmet, uzun vadeli yatırımcı olduğunu belirtti."
    ]
    
    for info in profile_data:
        memory.add_memory(info)
        print(f"Eklendi: {info}")
    
    print("\n[BAŞARILI] Hafıza güncellendi. Artık asistan bu bilgileri hatırlayacak.")

if __name__ == "__main__":
    seed()
