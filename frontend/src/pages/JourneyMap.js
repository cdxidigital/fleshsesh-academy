import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
    Sparkles, 
    Trophy, 
    BookOpen, 
    Clock, 
    ArrowRight,
    Check,
    Lock,
    Star,
    Target,
    Flame,
    Heart,
    Users,
    Zap,
    Crown,
    Medal,
    Award
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Progress } from '../components/ui/progress';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const levelThemes = {
    1: { 
        color: 'from-rose-500 to-pink-600', 
        icon: Heart, 
        name: 'Self-Intimacy',
        badge: 'Self-Intimacy Sovereign'
    },
    2: { 
        color: 'from-violet-500 to-purple-600', 
        icon: Users, 
        name: 'Connected Intimacy',
        badge: 'Connection Fluent'
    },
    3: { 
        color: 'from-amber-500 to-orange-600', 
        icon: Zap, 
        name: 'Diverse Intimacy',
        badge: 'Diversity Explorer'
    },
    4: { 
        color: 'from-emerald-500 to-teal-600', 
        icon: Crown, 
        name: 'Advanced Intimacy',
        badge: 'Intimacy Master'
    }
};

const JourneyMap = () => {
    const { user, token, isAuthenticated, updateUser } = useAuth();
    const navigate = useNavigate();
    const [courses, setCourses] = useState([]);
    const [lessons, setLessons] = useState({});
    const [labs, setLabs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/');
            return;
        }

        const fetchData = async () => {
            try {
                const [coursesRes, statsRes, labsRes, userRes] = await Promise.all([
                    axios.get(`${API_URL}/api/courses`),
                    axios.get(`${API_URL}/api/stats`),
                    axios.get(`${API_URL}/api/labs`),
                    axios.get(`${API_URL}/api/auth/me`, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                ]);
                
                setCourses(coursesRes.data);
                setStats(statsRes.data);
                setLabs(labsRes.data);
                updateUser(userRes.data);
                
                // Fetch lessons for each course
                const lessonsData = {};
                for (const course of coursesRes.data) {
                    const lessonsRes = await axios.get(`${API_URL}/api/courses/${course.id}/lessons`);
                    lessonsData[course.id] = lessonsRes.data;
                }
                setLessons(lessonsData);
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

    const completedLessons = user?.completed_lessons || [];
    const completedLabs = user?.completed_labs || [];
    const badges = user?.badges || [];
    const totalLessons = stats?.total_lessons || 28;
    const totalLabs = stats?.total_labs || 14;
    const overallProgress = Math.round((completedLessons.length / totalLessons) * 100);

    const getLevelProgress = (courseId) => {
        const courseLessons = lessons[courseId] || [];
        if (courseLessons.length === 0) return 0;
        const completed = courseLessons.filter(l => completedLessons.includes(l.id)).length;
        return Math.round((completed / courseLessons.length) * 100);
    };

    const isLevelComplete = (courseId) => {
        const courseLessons = lessons[courseId] || [];
        return courseLessons.every(l => completedLessons.includes(l.id));
    };

    const isLevelUnlocked = (level) => {
        if (level === 1) return true;
        // Check if previous level is complete
        const prevCourse = courses.find(c => c.level === level - 1);
        return prevCourse ? isLevelComplete(prevCourse.id) : false;
    };

    return (
        <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="journey-map-page">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 bg-[#E6005C]/10 border border-[#E6005C]/30 rounded-full px-4 py-2 mb-6">
                        <Target className="w-4 h-4 text-[#E6005C]" />
                        <span className="text-sm text-[#FFB3D1]">Your Journey</span>
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                        Student <span className="text-gradient">Journey Map</span>
                    </h1>
                    <p className="text-white/60 text-lg max-w-2xl mx-auto">
                        Track your transformation across all four levels of intimacy mastery. 
                        Every lesson completed brings you closer to becoming the person you're meant to be.
                    </p>
                </div>

                {/* Overall Progress Card */}
                <div className="glass-card rounded-2xl p-8 mb-12" data-testid="overall-progress">
                    <div className="flex flex-col md:flex-row items-center gap-8">
                        <div className="relative">
                            <div className="w-40 h-40 rounded-full bg-[#140C16] border-4 border-[#2E1E31] flex items-center justify-center">
                                <div className="text-center">
                                    <span className="text-5xl font-bold text-gradient font-['Outfit']">{overallProgress}%</span>
                                    <p className="text-white/40 text-sm mt-1">Complete</p>
                                </div>
                            </div>
                            <div 
                                className="absolute inset-0 rounded-full"
                                style={{
                                    background: `conic-gradient(#E6005C ${overallProgress * 3.6}deg, transparent 0deg)`,
                                    mask: 'radial-gradient(farthest-side, transparent calc(100% - 8px), white calc(100% - 8px))',
                                    WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 8px), white calc(100% - 8px))'
                                }}
                            />
                        </div>
                        
                        <div className="flex-1 text-center md:text-left">
                            <h2 className="text-2xl font-bold text-white mb-4 font-['Outfit']">
                                Welcome, <span className="text-[#E6005C]">{user?.name}</span>
                            </h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="bg-[#09050A] rounded-xl p-4">
                                    <BookOpen className="w-5 h-5 text-[#E6005C] mb-2" />
                                    <p className="text-2xl font-bold text-white">{completedLessons.length}/{totalLessons}</p>
                                    <p className="text-white/40 text-sm">Lessons</p>
                                </div>
                                <div className="bg-[#09050A] rounded-xl p-4">
                                    <Flame className="w-5 h-5 text-[#FFB3D1] mb-2" />
                                    <p className="text-2xl font-bold text-white">{completedLabs.length}/{totalLabs}</p>
                                    <p className="text-white/40 text-sm">Labs</p>
                                </div>
                                <div className="bg-[#09050A] rounded-xl p-4">
                                    <Sparkles className="w-5 h-5 text-[#E6005C] mb-2" />
                                    <p className="text-2xl font-bold text-white">{user?.xp || 0}</p>
                                    <p className="text-white/40 text-sm">Total XP</p>
                                </div>
                                <div className="bg-[#09050A] rounded-xl p-4">
                                    <Trophy className="w-5 h-5 text-[#FFB3D1] mb-2" />
                                    <p className="text-2xl font-bold text-white">{badges.length}/4</p>
                                    <p className="text-white/40 text-sm">Badges</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Level Progress Path */}
                <div className="relative mb-12">
                    {/* Connecting Line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-gradient-to-b from-[#E6005C] via-[#2E1E31] to-[#2E1E31] -translate-x-1/2 hidden md:block" />
                    
                    <div className="space-y-8">
                        {courses.map((course, index) => {
                            const theme = levelThemes[course.level];
                            const Icon = theme.icon;
                            const progress = getLevelProgress(course.id);
                            const isComplete = isLevelComplete(course.id);
                            const isUnlocked = isLevelUnlocked(course.level);
                            const hasBadge = badges.includes(theme.badge.toLowerCase().replace(/\s+/g, '-'));
                            const courseLessons = lessons[course.id] || [];
                            
                            return (
                                <div 
                                    key={course.id} 
                                    className={`relative ${index % 2 === 0 ? 'md:pr-1/2 md:text-right' : 'md:pl-1/2 md:ml-auto'}`}
                                    data-testid={`level-${course.level}-card`}
                                >
                                    {/* Level Node */}
                                    <div className={`absolute left-1/2 top-8 -translate-x-1/2 w-12 h-12 rounded-full hidden md:flex items-center justify-center z-10 ${
                                        isComplete 
                                            ? `bg-gradient-to-br ${theme.color}` 
                                            : isUnlocked 
                                                ? 'bg-[#140C16] border-2 border-[#E6005C]' 
                                                : 'bg-[#140C16] border-2 border-[#2E1E31]'
                                    }`}>
                                        {isComplete ? (
                                            <Check className="w-6 h-6 text-white" />
                                        ) : isUnlocked ? (
                                            <Icon className="w-5 h-5 text-[#E6005C]" />
                                        ) : (
                                            <Lock className="w-5 h-5 text-white/30" />
                                        )}
                                    </div>
                                    
                                    <div className={`glass-card rounded-2xl overflow-hidden max-w-xl mx-auto md:mx-0 ${
                                        !isUnlocked ? 'opacity-50' : ''
                                    } ${index % 2 === 0 ? 'md:mr-auto' : 'md:ml-auto'}`}>
                                        <div className={`h-2 bg-gradient-to-r ${theme.color}`} />
                                        <div className="p-6">
                                            <div className="flex items-start gap-4 mb-4">
                                                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${theme.color} flex items-center justify-center shrink-0 md:hidden`}>
                                                    <Icon className="w-7 h-7 text-white" />
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-xs font-bold text-white/40 uppercase tracking-wider">Level {course.level}</span>
                                                        {isComplete && (
                                                            <span className="flex items-center gap-1 text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full">
                                                                <Check className="w-3 h-3" /> Complete
                                                            </span>
                                                        )}
                                                    </div>
                                                    <h3 className="text-xl font-bold text-white font-['Outfit']">{course.title}</h3>
                                                    <p className="text-[#FFB3D1] text-sm">{course.theme}</p>
                                                </div>
                                            </div>
                                            
                                            <p className="text-white/60 text-sm mb-4">{course.description}</p>
                                            
                                            {/* Progress */}
                                            <div className="mb-4">
                                                <div className="flex justify-between text-sm mb-2">
                                                    <span className="text-white/40">Progress</span>
                                                    <span className="text-white">{progress}%</span>
                                                </div>
                                                <Progress value={progress} className="h-2 bg-[#2E1E31]" />
                                            </div>
                                            
                                            {/* Lessons Grid */}
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                {courseLessons.map((lesson, i) => {
                                                    const isLessonComplete = completedLessons.includes(lesson.id);
                                                    return (
                                                        <div 
                                                            key={lesson.id}
                                                            className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                                                                isLessonComplete 
                                                                    ? `bg-gradient-to-br ${theme.color} text-white` 
                                                                    : 'bg-[#09050A] text-white/30 border border-[#2E1E31]'
                                                            }`}
                                                            title={lesson.title}
                                                        >
                                                            {i + 1}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                            
                                            {/* Badge */}
                                            <div className={`flex items-center gap-3 p-3 rounded-xl ${
                                                hasBadge 
                                                    ? `bg-gradient-to-r ${theme.color}/20 border border-white/10` 
                                                    : 'bg-[#09050A]'
                                            }`}>
                                                <Award className={`w-6 h-6 ${hasBadge ? 'text-white' : 'text-white/20'}`} />
                                                <div className="flex-1">
                                                    <p className={`text-sm font-medium ${hasBadge ? 'text-white' : 'text-white/40'}`}>
                                                        {theme.badge}
                                                    </p>
                                                    <p className="text-xs text-white/30">
                                                        {hasBadge ? 'Earned!' : 'Complete all lessons to unlock'}
                                                    </p>
                                                </div>
                                                {hasBadge && <Star className="w-5 h-5 text-yellow-400" />}
                                            </div>
                                            
                                            {isUnlocked && (
                                                <Link 
                                                    to={`/courses/${course.id}`}
                                                    className="btn-primary w-full mt-4 text-center text-sm"
                                                >
                                                    {isComplete ? 'Review Level' : progress > 0 ? 'Continue Learning' : 'Start Level'}
                                                </Link>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Badges Section */}
                <div className="glass-card rounded-2xl p-8" data-testid="badges-section">
                    <h2 className="text-2xl font-bold text-white font-['Outfit'] mb-6 text-center">Your Badges</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {Object.entries(levelThemes).map(([level, theme]) => {
                            const badgeId = theme.badge.toLowerCase().replace(/\s+/g, '-');
                            const hasBadge = badges.includes(badgeId);
                            const Icon = theme.icon;
                            
                            return (
                                <div 
                                    key={level}
                                    className={`relative p-6 rounded-2xl text-center ${
                                        hasBadge 
                                            ? `bg-gradient-to-br ${theme.color}/20 border border-white/10` 
                                            : 'bg-[#09050A] border border-[#2E1E31]'
                                    }`}
                                >
                                    <div className={`w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-3 ${
                                        hasBadge 
                                            ? `bg-gradient-to-br ${theme.color}` 
                                            : 'bg-[#140C16]'
                                    }`}>
                                        {hasBadge ? (
                                            <Trophy className="w-8 h-8 text-white" />
                                        ) : (
                                            <Lock className="w-6 h-6 text-white/20" />
                                        )}
                                    </div>
                                    <p className={`font-semibold text-sm ${hasBadge ? 'text-white' : 'text-white/40'}`}>
                                        {theme.badge}
                                    </p>
                                    <p className="text-xs text-white/30 mt-1">Level {level}</p>
                                    {hasBadge && (
                                        <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
                                            <Star className="w-4 h-4 text-white" />
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default JourneyMap;
