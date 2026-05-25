import requests
import cloudscraper
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def scrape_website(url: str) -> str:
    """
    Belirtilen web sitesinin (URL) ana metin içeriğini kazır (scrape eder).
    Ghost (Araştırmacı) ajanı tarafından haber veya makale detaylarını okumak için kullanılır.
    Girdi olarak tam bir URL (örn: https://example.com) almalıdır.
    """
    if not url.startswith("http"):
        url = "https://" + url

    try:
        # Cloudflare gibi korumaları aşmak için cloudscraper kullanıyoruz
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
        response = scraper.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Gereksiz etiketleri (script, style) temizle
        for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            script_or_style.decompose()

        # Ana metni al
        text = soup.get_text(separator=' ', strip=True)
        
        # Çok uzun metinleri kısalt (LLM token sınırını aşmamak için)
        if len(text) > 8000:
            text = text[:8000] + "\n... [İÇERİK KISALTILDI]"

        return f"--- {url} İÇERİĞİ ---\n{text}"

    except requests.exceptions.RequestException as e:
        return f"Web sitesi kazınırken hata oluştu ({url}): {str(e)}"
    except Exception as e:
        return f"Beklenmeyen bir hata oluştu: {str(e)}"
