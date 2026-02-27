import { useState, useEffect, useRef } from 'react';
import { Send, Loader2, Trash2 } from 'lucide-react';
import { Message } from '../model/chat';
import { ChatMessage } from './ChatMessage';
import { Toast } from './Toast';
import axios from 'axios';

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Carrega mensagens do localStorage ao iniciar
    const stored = localStorage.getItem('chat_messages');
    if (stored) {
      setMessages(JSON.parse(stored));
    }
  }, []);

  // Salva mensagens no localStorage sempre que mudam
  useEffect(() => {
    localStorage.setItem('chat_messages', JSON.stringify(messages));
  }, [messages]);

  // Removeu generateAIResponse, pois agora a resposta vem da API

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Adiciona mensagem do usuário
    const conversation_id = 'local';
    const userMsg: Message = {
      id: Date.now().toString(),
      conversation_id,
      content: userMessage,
      role: 'user',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await axios.post('http://127.0.0.1:5000/ask', {
        question: userMessage,
      });
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        conversation_id,
        content: response.data.response || 'Desculpe, não consegui obter uma resposta.',
        role: 'assistant',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          conversation_id,
          content: 'Erro ao conectar ao servidor. Tente novamente.',
          role: 'assistant',
          created_at: new Date().toISOString(),
        } as Message,
      ]);
    }
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    localStorage.removeItem('chat_messages');
    setMessages([]);
    setShowToast(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black relative overflow-hidden flex items-center justify-center p-4">
      <div className="geometric-bg"></div>

      {showToast && (
        <Toast
          message="Chat limpo com sucesso!"
          onClose={() => setShowToast(false)}
        />
      )}

      <div className="flex flex-col h-[90vh] w-full max-w-5xl bg-white rounded-3xl shadow-2xl overflow-hidden animate-scale-in relative z-10">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-5 shadow-lg flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Assistente de Vendedor</h1>
            <p className="text-blue-100 text-sm mt-1">
              Tire suas dúvidas em tempo real
            </p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors duration-200 text-sm font-medium"
              title="Limpar chat"
            >
              <Trash2 className="w-4 h-4" />
              Limpar
            </button>
          )}
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 bg-gradient-to-b from-gray-50 to-white">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center animate-fade-in">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Send className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-800 mb-2">
                Bem-vindo!
              </h2>
              <p className="text-gray-600 max-w-md">
                Faça sua primeira pergunta sobre convenções trabalhistas, contratos ou direitos trabalhistas.
              </p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-3 mb-4 animate-slide-in">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                </div>
                <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm ring-1 ring-gray-200/60">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

        <div className="border-t border-gray-200 bg-white px-6 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Digite sua pergunta sobre convenções trabalhistas..."
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                rows={1}
                style={{
                  minHeight: '48px',
                  maxHeight: '120px',
                }}
                disabled={isLoading}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
