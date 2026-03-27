import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
    Sparkles, 
    Trophy, 
    BookOpen, 
    Clock, 
    ArrowRight,
    Flame,
    Target,
    TrendingUp,
    Star
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Progress } from '../components/ui/progress';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Dashboard = () => {
    const { user, token, isAuthenticated, updateUser } = useAuth();
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/');
            return;
        }

        const fetchData = async () => {
            try {
                const [coursesRes, userRes] = await Promise.all([
                    axios.get(`${API_URL}/api/courses`),
                    axios.get(`${API_URL}/api/auth/me`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                ]);
                setCourses(coursesRes.data);
                updateUser(userRes.data);
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [isAuthenticated, token, navigate, updateUser]);

    if (loading) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">
                    <Sparkles className="w-12 h-12 animate-spin" />
                </div>
            </div>
        );
    }

    const completedCount = user?.completed_lessons?.length || 0;
    const totalLessons = 1000;
    const progressPercent = Math.round((completedCount / totalLessons) * 100);
    const xpToNextLevel = ((user?.level || 1) * 500) - (user?.xp || 0);

    const stats = [
        { 
            icon: Sparkles, 
            value: user?.xp || 0, 
            label: 'Total XP',
            color: 'text-[#E6005C]'
        },
        { 
            icon: Trophy, 
            value: `Level ${user?.level || 1}`, 
            label: 'Current Level',
            color: 'text-[#FFB3D1]'
        },
        { 
            icon: BookOpen, 
            value: completedCount, 
            label: 'Lessons Completed',
            color: 'text-[#E6005C]'
        },
        { 
            icon: Flame, 
            value: user?.tokens || 0, 
            label: 'Desire Tokens',
            color: 'text-[#FFB3D1]'
        }
    ];

    return (
        <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="dashboard-page">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Welcome Header */}
                <div className="mb-8">
                    <h1 className="text-3xl sm:text-4xl font-bold text-white font-['Outfit']">
                        Welcome back, <span className="text-gradient">{user?.name}</span>
                    </h1>
                    <p className="text-white/60 mt-2">Continue your journey to intimacy mastery</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                    {stats.map((stat, i) => (
                        <div 
                            key={i} 
                            className="stats-card rounded-2xl p-6 transition-all duration-300"
                            data-testid={`stat-card-${i}`}
                        >
                            <stat.icon className={`w-6 h-6 ${stat.color} mb-3`} />
                            <p className="text-2xl font-bold text-white font-['Outfit']">{stat.value}</p>
                            <p className="text-white/60 text-sm">{stat.label}</p>
                        </div>
                    ))}
                </div>

                {/* Progress Section */}
                <div className="glass-card rounded-2xl p-6 mb-8" data-testid="progress-section">
                    <div className="flex items-center justify-between mb-4">
                        <div>
                            <h2 className="text-xl font-semibold text-white font-['Outfit']">Your Progress</h2>
                            <p className="text-white/60 text-sm">{completedCount} of {totalLessons} lessons completed</p>
                        </div>
                        <div className="text-right">
                            <p className="text-[#E6005C] font-semibold">{xpToNextLevel} XP to Level {(user?.level || 1) + 1}</p>
                        </div>
                    </div>
                    <Progress value={progressPercent} className="h-3 bg-[#2E1E31]" />
                    <div className="flex justify-between mt-2 text-sm text-white/40">
                        <span>Level {user?.level || 1}</span>
                        <span>{progressPercent}%</span>
                        <span>Level {(user?.level || 1) + 1}</span>
                    </div>
                </div>

                {/* Current Level & Continue Learning */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    {/* Continue Learning */}
                    <div className="lg:col-span-2 glass-card rounded-2xl p-6" data-testid="continue-learning">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-semibold text-white font-['Outfit']">Continue Learning</h2>
                            <Link 
                                to="/courses" 
                                className="text-[#E6005C] hover:text-[#FFB3D1] transition-colors text-sm flex items-center gap-1"
                            >
                                View All <ArrowRight className="w-4 h-4" />
                            </Link>
                        </div>
                        
                        <div className="space-y-4">
                            {courses.slice(0, 3).map((course) => (
                                <Link 
                                    key={course.id}
                                    to={`/courses/${course.id}`}
                                    className="flex items-center gap-4 p-4 bg-[#09050A] rounded-xl hover:bg-[#1a1020] transition-colors group"
                                    data-testid={`continue-course-${course.id}`}
                                >
                                    <div className="w-16 h-16 rounded-lg overflow-hidden shrink-0">
                                        <img 
                                            src={course.image_url} 
                                            alt={course.title}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs font-semibold text-[#E6005C] bg-[#E6005C]/10 px-2 py-0.5 rounded">
                                                Level {course.level}
                                            </span>
                                        </div>
                                        <h3 className="text-white font-medium truncate">{course.title}</h3>
                                        <p className="text-white/40 text-sm">{course.lessons} lessons</p>
                                    </div>
                                    <ArrowRight className="w-5 h-5 text-white/40 group-hover:text-[#E6005C] transition-colors" />
                                </Link>
                            ))}
                        </div>
                    </div>

                    {/* Subscription Status */}
                    <div className="glass-card rounded-2xl p-6" data-testid="subscription-status">
                        <h2 className="text-xl font-semibold text-white font-['Outfit'] mb-4">Your Plan</h2>
                        
                        <div className="bg-[#09050A] rounded-xl p-4 mb-4">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-full bg-[#E6005C]/10 flex items-center justify-center">
                                    <Star className="w-5 h-5 text-[#E6005C]" />
                                </div>
                                <div>
                                    <p className="text-white font-semibold capitalize">{user?.subscription_tier || 'Free'}</p>
                                    <p className="text-white/40 text-sm">Current Plan</p>
                                </div>
                            </div>
                            
                            {user?.subscription_tier === 'free' && (
                                <p className="text-white/60 text-sm mb-4">
                                    Upgrade to unlock all 1000 lessons and unlimited AI simulations
                                </p>
                            )}
                        </div>
                        
                        {user?.subscription_tier === 'free' && (
                            <Link 
                                to="/#pricing" 
                                className="btn-primary w-full text-center text-sm"
                                data-testid="upgrade-btn"
                            >
                                Upgrade Plan
                            </Link>
                        )}
                        
                        <div className="mt-6 space-y-3">
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-white/60">Simulations this month</span>
                                <span className="text-white">3 / {user?.subscription_tier === 'free' ? '5' : '∞'}</span>
                            </div>
                            <div className="flex items-center justify-between text-sm">
                                <span className="text-white/60">AI Chat Sessions</span>
                                <span className="text-white">{user?.subscription_tier === 'free' ? 'Not included' : 'Unlimited'}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Achievements Preview */}
                <div className="glass-card rounded-2xl p-6" data-testid="achievements-section">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-semibold text-white font-['Outfit']">Recent Achievements</h2>
                        <button className="text-[#E6005C] hover:text-[#FFB3D1] transition-colors text-sm flex items-center gap-1">
                            View All <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {[
                            { icon: Target, name: 'First Lesson', desc: 'Complete your first lesson', unlocked: completedCount > 0 },
                            { icon: Flame, name: '3-Day Streak', desc: 'Learn 3 days in a row', unlocked: false },
                            { icon: TrendingUp, name: 'Level Up', desc: 'Reach Level 2', unlocked: (user?.level || 1) >= 2 },
                            { icon: Star, name: 'Explorer', desc: 'Try all 4 AI instructors', unlocked: false }
                        ].map((achievement, i) => (
                            <div 
                                key={i}
                                className={`p-4 rounded-xl border ${
                                    achievement.unlocked 
                                        ? 'bg-[#E6005C]/10 border-[#E6005C]/30' 
                                        : 'bg-[#09050A] border-[#2E1E31]'
                                }`}
                            >
                                <achievement.icon className={`w-8 h-8 mb-3 ${
                                    achievement.unlocked ? 'text-[#E6005C]' : 'text-white/20'
                                }`} />
                                <p className={`font-medium text-sm ${
                                    achievement.unlocked ? 'text-white' : 'text-white/40'
                                }`}>{achievement.name}</p>
                                <p className={`text-xs mt-1 ${
                                    achievement.unlocked ? 'text-white/60' : 'text-white/20'
                                }`}>{achievement.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
