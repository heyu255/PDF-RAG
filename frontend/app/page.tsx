"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Send, Upload, Loader2, FileText, Database, Trash2 } from "lucide-react";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [resetting, setResetting] = useState(false);




  useEffect(() => {
    // 1. Fetch history from backend
    fetch("http://127.0.0.1:8000/history")
      .then((res) => res.json())
      .then((data) => {
        console.log("Loaded history:", data);
        // 2. Update the UI with the old messages
        setMessages(data); 
      })
      .catch((err) => console.error("Failed to load history:", err));
  }, []); // 👈 The empty [] means "run only once on startup"

  const fetchDocuments = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/documents");
      setDocuments(res.data.documents);
    } catch (error) {
      console.error("Failed to fetch docs", error);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("file", e.target.files[0]);

    try {
      await axios.post("http://127.0.0.1:8000/upload", formData);
      alert("PDF Uploaded Successfully!");
      fetchDocuments();
    } catch (error) {
      console.error(error);
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure? This will delete all uploaded documents and chat history.")) return;
    
    setResetting(true);
    try {
      await axios.delete("http://127.0.0.1:8000/reset");
      setDocuments([]);
      setMessages([]);
      alert("Knowledge base cleared!");
    } catch (error) {
      console.error("Reset failed", error);
      alert("Failed to reset database.");
    } finally {
      setResetting(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        question: input,
      });
      const aiMessage = { role: "ai", content: res.data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: "ai", content: "Error connecting to server." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans">
      
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r hidden md:flex flex-col">
        <div className="p-4 border-b flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-600" />
          <h2 className="font-bold text-gray-700">Knowledge Base</h2>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {documents.length === 0 ? (
            <p className="text-sm text-gray-400 text-center mt-10">No documents yet.</p>
          ) : (
            documents.map((doc, idx) => (
              <div key={idx} className="flex items-center gap-2 p-2 text-sm text-gray-600 bg-gray-50 rounded-md">
                <FileText className="w-4 h-4 text-gray-400" />
                <span className="truncate" title={doc}>{doc}</span>
              </div>
            ))
          )}
        </div>

        {/* Sidebar Actions - Removed border-t here */}
        <div className="p-4 space-y-2">
          <label className={`flex items-center justify-center gap-2 w-full py-2 px-4 rounded-lg cursor-pointer transition-colors ${uploading ? 'bg-gray-200' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}>
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            <span className="text-sm font-medium">{uploading ? "Uploading..." : "Upload PDF"}</span>
            <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
          </label>

          <button 
            onClick={handleReset} 
            disabled={resetting}
            className="flex items-center justify-center gap-2 w-full py-2 px-4 text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
          >
            {resetting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
            <span className="text-sm font-medium">Clear All</span>
          </button>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full">
        <header className="md:hidden p-4 bg-white border-b flex justify-between items-center">
          <h1 className="font-bold text-gray-800">PDF Genius</h1>
          <label className="p-2 text-blue-600">
            <Upload className="w-6 h-6" />
            <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" />
          </label>
        </header>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <FileText className="w-16 h-16 mb-4 opacity-20" />
              <p className="text-lg font-medium">Chat with your PDFs</p>
              <p className="text-sm">Upload a document to start.</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-white border text-gray-800 shadow-sm"}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
               <div className="bg-white border p-3 rounded-lg shadow-sm">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
               </div>
            </div>
          )}
        </div>

        <div className="p-4 bg-white border-t">
          <div className="flex gap-2 max-w-3xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask a question..."
              className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading} className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}