import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
    ArrowLeft, 
    BookOpen, 
    Clock, 
    Users, 
    Play, 
    Check,
    Lock,
    Sparkles,
    ChevronRight
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const { user, token, isAuthenticated, updateUser } = useAuth();
    const [course, setCourse] = useState(null);
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [completingLesson, setCompletingLesson] = useState(null);

    useEffect(() => {
        if (!isAuthenticated) {
            navigate('/');
            return;
        }

        const fetchData = async () => {
            try {
                const [courseRes, lessonsRes] = await Promise.all([
                    axios.get(`${API_URL}/api/courses/${courseId}`),
                    axios.get(`${API_URL}/api/courses/${courseId}/lessons`)
                ]);
                setCourse(courseRes.data);
                setLessons(lessonsRes.data);
            } catch (error) {
                console.error('Error fetching course:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [courseId, isAuthenticated, navigate]);

    const completeLesson = async (lessonId) => {
        setCompletingLesson(lessonId);
        try {
            const response = await axios.post(
                `${API_URL}/api/lessons/${lessonId}/complete`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            
            if (response.data.xp_earned > 0) {
                updateUser({
                    xp: response.data.total_xp,
                    level: response.data.level,
                    completed_lessons: [...(user?.completed_lessons || []), lessonId]
                });
            }
        } catch (error) {
            console.error('Error completing lesson:', error);
        } finally {
            setCompletingLesson(null);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">Loading course...</div>
            </div>
        );
    }

    if (!course) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="text-white">Course not found</div>
            </div>
        );
    }

    const completedLessons = user?.completed_lessons || [];
    const courseProgress = lessons.filter(l => completedLessons.includes(l.id)).length;
    const progressPercent = lessons.length > 0 ? Math.round((courseProgress / lessons.length) * 100) : 0;

    return (
        <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="course-detail-page">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Back Button */}
                <Link 
                    to="/courses" 
                    className="inline-flex items-center gap-2 text-white/60 hover:text-white transition-colors mb-6"
                    data-testid="back-to-courses"
                >
                    <ArrowLeft className="w-5 h-5" />
                    Back to Courses
                </Link>

                {/* Course Header */}
                <div className="glass-card rounded-2xl overflow-hidden mb-8">
                    <div className="relative h-64 md:h-80">
                        <img 
                            src={course.image_url} 
                            alt={course.title}
                            className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#140C16] via-[#140C16]/50 to-transparent" />
                        <div className="absolute bottom-0 left-0 right-0 p-8">
                            <div className="flex items-center gap-2 mb-3">
                                <span className="bg-[#E6005C] text-white text-sm font-bold px-3 py-1 rounded-full">
                                    Level {course.level}
                                </span>
                                <span className="bg-white/10 text-white text-sm px-3 py-1 rounded-full">
                                    {course.instructor}
                                </span>
                            </div>
                            <h1 className="text-3xl md:text-4xl font-bold text-white font-['Outfit'] mb-2">
                                {course.title}
                            </h1>
                            <p className="text-white/70 max-w-2xl">{course.description}</p>
                        </div>
                    </div>
                    
                    <div className="p-6 border-t border-[#2E1E31]">
                        <div className="flex flex-wrap items-center justify-between gap-4">
                            <div className="flex items-center gap-6 text-sm">
                                <span className="flex items-center gap-2 text-white/60">
                                    <BookOpen className="w-5 h-5 text-[#E6005C]" />
                                    {course.lessons} Lessons
                                </span>
                                <span className="flex items-center gap-2 text-white/60">
                                    <Clock className="w-5 h-5 text-[#E6005C]" />
                                    ~{course.lessons * 5} min
                                </span>
                                <span className="flex items-center gap-2 text-white/60">
                                    <Users className="w-5 h-5 text-[#E6005C]" />
                                    {course.modules} Modules
                                </span>
                            </div>
                            
                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <p className="text-white font-semibold">{progressPercent}% Complete</p>
                                    <p className="text-white/40 text-sm">{courseProgress}/{lessons.length} lessons</p>
                                </div>
                                <div className="w-32 h-2 bg-[#2E1E31] rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-[#E6005C] transition-all duration-500"
                                        style={{ width: `${progressPercent}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Skills */}
                <div className="glass-card rounded-2xl p-6 mb-8">
                    <h2 className="text-xl font-semibold text-white font-['Outfit'] mb-4">Skills You'll Learn</h2>
                    <div className="flex flex-wrap gap-2">
                        {course.skills.map((skill, i) => (
                            <span 
                                key={i}
                                className="bg-[#E6005C]/10 border border-[#E6005C]/30 text-[#FFB3D1] px-4 py-2 rounded-full text-sm"
                            >
                                {skill}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Lessons */}
                <div className="glass-card rounded-2xl p-6">
                    <h2 className="text-xl font-semibold text-white font-['Outfit'] mb-6">Lessons</h2>
                    
                    {lessons.length === 0 ? (
                        <div className="text-center py-12">
                            <Lock className="w-12 h-12 text-white/20 mx-auto mb-4" />
                            <p className="text-white/60">Full lesson content coming soon!</p>
                            <p className="text-white/40 text-sm mt-2">This course will include {course.lessons} comprehensive lessons.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {lessons.map((lesson, index) => {
                                const isCompleted = completedLessons.includes(lesson.id);
                                const isLocked = !isCompleted && index > 0 && !completedLessons.includes(lessons[index - 1]?.id);
                                
                                return (
                                    <div 
                                        key={lesson.id}
                                        className={`flex items-center gap-4 p-4 rounded-xl transition-colors ${
                                            isLocked 
                                                ? 'bg-[#09050A]/50 opacity-60' 
                                                : isCompleted 
                                                    ? 'bg-[#E6005C]/10 border border-[#E6005C]/30' 
                                                    : 'bg-[#09050A] hover:bg-[#1a1020]'
                                        }`}
                                        data-testid={`lesson-${lesson.id}`}
                                    >
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                                            isCompleted 
                                                ? 'bg-[#E6005C] text-white' 
                                                : isLocked 
                                                    ? 'bg-[#2E1E31] text-white/40' 
                                                    : 'bg-[#2E1E31] text-white'
                                        }`}>
                                            {isCompleted ? (
                                                <Check className="w-5 h-5" />
                                            ) : isLocked ? (
                                                <Lock className="w-4 h-4" />
                                            ) : (
                                                <span className="text-sm font-medium">{index + 1}</span>
                                            )}
                                        </div>
                                        
                                        <div className="flex-1 min-w-0">
                                            <h3 className={`font-medium ${isLocked ? 'text-white/40' : 'text-white'}`}>
                                                {lesson.title}
                                            </h3>
                                            <p className={`text-sm ${isLocked ? 'text-white/20' : 'text-white/60'}`}>
                                                {lesson.duration_minutes} min • {lesson.xp_reward} XP
                                            </p>
                                        </div>
                                        
                                        {!isLocked && !isCompleted && (
                                            <button
                                                onClick={() => completeLesson(lesson.id)}
                                                disabled={completingLesson === lesson.id}
                                                className="flex items-center gap-2 bg-[#E6005C] hover:bg-[#E6005C]/80 text-white px-4 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
                                                data-testid={`start-lesson-${lesson.id}`}
                                            >
                                                {completingLesson === lesson.id ? (
                                                    <>
                                                        <Sparkles className="w-4 h-4 animate-spin" />
                                                        Completing...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Play className="w-4 h-4" />
                                                        Start
                                                    </>
                                                )}
                                            </button>
                                        )}
                                        
                                        {isCompleted && (
                                            <span className="text-[#E6005C] text-sm font-medium flex items-center gap-1">
                                                <Check className="w-4 h-4" />
                                                Completed
                                            </span>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CourseDetail;
