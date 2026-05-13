import yfinance as yf
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
import os

@tool
def get_market_analysis(symbol: str):
    """
    Verilen sembol (örn: BTC-USD, AAPL, THYAO.IS) için güncel fiyat, 
    günlük değişim ve basit teknik analiz verilerini getirir.
    """
    try:
        # Ticker temizleme: $ işaretini kaldır, büyük harfe çevir
        clean_symbol = symbol.strip().upper().replace("$", "")
        # Kripto kısaltmalarını otomatik düzelt (BTC -> BTC-USD)
        crypto_map = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
        if clean_symbol in crypto_map:
            clean_symbol = crypto_map[clean_symbol]

        ticker = yf.Ticker(clean_symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return f"{clean_symbol} için veri bulunamadı. Sembolü kontrol et (örn: BTC-USD, AAPL, THYAO.IS)"
        
        current_price = data['Close'].iloc[-1]
        open_price = data['Open'].iloc[-1]
        change = ((current_price - open_price) / open_price) * 100
        
        return {
            "symbol": clean_symbol,
            "current_price": round(current_price, 2),
            "daily_change_percent": round(change, 2),
            "status": "Boğa" if change > 0 else "Ayı"
        }
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

@tool
def search_finance_news(query: str):
    """
    Finansal piyasalar, hisseler veya kripto paralar hakkında en güncel haberleri arar.
    """
    try:
        search = TavilySearchResults(k=3)
        results = search.run(query)
        return results
    except Exception as e:
        # Fallback to a simple message if Tavily fails or key is missing
        return f"Haber araması sırasında bir hata oluştu (Tavily anahtarını kontrol edin): {str(e)}"
