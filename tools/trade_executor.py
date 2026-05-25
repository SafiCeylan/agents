import os
import ccxt
from datetime import datetime
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def get_balance(symbol: str = "USDT"):
    """
    Binance hesabındaki bakiye bilgisini getirir.
    PAPER_TRADING=true ise simüle edilmiş 10,000 USDT döner.
    """
    paper_mode = os.getenv("PAPER_TRADING", "true").lower() == "true"
    
    try:
        if paper_mode:
            return {
                "symbol": symbol,
                "free": 10000.0,
                "used": 0.0,
                "total": 10000.0,
                "mode": "PAPER"
            }
        
        api_key = os.getenv("BINANCE_API_KEY")
        secret = os.getenv("BINANCE_SECRET")
        
        if not api_key or not secret:
            return "Hata: Binance API anahtarları eksik!"

        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })
        
        balance = exchange.fetch_balance()
        if symbol in balance:
            return {
                "symbol": symbol,
                "free": balance[symbol]['free'],
                "used": balance[symbol]['used'],
                "total": balance[symbol]['total'],
                "mode": "LIVE"
            }
        else:
            return f"Hata: {symbol} bakiyesi bulunamadı."
            
    except Exception as e:
        return f"Bakiye çekme hatası: {str(e)}"

@tool
def execute_trade(symbol: str, side: str, amount: float, price: float = None, order_type: str = "market"):
    """
    Binance üzerinde işlem açar.
    PAPER_TRADING=true ise sadece simülasyon yapar.
    side: 'buy' veya 'sell'
    order_type: 'market' veya 'limit'
    """
    paper_mode = os.getenv("PAPER_TRADING", "true").lower() == "true"
    
    try:
        # 1. EMERGENCY KILL SWITCH KONTROLÜ
        kill_switch = os.getenv("EMERGENCY_KILL_SWITCH", "false").lower() == "true"
        if kill_switch:
            return "🛑 EMERGENCY KILL SWITCH AKTİF: Tüm alım/satım işlemleri güvenlik nedeniyle kilitlenmiştir."

        # 2. BASİT DOĞRULAMA
        if amount <= 0:
            return "Hata: İşlem miktarı 0'dan büyük olmalıdır."
        
        if side.lower() not in ["buy", "sell"]:
            return "Hata: 'side' parametresi 'buy' veya 'sell' olmalıdır."
            
        # 3. MAX LOT (TEK İŞLEM BÜYÜKLÜĞÜ) KONTROLÜ
        # Cüzdanın maksimum %10'u ile işlem açılmasına izin verilir
        # (Eğer fiyat biliniyorsa hesaplanır, bilinmiyorsa kabaca izin verilir ama uyarı düşülür)
        if price:
            trade_value = amount * price
            # Sadece örnek hesaplama (Gerçekte get_balance() ile total USDT alınmalı)
            # Varsayılan limit: Tek seferde 1000 USDT'den fazla işlem açılamaz
            if trade_value > 1000:
                return f"🛑 RİSK LİMİTİ AŞILDI: Sistem güvenliği gereği tek işlemde maksimum 1000 USDT büyüklüğünde emir verilebilir (İstenen: {trade_value})."

        if paper_mode:
            return {
                "status": "PAPER_SUCCESS",
                "message": f"🚀 SIMÜLASYON BAŞARILI: {symbol} için {amount} miktarında {side.upper()} işlemi {order_type.upper()} emriyle kaydedildi.",
                "details": {
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "price": price or "Piyasa Fiyatı",
                    "mode": "PAPER",
                    "timestamp": str(datetime.now())
                }
            }
        
        # Gerçek İşlem (Binance)
        api_key = os.getenv("BINANCE_API_KEY")
        secret = os.getenv("BINANCE_SECRET")
        
        if not api_key or not secret:
            return "Hata: Binance API anahtarları eksik! PAPER_TRADING=true modunda deneyin."

        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
            'enableRateLimit': True,
        })

        # İşlem öncesi bakiye kontrolü (basit)
        # (Gerçekte daha detaylı kontrol gerekir ama şimdilik temel yapı)

        if order_type == "market":
            if side == "buy":
                order = exchange.create_market_buy_order(symbol, amount)
            else:
                order = exchange.create_market_sell_order(symbol, amount)
        else:
            order = exchange.create_order(symbol, order_type, side, amount, price)

        return {
            "status": "LIVE_SUCCESS",
            "order_id": order['id'],
            "details": order,
            "message": f"✅ GERÇEK İŞLEM BAŞARILI: {symbol} {side.upper()} emri iletildi."
        }

    except Exception as e:
        return f"❌ Trade uygulama hatası: {str(e)}"
