import React, { useState, useRef, useEffect } from 'react';

/**
 * AIChatbox Component — Interactive Trend Analysis & Insights
 * Dành cho hệ thống Skill Lens Lab Dashboard (Theme Teal/Cyan #0fa39e)
 * Tích hợp nhận diện ngữ cảnh Dashboard, Web Speech API (vi-VN), và gọi POST /api/insights/chat
 */
export default function AIChatbox({ context = {} }) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [lastFailedMessage, setLastFailedMessage] = useState(null);

  const [conversationId, setConversationId] = useState(() => 
    'conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9)
  );

  const initialWelcome = {
    id: 'welcome_msg',
    sender: 'ai',
    text: 'Xin chào! Tôi là AI Chatbox của Skill Lens Lab. Tôi có thể giúp bạn giải thích biểu đồ, phân tích xu hướng kỹ năng, so sánh dữ liệu và đưa ra những gợi ý dựa trên thông tin hiện có. Bạn muốn tìm hiểu điều gì?',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    evidence: null
  };

  const [messages, setMessages] = useState([initialWelcome]);
  const messagesEndRef = useRef(null);

  const quickPrompts = [
    { text: 'Giải thích biểu đồ này', icon: '📊' },
    { text: 'Kỹ năng nào đang tăng nhu cầu?', icon: '📈' },
    { text: 'Có điểm bất thường nào không?', icon: '🔍' },
    { text: 'Tôi nên chú ý xu hướng nào?', icon: '🎯' }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen, isTyping]);

  const handleResetChat = () => {
    setConversationId('conv_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9));
    setMessages([
      {
        id: 'welcome_' + Date.now(),
        sender: 'ai',
        text: 'Xin chào! Tôi là AI Chatbox của Skill Lens Lab. Tôi có thể giúp bạn giải thích biểu đồ, phân tích xu hướng kỹ năng, so sánh dữ liệu và đưa ra những gợi ý dựa trên thông tin hiện có. Bạn muốn tìm hiểu điều gì?',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        evidence: null
      }
    ]);
    setIsTyping(false);
    setLastFailedMessage(null);
  };

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputText).trim();
    if (!query) return;

    const userMsg = {
      id: 'user_' + Date.now(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsTyping(true);

    const historyPayload = messages.slice(-5).map(m => ({
      role: m.sender === 'user' ? 'user' : 'assistant',
      content: m.text
    }));

    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const apiBase = import.meta.env?.VITE_API_URL || 'http://localhost:8000';
      const resp = await fetch(`${apiBase}/api/insights/chat`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: query,
          conversation_id: conversationId,
          context: {
            page: context.page || 'dashboard',
            industry: context.industry || 'IT',
            location: context.location || 'all',
            period: context.period || '2026_Q3',
            active_chart: context.active_chart || 'industryTrendLineChart'
          },
          history: historyPayload
        })
      });

      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);

      const data = await resp.json();
      const aiMsg = {
        id: 'ai_' + Date.now(),
        sender: 'ai',
        text: data.answer || 'Đã phân tích xong dữ liệu.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        evidence: data.evidence || []
      };

      setMessages(prev => [...prev, aiMsg]);
      setLastFailedMessage(null);
    } catch (err) {
      console.warn('Lỗi kết nối AI Insights API:', err);
      setLastFailedMessage(query);
      const errAiMsg = {
        id: 'err_' + Date.now(),
        sender: 'ai',
        text: '⚠️ Không thể kết nối tới máy chủ AI Insights (cổng 8000). Vui lòng thử lại sau giây lát.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errAiMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleToggleVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Trình duyệt của bạn chưa hỗ trợ nhận diện giọng nói (Web Speech API).');
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = 'vi-VN';
      recognition.interimResults = false;

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        setInputText(transcript);
        handleSendMessage(transcript);
        setIsListening(false);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      recognition.start();
    } catch (e) {
      console.error(e);
      setIsListening(false);
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 99999, fontFamily: "'Be Vietnam Pro', system-ui, sans-serif" }}>
      {/* 1. Nút mở nổi */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '9px',
            background: 'linear-gradient(135deg, #0fa39e, #0d8f8a)',
            color: '#ffffff',
            padding: '12px 20px',
            borderRadius: '50px',
            boxShadow: '0 10px 28px rgba(15,163,158,0.45)',
            cursor: 'pointer',
            fontSize: '13.5px',
            fontWeight: 800,
            border: '1.5px solid rgba(255,255,255,0.25)',
            transition: 'all 0.2s ease'
          }}
        >
          <div style={{ width: '24px', height: '24px', background: 'rgba(255,255,255,0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            💬
          </div>
          <span>AI Chatbox</span>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
        </button>
      )}

      {/* 2. Cửa sổ Chatbox mở rộng */}
      {isOpen && (
        <div
          style={{
            width: '390px',
            maxWidth: 'calc(100vw - 32px)',
            height: '570px',
            maxHeight: 'calc(100vh - 80px)',
            background: 'var(--bg2, #ffffff)',
            border: '1.5px solid rgba(15,163,158,0.35)',
            borderRadius: '22px',
            boxShadow: '0 20px 50px rgba(0,0,0,0.25)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          {/* Header */}
          <div style={{ background: 'linear-gradient(135deg, #0fa39e, #0d8f8a)', color: '#ffffff', padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '34px', height: '34px', background: 'rgba(255,255,255,0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '12px' }}>
                AI
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 800 }}>AI Chatbox</h3>
                <span style={{ fontSize: '10.5px', opacity: 0.9 }}>🟢 Trực tuyến · Trend Insights</span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button onClick={handleResetChat} style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff', padding: '4px 8px', borderRadius: '8px', fontSize: '11px', cursor: 'pointer' }}>+ Chat mới</button>
              <button onClick={() => setIsOpen(false)} style={{ background: 'rgba(255,255,255,0.2)', border: 'none', color: '#fff', width: '26px', height: '26px', borderRadius: '8px', cursor: 'pointer' }}>✕</button>
            </div>
          </div>

          {/* Messages Body */}
          <div style={{ flex: 1, padding: '14px', overflowY: 'auto', background: 'var(--bg, #f0f8f8)' }}>
            {messages.map(msg => (
              <div key={msg.id} style={{ display: 'flex', gap: '8px', marginBottom: '12px', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '82%', padding: '10px 14px', borderRadius: '16px', fontSize: '12.5px', background: msg.sender === 'user' ? 'linear-gradient(135deg, #0fa39e, #0d8f8a)' : '#ffffff', color: msg.sender === 'user' ? '#ffffff' : '#1e293b', whiteSpace: 'pre-line' }}>
                  {msg.text}
                  <div style={{ fontSize: '9.5px', opacity: 0.7, textAlign: 'right', marginTop: '4px' }}>{msg.time}</div>
                </div>
              </div>
            ))}
            {isTyping && <div style={{ fontSize: '11px', color: '#64748b', fontStyle: 'italic' }}>AI đang phân tích dữ liệu...</div>}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          {messages.length === 1 && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', padding: '8px 14px', background: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
              {quickPrompts.map((p, idx) => (
                <button key={idx} onClick={() => handleSendMessage(p.text)} style={{ padding: '8px', fontSize: '11px', fontWeight: 700, borderRadius: '8px', border: '1px solid #cbd5e1', background: '#ffffff', cursor: 'pointer', textAlign: 'left' }}>
                  {p.icon} {p.text}
                </button>
              ))}
            </div>
          )}

          {/* Input Bar */}
          <div style={{ padding: '10px 14px', display: 'flex', gap: '8px', background: '#ffffff', borderTop: '1px solid #e2e8f0' }}>
            <button onClick={handleToggleVoiceInput} style={{ width: '36px', height: '36px', borderRadius: '10px', background: isListening ? '#ef4444' : '#f1f5f9', border: 'none', color: isListening ? '#fff' : '#64748b', cursor: 'pointer' }}>🎤</button>
            <input
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
              placeholder="Hỏi về biểu đồ, xu hướng, kỹ năng..."
              style={{ flex: 1, padding: '8px 12px', borderRadius: '10px', border: '1px solid #cbd5e1', fontSize: '12px' }}
            />
            <button onClick={() => handleSendMessage()} style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #0fa39e, #0d8f8a)', border: 'none', color: '#fff', cursor: 'pointer' }}>➤</button>
          </div>
        </div>
      )}
    </div>
  );
}
