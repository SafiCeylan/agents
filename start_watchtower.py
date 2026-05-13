import asyncio
from memory.vector_db import LongTermMemory
from core.observer import Watchtower

async def main():
    # 1. Hafıza bağlantısını kur
    memory = LongTermMemory()
    
    # 2. Gözcüyü başlat
    watchtower = Watchtower(memory)
    
    # Gözcünün devriyesini başlat
    await watchtower.run_patrol()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGözcü nöbeti sonlandırıldı.")
