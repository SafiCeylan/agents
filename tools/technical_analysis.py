import pandas as pd
import pandas_ta as ta
import yfinance as yf
from langchain.tools import tool

@tool
def get_technical_indicators(symbol: str, interval: str = "1h", period: str = "max"):
    """
    Belirli bir sembol ve zaman aralığı için teknik göstergeleri hesaplar.
    Göstergeler: RSI, MACD, Bollinger Bands, EMA20, EMA50.
    Interval seçenekleri: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1wk, 1mo
    """
    try:
        # Ticker temizleme
        clean_symbol = symbol.strip().upper().replace("$", "")
        crypto_map = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "BNB": "BNB-USD"}
        if clean_symbol in crypto_map:
            clean_symbol = crypto_map[clean_symbol]

        # Veri çekme
        df = yf.download(clean_symbol, interval=interval, period=period, progress=False)
        
        if df.empty:
            return f"{clean_symbol} için teknik veri bulunamadı."

        # MultiIndex kontrolü ve düzeltme (yfinance bazen katmanlı başlık döner)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Teknik Göstergeler (pandas_ta kullanarak)
        # RSI
        df.ta.rsi(append=True)
        # MACD
        df.ta.macd(append=True)
        # Bollinger Bands
        df.ta.bbands(append=True)
        # EMA
        df.ta.ema(length=20, append=True)
        df.ta.ema(length=50, append=True)

        # Son değerleri al
        last_row = df.iloc[-1]
        
        # Sütun isimlerini pandas_ta'nın oluşturduğu formata göre eşle
        # Not: pandas_ta genelde RSI_14, MACD_12_26_9 vb. isimler kullanır.
        rsi_col = [c for c in df.columns if 'RSI' in c][0]
        macd_col = [c for c in df.columns if 'MACD_' in c and 'MACDh' not in c and 'MACDs' not in c][0]
        macd_h_col = [c for c in df.columns if 'MACDh' in c][0]
        bb_upper = [c for c in df.columns if 'BBU' in c][0]
        bb_lower = [c for c in df.columns if 'BBL' in c][0]
        ema20_col = [c for c in df.columns if 'EMA_20' in c][0]
        ema50_col = [c for c in df.columns if 'EMA_50' in c][0]

        result = {
            "symbol": clean_symbol,
            "interval": interval,
            "price": round(float(last_row['Close']), 2),
            "RSI": round(float(last_row[rsi_col]), 2),
            "MACD": round(float(last_row[macd_col]), 2),
            "MACD_Hist": round(float(last_row[macd_h_col]), 2),
            "BB_Upper": round(float(last_row[bb_upper]), 2),
            "BB_Lower": round(float(last_row[bb_lower]), 2),
            "EMA20": round(float(last_row[ema20_col]), 2),
            "EMA50": round(float(last_row[ema50_col]), 2)
        }

        return result
    except Exception as e:
        return f"Teknik analiz sırasında hata: {str(e)}"
