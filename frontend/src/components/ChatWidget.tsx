import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import { sendChatMessage } from '../services/api';
import { ProductCard } from './ProductCard';
import './ChatWidget.css';

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(input, messages);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        products: response.products,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)} aria-label="Toggle chat">
        {isOpen ? '✕' : '💬'}
      </button>

      {isOpen && (
        <div className="chat-widget">
          <div className="chat-header">
            <span className="chat-header-icon">✦</span>
            <div>
              <h3>Mane Assistant</h3>
              <p>Ask about hair care products</p>
            </div>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-welcome">
                <p>Hi! I'm here to help you find the perfect hair care products.</p>
                <p className="chat-suggestions-label">Try asking:</p>
                <div className="chat-suggestions">
                  <button onClick={() => setInput('I have a dry scalp. What can help?')}>
                    Dry scalp solutions
                  </button>
                  <button onClick={() => setInput('Products to improve hair density')}>
                    Hair density
                  </button>
                  <button onClick={() => setInput('Best products for hair fall')}>
                    Hair fall
                  </button>
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.role}`}>
                <div className="message-content">{msg.content}</div>
                {msg.products && msg.products.length > 0 && (
                  <div className="message-products">
                    {msg.products.slice(0, 3).map(product => (
                      <ProductCard key={product.id} product={product} compact />
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="chat-message assistant">
                <div className="message-content typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-wrap">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about products..."
              disabled={loading}
            />
            <button onClick={handleSend} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
