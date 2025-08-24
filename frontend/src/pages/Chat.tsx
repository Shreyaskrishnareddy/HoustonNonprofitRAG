import React, { useState, useRef, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  Avatar,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { Send as SendIcon, Person, SmartToy } from '@mui/icons-material';

interface Source {
  name: string;
  ein: string;
  category: string;
  website: string;
  relevance_score: number;
  revenue: number;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  sources?: Source[];
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Welcome to Houston Impact Explorer! 🌟 I\'m your AI assistant specializing in Houston-area nonprofits. I can help you discover organizations by mission, impact area, financial data, or any specific causes you care about. What would you like to explore?',
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isUser: false,
        timestamp: new Date(),
        sources: data.sources || [],
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error while processing your request. Please try again.',
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const suggestedQuestions = [
    "What are Houston's largest nonprofits by impact?",
    "Show me organizations helping with food security",
    "Find nonprofits focused on education and youth",
    "Which organizations support healthcare access?",
    "Tell me about arts and culture nonprofits",
    "What nonprofits work on housing and homelessness?"
  ];

  const handleSuggestedQuestion = (question: string) => {
    setInputValue(question);
  };

  return (
    <Container maxWidth="md" sx={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <Typography variant="h3" gutterBottom sx={{ 
          background: 'linear-gradient(135deg, #007AFF 0%, #34C759 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 700,
        }}>
          Houston Impact Explorer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover and explore Houston's nonprofit ecosystem with AI
        </Typography>
      </Box>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Try asking:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {suggestedQuestions.map((question, index) => (
              <Button
                key={index}
                variant="outlined"
                size="small"
                onClick={() => handleSuggestedQuestion(question)}
                sx={{ fontSize: '0.75rem' }}
              >
                {question}
              </Button>
            ))}
          </Box>
        </Box>
      )}

      {/* Messages Container */}
      <Paper 
        sx={{ 
          flexGrow: 1, 
          overflow: 'auto', 
          p: 2, 
          mb: 2,
          maxHeight: 'calc(100vh - 350px)',
          minHeight: '400px'
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: 'flex',
              justifyContent: message.isUser ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'flex-start',
                flexDirection: message.isUser ? 'row-reverse' : 'row',
                maxWidth: '80%',
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.isUser ? 'primary.main' : 'secondary.main',
                  mx: 1,
                }}
              >
                {message.isUser ? <Person /> : <SmartToy />}
              </Avatar>
              <Paper
                sx={{
                  p: 2,
                  bgcolor: message.isUser ? 'primary.light' : 'grey.100',
                  color: message.isUser ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {message.text}
                </Typography>
                
                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                    <Typography variant="caption" sx={{ fontWeight: 'bold', display: 'block', mb: 1 }}>
                      Sources:
                    </Typography>
                    {message.sources.slice(0, 3).map((source, idx) => (
                      <Box key={idx} sx={{ mb: 1, fontSize: '0.8rem' }}>
                        <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                          {source.name}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', opacity: 0.8 }}>
                          {source.category} • Revenue: ${source.revenue?.toLocaleString() || 'N/A'}
                        </Typography>
                        {source.website && (
                          <Typography variant="caption" sx={{ display: 'block' }}>
                            <a href={source.website} target="_blank" rel="noopener noreferrer" 
                               style={{ color: 'inherit', opacity: 0.8 }}>
                              {source.website}
                            </a>
                          </Typography>
                        )}
                      </Box>
                    ))}
                  </Box>
                )}
                
                <Typography
                  variant="caption"
                  sx={{
                    display: 'block',
                    mt: 1,
                    opacity: 0.7,
                  }}
                >
                  {formatTime(message.timestamp)}
                </Typography>
              </Paper>
            </Box>
          </Box>
        ))}
        
        {/* Loading indicator */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ bgcolor: 'secondary.main', mx: 1 }}>
                <SmartToy />
              </Avatar>
              <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                <CircularProgress size={20} />
                <Typography variant="body2" sx={{ ml: 2, display: 'inline' }}>
                  Thinking...
                </Typography>
              </Paper>
            </Box>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={3}
          placeholder="Ask about nonprofits, causes, or impact areas in Houston..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <IconButton
          color="primary"
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
          sx={{ alignSelf: 'flex-end' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Container>
  );
};

export default Chat;