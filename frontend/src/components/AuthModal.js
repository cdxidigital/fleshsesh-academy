import React, { useState } from 'react';
import { X, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const AuthModal = ({ isOpen, onClose, mode, setMode }) => {
    const { login, register } = useAuth();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: ''
    });

    const handleChange = (e) => {
        setFormData(prev => ({
            ...prev,
            [e.target.name]: e.target.value
        }));
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            if (mode === 'login') {
                await login(formData.email, formData.password);
            } else {
                await register(formData.name, formData.email, formData.password);
            }
            onClose();
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const switchMode = () => {
        setMode(mode === 'login' ? 'register' : 'login');
        setError('');
        setFormData({ name: '', email: '', password: '' });
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay" data-testid="auth-modal">
            <div 
                className="absolute inset-0"
                onClick={onClose}
            />
            
            <div className="relative w-full max-w-md bg-[#140C16] border border-[#2E1E31] rounded-2xl p-8 shadow-2xl">
                <button 
                    onClick={onClose}
                    className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors"
                    data-testid="close-modal-btn"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="text-center mb-8">
                    <img 
                        src="https://customer-assets.emergentagent.com/job_body-training-lab/artifacts/p06q5ekn_Untitled%20design.png"
                        alt="Fleshsesh Academy"
                        className="h-16 mx-auto mb-4"
                    />
                    <h2 className="text-2xl font-bold text-white font-['Outfit']">
                        {mode === 'login' ? 'Welcome Back' : 'Join the Academy'}
                    </h2>
                    <p className="text-white/60 mt-2">
                        {mode === 'login' 
                            ? 'Continue your journey to intimacy mastery' 
                            : 'Start your transformation today'
                        }
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {mode === 'register' && (
                        <div>
                            <label className="block text-sm font-medium text-white/80 mb-2">
                                Your Name
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="Enter your name"
                                required
                                className="w-full bg-[#09050A] border border-[#2E1E31] rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent transition-all"
                                data-testid="name-input"
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                            Email Address
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="you@example.com"
                            required
                            className="w-full bg-[#09050A] border border-[#2E1E31] rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent transition-all"
                            data-testid="email-input"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                            Password
                        </label>
                        <div className="relative">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter your password"
                                required
                                minLength={6}
                                className="w-full bg-[#09050A] border border-[#2E1E31] rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent transition-all pr-12"
                                data-testid="password-input"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white transition-colors"
                            >
                                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                            </button>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-red-400 text-sm" data-testid="auth-error">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        data-testid="submit-auth-btn"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                {mode === 'login' ? 'Logging in...' : 'Creating account...'}
                            </>
                        ) : (
                            mode === 'login' ? 'Log In' : 'Create Account'
                        )}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-white/60 text-sm">
                        {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                        {' '}
                        <button 
                            onClick={switchMode}
                            className="text-[#E6005C] hover:text-[#FFB3D1] transition-colors font-medium"
                            data-testid="switch-auth-mode-btn"
                        >
                            {mode === 'login' ? 'Sign up' : 'Log in'}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default AuthModal;
