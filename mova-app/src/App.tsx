import { useState, useRef, useEffect } from 'react';
import './App.css';

const API_URL = 'http://127.0.0.1:8080/completion';

const GET_SYSTEM_PROMPT = (lang: string, biz: string) => `You are SabiCore, an offline assistant for ${biz}, an African informal retail business.
Follow these structural rules:
1. If the user pastes an M-Pesa, OPay, or MoMo SMS receipt, parse it and extract the Sender, Amount, Date, and Balance. Ignore telecom spam.
2. If the user pastes a WhatsApp chat export, parse the conversation to determine who owes who, the amount, and the terms of the informal credit.
3. If the user mentions "Ajo" or "Esusu", treat it as a rotating savings contribution, NOT an expense.
4. Always respond strictly in ${lang}, keeping it friendly and culturally relevant to the informal market. Format your output strictly like a printed receipt with dashes separating the lines.

### Instruction:
`;

function App() {
  const [screen, setScreen] = useState<'landing' | 'booting' | 'ledger'>('landing');
  const [businessName, setBusinessName] = useState('');
  const [bootText, setBootText] = useState<string[]>([]);
  
  const [language, setLanguage] = useState('Nigerian Pidgin');
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping, bootText]);

  const handleStartBoot = (e: React.FormEvent) => {
    e.preventDefault();
    if (!businessName.trim()) return;
    setScreen('booting');
    
    const bootSequence = [
      "INITIALIZING SABICORE KERNEL...",
      "BYPASSING CLOUD DEPENDENCIES...",
      "MOUNTING OFFLINE LEDGER MODULES...",
      "DETECTING HARDWARE ACCELERATION...",
      "VULKAN/METAL iGPU: [ OK ]",
      "LOADING 3B PARAMETER WEIGHTS...",
      "ALLOCATING 2.1GB VRAM: [ OK ]",
      "THERMAL LIMIT EXCEPTION HANDLER: ONLINE",
      "STRUCTURAL ADAPTATION PROTOCOL: ENGAGED",
      `BUSINESS CONTEXT: [ ${businessName.toUpperCase()} ]`,
      "SYSTEM FULLY OPERATIONAL."
    ];

    let i = 0;
    const interval = setInterval(() => {
      setBootText(prev => [...prev, bootSequence[i]]);
      i++;
      if (i >= bootSequence.length) {
        clearInterval(interval);
        setTimeout(() => {
          setMessages([
            { role: 'system', content: `SYSTEM BOOT COMPLETE.\\n\\nWelcome boss! I be the offline ledger for [ ${businessName.toUpperCase()} ]. \\nPaste your OPay/M-Pesa SMS make I record am, or paste WhatsApp chat make I track your debtors.` }
          ]);
          setScreen('ledger');
        }, 800);
      }
    }, 300);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsTyping(true);

    const prompt = GET_SYSTEM_PROMPT(language, businessName) + userMessage + "\\n\\n### Response:\\n";

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          n_predict: 256,
          temperature: 0.7,
          top_k: 40,
          top_p: 0.95,
          stop: ["### Instruction:", "\\n\\n\\n"]
        })
      });

      if (!response.ok) throw new Error('Server error');
      
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'system', content: data.content.trim() }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: 'ERROR: CONNECTION FAIL.\\nENGINE (llama-server) OFFLINE.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handlePasteSMS = () => {
    setInput("OPay: You have received N50,000.00 from CHINEDU OKAFOR. Ref: 20260817001. Bal: N125,450.00. Dial *955# for loans.");
  };

  const handlePasteWhatsApp = () => {
    setInput("[18/08/2026, 13:00:15] Mama Nkechi: Chinedu, the 20 bags of rice I supply you yesterday, you never pay the balance.\\n[18/08/2026, 13:05:22] Chinedu Okafor: Ah Mama, no vex. I go balance you the remaining N150,000 next market day.\\n[18/08/2026, 13:10:05] Mama Nkechi: No problem, I don record am.");
  };

  if (screen === 'landing') {
    return (
      <div className="app-container landing-container">
        <div className="landing-content">
          <h1 className="hero-title">SABICORE</h1>
          <h2 className="hero-subtitle">THE OFFLINE LEDGER.</h2>
          <p className="hero-desc">Formalizing the informal economy. Zero cloud. Zero data fees. 100% On-Device AI.</p>
          
          <form className="landing-form" onSubmit={handleStartBoot}>
            <input 
              type="text" 
              className="business-input"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              placeholder="ENTER BUSINESS NAME_ " 
              autoFocus
            />
            <button type="submit" className="initialize-btn">
              [ INITIALIZE ENGINE ]
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (screen === 'booting') {
    return (
      <div className="app-container boot-container">
        <div className="boot-terminal">
          {bootText.map((line, idx) => (
            <div key={idx} className="boot-line">{line}</div>
          ))}
          <div className="boot-cursor">_</div>
          <div ref={chatEndRef} />
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="brutalist-header">
        <div className="header-top">
          <div className="logo">
            <span className="logo-icon">₦</span>
            <h1>SabiCore</h1>
          </div>
          <div className="status-indicator">
            [ ENGINE ONLINE ]
          </div>
        </div>
        <div className="controls-bar">
          <select 
            className="lang-select" 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="Nigerian Pidgin">LANG: PIDGIN</option>
            <option value="Hausa">LANG: HAUSA</option>
            <option value="Swahili">LANG: SWAHILI</option>
          </select>
        </div>
      </header>

      <main className="chat-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role === 'user' ? 'user-message' : 'system-message'}`}>
            <div className="message-label">
              {msg.role === 'user' ? 'USER_INPUT' : 'SYSTEM_LEDGER'}
            </div>
            <div className="receipt-bubble">
              <p dangerouslySetInnerHTML={{ __html: msg.content.replace(/\\n/g, '<br/>') }} />
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message system-message">
            <div className="message-label">SYSTEM_LEDGER</div>
            <div className="receipt-bubble">
              <div className="typing-indicator">PARSING DATA...</div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>

      <footer className="input-area">
        <div className="input-controls">
          <button type="button" className="brutalist-btn sms-btn" onClick={handlePasteSMS}>[ + ] OPAY SMS</button>
          <button type="button" className="brutalist-btn wa-btn" onClick={handlePasteWhatsApp}>[ + ] WHATSAPP</button>
        </div>
        <form onSubmit={handleSend}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="ENTER TRANSACTION DATA..." 
            disabled={isTyping}
          />
          <button type="submit" disabled={isTyping}>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="square" strokeLinejoin="miter"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
