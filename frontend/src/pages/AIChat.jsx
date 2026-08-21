import { useState } from "react";
import api from "../services/api";

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      sender: "agent",
      text: "Hello! I am your PantryPilot AI Assistant. Ask me anything about your pantry, expiring food, recipes, or shopping list!",
      tools: [],
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const quickPrompts = [
    "What food in my pantry is expiring soon?",
    "What can I cook using ingredients that expire soon?",
    "Add 2 litres of Almond Milk to my pantry",
    "What is currently on my shopping list?",
  ];

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputMessage;
    if (!query.trim()) return;

    // Append user message
    const userMsg = { sender: "user", text: query };
    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputMessage("");

    setLoading(true);

    try {
      const response = await api.post("/agent/chat", { message: query });
      const agentMsg = {
        sender: "agent",
        text: response.data.response,
        tools: response.data.tools_used || [],
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      console.error("Agent chat failed", err);
      const errorMsg = {
        sender: "agent",
        text: "Sorry, I ran into an issue processing your request. Please try again.",
        tools: [],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "850px", margin: "0 auto" }}>
      <div className="page-header">
        <h1 className="page-title">🤖 PantryPilot AI Assistant</h1>
        <p className="page-subtitle">
          Autonomous AI Agent that inspects your pantry data, avoids food waste, and takes action.
        </p>
      </div>

      {/* Quick Suggestion Chips */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSendMessage(prompt)}
            data-magnetic
            className="chip"
            style={{ cursor: "pointer", fontSize: "0.8rem" }}
            disabled={loading}
          >
            ✨ {prompt}
          </button>
        ))}
      </div>

      {/* Chat Window */}
      <div className="card" style={{ padding: "1.5rem", minHeight: "450px", display: "flex", flexDirection: "column" }}>
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem", marginBottom: "1.5rem" }}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                maxWidth: "80%",
                padding: "0.85rem 1.15rem",
                borderRadius: "var(--radius-lg)",
                backgroundColor: msg.sender === "user" ? "var(--primary)" : "var(--bg-main)",
                color: msg.sender === "user" ? "white" : "var(--text-main)",
                border: msg.sender === "agent" ? "1px solid var(--border-color)" : "none",
                whiteSpace: "pre-wrap",
              }}
            >
              <div style={{ fontWeight: "700", fontSize: "0.8rem", marginBottom: "0.35rem", opacity: 0.8 }}>
                {msg.sender === "user" ? "You" : "🤖 PantryPilot Agent"}
              </div>

              <div>{msg.text}</div>

              {/* Tools Executed Badges */}
              {msg.tools && msg.tools.length > 0 && (
                <div style={{ marginTop: "0.65rem", paddingTop: "0.5rem", borderTop: "1px solid var(--border-color)", fontSize: "0.75rem", display: "flex", gap: "0.35rem", flexWrap: "wrap", alignItems: "center" }}>
                  <span style={{ color: "var(--text-muted)", fontWeight: "600" }}>🔧 Tools Used:</span>
                  {msg.tools.map((t, tIdx) => (
                    <span key={tIdx} className="badge badge-blue">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ alignSelf: "flex-start", padding: "0.85rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
              🤖 Agent is thinking & executing tools...
            </div>
          )}
        </div>

        {/* Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          style={{ display: "flex", gap: "0.75rem" }}
        >
          <input
            type="text"
            className="form-input"
            placeholder="Ask the AI agent anything (e.g. What can I cook with my expiring food?)..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !inputMessage.trim()} data-magnetic>
            Send 🚀
          </button>
        </form>
      </div>
    </div>
  );
};

export default AIChat;
