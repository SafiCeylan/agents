<div align="center">

# 🤖 Synthic — Multi-Agent Financial AI

**A modular, memory-persistent multi-agent system for real-time financial intelligence.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-purple?logo=langchain)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/FastAPI-Dashboard-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-orange)](https://groq.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

**Synthic** is a production-ready multi-agent AI framework built on top of [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://langchain.com). It orchestrates a team of specialized AI agents — each with distinct roles — to collaboratively answer complex financial questions using real-time market data, news, and long-term vector memory.

> Think of it as a "hedge fund command room" where a supervisor agent routes tasks to a financial analyst and a news researcher, then synthesizes everything into a coherent answer.

---

## 🧠 Agent Architecture

```
User Query
    │
    ▼
┌───────────────────────────────────────────┐
│         retrieve_memory (ChromaDB)        │  ← Fetches past context
└────────────────────┬──────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────┐
│           TAU — Supervisor Agent          │  ← Orchestrates the team
│          (Llama 3.3 70B via Groq)         │
└──────────┬────────────────────┬───────────┘
           │                    │
     ROUTE: analyst       ROUTE: researcher
           │                    │
           ▼                    ▼
┌──────────────────┐  ┌──────────────────────┐
│ KISHI — Analyst  │  │  GHOST — Researcher   │
│  (yfinance data) │  │  (Tavily news search) │
└────────┬─────────┘  └──────────┬────────────┘
         │                       │
         └────────┬──────────────┘
                  │  (Shared Blackboard)
                  ▼
         TAU synthesizes → Final Answer
                  │
                  ▼
         ChromaDB Memory Save
```

### Agents

| Agent | Role | Model | Tool |
|-------|------|-------|------|
| **TAU** | Supervisor / Orchestrator | Llama 3.3 70B (Groq) | — |
| **KISHI** | Financial Analyst | Llama 3.3 70B (Groq) | `get_market_analysis` (yfinance) |
| **GHOST** | News Researcher | Llama 3.3 70B (Groq) | `search_finance_news` (Tavily) |

---

## ✨ Features

- 🔀 **LangGraph State Machine** — Dynamic multi-agent routing with loop protection (max 6 steps)
- 🧩 **Shared Blackboard** — Agents communicate via a shared state dictionary
- 🧠 **Long-Term Memory** — ChromaDB vector store for persistent user profiles and market snapshots
- 📈 **Real-Time Market Data** — Live price, daily change %, and bull/bear status via yfinance
- 📰 **Live News Search** — Tavily-powered financial news retrieval
- 🌐 **FastAPI Dashboard** — Web interface at `http://localhost:8000`
- 🔄 **Auto Rate-Limit Retry** — Exponential backoff (15s/30s/45s) for Groq 429 errors
- 🔌 **Dual Backend** — Primary: Groq (free), Fallback: OpenRouter

---

## 🗂️ Project Structure

```
agents/
├── app.py                   # FastAPI web server & dashboard endpoint
├── main.py                  # CLI entry point
├── seed_memory.py           # Seeds ChromaDB with initial user profile data
├── start_watchtower.py      # Background monitoring / watchdog process
├── requirements.txt
│
├── core/
│   ├── brain.py             # LLM abstraction (Groq/OpenRouter + retry logic)
│   ├── multi_agent_system.py # Main multi-agent orchestrator (TAU/KISHI/GHOST)
│   ├── nervous_system.py    # Single-agent ReAct loop (alternative mode)
│   └── observer.py          # System monitoring utilities
│
├── tools/
│   └── finance.py           # LangChain tools: get_market_analysis, search_finance_news
│
├── memory/
│   └── vector_db.py         # ChromaDB long-term memory (add, search, snapshot)
│
├── templates/
│   └── index.html           # Dashboard UI template
│
└── data/                    # Persistent ChromaDB storage
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/SafiCeylan/agents.git
cd agents
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: OpenRouter fallback
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

> 🆓 **Groq** offers a generous free tier with Llama 3.3 70B. Sign up at [console.groq.com](https://console.groq.com).
> 
> 🔍 **Tavily** provides free API access for search. Get your key at [tavily.com](https://tavily.com).

### 5. Seed Long-Term Memory (Optional but Recommended)

```bash
python seed_memory.py
```

This populates ChromaDB with an initial user risk profile so agents have context from the first query.

### 6. Launch the Dashboard

```bash
python app.py
```

Navigate to **http://localhost:8000** in your browser and start chatting with the agent team.

### 7. Or Run via CLI

```bash
python main.py
```

---

## 💬 Example Queries

```
"BTC fiyatı ne kadar?"
"Ethereum hakkında son haberler neler?"
"THYAO.IS için hem fiyat hem de haber analizi yap"
"Apple hissesinin durumu nasıl, al-sat önerir misin?"
```

---

## ⚙️ How It Works

1. **Memory Retrieval** — The system first queries ChromaDB for relevant past context (user risk profile, past market snapshots).
2. **Supervisor Decision (TAU)** — TAU reads the query + context and decides: route to analyst, route to researcher, or answer directly.
3. **Specialist Execution** — KISHI fetches live market data; GHOST searches latest news. Results go to the shared blackboard.
4. **Synthesis** — TAU reads the blackboard and generates the final answer, incorporating all gathered data.
5. **Memory Persistence** — The Q&A pair and blackboard data are saved back to ChromaDB for future retrieval.

---

## 🛡️ Loop Protection

The multi-agent graph has built-in safeguards against infinite loops:
- **Max Steps**: Hard limit of 6 steps per query.
- **Visited Tracking**: Each agent can only be called once per conversation turn.
- **Fallback Response**: If the limit is exceeded, TAU summarizes available blackboard data gracefully.

---

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key (primary LLM backend) | Required |
| `TAVILY_API_KEY` | Tavily API key (news search) | Required |
| `OPENROUTER_API_KEY` | OpenRouter fallback key | Optional |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Multi-agent state machine |
| `langchain` | LLM orchestration |
| `langchain-openai` | OpenAI-compatible LLM client (Groq/OpenRouter) |
| `chromadb` | Vector memory store |
| `yfinance` | Real-time stock/crypto data |
| `tavily-python` | AI-powered news search |
| `fastapi` + `uvicorn` | Web API & dashboard |
| `sentence-transformers` | Text embeddings for ChromaDB |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ using [LangGraph](https://github.com/langchain-ai/langgraph) · [Groq](https://groq.com) · [FastAPI](https://fastapi.tiangolo.com)

</div>
