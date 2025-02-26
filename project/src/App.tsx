import React, { useState } from 'react';
import { Send, Mail, Loader2 } from 'lucide-react';
import { toast, Toaster } from 'react-hot-toast';
import { processEmail, approveAction } from './api';
import type { EmailResponse } from './types';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [pendingApproval, setPendingApproval] = useState<EmailResponse | null>(null);
  const [messages, setMessages] = useState<Array<{ type: 'query' | 'response', content: string }>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      setMessages(prev => [...prev, { type: 'query', content: query }]);
      const response = await processEmail({ query });
      
      if (response.requiresApproval) {
        setPendingApproval(response);
        toast.success('Action requires your approval');
      } else {
        setMessages(prev => [...prev, { type: 'response', content: response.result || 'Process completed successfully' }]);
        toast.success('Process completed successfully');
      }
    } catch (error) {
      toast.error('An error occurred while processing your request');
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  const handleApproval = async (approved: boolean) => {
    if (!pendingApproval?.toolName || !pendingApproval?.args) return;

    try {
      if (approved) {
        const response = await approveAction({
          toolName: pendingApproval.toolName,
          args: pendingApproval.args
        });
        setMessages(prev => [...prev, { type: 'response', content: response.result || 'Action completed successfully' }]);
        toast.success('Action completed successfully');
      } else {
        setMessages(prev => [...prev, { type: 'response', content: 'Action cancelled' }]);
        toast.info('Action cancelled');
      }
    } catch (error) {
      toast.error('An error occurred while processing approval');
    } finally {
      setPendingApproval(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center gap-2 mb-6">
            <Mail className="w-6 h-6 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-800">Email Assistant</h1>
          </div>

          {/* Messages Container */}
          <div className="mb-6 space-y-4 max-h-[400px] overflow-y-auto">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === 'query' ? 'justify-start' : 'justify-end'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.type === 'query'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-blue-600 text-white'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                What would you like to do?
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your request here..."
              />
            </div>

            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Send Request
                </>
              )}
            </button>
          </form>
        </div>

        {/* Approval Dialog */}
        {pendingApproval && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full">
              <h2 className="text-xl font-semibold mb-4">Approval Required</h2>
              <div className="bg-gray-50 p-4 rounded-md mb-4">
                <pre className="whitespace-pre-wrap text-sm">
                  {JSON.stringify(pendingApproval.args, null, 2)}
                </pre>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={() => handleApproval(true)}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  Approve
                </button>
                <button
                  onClick={() => handleApproval(false)}
                  className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;