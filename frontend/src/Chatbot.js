import React, { useState, useRef, useEffect } from "react";
import { Box, TextField, IconButton, Paper, Typography } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import dayjs from "dayjs";

const Chatbot = () => {
  const [chat, setChat] = useState([]);
  const [userMessage, setUserMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chat, loading]);

  const handleSend = async () => {
    if (!userMessage.trim()) return;

    const userEntry = {
      sender: "user",
      text: userMessage,
      time: dayjs().format("HH:mm"),
    };
    setChat((prev) => [...prev, userEntry]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8001/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });
      const data = await response.json();
      const aiEntry = {
        sender: "ai",
        text: data.answer,
        time: dayjs().format("HH:mm"),
      };
      setChat((prev) => [...prev, aiEntry]);
    } catch (error) {
      console.error("Error:", error);
      setChat((prev) => [
        ...prev,
        { sender: "ai", text: "❌ Error getting response", time: dayjs().format("HH:mm") },
      ]);
    }

    setUserMessage("");
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <Box
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "rgba(0,0,0,0.2)",
      }}
    >
      <Box
        sx={{
          width: { xs: "95%", sm: 600 },
          height: 600,
          display: "flex",
          flexDirection: "column",
          boxShadow: 4,
          borderRadius: 3,
          overflow: "hidden",
          background: "linear-gradient(to bottom right, #1976d2, #42a5f5)",
          color: "#fff",
          fontFamily: "Roboto, sans-serif",
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            fontWeight: "bold",
            fontSize: 18,
            backgroundColor: "#1565c0",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            textAlign: "center",
          }}
        >
          EcoCart Chatbot
        </Box>

        {/* Chat Messages */}
        <Box
          sx={{
            flex: 1,
            padding: 2,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            backgroundColor: "#e3f2fd",
            color: "#000",
          }}
        >
          {chat.map((msg, idx) => (
            <Paper
              key={idx}
              sx={{
                p: 1.5,
                m: 1,
                maxWidth: "80%",
                alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                backgroundColor: msg.sender === "user" ? "#1976d2" : "#fff",
                color: msg.sender === "user" ? "#fff" : "#000",
                borderRadius: 2,
                wordBreak: "break-word",
              }}
            >
              {/* Preserve line breaks and bullets */}
              <Typography 
                variant="body2" 
                sx={{ whiteSpace: "pre-line" }}
              >
                {msg.text}
              </Typography>
              <Typography
                variant="caption"
                sx={{ display: "block", textAlign: "right", mt: 0.5 }}
              >
                {msg.time}
              </Typography>
            </Paper>
          ))}
          {loading && <Typography sx={{ ml: 1 }}>🤖 AI is typing...</Typography>}
          <div ref={chatEndRef} />
        </Box>

        {/* Input Box */}
        <Box sx={{ display: "flex", p: 1, backgroundColor: "#f5f5f5" }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your question..."
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <IconButton color="primary" onClick={handleSend} sx={{ ml: 1 }}>
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default Chatbot;
