# 📅 Daily Point — Synthic Project Log

---

## 🗓️ 14 Mayıs 2026

### 🚀 Günün Başarısı: İlk Otonom Trade Döngüsü!
Bugün sistem en karmaşık görevini başarıyla tamamladı. 
- **Sorgu:** "BTC 1h analiz yap, Nexus ile planla ve Vega ile başlat."
- **Sonuç:** 
  1. **ATLAS** teknik indikatörleri çekti (RSI/MACD).
  2. **KISHI** fiyat verilerini doğruladı.
  3. **GHOST** haberleri taradı.
  4. **NEXUS** risk parametrelerini (%1 risk, SL/TP) hesapladı.
  5. **VEGA** işlemi Paper Trading üzerinden başarıyla başlattı. ✅

### Yeni Eklenen Ajanlar
- **ATLAS (Technical Analyst):** `pandas-ta` ile RSI, MACD, BB, EMA hesaplar.
- **NEXUS (Risk Manager):** Bakiye ve risk yönetimi yapar (Lot, SL, TP).
- **VEGA (Trade Executor):** `ccxt` ile Binance üzerinden (şimdilik Paper) işlem yapar.

### Teknik İyileştirmeler
- **Parsing Fix:** Tau'nun (Supervisor) yönlendirme mesajları artık daha esnek yakalanıyor. Sonsuz döngü engellendi.
- **Type Safety:** LLM'den gelen sayısal veriler için float zorlaması eklendi.
- **UI Upgrade:** Dashboard arayüzü 6 ajanlı yapıya uygun şekilde modernize edildi. Ajan mesajları için renkli baloncuklar eklendi.
- **Strict Trading Logic:** Atlas'ın teknik verileri doğrudan "BOĞA" veya "AYI" olarak yorumlaması sağlandı. Tau'ya bu yoruma göre yönlendirme yapması emredildi.
- **Clean Formatting:** Nexus ve Vega'nın JSON çıktıları yerine markdown destekli, emojili ve okunaklı raporlar üretmesi sağlandı.
- **Rate Limit Resilience:** Groq üzerinde günlük kota dolduğunda `llama-3.1-8b-instant` ve `llama3-70b-8192` modellerine geçiş yapılarak testler sürdürüldü. Limit sıfırlandığında tekrar `llama-3.3-70b-versatile` ana modele dönüldü.

---

## 🗓️ 12-13 Mayıs 2026

### ✅ Tamamlanan Fazlar

#### Faz 1 — Temel Altyapı
- `core/brain.py` → LLM yöneticisi (OpenRouter/Groq destekli, retry mekanizmalı)
- `memory/vector_db.py` → ChromaDB + HuggingFace local embeddings (ücretsiz)
- `core/nervous_system.py` → Tek ajan için temel LangGraph döngüsü

#### Faz 2 — Araçlar & ReAct Döngüsü
- `tools/finance.py` → yfinance (anlık fiyat) + Tavily (haber tarama)
- LangGraph üzerinde **Düşün → Araç Kullan → Gözlemle** döngüsü

#### Faz 3 — Watchtower (Otonom Gözcü)
- `core/observer.py` → Arka planda async çalışan piyasa gözcüsü
- `start_watchtower.py` → Ayrı process olarak başlatılıyor
- Volatilite %3'ü geçerse alarm üretiyor

#### Faz 5 — Multi-Agent Orchestration
- `core/multi_agent_system.py` → LangGraph Supervisor mimarisi
- **TAU** (Supervisor/Komuta) → Llama 3.3 70B
- **KISHI** (Analist) → Finansal veri çeker
- **GHOST** (Researcher) → Haber tarar
- Shared Blackboard → Ajanlar birbirinin verilerini görebilir
- Loop koruması → `visited` listesi + `steps` sayacı (max 6)

#### Faz 6 — Web UI Dashboard
- `app.py` → FastAPI sunucusu
- `templates/index.html` → Dark theme, TailwindCSS, mobil uyumlu
- Chat arayüzü + ajan durum paneli

### 🔧 Çözülen Kritik Buglar

| Bug | Çözüm |
|-----|-------|
| Sonsuz döngü (Tau→Kishi→Tau...) | `visited` listesi + `steps` sayacı |
| `$BTC-USD` ticker hatası | Otomatik ticker sanitization |
| OpenRouter 402 (yetersiz kredi) | `max_tokens=1000` limiti |
| OpenRouter 404 (model yok) | Doğrulanmış model ID kullanımı |
| OpenRouter 429 (rate limit) | **Groq'a taşıma** + exponential backoff retry |
| FastAPI async/sync çakışması | `async def` → `def` endpoint |
| Starlette TemplateResponse syntax | `request=request, name=...` formatı |

### 🔑 API Yapılandırması
```env
GROQ_API_KEY=gsk_...          # TAU, KISHI, GHOST için (Llama 3.3 70B)
OPENROUTER_API_KEY=sk-or-v1-... # Yedek
SUPERVISOR_API_KEY=sk-or-v1-...
ANALYST_API_KEY=sk-or-v1-...
RESEARCHER_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-dev-...    # Haber tarama
CHROMA_DB_PATH=./data/chroma   # Vektör DB yolu
```

### 🏗️ Mimari Özeti
```
Kullanıcı → TAU (Supervisor)
               ├─→ KISHI (Analist) → yfinance → Fiyat/Hacim
               ├─→ GHOST (Researcher) → Tavily → Haberler
               └─→ ChromaDB → Geçmiş + Kullanıcı Profili
                                (Zaman damgalı snapshot)
```

### 📁 Proje Yapısı
```
agents/
├── app.py                    # FastAPI Web UI sunucusu
├── main.py                   # Terminal arayüzü
├── test_run.py               # Tek seferlik test scripti
├── seed_memory.py            # ChromaDB başlangıç verisi
├── start_watchtower.py       # Arka plan gözcüsü
├── requirements.txt          # Bağımlılıklar
├── .env                      # API anahtarları
├── core/
│   ├── brain.py              # LLM yöneticisi (Groq/OpenRouter)
│   ├── multi_agent_system.py # TAU/KISHI/GHOST orchestration
│   ├── nervous_system.py     # Tekli ajan (eski sistem)
│   └── observer.py           # Watchtower otonom gözcü
├── memory/
│   └── vector_db.py          # ChromaDB + HuggingFace embeddings
├── tools/
│   └── finance.py            # yfinance + Tavily araçları
└── templates/
    └── index.html            # Synthic Dashboard UI
```

### 🚀 GitHub
- Repo: `github.com/SafiCeylan/agents`
- İlk commit: `feat: initial commit — Synthic multi-agent financial AI system`
- README.md: Mimari diyagram, kurulum rehberi, örnek sorgular

---

## 📌 Sonraki Adımlar (Backlog)

- [ ] **Termux deploy** — Android telefona sistemi kurma
- [ ] **Telegram bildirimleri** — Watchtower alarmlarını cebe iletme
- [ ] **Yeni ajan ekleme** — Modüler yapı hazır, sadece tanıtmak yeterli
- [ ] **Seed memory güncelleme** — Kullanıcı profili kişiselleştirme
- [ ] **HF_TOKEN** ekleme — HuggingFace rate limit uyarısını giderme

---

---

## 🗓️ 15 Mayıs 2026

### 🚀 Günün Başarısı: Profesyonel Risk ve İşlem Katmanı!
Bugün Nexus ve Vega ajanları, basit simülasyondan profesyonel trading standartlarına yükseltildi.

- **NEXUS (Risk Manager):** Artık **ATR (Average True Range)** bazlı dinamik Stop Loss hesaplayabiliyor. Piyasa oynaklığına göre riskini otomatik ayarlıyor.
- **VEGA (Trade Executor):** İşlem öncesi bakiye kontrolü (`get_balance`) ve daha sıkı veri doğrulaması eklendi.
- **ATLAS (Technical Analyst):** Diğer ajanların kullanımı için teknik verilere ATR indikatörü eklendi.
- **Shared Blackboard:** Ajanlar arası veri paylaşımı (ATR, bakiye vb.) optimize edildi.

### Teknik Detaylar
- `tools/technical_analysis.py` → ATR hesaplaması eklendi.
- `tools/risk_manager.py` → `calculate_risk_parameters` artık `atr` parametresini destekliyor.
- `tools/trade_executor.py` → `get_balance` aracı eklendi, simülasyon çıktıları güzelleştirildi.
- `core/multi_agent_system.py` → Ajanlar arası ATR aktarımı sağlandı.

---

*Son güncelleme: 15 Mayıs 2026 — 10:21*
