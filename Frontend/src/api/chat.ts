import { atom } from 'jotai';

// Example atom for chat history
export const chatHistoryAtom = atom<{role: string, content: string}[]>([]);

// Sends plain English or raw SQL messages to the conversational agent backend
export const sendMessage = async (text: string) => {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text }), 
  });
  
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  
  return response.json();
};
