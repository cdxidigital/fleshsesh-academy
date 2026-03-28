import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
    Send, 
    ArrowLeft, 
    Sparkles, 
    User,
    MessageCircle,
    History,
    Trash2,
    Clock,
    BookOpen,
    Loader2
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FacultyChat = () => {
    const { instructorId } = useParams();
    const navigate = useNavigate();
    const { isAuthenticated, token, user, loading } = useAuth();
    const [instructor, setInstructor] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [sessions, setSessions] = useState([]);
    const [showHistory, setShowHistory] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        // Wait for auth to finish loading before checking authentication
        if (loading) {
            return;
        }
        
        if (!isAuthenticated) {
            toast.error('Please login to chat with faculty');
            navigate('/');
            return;
        }

        const fetchData = async () => {
            try {
                // Fetch instructor details
                const instructorRes = await axios.get(`${API_URL}/api/instructors/${instructorId}`);
                setInstructor(instructorRes.data);

                // Fetch user's chat sessions with this instructor
                const sessionsRes = await axios.get(`${API_URL}/api/chat/sessions`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const instructorSessions = sessionsRes.data.filter(
                    s => s.instructor_id === instructorId
                );
                setSessions(instructorSessions);

                // Add welcome message
                setMessages([{
                    role: 'assistant',
                    content: `Hello! I'm ${instructorRes.data.name}. ${getWelcomeMessage(instructorRes.data)}`,
                    timestamp: new Date().toISOString()
                }]);

            } catch (error) {
                console.error('Error fetching data:', error);
                toast.error('Failed to load instructor');
            }
        };

        fetchData();
    }, [instructorId, isAuthenticated, token, navigate, loading]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const getWelcomeMessage = (inst) => {
        const welcomes = {
            'dr-nova-vale': "I'm here to help you understand your body's incredible capacity for pleasure. What would you like to explore today?",
            'coach-mira-sol': "Ready to work through any shame or self-doubt you're carrying? Let's talk.",
            'prof-arden-moss': "Communication and consent are the foundations of meaningful connection. How can I help you build those skills?",
            'dr-elise-hart': "Let's explore the art of shared pleasure together. What questions do you have?",
            'dr-sera-quinn': "Identity and desire are beautifully complex. I'm here to help you navigate that journey.",
            'kai-voss': "Curious about power dynamics or kink? You're in the right place. Let's dive in.",
            'talia-rhine': "Digital intimacy and safety are my specialty. What's on your mind?",
            'prof-jun-hart': "Building a lifelong practice of intimacy mastery starts with the right questions. What's yours?"
        };
        return welcomes[inst.id] || "How can I assist you on your intimacy journey today?";
    };

    const loadSession = async (session) => {
        setSessionId(session.id);
        setMessages(session.messages.map(m => ({
            ...m,
            timestamp: m.timestamp
        })));
        setShowHistory(false);
    };

    const startNewChat = () => {
        setSessionId(null);
        setMessages([{
            role: 'assistant',
            content: `Hello! I'm ${instructor.name}. ${getWelcomeMessage(instructor)}`,
            timestamp: new Date().toISOString()
        }]);
        setShowHistory(false);
    };

    const deleteSession = async (e, sessionIdToDelete) => {
        e.stopPropagation();
        try {
            await axios.delete(`${API_URL}/api/chat/sessions/${sessionIdToDelete}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setSessions(sessions.filter(s => s.id !== sessionIdToDelete));
            if (sessionId === sessionIdToDelete) {
                startNewChat();
            }
            toast.success('Chat deleted');
        } catch (error) {
            toast.error('Failed to delete chat');
        }
    };

    const handleSend = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = inputValue.trim();
        setInputValue('');
        
        // Add user message to UI immediately
        setMessages(prev => [...prev, {
            role: 'user',
            content: userMessage,
            timestamp: new Date().toISOString()
        }]);

        setIsLoading(true);

        try {
            const response = await axios.post(
                `${API_URL}/api/chat/faculty`,
                {
                    message: userMessage,
                    instructor_id: instructorId,
                    session_id: sessionId
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Set session ID if new
            if (!sessionId) {
                setSessionId(response.data.session_id);
            }

            // Add assistant response
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: response.data.response,
                timestamp: new Date().toISOString()
            }]);

        } catch (error) {
            console.error('Chat error:', error);
            toast.error('Failed to send message. Please try again.');
            // Remove the user message on error
            setMessages(prev => prev.slice(0, -1));
            setInputValue(userMessage);
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    // Show loading while auth is being checked
    if (loading) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">
                    <Sparkles className="w-12 h-12 animate-spin" />
                </div>
            </div>
        );
    }

    if (!instructor) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">
                    <Sparkles className="w-12 h-12 animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#09050A] pt-16" data-testid="faculty-chat-page">
            {/* Header */}
            <div className="fixed top-16 left-0 right-0 z-40 bg-[#140C16]/95 backdrop-blur-md border-b border-[#2E1E31]">
                <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button 
                            onClick={() => navigate(-1)}
                            className="p-2 hover:bg-[#2E1E31] rounded-lg transition-colors"
                            data-testid="back-btn"
                        >
                            <ArrowLeft className="w-5 h-5 text-white/60" />
                        </button>
                        <div className="flex items-center gap-3">
                            <img 
                                src={instructor.image_url} 
                                alt={instructor.name}
                                className="w-10 h-10 rounded-full object-cover border-2 border-[#E6005C]"
                            />
                            <div>
                                <h1 className="text-white font-semibold font-['Outfit']">{instructor.name}</h1>
                                <p className="text-xs text-[#FFB3D1]">{instructor.title}</p>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <button 
                            onClick={() => setShowHistory(!showHistory)}
                            className={`p-2 rounded-lg transition-colors ${showHistory ? 'bg-[#E6005C] text-white' : 'hover:bg-[#2E1E31] text-white/60'}`}
                            data-testid="history-btn"
                        >
                            <History className="w-5 h-5" />
                        </button>
                        <button 
                            onClick={startNewChat}
                            className="p-2 hover:bg-[#2E1E31] rounded-lg transition-colors text-white/60"
                            data-testid="new-chat-btn"
                        >
                            <MessageCircle className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Chat History Sidebar */}
            {showHistory && (
                <div className="fixed top-[120px] right-4 z-50 w-80 bg-[#140C16] border border-[#2E1E31] rounded-xl shadow-xl max-h-96 overflow-y-auto">
                    <div className="p-4 border-b border-[#2E1E31]">
                        <h3 className="text-white font-semibold">Chat History</h3>
                    </div>
                    <div className="p-2">
                        {sessions.length === 0 ? (
                            <p className="text-white/40 text-sm text-center py-4">No previous chats</p>
                        ) : (
                            sessions.map(session => (
                                <div 
                                    key={session.id}
                                    onClick={() => loadSession(session)}
                                    className={`p-3 rounded-lg cursor-pointer group transition-colors ${
                                        sessionId === session.id ? 'bg-[#E6005C]/20' : 'hover:bg-[#2E1E31]'
                                    }`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-white text-sm truncate">
                                                {session.messages[0]?.content?.substring(0, 40)}...
                                            </p>
                                            <p className="text-white/40 text-xs flex items-center gap-1 mt-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(session.updated_at).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <button 
                                            onClick={(e) => deleteSession(e, session.id)}
                                            className="p-1 opacity-0 group-hover:opacity-100 hover:text-red-400 text-white/40 transition-all"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {/* Messages Container */}
            <div className="max-w-4xl mx-auto px-4 pt-24 pb-32">
                <div className="space-y-4">
                    {messages.map((msg, index) => (
                        <div 
                            key={index}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`flex items-start gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                {msg.role === 'assistant' ? (
                                    <img 
                                        src={instructor.image_url}
                                        alt={instructor.name}
                                        className="w-8 h-8 rounded-full object-cover border border-[#E6005C] shrink-0"
                                    />
                                ) : (
                                    <div className="w-8 h-8 rounded-full bg-[#E6005C] flex items-center justify-center shrink-0">
                                        <User className="w-4 h-4 text-white" />
                                    </div>
                                )}
                                <div className={`rounded-2xl px-4 py-3 ${
                                    msg.role === 'user' 
                                        ? 'bg-[#E6005C] text-white' 
                                        : 'bg-[#140C16] border border-[#2E1E31] text-white/90'
                                }`}>
                                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                    
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="flex items-start gap-3">
                                <img 
                                    src={instructor.image_url}
                                    alt={instructor.name}
                                    className="w-8 h-8 rounded-full object-cover border border-[#E6005C]"
                                />
                                <div className="rounded-2xl px-4 py-3 bg-[#140C16] border border-[#2E1E31]">
                                    <div className="flex items-center gap-2 text-[#FFB3D1]">
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        <span className="text-sm">{instructor.name} is typing...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input Area */}
            <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#09050A] via-[#09050A] to-transparent pt-8 pb-6">
                <div className="max-w-4xl mx-auto px-4">
                    <div className="glass-card rounded-2xl p-3 flex items-end gap-3">
                        <textarea
                            ref={inputRef}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder={`Ask ${instructor.name.split(' ')[0]} anything...`}
                            className="flex-1 bg-transparent border-none outline-none text-white placeholder-white/40 resize-none min-h-[44px] max-h-32"
                            rows={1}
                            disabled={isLoading}
                            data-testid="chat-input"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!inputValue.trim() || isLoading}
                            className={`p-3 rounded-xl transition-all ${
                                inputValue.trim() && !isLoading
                                    ? 'bg-[#E6005C] hover:bg-[#FF1A75] text-white' 
                                    : 'bg-[#2E1E31] text-white/30 cursor-not-allowed'
                            }`}
                            data-testid="send-btn"
                        >
                            <Send className="w-5 h-5" />
                        </button>
                    </div>
                    <p className="text-center text-white/30 text-xs mt-2">
                        AI responses are for educational purposes. Always consult professionals for medical advice.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default FacultyChat;
