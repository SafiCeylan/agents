import asyncio
from tools.finance import get_market_analysis
from memory.vector_db import LongTermMemory

class Watchtower:
    def __init__(self, memory: LongTermMemory):
        self.memory = memory
        self.active = True

    async def run_patrol(self):
        print("--- Gözcü (Watchtower) Nöbete Başladı ---")
        while self.active:
            # 1. Hafızadan izleme listesini ve kullanıcı tercihlerini al
            # Şimdilik statik bir örnek, sonra bunu dinamik yapacağız
            target_assets = ["BTC-USD", "AAPL"] 
            
            for asset in target_assets:
                # get_market_analysis LangChain Tool olduğu için invoke kullanıyoruz
                data = get_market_analysis.invoke({"symbol": asset})
                
                # Eğer veri sözlük formatında döndüyse (hata mesajı değilse)
                if isinstance(data, dict) and 'daily_change_percent' in data:
                    # 2. Risk Analizi: Eğer günlük değişim %3'ten fazlaysa
                    if abs(data['daily_change_percent']) > 3.0:
                        alert_msg = f"Kanka dikkat! {asset} piyasasında %{data['daily_change_percent']} değişim var. Senin stratejin için kritik olabilir!"
                        # Burada Telegram üzerinden mesaj atma fonksiyonu çağrılacak
                        print(f"\n[ALARM]: {alert_msg}")
                else:
                    pass # Veri bulunamadıysa veya hata ise geç
            
            # Test için 30 saniye bekle (Gerçekte 3600 olacak)
            print("Gözcü etrafı kolaçan etti, bir sorun yok. Dinleniyor... (30sn)")
            await asyncio.sleep(30)
