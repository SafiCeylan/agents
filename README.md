# SYNTHIC AI | The Agency Dashboard 🌐

SYNTHIC AI, tamamen otonom çalışan ve farklı uzmanlık alanlarına sahip yapay zeka ajanlarından oluşan gelişmiş bir **Çoklu Ajan Sistemi'dir (Multi-Agent System)**. LangGraph, FastAPI ve React kullanılarak inşa edilmiştir.

Bu sistemde tek bir yapay zeka yerine, her biri kendi alanında uzmanlaşmış yapay zekalardan oluşan bir takım (squad) bulunur. Ajanlar kendi aralarında bilgi paylaşır, ortak bir pano (blackboard) üzerinden veri aktarır ve "TAU" adındaki merkez komuta ajanı tarafından yönetilirler.

![Synthic UI](https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/static/img/langchain_logo.png) *(UI Screenshot eklenebilir)*

## 🚀 Öne Çıkan Özellikler

*   **🧠 LangGraph Ortak Akıl Mimarisi:** Tüm ajanlar tek bir StateGraph (Durum Grafiği) üzerinde birbirleriyle konuşur ve verileri ortak panoya yazarlar.
*   **🎯 7 Farklı Uzman Ajan:** 
    *   **TAU (Supervisor):** Sistem Yöneticisi, Orkestratör.
    *   **KISHI (Analyst):** Finansal Piyasa Analisti (Hisse/Kripto fiyat ve hacim verileri).
    *   **GHOST (Researcher):** Web Kazıma (Scraping) ve Haber Tarama uzmanı (Cloudflare bypass özellikli).
    *   **ATLAS (Technical):** Teknik Analiz, RSI/MACD hesaplamaları.
    *   **NEXUS (Risk):** Risk Yönetimi, Lot ve SL/TP hesaplayıcısı.
    *   **VEGA (Trader):** Otonom işlem komite başkanı. Riskleri değerlendirip kendi inisiyatifiyle işlem açar/reddeder.
    *   **CYPHER (OS Agent):** Bilgisayarda lokal işlemler yapan (terminal, email, script) Sistem Operatörü.
*   **🛡️ İleri Seviye Güvenlik (Phase 7):**
    *   **Beyaz Liste (Whitelist):** Cypher'ın terminalde sadece onaylı komutları çalıştırmasına izin verilir.
    *   **Sandbox İzolasyonu:** İşletim sistemi eylemleri yalnızca izole bir klasör (`sandbox/`) içerisinde yürütülür.
    *   **İnsan Onayı (HITL):** Cypher terminalde bir eylem yapmak istediğinde doğrudan arayüze "Onay İsteği" gönderir. Kullanıcı "ONAYLA" butonuna basmadan işlem gerçekleşmez.
*   **💾 ChromaDB Hafıza Desteği:** Kullanıcı tercihlerini ve geçmiş işlemleri RAG (Retrieval-Augmented Generation) altyapısı ile kalıcı hafızaya yazar. Gece döngülerinde bu verilerden evrim (profilleme) çıkarır.
*   **🌌 Sinematik Stardust Arayüz (React):** Ajanların yörüngede döndüğü, görevlerin ve sistem yükünün (CPU/RAM) gerçek zamanlı olarak monitör edildiği, yüksek estetiğe sahip fütüristik kontrol paneli.

## 🛠️ Kurulum

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/SafiCeylan/agents.git
    cd agents
    ```

2.  **Gerekli Kütüphaneleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```
    *Eğer requirements.txt yoksa:*
    ```bash
    pip install fastapi uvicorn langchain langgraph langchain-groq yfinance beautifulsoup4 cloudscraper chromadb
    ```

3.  **Çevre Değişkenlerini (Environment Variables) Ayarlayın:**
    Proje ana dizininde `.env` adında bir dosya oluşturun ve API anahtarlarınızı ekleyin:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    TAVILY_API_KEY=your_tavily_api_key_here
    ```

4.  **Uygulamayı Başlatın:**
    ```bash
    python app.py
    ```

5.  **Arayüze Erişin:**
    Tarayıcınızdan `http://localhost:8000` adresine giderek Stardust Interface'i kullanmaya başlayın.

## 🏗️ Sistem Mimarisi

*   **Backend:** `FastAPI` (Sunucu & API), `LangGraph` (Ajan Orkestrasyonu), `Chroma` (Vektör Veritabanı).
*   **Frontend:** `React 18` (Standalone/CDN), HTML5 Canvas (Holografik render ve yörünge animasyonları için).
*   **Yapay Zeka Modeli:** Varsayılan olarak Groq üzerinde çalışan `llama-3.3-70b-versatile` kullanılmaktadır.

### Gelecek Planları (Phase 8+)
- Web kazıma sisteminin Hiyerarşik Ajan ağlarına (Hierarchical LangGraph / CrewAI) dönüştürülmesi.
- Otonom Kod İnceleme (Review) ve Takvim ajanı eklenmesi.

## Lisans
Bu proje eğitim ve kişisel kullanım amacıyla geliştirilmiştir. Otonom finansal kararlar (VEGA) simülasyon amaçlıdır, gerçek bir broker API'sine bağlanmadan önce tüm güvenlik (Kill-Switch) mekanizmalarının aktif olduğundan emin olun.
