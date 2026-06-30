import { atom } from 'jotai';

// Example atom for chat history
export const chatHistoryAtom = atom<{role: string, content: string}[]>([]);

// Fixed function to match the backend expectation of {"sql": "..."}
export const sendMessage = async (sqlQuery: string) => {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // Changed key from 'message' to 'sql'
    body: JSON.stringify({ sql: sqlQuery }), 
  });
  
  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  
  return response.json();
};