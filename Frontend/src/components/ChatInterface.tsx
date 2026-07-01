import { useMutation } from '@tanstack/react-query';
import { useAtom } from 'jotai';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { chatHistoryAtom, sendMessage } from '../api/chat';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useAtom(chatHistoryAtom);

  const mutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      setHistory([
        ...history, 
        { role: 'user', content: input }, 
        { role: 'assistant', content: data.response }
      ]);
      setInput('');
    },
  });

  return (
    <div className="chat-container">
      <div className="chat-window" style={{ padding: '20px', border: '1px solid #ccc', marginBottom: '10px' }}>
        {history.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`} style={{ marginBottom: '10px' }}>
            <strong>{msg.role === 'user' ? 'You' : 'Agent'}:</strong> 
            <div style={{ marginLeft: '10px' }}>
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
        {mutation.isPending && (
          <p>
            <em>Agent is thinking...</em>
          </p>
        )}
      </div>
      
      <div className="input-area">
        <input 
          value={input} 
          onChange={(e) => setInput(e.target.value)} 
          placeholder="Ask about your retail data..."
          disabled={mutation.isPending}
          style={{ width: '70%', padding: '8px' }}
        />
        <button 
          onClick={() => mutation.mutate(input)} 
          disabled={mutation.isPending}
          style={{ marginLeft: '10px', padding: '8px' }}
        >
          {mutation.isPending ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
};