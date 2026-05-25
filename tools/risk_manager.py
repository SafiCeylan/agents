import os
from langchain.tools import tool

@tool
def calculate_risk_parameters(balance: float, entry_price: float, risk_percent: float = 1.0, side: str = "buy", atr: float = None):
    """
    İşlem için risk parametrelerini hesaplar (Lot büyüklüğü, SL, TP).
    Eğer 'atr' (Average True Range) sağlanırsa, Stop Loss buna göre dinamik hesaplanır (SL = 2 * ATR).
    Sağlanmazsa varsayılan %1.5 kullanılır.
    side: 'buy' veya 'sell'
    """
    try:
        # Risk miktarı (Dolar cinsinden)
        risk_amount = balance * (risk_percent / 100)
        
        # Stop Loss hesaplama
        if atr:
            # Dinamik ATR bazlı SL (2 * ATR kuralı yaygındır)
            sl_distance = atr * 2
            if side == "buy":
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + (sl_distance * 2) # 1:2 R/R
            else: # sell
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - (sl_distance * 2)
        else:
            # Varsayılan %1.5 Stop Loss mesafesi
            sl_percent = 0.015 
            if side == "buy":
                stop_loss = entry_price * (1 - sl_percent)
                take_profit = entry_price * (1 + (sl_percent * 2))
            else: # sell
                stop_loss = entry_price * (1 + sl_percent)
                take_profit = entry_price * (1 - (sl_percent * 2))

        # Lot büyüklüğü (Position Size)
        # Formül: Risk Miktarı / (Giriş - Stop Loss)
        price_diff = abs(entry_price - stop_loss)
        if price_diff <= 0:
            return "Hata: Geçersiz fiyat verisi veya Stop Loss girişe çok yakın."
            
        quantity = risk_amount / price_diff
        
        return {
            "balance": balance,
            "risk_amount_usd": round(risk_amount, 2),
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "quantity": round(quantity, 4),
            "risk_reward_ratio": "1:2",
            "method": "ATR-Based" if atr else "Percentage-Based"
        }
    except Exception as e:
        return f"Risk hesaplama hatası: {str(e)}"
