import React, { useState } from 'react';
import './ChatBot.css';

interface ChatMessage {
  type: 'user' | 'bot';
  text: string;
}

interface ChatBotProps {
  email: string;
}

const ChatBot: React.FC<ChatBotProps> = ({ email }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const newMessages: ChatMessage[] = [...messages, { type: 'user' as const, text: query }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/search_answer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, email })
      });

      const data = await response.json();

      if (response.ok) {
        setMessages([...newMessages, { type: 'bot', text: data.answer }]);
      } else {
        setMessages([...newMessages, { type: 'bot', text: 'No answer found.' }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages([...newMessages, { type: 'bot', text: 'Error occurred.' }]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.type}`}>{msg.text}</div>
        ))}
        {loading && <div className="chat-message bot">Typing...</div>}
      </div>
      <form onSubmit={handleQuerySubmit} className="chat-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your docs..."
        />
        <button type="submit">Ask</button>
      </form>
    </div>
  );
};

export default ChatBot;