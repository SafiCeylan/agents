import os
import ccxt
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

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
        if paper_mode:
            return {
                "status": "PAPER_SUCCESS",
                "message": f"SIMÜLASYON: {symbol} için {amount} miktarında {side} işlemi {order_type} emriyle (Fiyat: {price or 'Market'}) kaydedildi.",
                "details": {
                    "symbol": symbol,
                    "side": side,
                    "amount": amount,
                    "price": price,
                    "mode": "PAPER"
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
            "details": order
        }

    except Exception as e:
        return f"Trade uygulama hatası: {str(e)}"
