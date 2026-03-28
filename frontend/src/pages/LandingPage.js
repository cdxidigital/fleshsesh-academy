import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
    ArrowRight, 
    Sparkles, 
    Heart, 
    Users, 
    Shield, 
    Flame,
    Check,
    Star,
    Play,
    BookOpen,
    Trophy,
    Zap,
    X,
    MessageCircle
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from '../components/AuthModal';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LandingPage = () => {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [instructors, setInstructors] = useState([]);
    const [authModalOpen, setAuthModalOpen] = useState(false);
    const [authMode, setAuthMode] = useState('register');
    const [selectedInstructor, setSelectedInstructor] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [coursesRes, instructorsRes] = await Promise.all([
                    axios.get(`${API_URL}/api/courses`),
                    axios.get(`${API_URL}/api/instructors`)
                ]);
                setCourses(coursesRes.data);
                setInstructors(instructorsRes.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
    }, []);

    const openAuthModal = (mode) => {
        setAuthMode(mode);
        setAuthModalOpen(true);
    };

    const pricingTiers = [
        {
            name: 'Free',
            price: '$0',
            period: 'forever',
            description: 'Start your journey with Level 1: Self-Intimacy',
            features: [
                'Full access to Level 1 (7 lessons)',
                '2 Hedonistic Labs',
                'Basic progress tracking',
                'Community forum access',
                'AI Advisor support'
            ],
            cta: 'Start Free',
            highlighted: false
        },
        {
            name: 'Premium',
            price: '$24.99',
            period: 'per month',
            description: 'Unlock the complete Intimacy Course',
            features: [
                'All 4 levels (28 lessons)',
                '14 Hedonistic Labs',
                'Full lesson content & exercises',
                'AI Faculty chat sessions',
                'Progress analytics & certificates',
                'Priority support',
                'Intimacy Mastery credential'
            ],
            cta: 'Go Premium',
            highlighted: true
        },
        {
            name: 'Elite',
            price: '$64.99',
            period: 'per month',
            description: 'For those committed to mastery',
            features: [
                'Everything in Premium',
                'Live group coaching calls',
                '1-on-1 AI coaching sessions',
                'A-Z Encyclopedia full access',
                'VIP community access',
                'Partner/couples account',
                'Early access to new content'
            ],
            cta: 'Join Elite',
            highlighted: false
        }
    ];

    return (
        <div className="min-h-screen bg-[#09050A]" data-testid="landing-page">
            {/* Hero Section */}
            <section className="relative min-h-screen flex items-center justify-center overflow-hidden" data-testid="hero-section">
                <div 
                    className="absolute inset-0 bg-cover bg-center opacity-30"
                    style={{ backgroundImage: "url('https://images.pexels.com/photos/1910229/pexels-photo-1910229.jpeg')" }}
                />
                <div className="absolute inset-0 bg-gradient-to-b from-[#09050A]/50 via-transparent to-[#09050A]" />
                <div className="absolute inset-0 hero-gradient" />
                
                <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16 text-center">
                    {/* Hero Logo */}
                    <div className="flex flex-col items-center mb-8">
                        <img 
                            src="https://customer-assets.emergentagent.com/job_body-training-lab/artifacts/3848ji5y_82bcdafd-9834-4c0f-b899-cc5eb2810f81-removebg-preview_transparent.png"
                            alt="Fleshsesh Academy"
                            className="h-32 md:h-44 object-contain"
                        />
                    </div>

                    <div className="inline-flex items-center gap-2 bg-[#E6005C]/10 border border-[#E6005C]/30 rounded-full px-4 py-2 mb-8">
                        <Sparkles className="w-4 h-4 text-[#E6005C]" />
                        <span className="text-sm text-[#FFB3D1]">AI-Powered Intimacy Education</span>
                    </div>
                    
                    <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 font-['Outfit'] tracking-tight">
                        Master the Art of
                        <span className="block text-gradient">Intimate Connection</span>
                    </h1>
                    
                    <p className="text-lg sm:text-xl text-white/70 max-w-2xl mx-auto mb-10">
                        28 transformative lessons across 4 levels. 8 expert AI faculty. Hedonistic Labs. 
                        Transform your relationship with intimacy, connection, and pleasure.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        {isAuthenticated ? (
                            <Link to="/dashboard" className="btn-primary inline-flex items-center gap-2" data-testid="hero-cta">
                                Go to Dashboard
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                        ) : (
                            <>
                                <button 
                                    onClick={() => openAuthModal('register')} 
                                    className="btn-primary inline-flex items-center gap-2"
                                    data-testid="hero-cta"
                                >
                                    Start Learning Free
                                    <ArrowRight className="w-5 h-5" />
                                </button>
                                <button 
                                    onClick={() => openAuthModal('login')}
                                    className="btn-secondary inline-flex items-center gap-2"
                                >
                                    <Play className="w-5 h-5" />
                                    Watch Demo
                                </button>
                            </>
                        )}
                    </div>
                    
                    {/* Stats */}
                    <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
                        {[
                            { value: '28', label: 'Lessons', icon: BookOpen },
                            { value: '14', label: 'Hedonistic Labs', icon: Play },
                            { value: '4', label: 'Mastery Levels', icon: Trophy },
                            { value: '8', label: 'AI Faculty', icon: Users }
                        ].map((stat, i) => (
                            <div key={i} className="text-center">
                                <div className="flex items-center justify-center gap-2 mb-2">
                                    <stat.icon className="w-5 h-5 text-[#E6005C]" />
                                    <span className="text-3xl font-bold text-white font-['Outfit']">{stat.value}</span>
                                </div>
                                <span className="text-white/60 text-sm">{stat.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-24 relative" data-testid="features-section">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                            Why Fleshsesh Academy?
                        </h2>
                        <p className="text-white/60 text-lg max-w-2xl mx-auto">
                            A revolutionary approach to intimacy education that combines AI technology with evidence-based learning
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {[
                            { 
                                icon: Sparkles, 
                                title: 'AI-Powered Learning', 
                                desc: 'Personalized curriculum that adapts to your pace and goals' 
                            },
                            { 
                                icon: Shield, 
                                title: 'Safe & Private', 
                                desc: 'Learn sensitive topics in a judgment-free, private environment' 
                            },
                            { 
                                icon: Heart, 
                                title: 'Evidence-Based', 
                                desc: 'Content grounded in psychology, neuroscience, and relationship research' 
                            },
                            { 
                                icon: Flame, 
                                title: 'Practical Skills', 
                                desc: 'Real scenarios and simulations you can apply immediately' 
                            }
                        ].map((feature, i) => (
                            <div 
                                key={i} 
                                className="glass-card rounded-2xl p-6 card-hover"
                                data-testid={`feature-card-${i}`}
                            >
                                <div className="w-12 h-12 rounded-xl bg-[#E6005C]/10 flex items-center justify-center mb-4">
                                    <feature.icon className="w-6 h-6 text-[#E6005C]" />
                                </div>
                                <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">{feature.title}</h3>
                                <p className="text-white/60 text-sm">{feature.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Courses Preview Section */}
            <section className="py-24 bg-[#0d080e]" data-testid="courses-section">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                            Your Journey to Mastery
                        </h2>
                        <p className="text-white/60 text-lg max-w-2xl mx-auto">
                            4 comprehensive levels covering every aspect of self-intimacy, connection, and mastery
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {courses.slice(0, 6).map((course, i) => (
                            <div 
                                key={course.id}
                                className="course-card glass-card rounded-2xl overflow-hidden card-hover"
                                data-testid={`course-card-${course.id}`}
                            >
                                <div className="relative h-48 overflow-hidden">
                                    <img 
                                        src={course.image_url} 
                                        alt={course.title}
                                        className="course-image w-full h-full object-cover"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-[#140C16] to-transparent" />
                                    <div className="absolute top-4 left-4 bg-[#E6005C] text-white text-xs font-bold px-3 py-1 rounded-full">
                                        Level {course.level}
                                    </div>
                                </div>
                                <div className="p-6">
                                    <h3 className="text-lg font-semibold text-white mb-2 font-['Outfit']">
                                        {course.title}
                                    </h3>
                                    <p className="text-white/60 text-sm mb-4 line-clamp-2">
                                        {course.description}
                                    </p>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-white/40">{course.lessons} lessons</span>
                                        <span className="text-[#FFB3D1]">{course.instructor}</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                    
                    <div className="text-center mt-12">
                        <Link 
                            to="/courses" 
                            className="btn-secondary inline-flex items-center gap-2"
                            data-testid="view-all-courses-btn"
                        >
                            View All 4 Levels
                            <ArrowRight className="w-5 h-5" />
                        </Link>
                    </div>
                </div>
            </section>

            {/* Instructors Section */}
            <section id="instructors" className="py-24" data-testid="instructors-section">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                            Meet Your AI Faculty
                        </h2>
                        <p className="text-white/60 text-lg max-w-2xl mx-auto">
                            8 expert AI personalities designed to guide you through every aspect of intimacy education—each with unique specialties, personalities, and teaching styles
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {instructors.map((instructor) => (
                            <div 
                                key={instructor.id}
                                className="instructor-card glass-card rounded-2xl overflow-hidden card-hover group cursor-pointer"
                                data-testid={`instructor-card-${instructor.id}`}
                                onClick={() => setSelectedInstructor(instructor)}
                            >
                                <div className="relative h-64 overflow-hidden">
                                    <img 
                                        src={instructor.image_url} 
                                        alt={instructor.name}
                                        className="w-full h-full object-cover"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-[#09050A] via-[#09050A]/50 to-transparent z-10" />
                                    <div className="absolute bottom-0 left-0 right-0 p-5 z-20">
                                        <h3 className="text-lg font-bold text-white mb-1 font-['Outfit']">
                                            {instructor.name}
                                        </h3>
                                        <p className="text-[#E6005C] text-xs font-medium mb-2">
                                            {instructor.title}
                                        </p>
                                        <p className="text-white/60 text-xs line-clamp-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                            {instructor.specialty}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Instructor Detail Modal */}
            {selectedInstructor && (
                <div 
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay"
                    onClick={() => setSelectedInstructor(null)}
                >
                    <div 
                        className="relative w-full max-w-2xl bg-[#140C16] border border-[#2E1E31] rounded-2xl overflow-hidden shadow-2xl"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="relative h-48 overflow-hidden">
                            <img 
                                src={selectedInstructor.image_url} 
                                alt={selectedInstructor.name}
                                className="w-full h-full object-cover"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-[#140C16] to-transparent" />
                            <button 
                                onClick={() => setSelectedInstructor(null)}
                                className="absolute top-4 right-4 text-white/60 hover:text-white bg-black/50 rounded-full p-2 transition-colors"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        
                        <div className="p-6 -mt-12 relative z-10">
                            <h3 className="text-2xl font-bold text-white font-['Outfit'] mb-1">
                                {selectedInstructor.name}
                            </h3>
                            <p className="text-[#E6005C] font-medium mb-4">
                                {selectedInstructor.title}
                            </p>
                            
                            <div className="space-y-4">
                                <div>
                                    <h4 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">Specialty</h4>
                                    <p className="text-white/70 text-sm">{selectedInstructor.specialty}</p>
                                </div>
                                
                                <div>
                                    <h4 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">About</h4>
                                    <p className="text-white/70 text-sm">{selectedInstructor.description}</p>
                                </div>
                                
                                {selectedInstructor.personality && (
                                    <div>
                                        <h4 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">Personality</h4>
                                        <p className="text-white/70 text-sm">{selectedInstructor.personality}</p>
                                    </div>
                                )}
                                
                                {selectedInstructor.teaching_style && (
                                    <div>
                                        <h4 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">Teaching Style</h4>
                                        <p className="text-white/70 text-sm">{selectedInstructor.teaching_style}</p>
                                    </div>
                                )}
                                
                                {/* Chat with Faculty Button */}
                                <button
                                    onClick={() => {
                                        if (!isAuthenticated) {
                                            toast.error('Please login to chat with faculty');
                                            setSelectedInstructor(null);
                                            setAuthMode('login');
                                            setAuthModalOpen(true);
                                        } else {
                                            navigate(`/chat/${selectedInstructor.id}`);
                                        }
                                    }}
                                    className="w-full btn-primary flex items-center justify-center gap-2 mt-4"
                                    data-testid={`chat-with-${selectedInstructor.id}`}
                                >
                                    <MessageCircle className="w-5 h-5" />
                                    Chat Now
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Pricing Section */}
            <section id="pricing" className="py-24 bg-[#0d080e]" data-testid="pricing-section">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                            Choose Your Path
                        </h2>
                        <p className="text-white/60 text-lg max-w-2xl mx-auto">
                            Flexible plans designed to meet you where you are in your journey
                        </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {pricingTiers.map((tier, i) => (
                            <div 
                                key={tier.name}
                                className={`relative rounded-2xl p-8 ${
                                    tier.highlighted 
                                        ? 'pricing-highlight bg-[#140C16] border-2 border-[#E6005C]' 
                                        : 'glass-card'
                                }`}
                                data-testid={`pricing-tier-${tier.name.toLowerCase()}`}
                            >
                                {tier.highlighted && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[#E6005C] text-white text-xs font-bold px-4 py-1 rounded-full">
                                        Most Popular
                                    </div>
                                )}
                                
                                <h3 className="text-xl font-bold text-white mb-2 font-['Outfit']">{tier.name}</h3>
                                <div className="flex items-baseline gap-1 mb-2">
                                    <span className="text-4xl font-bold text-white font-['Outfit']">{tier.price}</span>
                                    <span className="text-white/60 text-sm">/{tier.period}</span>
                                </div>
                                <p className="text-white/60 text-sm mb-6">{tier.description}</p>
                                
                                <ul className="space-y-3 mb-8">
                                    {tier.features.map((feature, j) => (
                                        <li key={j} className="flex items-start gap-3">
                                            <Check className="w-5 h-5 text-[#E6005C] shrink-0 mt-0.5" />
                                            <span className="text-white/80 text-sm">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                                
                                <button 
                                    onClick={() => openAuthModal('register')}
                                    className={`w-full ${tier.highlighted ? 'btn-primary' : 'btn-secondary'}`}
                                    data-testid={`pricing-cta-${tier.name.toLowerCase()}`}
                                >
                                    {tier.cta}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24" data-testid="cta-section">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="glass-card rounded-3xl p-12 relative overflow-hidden">
                        <div className="absolute inset-0 hero-gradient opacity-50" />
                        <div className="relative z-10">
                            <Zap className="w-12 h-12 text-[#E6005C] mx-auto mb-6" />
                            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4 font-['Outfit']">
                                Ready to Transform Your Intimate Life?
                            </h2>
                            <p className="text-white/60 text-lg mb-8 max-w-2xl mx-auto">
                                Join thousands of learners who have already started their journey to deeper connections and more fulfilling relationships.
                            </p>
                            <button 
                                onClick={() => openAuthModal('register')}
                                className="btn-primary inline-flex items-center gap-2 text-lg"
                                data-testid="final-cta"
                            >
                                Begin Your Journey
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <AuthModal 
                isOpen={authModalOpen} 
                onClose={() => setAuthModalOpen(false)}
                mode={authMode}
                setMode={setAuthMode}
            />
        </div>
    );
};

export default LandingPage;
