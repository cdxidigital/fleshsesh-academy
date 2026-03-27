import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, User, LogOut, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';

const Header = () => {
    const { user, isAuthenticated, logout } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [authModalOpen, setAuthModalOpen] = useState(false);
    const [authMode, setAuthMode] = useState('login');
    const location = useLocation();

    const navLinks = [
        { name: 'Home', path: '/' },
        { name: 'Courses', path: '/courses' },
        { name: 'Instructors', path: '/#instructors' },
        { name: 'Pricing', path: '/#pricing' },
    ];

    const openAuthModal = (mode) => {
        setAuthMode(mode);
        setAuthModalOpen(true);
    };

    return (
        <>
            <header className="fixed top-0 left-0 right-0 z-50 glass-header" data-testid="main-header">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16 md:h-20">
                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-3" data-testid="logo-link">
                            <img 
                                src="https://customer-assets.emergentagent.com/job_body-training-lab/artifacts/e3yqun9k_Gemini_Generated_Image_ri5c9vri5c9vri5c-removebg-preview.png"
                                alt="Fleshsesh"
                                className="h-10 w-10 object-contain"
                            />
                            <div className="flex flex-col leading-none">
                                <span className="text-xl font-bold text-white font-['Outfit']">fleshsesh</span>
                                <span className="text-xs font-bold text-[#E6005C] tracking-widest uppercase">Academy</span>
                            </div>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden md:flex items-center gap-8">
                            {navLinks.map((link) => (
                                <Link
                                    key={link.name}
                                    to={link.path}
                                    className={`text-sm font-medium transition-colors hover:text-[#E6005C] ${
                                        location.pathname === link.path ? 'text-[#E6005C]' : 'text-white/80'
                                    }`}
                                    data-testid={`nav-${link.name.toLowerCase()}`}
                                >
                                    {link.name}
                                </Link>
                            ))}
                        </nav>

                        {/* Desktop Auth */}
                        <div className="hidden md:flex items-center gap-4">
                            {isAuthenticated ? (
                                <div className="flex items-center gap-4">
                                    <Link 
                                        to="/dashboard" 
                                        className="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
                                        data-testid="dashboard-link"
                                    >
                                        <div className="flex items-center gap-2 bg-[#140C16] px-3 py-1.5 rounded-full border border-[#2E1E31]">
                                            <Sparkles className="w-4 h-4 text-[#E6005C]" />
                                            <span className="text-sm font-medium">{user?.xp || 0} XP</span>
                                        </div>
                                    </Link>
                                    <Link 
                                        to="/dashboard"
                                        className="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
                                    >
                                        <User className="w-5 h-5" />
                                        <span className="text-sm font-medium">{user?.name}</span>
                                    </Link>
                                    <button 
                                        onClick={logout}
                                        className="text-white/60 hover:text-white transition-colors"
                                        data-testid="logout-btn"
                                    >
                                        <LogOut className="w-5 h-5" />
                                    </button>
                                </div>
                            ) : (
                                <>
                                    <button 
                                        onClick={() => openAuthModal('login')}
                                        className="text-sm font-medium text-white/80 hover:text-white transition-colors"
                                        data-testid="login-btn"
                                    >
                                        Log In
                                    </button>
                                    <button 
                                        onClick={() => openAuthModal('register')}
                                        className="btn-primary text-sm"
                                        data-testid="signup-btn"
                                    >
                                        Start Learning
                                    </button>
                                </>
                            )}
                        </div>

                        {/* Mobile Menu Button */}
                        <button 
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden text-white p-2"
                            data-testid="mobile-menu-btn"
                        >
                            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>

                    {/* Mobile Menu */}
                    {mobileMenuOpen && (
                        <div className="md:hidden py-4 border-t border-white/10">
                            <nav className="flex flex-col gap-4">
                                {navLinks.map((link) => (
                                    <Link
                                        key={link.name}
                                        to={link.path}
                                        onClick={() => setMobileMenuOpen(false)}
                                        className={`text-sm font-medium transition-colors hover:text-[#E6005C] ${
                                            location.pathname === link.path ? 'text-[#E6005C]' : 'text-white/80'
                                        }`}
                                    >
                                        {link.name}
                                    </Link>
                                ))}
                                {isAuthenticated ? (
                                    <>
                                        <Link 
                                            to="/dashboard" 
                                            onClick={() => setMobileMenuOpen(false)}
                                            className="text-sm font-medium text-white/80 hover:text-white"
                                        >
                                            Dashboard
                                        </Link>
                                        <button 
                                            onClick={() => { logout(); setMobileMenuOpen(false); }}
                                            className="text-sm font-medium text-white/60 hover:text-white text-left"
                                        >
                                            Log Out
                                        </button>
                                    </>
                                ) : (
                                    <div className="flex flex-col gap-2 pt-2">
                                        <button 
                                            onClick={() => { openAuthModal('login'); setMobileMenuOpen(false); }}
                                            className="btn-secondary text-sm"
                                        >
                                            Log In
                                        </button>
                                        <button 
                                            onClick={() => { openAuthModal('register'); setMobileMenuOpen(false); }}
                                            className="btn-primary text-sm"
                                        >
                                            Start Learning
                                        </button>
                                    </div>
                                )}
                            </nav>
                        </div>
                    )}
                </div>
            </header>

            <AuthModal 
                isOpen={authModalOpen} 
                onClose={() => setAuthModalOpen(false)}
                mode={authMode}
                setMode={setAuthMode}
            />
        </>
    );
};

export default Header;
