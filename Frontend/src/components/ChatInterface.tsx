import { useMutation } from '@tanstack/react-query';
import { useAtom } from 'jotai';
import { useState } from 'react';
import { chatHistoryAtom, sendMessage } from '../api/chat';

export const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useAtom(chatHistoryAtom);

  const mutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      setHistory([...history, { role: 'user', content: input }, { role: 'assistant', content: data.response }]);
      setInput('');
    },
  });

  return (
    <div>
      <div className="chat-window">
        {history.map((msg, i) => <p key={i}>{msg.role}: {msg.content}</p>)}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={() => mutation.mutate(input)}>Send</button>
    </div>
  );
};