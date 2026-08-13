import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thought_process?: string;
  tables_used?: string[];
}

export interface ChatSession {
  id: string;
  title: string;
  updatedAt: number;
  messages: ChatMessage[];
}

interface ChatStore {
  sessions: ChatSession[];
  currentSessionId: string | null;
  isLoading: boolean;
  addMessage: (msg: ChatMessage) => void;
  setLoading: (loading: boolean) => void;
  createNewSession: () => void;
  loadSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      sessions: [],
      currentSessionId: null,
      isLoading: false,
      
      addMessage: (msg) => set((state) => {
        let sessionId = state.currentSessionId;
        let sessions = [...state.sessions];
        
        if (!sessionId) {
          sessionId = Date.now().toString();
          sessions.unshift({
            id: sessionId,
            title: msg.role === 'user' ? msg.content.slice(0, 40) + (msg.content.length > 40 ? '...' : '') : 'New Chat',
            updatedAt: Date.now(),
            messages: []
          });
        }
        
        const sessionIndex = sessions.findIndex(s => s.id === sessionId);
        if (sessionIndex >= 0) {
          const updatedSession = {
            ...sessions[sessionIndex],
            updatedAt: Date.now(),
            messages: [...sessions[sessionIndex].messages, msg]
          };
          sessions.splice(sessionIndex, 1);
          sessions.unshift(updatedSession);
        }
        
        return { sessions, currentSessionId: sessionId };
      }),
      
      setLoading: (loading) => set({ isLoading: loading }),
      
      createNewSession: () => set({ currentSessionId: null }),
      
      loadSession: (sessionId) => set({ currentSessionId: sessionId }),
      
      deleteSession: (sessionId) => set((state) => ({
        sessions: state.sessions.filter(s => s.id !== sessionId),
        currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId
      })),
      
      clearMessages: () => set((state) => {
        if (!state.currentSessionId) return state;
        const sessions = state.sessions.map(s => 
          s.id === state.currentSessionId ? { ...s, messages: [], updatedAt: Date.now() } : s
        );
        return { sessions };
      }),
    }),
    {
      name: 'finagent-chat-storage',
    }
  )
);
