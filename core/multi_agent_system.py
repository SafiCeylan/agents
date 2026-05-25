from typing import Annotated, TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from core.brain import Brain
from memory.vector_db import LongTermMemory
from tools.finance import get_market_analysis, search_finance_news
from tools.technical_analysis import get_technical_indicators
from tools.risk_manager import calculate_risk_parameters
from tools.trade_executor import execute_trade, get_balance
from tools.os_agent import execute_system_command, open_website, send_email_draft
from tools.web_scraper import scrape_website
from datetime import datetime

# Ortak Akıl (Shared State)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str
    shared_blackboard: dict
    next_node: str
    steps: int  # Döngü koruması: kaç adım atıldı
    visited: List[str]  # Hangi ajanlar çalıştı (aynı ajana 2 kez gitmeyi engeller)

class MultiAgentSystem:
    def __init__(self, memory: LongTermMemory):
        self.memory = memory
        
        # Ajan beyinlerini başlat (Her biri için farklı API veya model verilebilir)
        import os
        # TAU
        self.supervisor_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.supervisor_brain = self.supervisor_brain_obj.get_llm()

        # KISHI
        self.analyst_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.analyst_brain = self.analyst_brain_obj.get_llm()

        # GHOST
        self.researcher_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.researcher_brain = self.researcher_brain_obj.get_llm()

        # ATLAS
        self.atlas_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.atlas_brain = self.atlas_brain_obj.get_llm()

        # NEXUS
        self.nexus_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.nexus_brain = self.nexus_brain_obj.get_llm()

        # VEGA — Trade Executor
        self.vega_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.vega_brain = self.vega_brain_obj.get_llm()

        # CYPHER — OS & World Control
        self.cypher_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.cypher_brain = self.cypher_brain_obj.get_llm()
        
        # İşçilerin kullanacağı araçlar
        self.analyst_tools = [get_market_analysis]
        self.researcher_tools = [search_finance_news, scrape_website]
        self.atlas_tools = [get_technical_indicators]
        self.nexus_tools = [calculate_risk_parameters]
        self.vega_tools = [execute_trade, get_balance]
        self.cypher_tools = [execute_system_command, open_website, send_email_draft]
        
        self.workflow = StateGraph(AgentState)
        self._setup_graph()

    def _setup_graph(self):
        # Düğümleri (Ajanları) ekle
        self.workflow.add_node("retrieve_memory", self.retrieve_memory_node)
        self.workflow.add_node("supervisor", self.supervisor_node)
        self.workflow.add_node("analyst", self.analyst_node)
        self.workflow.add_node("researcher", self.researcher_node)
        self.workflow.add_node("atlas", self.atlas_node)
        self.workflow.add_node("nexus", self.nexus_node)
        self.workflow.add_node("vega", self.vega_node)
        self.workflow.add_node("cypher", self.cypher_node)

        # Akışı tanımla
        self.workflow.set_entry_point("retrieve_memory")
        self.workflow.add_edge("retrieve_memory", "supervisor")
        
        # Supervisor'ın kararına göre yönlendirme
        self.workflow.add_conditional_edges(
            "supervisor",
            lambda state: state.get("next_node", "FINISH"),
            {
                "analyst": "analyst",
                "researcher": "researcher",
                "atlas": "atlas",
                "nexus": "nexus",
                "vega": "vega",
                "cypher": "cypher",
                "FINISH": END
            }
        )
        
        # İşçiler işini bitirince her zaman Şef'e döner
        self.workflow.add_edge("analyst", "supervisor")
        self.workflow.add_edge("researcher", "supervisor")
        self.workflow.add_edge("atlas", "supervisor")
        self.workflow.add_edge("nexus", "supervisor")
        self.workflow.add_edge("vega", "supervisor")
        self.workflow.add_edge("cypher", "supervisor")

        self.app = self.workflow.compile()

    def retrieve_memory_node(self, state: AgentState):
        """Kullanıcı bilgisini ve piyasa geçmişini ChromaDB'den çeker."""
        last_message = state["messages"][0].content
        # Genel kullanıcı profili
        relevant_docs = self.memory.search_memory(f"Kullanıcı profili risk tercihi: {last_message}")
        context = "\n".join([doc.page_content for doc in relevant_docs])
        # Geçmiş piyasa anlık görüntüleri (varsa)
        history_docs = self.memory.search_memory(f"piyasa raporu analizi: {last_message}", k=3)
        history_texts = [d.page_content for d in history_docs if "raporu" in d.page_content]
        # Zaman ve Psikoloji verisini entegre et
        current_time = datetime.now().strftime("%H:%M")
        user_profile = self.memory.get_user_profile()
        context += f"\n\n--- ZAMAN VE PSİKOLOJİ ---\nŞu anki saat: {current_time}\n"
        context += f"Kullanıcı Profil ve Alışkanlıkları:\n{user_profile}\n"
        return {"context": context, "shared_blackboard": {}}

    def supervisor_node(self, state: AgentState):
        """Tau: Ortak panoya ve psikolojik profile bakar, karar verir."""
        blackboard_info = str(state.get("shared_blackboard", {}))
        steps = state.get("steps", 0) + 1
        visited = state.get("visited", [])

        # Döngü koruması: max 6 adımda zorla bitir
        if steps > 6:
            print(f"[Tau] Max adım ({steps}) aşıldı, zorla bitiriliyor.")
            fallback = f"Veri toplayabildiklerimle bir özet: {blackboard_info if blackboard_info != '{{}}' else 'İşlem tamamlanamadı.'}"
            return {"next_node": "FINISH", "steps": steps, "messages": [AIMessage(content=fallback, name="Supervisor")]}

        system_prompt = (
            "Sen Synthic'in Komuta Ajanı (Dijital Partner) TAU'sun.\n"
            f"Senin Görevin: Sadece veri sağlamak değil, kullanıcıyı anlayan otonom bir yapı yönetmek.\n\n"
            f"--- BİLGİ MERKEZİ ---\n"
            f"{state.get('context', 'Bilinmiyor')}\n\n"
            f"Mevcut Pano Verileri:\n{blackboard_info}\n\n"
            f"Ziyaret Edilen Ajanlar: {visited}\n"
            "----------------------\n\n"
            "Seçeneklerin (SADECE BİRİNİ SEÇ):\n"
            "1. 'analyst': Fiyat/hacim verisi için Kishi'ye.\n"
            "2. 'researcher': Haber arama ve Belirli bir WEBSİTESİNİ OKUMA/KAZIMA (Scraping) için Ghost'a.\n"
            "3. 'atlas': Teknik analiz (RSI/MACD) için Atlas'a.\n"
            "4. 'nexus': Risk hesabı için Nexus'a.\n"
            "5. 'vega': İşlem/Trade eylemi için Vega'ya.\n"
            "6. 'cypher': İşletim sistemi eylemi (mail atma, script çalıştırma, site açma vb.) için Cypher'a.\n"
            "7. 'FINISH': İşlem bittiyse kapat.\n\n"
            "🛑 ROUTING KURALLARI:\n"
            "SADECE 'ROUTE: <ajan_adı>' formatını kullan.\n"
            "- Örnek: 'ROUTE: cypher' (eğer kullanıcı site açmanı/mail atmanı isterse)\n"
            "- Eğer saat çok geçse ve kullanıcı riskli işlem istiyorsa, 'FINAL: Şu an çok geç, bu saatlerde trade yapmak genelde hata oranını artırıyor. Emin misin?' şeklinde uyarıp FINISH'e yönlendirebilirsin.\n"
        )

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        # 429 rate limit durumunda otomatik yeniden dene
        response = self.supervisor_brain_obj.invoke_with_retry(messages).content
        
        # Daha esnek yönlendirme yakalama (Fallback ile)
        response_lower = response.lower()
        
        target_node = None
        if ("route: analyst" in response_lower or "analyst" in response_lower) and "analyst" not in visited:
            target_node = "analyst"
        elif ("route: researcher" in response_lower or "route: ghost" in response_lower or "ghost" in response_lower) and "researcher" not in visited:
            target_node = "researcher"
        elif ("route: atlas" in response_lower or "atlas" in response_lower) and "atlas" not in visited:
            target_node = "atlas"
        elif ("route: nexus" in response_lower or "nexus" in response_lower) and "nexus" not in visited:
            target_node = "nexus"
        elif ("route: vega" in response_lower or "vega" in response_lower) and "vega" not in visited:
            target_node = "vega"
        elif ("route: cypher" in response_lower or "cypher" in response_lower) and "cypher" not in visited:
            target_node = "cypher"

        if target_node:
            try:
                print(f"Tau -> {target_node.capitalize()}'e Yönlendiriyor... (Yanıt: {response[:30]}...)")
            except UnicodeEncodeError:
                clean_resp = response[:30].encode('ascii', 'ignore').decode('ascii')
                print(f"Tau -> {target_node.capitalize()}'e Yonlendiriyor... (Yanit: {clean_resp}...)")
            return {"next_node": target_node, "steps": steps, "visited": visited + [target_node]}
        else:
            final_ans = response.replace("FINAL:", "").replace("ROUTE: FINISH", "").strip()
            for r in ["ROUTE: analyst", "ROUTE: researcher", "ROUTE: atlas", "ROUTE: nexus", "ROUTE: vega", "ROUTE: cypher"]:
                final_ans = final_ans.replace(r, "").strip()
            
            if not final_ans:
                final_ans = "Tau: İşlem döngüsü tamamlandı veya risk koşulları nedeniyle durduruldu."
                
            return {"next_node": "FINISH", "steps": steps, "messages": [AIMessage(content=final_ans, name="Supervisor")]}

    def analyst_node(self, state: AgentState):
        """Analist Ajan: Fiyat verisi çeker ve panoya (blackboard) özet bırakır."""
        llm_with_tools = self.analyst_brain.bind_tools(self.analyst_tools)
        # Analistin aklında sadece finansal veriler var
        sys_msg = SystemMessage(content="Sen Kishi'sin, Synthic'in finansal analistsin. Kullanıcının talebinden sembolleri çıkar ve araç kullanarak finansal analizi yap.")
        response = self.analyst_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Kishi: Veri çekme hatası oluştu."
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                tool_result = get_market_analysis.invoke(tool_call["args"])
                symbol = tool_call["args"].get("symbol") or tool_call["args"].get("ticker", "UNKNOWN")
                price = tool_result.get("current_price", "Bilinmiyor")
                self.memory.save_market_snapshot(symbol, str(tool_result), "Kishi")
                results.append(f"💰 **{symbol}** şu an **{price} USD** seviyesinde işlem görüyor.")
                blackboard["Kishi_Ozeti"] = f"{symbol} fiyat: {price}"
            msg_content = "### 📊 Fiyat Bilgisi\n" + "\n".join(results)
        elif response.content:
            msg_content = response.content
                
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Kishi")]}

    def researcher_node(self, state: AgentState):
        """Hafiye Ajan: Haber arar ve panoya özet bırakır."""
        llm_with_tools = self.researcher_brain.bind_tools(self.researcher_tools)
        sys_msg = SystemMessage(content="Sen Ghost'sun, Synthic'in haber ajanısın. Aracı kullanarak internetten haberleri tara.")
        response = self.researcher_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Ghost: Araştırma yapılamadı."
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                func_name = tool_call["name"]
                args = tool_call["args"]
                
                if func_name == "search_finance_news":
                    tool_result = search_finance_news.invoke(args)
                    query_term = args.get("query", "haber")
                    self.memory.save_market_snapshot(query_term, str(tool_result), "Ghost")
                    results.append(str(tool_result))
                    blackboard["Ghost_Ozeti"] = f"{query_term} haberleri: {tool_result}"
                elif func_name == "scrape_website":
                    tool_result = scrape_website.invoke(args)
                    url = args.get("url", "UNKNOWN_URL")
                    self.memory.save_market_snapshot(url, str(tool_result), "Ghost_Scraper")
                    results.append(f"📄 **{url}** adresinden veri çekildi:\n{tool_result[:500]}...") # Ekrana özet bas
                    blackboard["Ghost_Web_Scraping"] = f"{url} kazındı. İçerik özeti eklendi."

            msg_content = f"### 🕵️ Araştırma Sonuçları (GHOST)\n" + "\n\n".join(results)
        elif response.content:
            msg_content = response.content
                
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Ghost")]}

    def atlas_node(self, state: AgentState):
        """Atlas Ajanı: Teknik analiz göstergelerini hesaplar."""
        llm_with_tools = self.atlas_brain.bind_tools(self.atlas_tools)
        sys_msg = SystemMessage(content="Sen Atlas'sın, Synthic'in teknik analistisin. Teknik göstergeleri hesapla.")
        response = self.atlas_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Atlas: Teknik analiz yapılamadı."
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                tool_result = get_technical_indicators.invoke(tool_call["args"])
                symbol = tool_call["args"].get("symbol", "UNKNOWN")
                
                if isinstance(tool_result, str):
                    analysis_msg = f"Atlas: {symbol} için teknik analiz başarısız oldu. Hata: {tool_result}"
                    results.append(analysis_msg)
                    continue

                # YORUMLAMA VE KARAR KATMANI
                rsi = tool_result.get("RSI", 50)
                macd = tool_result.get("MACD", 0)
                verdict = "NÖTR"
                side = "none"
                
                if rsi > 60 and macd > 0: 
                    verdict = "🚀 **BOĞA (LONG)** - Yükseliş trendi güçlü."
                    side = "buy"
                elif rsi < 40 and macd < 0: 
                    verdict = "📉 **AYI (SHORT)** - Düşüş trendi hakim."
                    side = "sell"
                else:
                    verdict = "⚖️ **NÖTR** - Net bir sinyal yok, beklemedeyiz."
                
                analysis_msg = f"**{symbol} Analizi:**\n- RSI: `{rsi}`\n- MACD: `{macd}`\n- **KARAR:** {verdict}"
                blackboard["Atlas_Ozeti"] = analysis_msg
                blackboard["Trade_Side"] = side
                blackboard["ATR"] = tool_result.get("ATR")
                self.memory.save_market_snapshot(symbol, analysis_msg, "Atlas")
                results.append(analysis_msg)
            msg_content = "### 🧭 Teknik Yol Haritası\n" + "\n".join(results)
        
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Atlas")]}

    def nexus_node(self, state: AgentState):
        """Nexus Ajanı: Risk ve pozisyon büyüklüğü hesaplar."""
        llm_with_tools = self.nexus_brain.bind_tools(self.nexus_tools)
        sys_msg = SystemMessage(content=(
            "Sen Nexus'sun, Synthic'in risk yöneticisisin. Pano verilerine bakarak lot, SL ve TP seviyelerini hesapla. "
            "ÖNEMLİ: Sayısal değerleri mutlaka SAYI olarak gönder!"
        ))
        response = self.nexus_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Nexus: Risk hesabı yapılamadı."
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                args = tool_call["args"]
                if "balance" not in args: args["balance"] = 10000.0
                if "atr" not in args and "ATR" in blackboard:
                    args["atr"] = blackboard["ATR"]
                    
                tool_result = calculate_risk_parameters.invoke(args)
                
                if isinstance(tool_result, str):
                    analysis_msg = f"Nexus: Risk hesabı başarısız. Hata: {tool_result}"
                    results.append(analysis_msg)
                    continue

                blackboard["Nexus_Ozeti"] = f"Risk Planı: {tool_result}"
                
                # PRETTY FORMAT
                bal = tool_result.get("balance", 0)
                risk_usd = tool_result.get("risk_amount_usd", 0)
                ep = tool_result.get("entry_price", 0)
                sl = tool_result.get("stop_loss", 0)
                tp = tool_result.get("take_profit", 0)
                qty = tool_result.get("quantity", 0)
                rr = tool_result.get("risk_reward_ratio", "N/A")
                method = tool_result.get("method", "Percentage")
                
                pretty_msg = (
                    f"**🛡️ Risk Stratejisi:** `{method}`\n"
                    f"**💰 Bakiye:** `{bal} USD` | **🛡️ Riske Edilen:** `{risk_usd} USD`\n\n"
                    f"**🎯 Giriş:** `{ep}` | **🛑 SL:** `{sl}` | **✅ TP:** `{tp}`\n\n"
                    f"**📦 Lot:** `{qty}` | **⚖️ R/R:** `{rr}`"
                )
                results.append(pretty_msg)
            msg_content = "### 🛡️ Risk ve Pozisyon Yönetimi Planı\n" + "\n\n".join(results)
        
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Nexus")]}

    def cypher_node(self, state: AgentState):
        """Cypher Ajanı: Gerçek dünya eylemlerini (işletim sistemi, mail, web) yürütür."""
        llm_with_tools = self.cypher_brain.bind_tools(self.cypher_tools)
        sys_msg = SystemMessage(content="Sen Cypher'sın. Sistemin gerçek dünyadaki (OS, Tarayıcı, Email) operatörüsün. Gerekli araçları çağırarak eylemi gerçekleştir.")
        response = self.cypher_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Cypher: İşlem yapılamadı."
        
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                func_name = tool_call["name"]
                args = tool_call["args"]
                tool_result = "Araç bulunamadı."
                if func_name == "execute_system_command":
                    tool_result = execute_system_command.invoke(args)
                elif func_name == "open_website":
                    tool_result = open_website.invoke(args)
                elif func_name == "send_email_draft":
                    tool_result = send_email_draft.invoke(args)
                
                results.append(str(tool_result))
            msg_content = "### 💻 Sistem Operatörü (CYPHER)\n" + "\n".join(results)
        elif response.content:
            msg_content = response.content
            
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Cypher")]}

    def vega_node(self, state: AgentState):
        """Vega Ajanı: Otonom Komite Başkanı. Tüm veriyi inceler ve kendi inisiyatifiyle trade kararını alır/uygular."""
        llm_with_tools = self.vega_brain.bind_tools(self.vega_tools)
        blackboard = state.get("shared_blackboard", {})
        
        sys_msg = SystemMessage(content=(
            "Sen Vega'sın, Otonom Trader Ajanı. Artık sadece bir emir kulu değilsin.\n"
            f"Panodaki Veriler:\n{str(blackboard)}\n\n"
            "GÖREVİN:\n"
            "1. Teknik Analiz (Atlas), Haber Duyarlılığı (Ghost) ve Risk Planı (Nexus) verilerini bir insan trader gibi sentezle.\n"
            "2. Eğer risk yüksekse veya sinyaller çelişiyorsa İŞLEMİ REDDET.\n"
            "3. Eğer komite ortak bir başarı (BOĞA) sinyali veriyorsa aracı (execute_trade) çağırarak işlemi aç.\n"
            "Her halükarda analiz sonucunu kullanıcıya 'Neden' bu kararı aldığını açıklayarak bildir."
        ))
        response = self.vega_brain_obj.safe_invoke(llm_with_tools, [sys_msg] + state["messages"])
        
        msg_content = "Vega: Karar verilemedi."
        if response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                tool_result = execute_trade.invoke(tool_call["args"])
                if isinstance(tool_result, str):
                    results.append(f"Vega: Hata: {tool_result}")
                    continue
                
                blackboard["Vega_Ozeti"] = f"İşlem: {tool_result}"
                self.memory.add_memory(f"İşlem Kaydı: {tool_result}")
                
                stat = tool_result.get("status", "Bilinmiyor")
                msg = tool_result.get("message", "Açıklama yok")
                icon = "✅" if "SUCCESS" in stat else "❌"
                trade_info = f"{icon} **Durum:** {stat}\n📝 **Mesaj:** {msg}"
                results.append(trade_info)
            msg_content = "### 🚀 Otonom İşlem Kararı (VEGA)\n" + "\n\n".join(results)
        elif response.content:
            msg_content = "### 🛑 Otonom Trade Kararı (İptal)\n" + response.content
        
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Vega")]}

    def run(self, user_input: str):
        """Sistemi başlatır."""
        initial_state = {
            "messages": [HumanMessage(content=user_input)], 
            "context": "",
            "shared_blackboard": {},
            "next_node": "",
            "steps": 0,
            "visited": []
        }
        result = self.app.invoke(initial_state)
        
        final_response = result["messages"][-1].content
        
        # Tau: Soru-Cevap özetini ve pano verilerini genel hafızaya kaydet
        blackboard = result.get("shared_blackboard", {})
        final_response = result["messages"][-1].content
        memory_entry = f"Soru: {user_input}\nTau'nun Kararı: {final_response}"
        if blackboard:
            memory_entry += f"\nKishi/Ghost Panosası: {blackboard}"
        self.memory.add_memory(memory_entry)
        
        # Tüm mesaj listesini döndür (ilk mesaj kullanıcı olduğu için onu atla)
        return result["messages"][1:]

    def evolve(self):
        """
        Gece optimizasyon ve evrim döngüsü.
        Geçmiş işlemleri ve kullanıcı etkileşimlerini okuyup profili günceller.
        """
        try:
            # Son 10 işlemi çek
            history = self.memory.search_memory("İşlem Kaydı", k=10)
            if not history:
                return "Yeterli işlem verisi yok, evrim atlandı."
            
            history_text = "\n".join([doc.page_content for doc in history])
            
            # Supervisor'a evrim analizi yaptır
            sys_msg = SystemMessage(content=(
                "Sen TAU'sun. Evrim ve Öğrenme modundasın.\n"
                "Aşağıdaki geçmiş kayıtlarını analiz et. Kullanıcının psikolojisi, ajanların başarı oranı ve sistemin hataları hakkında 1-2 cümlelik kalıcı bir 'Profil İçgörüsü' çıkar.\n\n"
                f"Kayıtlar:\n{history_text}"
            ))
            
            response = self.supervisor_brain_obj.invoke_with_retry([sys_msg]).content
            
            # İçgörüyü kalıcı hafızaya kaydet
            self.memory.save_user_profile(f"Sistem Öğrenimi: {response}")
            
            return f"Evrim tamamlandı. Yeni içgörü kaydedildi:\n{response}"
        except Exception as e:
            return f"Evrim sırasında hata oluştu: {str(e)}"
