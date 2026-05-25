import { useState, useEffect, useRef } from "react";

const GF = "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&display=swap";

const AGENTS = [
  { id:"TAU",    name:"TAU",    role:"Supervisor",  status:"active",  color:"#7C6FE0", angle:270, tasks:2, load:45, desc:"Departman koordinasyonu aktif. Tüm ajanlar senkron."  },
  { id:"KISHI",  name:"KISHI",  role:"Analyst",     status:"active",  color:"#38BDF8", angle:330, tasks:3, load:72, desc:"BTC/USDT parite analizi devam ediyor. Dominans takipte." },
  { id:"GHOST",  name:"GHOST",  role:"Researcher",  status:"active",  color:"#A78BFA", angle:30,  tasks:1, load:38, desc:"Reuters ve Bloomberg taranıyor. 3 kritik haber bulundu."  },
  { id:"ATLAS",  name:"ATLAS",  role:"Technical",   status:"active",  color:"#34D399", angle:90,  tasks:4, load:88, desc:"RSI aşırı alım bölgesinde. MACD kesişimi bekleniyor."    },
  { id:"NEXUS",  name:"NEXUS",  role:"Risk Mgmt",   status:"idle",    color:"#F87171", angle:150, tasks:0, load:12, desc:"Portföy koruması pasif. Risk limitleri nominal seviyede." },
  { id:"VEGA",   name:"VEGA",   role:"Trader",      status:"active",  color:"#FBBF24", angle:210, tasks:2, load:60, desc:"ETH long pozisyon simülasyonu. Kâr hedefi: %4.2."         },
];

const INIT_TASKS = [
  { id:"TSK-041", agentId:"KISHI",  title:"BTC/USDT fiyat analizi",        priority:"high",     progress:72 },
  { id:"TSK-042", agentId:"GHOST",  title:"Fed açıklaması haber taraması", priority:"critical", progress:41 },
  { id:"TSK-043", agentId:"ATLAS",  title:"RSI + MACD sinyal kontrolü",    priority:"normal",   progress:88 },
  { id:"TSK-044", agentId:"VEGA",   title:"ETH long pozisyon simülasyonu", priority:"high",     progress:20 },
  { id:"TSK-045", agentId:"TAU",    title:"Günlük rapor derleme",          priority:"normal",   progress:55 },
  { id:"TSK-046", agentId:"ATLAS",  title:"Destek/direnç seviyeleri",      priority:"high",     progress:63 },
];

const INIT_CHAT = [
  { id:1, from:"TAU",   text:"Tüm sistemler aktif. Departman göreve hazır. Kishi ve Ghost da panoda bekliyor.", ts:"08:14" },
  { id:2, from:"user",  text:"bana tetherin analizini yapar mısın", ts:"08:15" },
  { id:3, from:"KISHI", text:"USDT/TRY parite: 38.42 ▲0.12%. Tether dominansı %8.3 — son 24s giriş 200M$. Detaylı rapor geliyor.", ts:"08:15" },
  { id:4, from:"GHOST", text:"Tether haber taraması tamamlandı. SEC incelemesi devam ediyor. 3 makale özeti hazır.", ts:"08:16" },
];

const MARKET = [
  { sym:"BTC",  base:67420 },
  { sym:"ETH",  base:3541  },
  { sym:"USDT", base:38.42 },
  { sym:"BNB",  base:412   },
  { sym:"SOL",  base:178   },
  { sym:"AVAX", base:38.9  },
];

const PCOLOR = { critical:"#F87171", high:"#FBBF24", normal:"#38BDF8" };

export default function JarvisV2() {
  const [tasks, setTasks]     = useState(INIT_TASKS);
  const [chat, setChat]       = useState(INIT_CHAT);
  const [input, setInput]     = useState("");
  const [selAgent, setSelAgent] = useState(null);
  const [time, setTime]       = useState("");
  const [date, setDate]       = useState("");
  const [tick, setTick]       = useState(0);
  const [radarAngle, setRadarAngle] = useState(0);
  const [market, setMarket]   = useState(MARKET.map(m=>({...m, price:m.base, change:0})));
  const [alerts, setAlerts]   = useState([]);
  const [agentLoads, setAgentLoads] = useState(Object.fromEntries(AGENTS.map(a=>[a.id,a.load])));
  const chatRef  = useRef(null);
  const nextId   = useRef(5);
  const nextTask = useRef(47);
  const radarRef = useRef(0);

  useEffect(() => {
    const lnk = document.createElement("link");
    lnk.rel="stylesheet"; lnk.href=GF;
    document.head.appendChild(lnk);
  }, []);

  useEffect(() => {
    let frame;
    const loop = () => {
      radarRef.current = (radarRef.current + 0.8) % 360;
      setRadarAngle(radarRef.current);
      frame = requestAnimationFrame(loop);
    };
    frame = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frame);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      const now = new Date();
      setTime(now.toLocaleTimeString("tr-TR",{hour12:false}));
      setDate(now.toLocaleDateString("tr-TR",{day:"2-digit",month:"2-digit",year:"numeric"}));
      setTick(t => t+1);
      setMarket(m => m.map(item => {
        const delta = (Math.random()-0.49) * item.base * 0.003;
        const newPrice = Math.max(item.base*0.92, Math.min(item.base*1.08, item.price + delta));
        return { ...item, price: newPrice, change: ((newPrice - item.base)/item.base*100) };
      }));
      setAgentLoads(l => {
        const nl = {...l};
        AGENTS.forEach(a => {
          if (a.status === "active") nl[a.id] = Math.max(10, Math.min(98, (nl[a.id]||50) + (Math.random()-0.5)*8));
        });
        return nl;
      });
    }, 1200);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      setTasks(t => t.map(tk =>
        tk.progress < 100 && tk.progress > 0
          ? { ...tk, progress: Math.min(100, tk.progress + Math.floor(Math.random()*3+1)) }
          : tk
      ));
    }, 1800);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      const msgs = [
        { ag:"ATLAS",  txt:"Bollinger Band sıkışması tespit edildi. Kırılım bekleniyor." },
        { ag:"GHOST",  txt:`Yeni haber: Kripto piyasaları ${Math.random()>0.5?"yükseliş":"düşüş"} eğiliminde.` },
        { ag:"KISHI",  txt:`BTC anlık: $${(67000+Math.random()*1000).toFixed(0)}` },
        { ag:"NEXUS",  txt:"Portföy risk skoru normal seviyelerde." },
        { ag:"VEGA",   txt:"Stop-loss seviyeleri güncellendi." },
      ];
      const m = msgs[Math.floor(Math.random()*msgs.length)];
      const ts = new Date().toLocaleTimeString("tr-TR",{hour12:false,hour:"2-digit",minute:"2-digit"});
      setAlerts(a => [...a.slice(-3), { id:Date.now(), agentId:m.ag, text:m.txt, ts }]);
    }, 5000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [chat]);

  const send = () => {
    if (!input.trim()) return;
    const msg = input.trim(); setInput("");
    const ts = new Date().toLocaleTimeString("tr-TR",{hour12:false,hour:"2-digit",minute:"2-digit"});
    setChat(c => [...c, { id:nextId.current++, from:"user", text:msg, ts }]);
    const active = AGENTS.filter(a=>a.status==="active");
    const resp = active[Math.floor(Math.random()*active.length)];
    const replies = [
      `"${msg}" komutu işleme alındı. Analiz başlatılıyor.`,
      `Veri tabanı taranıyor. Sonuçlar kısa sürede hazır olacak.`,
      `Görev kuyruğa eklendi. Öncelik seviyesi: YÜKSEK.`,
      `Tau yönlendirmesiyle görevi üstlendim. İşlem devam ediyor.`,
    ];
    setTimeout(() => {
      setChat(c => [...c, { id:nextId.current++, from:resp.id, text:replies[Math.floor(Math.random()*replies.length)], ts }]);
      setTasks(t => [...t, { id:`TSK-0${nextTask.current++}`, agentId:resp.id, title:msg.slice(0,38), priority:"high", progress:0 }]);
    }, 700);
  };

  const selA = AGENTS.find(a=>a.id===selAgent);

  const CSS = `
    @import url('${GF}');
    *{box-sizing:border-box;margin:0;padding:0;}
    html,body{background:#000;height:100%;}
    .jr{font-family:'Share Tech Mono',monospace;background:#000912;color:#00D4FF;height:100vh;overflow:hidden;display:grid;grid-template-rows:44px 28px 1fr 52px;position:relative;}
    .jr::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,212,255,.013) 2px,rgba(0,212,255,.013) 3px);pointer-events:none;z-index:0;}
    .hud-corner{position:fixed;width:60px;height:60px;pointer-events:none;z-index:10;}
    .hud-corner.tl{top:0;left:0;border-top:1.5px solid rgba(0,212,255,.45);border-left:1.5px solid rgba(0,212,255,.45);}
    .hud-corner.tr{top:0;right:0;border-top:1.5px solid rgba(0,212,255,.45);border-right:1.5px solid rgba(0,212,255,.45);}
    .hud-corner.bl{bottom:0;left:0;border-bottom:1.5px solid rgba(0,212,255,.45);border-left:1.5px solid rgba(0,212,255,.45);}
    .hud-corner.br{bottom:0;right:0;border-bottom:1.5px solid rgba(0,212,255,.45);border-right:1.5px solid rgba(0,212,255,.45);}
    .top-bar{display:flex;align-items:center;justify-content:space-between;padding:0 20px;border-bottom:1px solid rgba(0,212,255,.15);background:rgba(0,9,18,.97);z-index:2;position:relative;}
    .logo{font-family:'Orbitron',monospace;font-size:13px;font-weight:900;color:#00D4FF;letter-spacing:6px;display:flex;align-items:center;gap:10px;}
    .arc-btn{width:20px;height:20px;border-radius:50%;border:2px solid #00D4FF;display:flex;align-items:center;justify-content:center;position:relative;}
    .arc-btn::before{content:'';position:absolute;width:8px;height:8px;border-radius:50%;background:#00D4FF;opacity:.8;animation:corepulse 2s infinite;}
    @keyframes corepulse{0%,100%{opacity:.8;transform:scale(1);}50%{opacity:.3;transform:scale(.6);}}
    .top-pills{display:flex;gap:10px;align-items:center;}
    .tpill{font-size:9px;padding:2px 9px;border-radius:2px;letter-spacing:.5px;font-weight:600;}
    .tp-g{background:rgba(52,211,153,.1);color:#34D399;border:1px solid rgba(52,211,153,.25);}
    .tp-y{background:rgba(251,191,36,.1);color:#FBBF24;border:1px solid rgba(251,191,36,.25);}
    .tp-r{background:rgba(248,113,113,.1);color:#F87171;border:1px solid rgba(248,113,113,.25);}
    .tp-b{background:rgba(0,212,255,.08);color:#00D4FF;border:1px solid rgba(0,212,255,.2);}
    .hdr-time{font-family:'Orbitron',monospace;font-size:12px;color:#00D4FF;letter-spacing:2.5px;}
    .hdr-date{font-size:9px;color:rgba(0,212,255,.4);letter-spacing:1.5px;text-align:right;margin-top:1px;}
    .ticker{overflow:hidden;background:rgba(0,4,12,.9);border-bottom:1px solid rgba(0,212,255,.1);z-index:2;position:relative;display:flex;align-items:center;}
    .ticker-inner{display:flex;gap:32px;padding:0 16px;animation:tickscroll 30s linear infinite;white-space:nowrap;}
    @keyframes tickscroll{0%{transform:translateX(0);}100%{transform:translateX(-50%);}}
    .tick-item{display:flex;align-items:center;gap:7px;font-size:10px;}
    .tick-sym{font-family:'Orbitron',monospace;font-size:9px;font-weight:700;color:rgba(0,212,255,.7);}
    .tick-price{color:#C8E6FF;}
    .tick-chg{font-size:9px;}
    .body{display:grid;grid-template-columns:250px 1fr 262px;overflow:hidden;z-index:1;position:relative;}
    .lp,.rp{display:flex;flex-direction:column;overflow:hidden;}
    .lp{border-right:1px solid rgba(0,212,255,.1);}
    .rp{border-left:1px solid rgba(0,212,255,.1);}
    .cp{display:flex;flex-direction:column;align-items:center;overflow:hidden;}
    .sec{font-family:'Orbitron',monospace;font-size:8px;letter-spacing:2.5px;color:rgba(0,212,255,.35);padding:9px 14px 7px;border-bottom:1px solid rgba(0,212,255,.07);flex-shrink:0;display:flex;justify-content:space-between;align-items:center;}
    .agent-scroll{flex:1;overflow-y:auto;}
    .agent-scroll::-webkit-scrollbar{width:2px;}
    .agent-scroll::-webkit-scrollbar-thumb{background:rgba(0,212,255,.25);}
    .aitem{display:flex;align-items:center;gap:9px;padding:9px 14px;cursor:pointer;border-left:2px solid transparent;transition:all .12s;}
    .aitem:hover{background:rgba(0,212,255,.04);}
    .aitem.asel{border-left-color:var(--ac);background:rgba(0,212,255,.07);}
    .aava{width:36px;height:36px;border-radius:50%;border:1.5px solid var(--ac);display:flex;align-items:center;justify-content:center;font-family:'Orbitron',monospace;font-size:9px;font-weight:700;flex-shrink:0;position:relative;color:var(--ac);}
    .aava::after{content:'';position:absolute;inset:-4px;border-radius:50%;border:1px solid var(--ac);opacity:.2;animation:spin 6s linear infinite;}
    @keyframes spin{to{transform:rotate(360deg);}}
    .aname{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;}
    .arole{font-size:9px;color:rgba(0,212,255,.4);margin-top:1px;letter-spacing:.5px;}
    .aload-row{display:flex;align-items:center;gap:5px;margin-top:3px;}
    .aload-bar{flex:1;height:2px;background:rgba(0,212,255,.1);border-radius:1px;}
    .aload-fill{height:100%;border-radius:1px;transition:width .8s;}
    .aload-val{font-size:8px;color:rgba(0,212,255,.35);font-family:'Orbitron',monospace;min-width:24px;}
    .adot{width:6px;height:6px;border-radius:50%;flex-shrink:0;margin-left:auto;animation:adp 2s infinite;}
    @keyframes adp{0%,100%{opacity:1;}50%{opacity:.2;}}
    .agent-detail{margin:8px 14px;padding:10px 12px;border-radius:4px;border:1px solid rgba(0,212,255,.15);background:rgba(0,8,18,.6);flex-shrink:0;}
    .ad-title{font-family:'Orbitron',monospace;font-size:8px;letter-spacing:2px;margin-bottom:6px;}
    .ad-text{font-size:10px;color:rgba(200,230,255,.6);line-height:1.6;}
    .ad-meta{display:flex;gap:10px;margin-top:7px;font-size:9px;}
    .sys-block{padding:8px 14px;border-top:1px solid rgba(0,212,255,.08);flex-shrink:0;}
    .sys-row{display:flex;justify-content:space-between;font-size:9px;color:rgba(0,212,255,.35);line-height:2;}
    .sys-val{color:rgba(0,212,255,.7);}
    .alert-feed{padding:6px 14px;border-top:1px solid rgba(0,212,255,.08);flex-shrink:0;max-height:110px;overflow:hidden;}
    .alert-item{font-size:9px;padding:3px 0;border-bottom:1px solid rgba(0,212,255,.05);display:flex;gap:6px;animation:afade .4s ease;}
    @keyframes afade{from{opacity:0;transform:translateX(-4px);}to{opacity:1;transform:translateX(0);}}
    .alert-ag{font-family:'Orbitron',monospace;font-size:8px;font-weight:700;flex-shrink:0;}
    .alert-txt{color:rgba(200,230,255,.5);flex:1;}
    .ARC{position:relative;flex-shrink:0;}
    .arc-svg{position:absolute;inset:0;pointer-events:none;}
    .arc-core{position:absolute;border-radius:50%;overflow:hidden;display:flex;flex-direction:column;}
    .core-label{font-family:'Orbitron',monospace;font-size:7px;letter-spacing:3px;color:rgba(0,212,255,.3);text-align:center;padding:8px 0 2px;flex-shrink:0;}
    .core-chat{flex:1;overflow-y:auto;padding:8px 10px;display:flex;flex-direction:column;gap:7px;}
    .core-chat::-webkit-scrollbar{width:2px;}
    .core-chat::-webkit-scrollbar-thumb{background:rgba(0,212,255,.15);}
    .cmsg{padding:6px 9px;border-radius:3px;font-size:10.5px;line-height:1.55;}
    .cm-user{background:rgba(0,212,255,.09);border:1px solid rgba(0,212,255,.2);color:#C8E6FF;text-align:right;}
    .cm-agent{border:1px solid;color:#a0c8e8;}
    .cm-who{font-family:'Orbitron',monospace;font-size:7.5px;font-weight:700;letter-spacing:.5px;margin-bottom:2px;}
    .cm-ts{font-size:7px;color:rgba(0,212,255,.25);text-align:right;margin-top:2px;}
    .core-input{display:flex;gap:6px;padding:6px 10px 8px;border-top:1px solid rgba(0,212,255,.1);flex-shrink:0;}
    .ci{flex:1;background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.18);color:#C8E6FF;font-family:'Share Tech Mono',monospace;font-size:11px;padding:6px 10px;outline:none;}
    .ci:focus{border-color:rgba(0,212,255,.45);}
    .ci::placeholder{color:rgba(0,212,255,.2);}
    .cs{background:rgba(0,212,255,.12);border:1px solid rgba(0,212,255,.3);color:#00D4FF;font-family:'Orbitron',monospace;font-size:8px;letter-spacing:1.5px;padding:6px 10px;cursor:pointer;transition:all .12s;}
    .cs:hover{background:rgba(0,212,255,.25);}
    .arc-stats{display:flex;gap:20px;margin-top:6px;flex-shrink:0;}
    .as-item{text-align:center;}
    .as-val{font-family:'Orbitron',monospace;font-size:16px;font-weight:700;}
    .as-lbl{font-size:7.5px;color:rgba(0,212,255,.35);letter-spacing:1px;margin-top:1px;}
    .task-scroll{flex:1;overflow-y:auto;}
    .task-scroll::-webkit-scrollbar{width:2px;}
    .task-scroll::-webkit-scrollbar-thumb{background:rgba(0,212,255,.2);}
    .tsk{padding:8px 14px;border-bottom:1px solid rgba(0,212,255,.06);}
    .tsk-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;}
    .tsk-id{font-size:8px;color:rgba(0,212,255,.3);font-family:'Orbitron',monospace;}
    .tsk-pri{font-size:7px;padding:1px 5px;border-radius:1px;font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.5px;}
    .tsk-who{font-size:9px;margin-bottom:3px;letter-spacing:.3px;display:flex;align-items:center;gap:4px;}
    .tsk-title{font-size:11px;color:rgba(200,230,255,.65);margin-bottom:5px;line-height:1.4;}
    .tsk-bar{height:2.5px;background:rgba(0,212,255,.08);border-radius:2px;}
    .tsk-fill{height:100%;border-radius:2px;transition:width .6s;}
    .tsk-bot{display:flex;justify-content:space-between;margin-top:2px;font-size:8px;color:rgba(0,212,255,.3);font-family:'Orbitron',monospace;}
    .wt-block{margin:8px 14px 0;padding:10px 12px;border-radius:3px;border:1px solid rgba(148,163,184,.18);background:rgba(148,163,184,.04);flex-shrink:0;}
    .wt-title{font-family:'Orbitron',monospace;font-size:8px;letter-spacing:2px;color:#94A3B8;margin-bottom:5px;display:flex;align-items:center;gap:6px;}
    .wt-dot{width:5px;height:5px;border-radius:50%;background:#34D399;animation:adp 1.5s infinite;}
    .wt-line{font-size:9.5px;color:rgba(200,230,255,.45);line-height:1.9;display:flex;align-items:center;gap:6px;}
    .wt-bullet{color:#34D399;flex-shrink:0;}
    .bottom-bar{display:flex;align-items:center;gap:12px;padding:0 18px;border-top:1px solid rgba(0,212,255,.12);background:rgba(0,9,18,.97);z-index:2;position:relative;}
    .b-sel{font-family:'Orbitron',monospace;font-size:9px;color:rgba(0,212,255,.4);letter-spacing:1.5px;flex-shrink:0;}
    .b-inp{flex:1;background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.18);color:#C8E6FF;font-family:'Share Tech Mono',monospace;font-size:12px;padding:9px 14px;outline:none;}
    .b-inp:focus{border-color:rgba(0,212,255,.45);}
    .b-inp::placeholder{color:rgba(0,212,255,.2);}
    .b-send{background:rgba(0,212,255,.14);border:1px solid rgba(0,212,255,.35);color:#00D4FF;font-family:'Orbitron',monospace;font-size:9px;letter-spacing:2px;padding:9px 18px;cursor:pointer;transition:all .12s;flex-shrink:0;}
    .b-send:hover{background:rgba(0,212,255,.28);}
    .b-tick{font-family:'Share Tech Mono',monospace;font-size:9px;color:rgba(0,212,255,.2);letter-spacing:1px;flex-shrink:0;}
  `;

  const SIZE  = 370;
  const CX    = SIZE / 2;
  const CY    = SIZE / 2;
  const RINGS = [170, 155, 138, 118, 95];
  const CORE  = 88;
  const radarRad = (radarAngle * Math.PI) / 180;

  return (
    <>
      <style>{CSS}</style>
      <div className="hud-corner tl"/><div className="hud-corner tr"/>
      <div className="hud-corner bl"/><div className="hud-corner br"/>

      <div className="jr">

        {/* TOP BAR */}
        <div className="top-bar">
          <div className="logo">
            <div className="arc-btn"/>
            SYNTHIC
            <span style={{fontSize:8,color:"rgba(0,212,255,.35)",fontWeight:400,letterSpacing:2}}>JARVIS CORE v2.1</span>
          </div>
          <div className="top-pills">
            <span className="tpill tp-g">● {AGENTS.filter(a=>a.status==="active").length} AKTİF</span>
            <span className="tpill tp-b">◈ {tasks.filter(t=>t.progress<100).length} GÖREV</span>
            <span className="tpill tp-y">⚑ WATCHTOWER ON</span>
            <span className="tpill tp-r">! 1 UYARI</span>
          </div>
          <div style={{textAlign:"right"}}>
            <div className="hdr-time">{time||"--:--:--"}</div>
            <div className="hdr-date">{date}</div>
          </div>
        </div>

        {/* TICKER */}
        <div className="ticker">
          <div className="ticker-inner">
            {[...market,...market].map((m,i) => (
              <span key={i} className="tick-item">
                <span className="tick-sym">{m.sym}</span>
                <span className="tick-price">
                  {m.sym==="USDT" ? m.price.toFixed(2) : m.price >= 1000 ? `$${m.price.toFixed(0)}` : `$${m.price.toFixed(2)}`}
                </span>
                <span className="tick-chg" style={{color: m.change>=0?"#34D399":"#F87171"}}>
                  {m.change>=0?"+":""}{m.change.toFixed(2)}%
                </span>
              </span>
            ))}
          </div>
        </div>

        {/* MAIN BODY */}
        <div className="body">

          {/* LEFT */}
          <div className="lp">
            <div className="sec">
              <span>AJAN MATRİSİ</span>
              <span style={{color:"rgba(0,212,255,.5)"}}>{AGENTS.length} KAYITLI</span>
            </div>
            <div className="agent-scroll">
              {AGENTS.map(ag => {
                const load = agentLoads[ag.id] ?? ag.load;
                return (
                  <div key={ag.id} className={`aitem${selAgent===ag.id?" asel":""}`}
                    style={{"--ac":ag.color}} onClick={()=>setSelAgent(s=>s===ag.id?null:ag.id)}>
                    <div className="aava" style={{background:`${ag.color}14`}}>
                      {ag.name.slice(0,2)}
                    </div>
                    <div style={{flex:1,minWidth:0}}>
                      <div style={{display:"flex",alignItems:"center",gap:5}}>
                        <span className="aname" style={{color:ag.color}}>{ag.name}</span>
                        {ag.id==="TAU" && (
                          <span style={{fontSize:7,padding:"1px 4px",background:`${ag.color}20`,color:ag.color,border:`1px solid ${ag.color}40`,fontFamily:"'Orbitron',monospace",letterSpacing:.5}}>ŞEF</span>
                        )}
                      </div>
                      <div className="arole">{ag.role}</div>
                      <div className="aload-row">
                        <div className="aload-bar">
                          <div className="aload-fill" style={{width:`${load}%`,background:load>80?`#F87171`:ag.color}}/>
                        </div>
                        <span className="aload-val">{Math.round(load)}%</span>
                      </div>
                    </div>
                    <div className="adot" style={{background:ag.status==="active"?"#34D399":"#475569"}}/>
                  </div>
                );
              })}
            </div>

            {selA && (
              <div className="agent-detail" style={{borderColor:`${selA.color}30`,background:`${selA.color}08`}}>
                <div className="ad-title" style={{color:selA.color}}>// {selA.name} — {selA.role}</div>
                <div className="ad-text">{selA.desc}</div>
                <div className="ad-meta">
                  <span style={{color:selA.color,fontSize:9}}>{selA.tasks} aktif görev</span>
                  <span style={{color:"rgba(0,212,255,.35)",fontSize:9}}>●</span>
                  <span style={{color:selA.status==="active"?"#34D399":"#94A3B8",fontSize:9}}>
                    {selA.status==="active"?"ÇEVRIM İÇİ":"HAZIR BEKLEMEDE"}
                  </span>
                </div>
              </div>
            )}

            <div className="alert-feed">
              <div style={{fontFamily:"'Orbitron',monospace",fontSize:7,letterSpacing:2,color:"rgba(0,212,255,.25)",marginBottom:4}}>// CANLI UYARILAR</div>
              {alerts.slice(-3).map(al => {
                const ag = AGENTS.find(a=>a.id===al.agentId);
                return (
                  <div key={al.id} className="alert-item">
                    <span className="alert-ag" style={{color:ag?.color??"#00D4FF"}}>{al.agentId}</span>
                    <span className="alert-txt">{al.text}</span>
                    <span style={{fontSize:8,color:"rgba(0,212,255,.2)",flexShrink:0}}>{al.ts}</span>
                  </div>
                );
              })}
            </div>

            <div className="sys-block">
              {[["CPU",`${Math.round(tick*7%30+42)}%`],["MEM",`${Math.round(tick*3%15+55)}%`],["NET",`${Math.round(tick*11%40+100)} ms`],["API","● BAĞLI"]].map(([k,v])=>(
                <div key={k} className="sys-row"><span>{k}</span><span className="sys-val">{v}</span></div>
              ))}
            </div>
          </div>

          {/* CENTER */}
          <div className="cp">
            <div className="ARC" style={{width:SIZE,height:SIZE,marginTop:8}}>

              <svg className="arc-svg" viewBox={`0 0 ${SIZE} ${SIZE}`} xmlns="http://www.w3.org/2000/svg">
                {/* Rings */}
                {RINGS.map((r,i) => (
                  <circle key={i} cx={CX} cy={CY} r={r} fill="none" stroke={`rgba(0,212,255,${.04+i*.03})`} strokeWidth="1"/>
                ))}
                {/* Tick marks on outermost ring */}
                {Array.from({length:72}).map((_,i) => {
                  const a = (i*5*Math.PI)/180;
                  const outerR = RINGS[0];
                  const innerR = i%6===0 ? outerR-10 : i%2===0 ? outerR-5 : outerR-3;
                  return (
                    <line key={i}
                      x1={CX+outerR*Math.cos(a)} y1={CY+outerR*Math.sin(a)}
                      x2={CX+innerR*Math.cos(a)} y2={CY+innerR*Math.sin(a)}
                      stroke={`rgba(0,212,255,${i%6===0?.45:i%2===0?.2:.1})`} strokeWidth={i%6===0?1.2:.7}/>
                  );
                })}
                {/* Degree labels */}
                {[0,90,180,270].map(deg => {
                  const a = (deg*Math.PI)/180;
                  const r = RINGS[0]+14;
                  return <text key={deg} x={CX+r*Math.cos(a)} y={CY+r*Math.sin(a)} fill="rgba(0,212,255,.3)" fontSize="7" textAnchor="middle" dominantBaseline="middle" fontFamily="Orbitron">{deg}°</text>;
                })}
                {/* Crosshairs */}
                <line x1={CX-RINGS[0]} y1={CY} x2={CX+RINGS[0]} y2={CY} stroke="rgba(0,212,255,.06)" strokeWidth="1"/>
                <line x1={CX} y1={CY-RINGS[0]} x2={CX} y2={CY+RINGS[0]} stroke="rgba(0,212,255,.06)" strokeWidth="1"/>
                {/* Radar sweep */}
                <defs>
                  <radialGradient id="sweep" cx="0%" cy="0%">
                    <stop offset="0%" stopColor="#00D4FF" stopOpacity=".5"/>
                    <stop offset="100%" stopColor="#00D4FF" stopOpacity="0"/>
                  </radialGradient>
                </defs>
                <path
                  d={`M ${CX} ${CY} L ${CX + RINGS[1]*Math.cos(radarRad)} ${CY + RINGS[1]*Math.sin(radarRad)} A ${RINGS[1]} ${RINGS[1]} 0 0 0 ${CX + RINGS[1]*Math.cos(radarRad - 0.6)} ${CY + RINGS[1]*Math.sin(radarRad - 0.6)} Z`}
                  fill="rgba(0,212,255,.08)"/>
                <line
                  x1={CX} y1={CY}
                  x2={CX+RINGS[1]*Math.cos(radarRad)} y2={CY+RINGS[1]*Math.sin(radarRad)}
                  stroke="rgba(0,212,255,.55)" strokeWidth="1.2"/>
                {/* Agent orbit dots */}
                {AGENTS.map(ag => {
                  const rad2 = (ag.angle*Math.PI)/180;
                  const orbitR = RINGS[2];
                  const bx = CX+orbitR*Math.cos(rad2);
                  const by = CY+orbitR*Math.sin(rad2);
                  const isSelected = selAgent===ag.id;
                  return (
                    <g key={ag.id} style={{cursor:"pointer"}} onClick={()=>setSelAgent(s=>s===ag.id?null:ag.id)}>
                      {isSelected && <circle cx={bx} cy={by} r="20" fill={`${ag.color}18`} stroke={ag.color} strokeWidth="1" strokeDasharray="3 2"/>}
                      <circle cx={bx} cy={by} r={isSelected?13:11} fill={`${ag.color}20`} stroke={ag.color} strokeWidth={isSelected?1.5:1}/>
                      <circle cx={bx} cy={by} r="3" fill={ag.color} opacity={ag.status==="active"?.9:.4}/>
                      <text x={bx} y={by+20} fill={ag.color} fontSize="7" textAnchor="middle" fontFamily="Orbitron" fontWeight="700">{ag.name}</text>
                    </g>
                  );
                })}
                {/* Center circle */}
                <circle cx={CX} cy={CY} r={CORE+2} fill="#000912" stroke="rgba(0,212,255,.18)" strokeWidth="1"/>
              </svg>

              {/* Core chat window */}
              <div className="arc-core" style={{inset: SIZE/2-CORE+2, borderRadius:"50%", border:"1px solid rgba(0,212,255,.18)", background:"rgba(0,4,14,.95)"}}>
                <div className="core-label">KOMUTA</div>
                <div className="core-chat" ref={chatRef}>
                  {(selAgent ? chat.filter(m=>m.from===selAgent||m.from==="user") : chat).map(m => {
                    const ag = AGENTS.find(a=>a.id===m.from);
                    const isUser = m.from==="user";
                    return (
                      <div key={m.id} className={`cmsg ${isUser?"cm-user":"cm-agent"}`}
                        style={!isUser?{borderColor:`${ag?.color??"#00D4FF"}35`,background:`${ag?.color??"#00D4FF"}08`}:{}}>
                        {!isUser && <div className="cm-who" style={{color:ag?.color??"#00D4FF"}}>{ag?.name}</div>}
                        {m.text}
                        <div className="cm-ts">{m.ts}</div>
                      </div>
                    );
                  })}
                </div>
                <div className="core-input">
                  <input className="ci" placeholder="komut..." value={input}
                    onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()}/>
                  <button className="cs" onClick={send}>▶</button>
                </div>
              </div>
            </div>

            <div className="arc-stats">
              {[
                {val:AGENTS.filter(a=>a.status==="active").length, lbl:"AKTİF", color:"#34D399"},
                {val:tasks.filter(t=>t.progress<100).length,       lbl:"GÖREV", color:"#38BDF8"},
                {val:tasks.filter(t=>t.progress===100).length,     lbl:"TAMAM", color:"#7C6FE0"},
                {val:`${Math.round(Object.values(agentLoads).reduce((a,b)=>a+b,0)/AGENTS.length)}%`, lbl:"ORT YÜK", color:"#FBBF24"},
              ].map((s,i)=>(
                <div key={i} className="as-item">
                  <div className="as-val" style={{color:s.color}}>{s.val}</div>
                  <div className="as-lbl">{s.lbl}</div>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT */}
          <div className="rp">
            <div className="sec">
              <span>GÖREV KUYRUĞU</span>
              <span style={{color:"rgba(0,212,255,.45)"}}>{tasks.filter(t=>t.progress<100).length} AKTİF</span>
            </div>
            <div className="task-scroll">
              {tasks.map(t => {
                const ag = AGENTS.find(a=>a.id===t.agentId);
                const pc = PCOLOR[t.priority]??"#38BDF8";
                return (
                  <div key={t.id} className="tsk">
                    <div className="tsk-top">
                      <span className="tsk-id">{t.id}</span>
                      <span className="tsk-pri" style={{background:`${pc}15`,color:pc,border:`1px solid ${pc}35`}}>{t.priority.toUpperCase()}</span>
                    </div>
                    <div className="tsk-who">
                      <span style={{width:6,height:6,borderRadius:"50%",background:ag?.color??"#00D4FF",display:"inline-block",flexShrink:0}}/>
                      <span style={{color:ag?.color??"#00D4FF",fontFamily:"'Orbitron',monospace",fontSize:9,fontWeight:700}}>{ag?.name}</span>
                      <span style={{color:"rgba(0,212,255,.3)",fontSize:9}}>— {ag?.role}</span>
                    </div>
                    <div className="tsk-title">{t.title}</div>
                    <div className="tsk-bar">
                      <div className="tsk-fill" style={{width:`${t.progress}%`,background:t.progress===100?"#34D399":pc}}/>
                    </div>
                    <div className="tsk-bot">
                      <span>{t.id}</span><span>{t.progress}%</span>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="wt-block">
              <div className="wt-title"><div className="wt-dot"/>WATCHTOWER</div>
              <div className="wt-line"><span className="wt-bullet">▸</span>7/24 piyasa gözlemi aktif</div>
              <div className="wt-line"><span className="wt-bullet">▸</span>Volatilite taraması devam ediyor</div>
              <div className="wt-line" style={{color:"rgba(251,191,36,.65)"}}><span style={{color:"#FBBF24"}}>⚑</span>BTC hacmi +12% artış algılandı</div>
              <div className="wt-line" style={{color:"rgba(248,113,113,.55)"}}><span style={{color:"#F87171"}}>!</span>Atlas yük %88 — izlemede</div>
            </div>
          </div>
        </div>

        {/* BOTTOM */}
        <div className="bottom-bar">
          <span className="b-sel">
            {selAgent ? `TARGET: ${selAgent}` : "TARGET: TAU"}
          </span>
          <input className="b-inp" placeholder="Tau'ya görev ver... (Enter ile gönder)"
            value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()}/>
          <button className="b-send" onClick={send}>EXEC ▶</button>
          <span className="b-tick">SYN/{String(tick).padStart(5,"0")}</span>
        </div>

      </div>
    </>
  );
}
