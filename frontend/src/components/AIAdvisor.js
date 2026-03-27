import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Sparkles, User, Minimize2, Maximize2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AIAdvisor = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState([
        {
            role: 'advisor',
            content: "Hey there! I'm Sage, your personal guide to Fleshsesh Academy. Whether you're curious about a course, need help navigating the platform, or just want someone to chat with about your learning journey — I'm here for you! What can I help you with today?",
            timestamp: new Date()
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const quickReplies = [
        "What courses should I start with?",
        "Tell me about the AI Faculty",
        "How does the XP system work?",
        "What's included in Premium?"
    ];

    const getAdvisorResponse = async (userMessage) => {
        const lowerMessage = userMessage.toLowerCase();
        
        // Course recommendations
        if (lowerMessage.includes('course') || lowerMessage.includes('start') || lowerMessage.includes('begin') || lowerMessage.includes('recommend')) {
            return "Great question! I'd recommend starting with **Level 1: Foundations of Presence**. It covers self-awareness, body language, and emotional literacy — essential skills for everything else! Once you've built that foundation, you can explore Level 2 (Attraction) or Level 3 (Connection) based on your goals. Want me to tell you more about any specific level?";
        }
        
        // Faculty questions
        if (lowerMessage.includes('faculty') || lowerMessage.includes('instructor') || lowerMessage.includes('teacher')) {
            return "Our AI Faculty is incredible! We have 8 specialist instructors:\n\n• **Marcus Vale** - Attraction & confidence\n• **Nyx** - Power dynamics & kink\n• **Aria Wren** - Emotional intelligence\n• **Luca Amore** - Physical intimacy\n• **Dr. Evelyn Hart** - Relationship therapy\n• **Kai Storm** - Digital dating\n• **Maya Oasis** - Tantric practices\n• **Rex Sterling** - Masculinity coaching\n\nEach has their own personality and teaching style. Click on any instructor card to learn more about them!";
        }
        
        // XP and gamification
        if (lowerMessage.includes('xp') || lowerMessage.includes('level') || lowerMessage.includes('progress') || lowerMessage.includes('gamif')) {
            return "The XP system is designed to keep you motivated! Here's how it works:\n\n• **Complete lessons** = Earn 25 XP each\n• **Finish modules** = Bonus XP rewards\n• **Daily streaks** = Multiplier bonuses\n• **Level up** every 500 XP\n\nYou also earn **Desire Tokens** that can unlock special content and boosters. Check your Dashboard to see your current progress!";
        }
        
        // Pricing and premium
        if (lowerMessage.includes('premium') || lowerMessage.includes('price') || lowerMessage.includes('cost') || lowerMessage.includes('subscription') || lowerMessage.includes('pay')) {
            return "We have three tiers designed for different needs:\n\n**Free** ($0) - Level 1 access, basic features\n**Premium** ($24.99/mo) - All 1000 lessons, unlimited AI simulations, personalized learning\n**Elite** ($64.99/mo) - Everything + live coaching, 1-on-1 AI sessions, VIP community\n\nThe Free tier is a great way to explore before committing. Most learners find Premium gives them everything they need!";
        }
        
        // Privacy and safety
        if (lowerMessage.includes('privacy') || lowerMessage.includes('safe') || lowerMessage.includes('confidential') || lowerMessage.includes('secret')) {
            return "Your privacy is sacred to us! All your progress, notes, and interactions are completely private. We use encryption for all data, never share your information with third parties, and you can delete your account and all data at any time. Learning about intimacy requires trust, and we take that seriously.";
        }
        
        // Greeting
        if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
            return "Hey! So glad you reached out. I'm Sage, always here to help! What's on your mind? Whether it's choosing a course, understanding features, or just exploring what's possible — I've got you covered.";
        }
        
        // Thanks
        if (lowerMessage.includes('thank')) {
            return "You're so welcome! That's what I'm here for. Remember, there's no question too small or too awkward — this is a judgment-free zone. Anything else you'd like to know?";
        }
        
        // Default response
        return "That's a great question! While I'm here to help with platform navigation, course recommendations, and general guidance, I might not have the specific answer you're looking for. Here's what I can help with:\n\n• Course recommendations\n• Understanding features\n• Subscription questions\n• Learning path guidance\n\nWant me to help with any of these, or shall I point you to one of our AI Faculty members who might know more?";
    };

    const handleSend = async () => {
        if (!inputValue.trim()) return;

        const userMessage = {
            role: 'user',
            content: inputValue,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsTyping(true);

        // Simulate typing delay
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));

        const response = await getAdvisorResponse(inputValue);
        
        setMessages(prev => [...prev, {
            role: 'advisor',
            content: response,
            timestamp: new Date()
        }]);
        setIsTyping(false);
    };

    const handleQuickReply = (reply) => {
        setInputValue(reply);
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 bg-[#E6005C] hover:bg-[#E6005C]/90 text-white p-4 rounded-full shadow-lg shadow-[#E6005C]/30 transition-all duration-300 hover:scale-110 group"
                data-testid="open-advisor-btn"
            >
                <MessageCircle className="w-6 h-6" />
                <span className="absolute -top-2 -right-2 w-5 h-5 bg-[#FFB3D1] rounded-full flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-[#09050A]" />
                </span>
                <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-[#140C16] text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity border border-[#2E1E31]">
                    Chat with Sage
                </span>
            </button>
        );
    }

    return (
        <div 
            className={`fixed z-50 bg-[#140C16] border border-[#2E1E31] rounded-2xl shadow-2xl transition-all duration-300 ${
                isMinimized 
                    ? 'bottom-6 right-6 w-72' 
                    : 'bottom-6 right-6 w-96 h-[600px] max-h-[80vh]'
            }`}
            data-testid="advisor-chat"
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[#2E1E31]">
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#E6005C] to-[#FFB3D1] flex items-center justify-center">
                            <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-[#140C16]"></span>
                    </div>
                    <div>
                        <h3 className="text-white font-semibold font-['Outfit']">Sage</h3>
                        <p className="text-[#E6005C] text-xs">Your Academy Advisor</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button 
                        onClick={() => setIsMinimized(!isMinimized)}
                        className="text-white/60 hover:text-white transition-colors p-1"
                    >
                        {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
                    </button>
                    <button 
                        onClick={() => setIsOpen(false)}
                        className="text-white/60 hover:text-white transition-colors p-1"
                        data-testid="close-advisor-btn"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {!isMinimized && (
                <>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 h-[calc(100%-180px)]">
                        {messages.map((msg, i) => (
                            <div 
                                key={i} 
                                className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                                    msg.role === 'advisor' 
                                        ? 'bg-gradient-to-br from-[#E6005C] to-[#FFB3D1]' 
                                        : 'bg-[#2E1E31]'
                                }`}>
                                    {msg.role === 'advisor' 
                                        ? <Sparkles className="w-4 h-4 text-white" />
                                        : <User className="w-4 h-4 text-white/60" />
                                    }
                                </div>
                                <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                                    msg.role === 'advisor' 
                                        ? 'bg-[#09050A] border border-[#2E1E31]' 
                                        : 'bg-[#E6005C]'
                                }`}>
                                    <p className="text-white/90 text-sm whitespace-pre-line"
                                       dangerouslySetInnerHTML={{ 
                                           __html: msg.content
                                               .replace(/\*\*(.*?)\*\*/g, '<strong class="text-[#FFB3D1]">$1</strong>')
                                               .replace(/\n/g, '<br/>')
                                       }}
                                    />
                                </div>
                            </div>
                        ))}
                        
                        {isTyping && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#E6005C] to-[#FFB3D1] flex items-center justify-center">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                                <div className="bg-[#09050A] border border-[#2E1E31] rounded-2xl px-4 py-3">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-[#E6005C] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                        <span className="w-2 h-2 bg-[#E6005C] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                        <span className="w-2 h-2 bg-[#E6005C] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Quick Replies */}
                    {messages.length <= 2 && (
                        <div className="px-4 pb-2">
                            <div className="flex flex-wrap gap-2">
                                {quickReplies.map((reply, i) => (
                                    <button
                                        key={i}
                                        onClick={() => handleQuickReply(reply)}
                                        className="text-xs bg-[#09050A] border border-[#2E1E31] text-white/70 hover:text-white hover:border-[#E6005C] px-3 py-1.5 rounded-full transition-colors"
                                    >
                                        {reply}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input */}
                    <div className="p-4 border-t border-[#2E1E31]">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Ask me anything..."
                                className="flex-1 bg-[#09050A] border border-[#2E1E31] rounded-full px-4 py-2 text-white text-sm placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent"
                                data-testid="advisor-input"
                            />
                            <button
                                onClick={handleSend}
                                disabled={!inputValue.trim()}
                                className="bg-[#E6005C] hover:bg-[#E6005C]/90 text-white p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                data-testid="advisor-send-btn"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default AIAdvisor;
