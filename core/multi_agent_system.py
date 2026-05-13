from typing import Annotated, TypedDict, List, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from core.brain import Brain
from memory.vector_db import LongTermMemory
from tools.finance import get_market_analysis, search_finance_news

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
        # TAU — Groq / Llama 3.3 70B (limitsiz ücretsiz)
        self.supervisor_brain_obj = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.supervisor_brain = self.supervisor_brain_obj.get_llm()

        # KISHI — Groq / Llama 3.3 70B (70B daha iyi araç çağrısı yapar)
        self.analyst_brain = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        ).get_llm()

        # GHOST — Groq / Llama 3.3 70B
        self.researcher_brain = Brain(
            model_name="llama-3.3-70b-versatile",
            backend="groq",
            api_key=os.getenv("GROQ_API_KEY")
        ).get_llm()
        
        # İşçilerin kullanacağı araçlar
        self.analyst_tools = [get_market_analysis]
        self.researcher_tools = [search_finance_news]
        
        self.workflow = StateGraph(AgentState)
        self._setup_graph()

    def _setup_graph(self):
        # Düğümleri (Ajanları) ekle
        self.workflow.add_node("retrieve_memory", self.retrieve_memory_node)
        self.workflow.add_node("supervisor", self.supervisor_node)
        self.workflow.add_node("analyst", self.analyst_node)
        self.workflow.add_node("researcher", self.researcher_node)

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
                "FINISH": END
            }
        )
        
        # İşçiler işini bitirince her zaman Şef'e döner
        self.workflow.add_edge("analyst", "supervisor")
        self.workflow.add_edge("researcher", "supervisor")

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
        if history_texts:
            context += "\n\n--- TAU'NUN GEÇMİŞ HAFIZASI (Karşılaştırma için) ---\n" + "\n---\n".join(history_texts)
        return {"context": context, "shared_blackboard": {}}

    def supervisor_node(self, state: AgentState):
        """Tau: Ortak panoya bakar, eksik varsa ajana atar, yoksa yanıtlar."""
        blackboard_info = str(state.get("shared_blackboard", {}))
        steps = state.get("steps", 0) + 1
        visited = state.get("visited", [])

        # Döngü koruması: max 6 adımda zorla bitir
        if steps > 6:
            print(f"[Tau] Max adım ({steps}) aşıldı, zorla bitiriliyor.")
            fallback = f"Veri toplayabildiklerimle bir özet: {blackboard_info if blackboard_info != '{{}}' else 'Veri edinilemedi.'}"
            return {"next_node": "FINISH", "steps": steps, "messages": [AIMessage(content=fallback, name="Supervisor")]}

        system_prompt = (
            "Sen Synthic'in Komuta Ajanı TAU'sun. "
            f"Kullanıcı Profili:\n{state.get('context', 'Bilinmiyor')}\n\n"
            f"Mevcut Pano Verileri (Kishi ve Ghost'un getirdiği bilgiler):\n{blackboard_info}\n\n"
            f"Ziyaret Edilen Ajanlar: {visited}\n"
            "Görevin, kullanıcıya nihai bir yanıt vermek veya veri eksikse doğru ajana yönlendirmektir.\n"
            "Seçeneklerin:\n"
            "1. 'analyst': Finansal fiyat veya borsa verisi eksikse Kishi'ye yönlendir (zaten ziyaret edilmediyse).\n"
            "2. 'researcher': Haber, dedikodu veya güncel olay eksikse Ghost'a yönlendir (zaten ziyaret edilmediyse).\n"
            "3. 'FINISH': Tüm gerekli ajanlar çalıştıysa veya elimdeki veriler yeterliyse FINAL yanıt ver.\n\n"
            "YANIT FORMATI: Yönlendireceksen sadece 'ROUTE: <seçenek>' yaz. "
            "Eğer yanıt vereceksen 'FINAL: <kullanıcıya cevabın>' şeklinde yaz."
        )

        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        # 429 rate limit durumunda otomatik yeniden dene
        response = self.supervisor_brain_obj.invoke_with_retry(messages).content

        if response.startswith("ROUTE: analyst") and "analyst" not in visited:
            print("Tau -> Kishi'ye Yönlendiriyor...")
            return {"next_node": "analyst", "steps": steps, "visited": visited + ["analyst"]}
        elif response.startswith("ROUTE: researcher") and "researcher" not in visited:
            print("Tau -> Ghost'a Yönlendiriyor...")
            return {"next_node": "researcher", "steps": steps, "visited": visited + ["researcher"]}
        else:
            final_ans = response.replace("FINAL:", "").replace("ROUTE: FINISH", "").strip()
            return {"next_node": "FINISH", "steps": steps, "messages": [AIMessage(content=final_ans, name="Supervisor")]}

    def analyst_node(self, state: AgentState):
        """Analist Ajan: Fiyat verisi çeker ve panoya (blackboard) özet bırakır."""
        llm_with_tools = self.analyst_brain.bind_tools(self.analyst_tools)
        # Analistin aklında sadece finansal veriler var
        sys_msg = SystemMessage(content="Sen Kishi'sin, Synthic'in finansal analistsin. Kullanıcının talebinden sembolleri çıkar ve araç kullanarak finansal analizi yap.")
        response = llm_with_tools.invoke([sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Kishi: Gerekli finansal veri araçla bulunamadı."
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_result = get_market_analysis.invoke(tool_call["args"])
                # 'symbol' veya 'ticker' olarak gelebilir, ikisini de dene
                symbol = tool_call["args"].get("symbol") or tool_call["args"].get("ticker", "UNKNOWN")
                ts = self.memory.save_market_snapshot(
                    symbol=symbol,
                    data=str(tool_result),
                    source="Kishi"
                )
                blackboard["Kishi_Ozeti"] = f"{symbol} sonucu [{ts}]: {tool_result}"
            msg_content = "Kishi: Fiyat analizi tamamlandı ve Ortak Panoya + Hafizaya eklendi."
        elif response.content:
            msg_content = f"Kishi: {response.content}"
                
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Kishi")]}

    def researcher_node(self, state: AgentState):
        """Hafiye Ajan: Haber arar ve panoya özet bırakır."""
        llm_with_tools = self.researcher_brain.bind_tools(self.researcher_tools)
        sys_msg = SystemMessage(content="Sen Ghost'sun, Synthic'in haber ajanısın. Kullanıcının talebini incele, aracı kullanarak internetten haberleri tara.")
        response = llm_with_tools.invoke([sys_msg] + state["messages"])
        
        blackboard = state.get("shared_blackboard", {})
        msg_content = "Ghost: Haber araması yapılamadı."
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_result = search_finance_news.invoke(tool_call["args"])
                query_term = tool_call["args"].get("query", "haber")
                # Tau emriyle: Haberleri de zaman damgalı kaydet
                self.memory.save_market_snapshot(
                    symbol=query_term,
                    data=str(tool_result),
                    source="Ghost"
                )
                blackboard["Ghost_Ozeti"] = f"{query_term} haberleri: {tool_result}"
            msg_content = "Ghost: İlgili haberler tarandı, Ortak Panoya + Hafızaya eklendi."
        elif response.content:
            msg_content = f"Ghost: {response.content}"
                
        return {"shared_blackboard": blackboard, "messages": [AIMessage(content=msg_content, name="Ghost")]}

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
        memory_entry = f"Soru: {user_input}\nTau'nun Kararı: {final_response}"
        if blackboard:
            memory_entry += f"\nKishi/Ghost Panosası: {blackboard}"
        self.memory.add_memory(memory_entry)
        
        return final_response
