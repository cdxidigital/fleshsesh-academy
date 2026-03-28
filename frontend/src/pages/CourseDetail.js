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
    FlaskConical,
    FileQuestion,
    PenLine,
    Award,
    ChevronRight
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Progress } from '../components/ui/progress';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const { user, token, isAuthenticated, updateUser } = useAuth();
    const [course, setCourse] = useState(null);
    const [lessons, setLessons] = useState([]);
    const [loading, setLoading] = useState(true);
    const [completingLesson, setCompletingLesson] = useState(null);
    const [selectedLesson, setSelectedLesson] = useState(null);

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
                    completed_lessons: [...(user?.completed_lessons || []), lessonId],
                    badges: response.data.badges_earned?.length > 0 
                        ? [...(user?.badges || []), ...response.data.badges_earned]
                        : user?.badges
                });
            }
        } catch (error) {
            console.error('Error completing lesson:', error);
        } finally {
            setCompletingLesson(null);
        }
    };

    const viewLesson = async (lessonId) => {
        try {
            const response = await axios.get(`${API_URL}/api/lessons/${lessonId}`);
            setSelectedLesson(response.data);
        } catch (error) {
            console.error('Error fetching lesson:', error);
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

    // Lesson content modal
    if (selectedLesson) {
        return (
            <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="lesson-view">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                    <button 
                        onClick={() => setSelectedLesson(null)}
                        className="inline-flex items-center gap-2 text-white/60 hover:text-white transition-colors mb-6"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Back to Course
                    </button>

                    <div className="glass-card rounded-2xl p-8 mb-6">
                        <div className="flex items-center gap-3 mb-4">
                            <span className="bg-[#E6005C] text-white text-xs font-bold px-3 py-1 rounded-full">
                                Lesson {selectedLesson.lesson_number}
                            </span>
                            <span className="text-[#FFB3D1] text-sm">{selectedLesson.instructor}</span>
                        </div>
                        
                        <h1 className="text-3xl font-bold text-white font-['Outfit'] mb-4">
                            {selectedLesson.title}
                        </h1>
                        
                        <div className="flex items-center gap-4 text-sm text-white/60 mb-6">
                            <span className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {selectedLesson.duration_minutes} min
                            </span>
                            <span className="flex items-center gap-1">
                                <Sparkles className="w-4 h-4" />
                                {selectedLesson.xp_reward} XP
                            </span>
                        </div>
                        
                        <div 
                            className="lesson-content prose prose-invert max-w-none"
                            dangerouslySetInnerHTML={{ 
                                __html: selectedLesson.content
                                    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                                    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                                    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                    .replace(/^- (.*$)/gm, '<li>$1</li>')
                                    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
                                    .replace(/\n\n/g, '</p><p>')
                                    .replace(/^(?!<[h|u|l|p])/gm, '<p>')
                            }}
                        />
                    </div>

                    {/* Lab Section */}
                    {selectedLesson.lab && (
                        <div className="glass-card rounded-2xl p-6 mb-6 border-l-4 border-[#E6005C]">
                            <div className="flex items-center gap-3 mb-3">
                                <FlaskConical className="w-5 h-5 text-[#E6005C]" />
                                <h3 className="text-lg font-semibold text-white font-['Outfit']">
                                    Hedonistic Lab: {selectedLesson.lab.title}
                                </h3>
                            </div>
                            <p className="text-white/70 mb-3">{selectedLesson.lab.description}</p>
                            <p className="text-sm text-white/40">Duration: {selectedLesson.lab.duration_minutes} minutes</p>
                        </div>
                    )}

                    {/* Quiz Section */}
                    {selectedLesson.quiz && (
                        <div className="glass-card rounded-2xl p-6 mb-6 border-l-4 border-[#FFB3D1]">
                            <div className="flex items-center gap-3 mb-3">
                                <FileQuestion className="w-5 h-5 text-[#FFB3D1]" />
                                <h3 className="text-lg font-semibold text-white font-['Outfit']">
                                    {selectedLesson.quiz.title}
                                </h3>
                            </div>
                            <p className="text-white/70">{selectedLesson.quiz.description}</p>
                        </div>
                    )}

                    {/* Reflection Section */}
                    {selectedLesson.reflection && (
                        <div className="glass-card rounded-2xl p-6 mb-6 border-l-4 border-purple-500">
                            <div className="flex items-center gap-3 mb-3">
                                <PenLine className="w-5 h-5 text-purple-400" />
                                <h3 className="text-lg font-semibold text-white font-['Outfit']">
                                    Reflection: {selectedLesson.reflection.title}
                                </h3>
                            </div>
                            <p className="text-white/70">{selectedLesson.reflection.prompt}</p>
                        </div>
                    )}

                    {/* Complete Button */}
                    <div className="flex justify-center">
                        <button
                            onClick={() => {
                                completeLesson(selectedLesson.id);
                                setSelectedLesson(null);
                            }}
                            disabled={completedLessons.includes(selectedLesson.id)}
                            className={`px-8 py-4 rounded-full font-semibold text-lg flex items-center gap-3 transition-all ${
                                completedLessons.includes(selectedLesson.id)
                                    ? 'bg-green-600 text-white cursor-default'
                                    : 'btn-primary'
                            }`}
                        >
                            {completedLessons.includes(selectedLesson.id) ? (
                                <>
                                    <Check className="w-6 h-6" />
                                    Lesson Completed
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-6 h-6" />
                                    Complete Lesson (+{selectedLesson.xp_reward} XP)
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        );
    }

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
                            <div className="flex items-center gap-3 mb-3">
                                <span className="bg-[#E6005C] text-white text-sm font-bold px-4 py-1.5 rounded-full">
                                    Level {course.level}
                                </span>
                                <span className="bg-white/10 text-white/90 text-sm px-4 py-1.5 rounded-full">
                                    {course.theme}
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
                                    {course.duration}
                                </span>
                                <span className="flex items-center gap-2 text-white/60">
                                    <Users className="w-5 h-5 text-[#E6005C]" />
                                    {course.lead_instructors?.join(' & ')}
                                </span>
                            </div>
                            
                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <p className="text-white font-semibold">{progressPercent}% Complete</p>
                                    <p className="text-white/40 text-sm">{courseProgress}/{lessons.length} lessons</p>
                                </div>
                                <div className="w-32">
                                    <Progress value={progressPercent} className="h-2 bg-[#2E1E31]" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Transformation Goal */}
                <div className="glass-card rounded-2xl p-6 mb-8">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-[#E6005C]/10 flex items-center justify-center shrink-0">
                            <Award className="w-6 h-6 text-[#E6005C]" />
                        </div>
                        <div>
                            <p className="text-white/40 text-sm uppercase tracking-wider">Your Transformation</p>
                            <p className="text-xl font-semibold text-white font-['Outfit']">{course.transformation}</p>
                        </div>
                    </div>
                </div>

                {/* Skills */}
                <div className="glass-card rounded-2xl p-6 mb-8">
                    <h2 className="text-xl font-semibold text-white font-['Outfit'] mb-4">Skills You'll Develop</h2>
                    <div className="flex flex-wrap gap-3">
                        {course.skills.map((skill, i) => (
                            <span 
                                key={i}
                                className="bg-[#E6005C]/10 border border-[#E6005C]/30 text-[#FFB3D1] px-4 py-2 rounded-full text-sm font-medium"
                            >
                                {skill}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Lessons */}
                <div className="glass-card rounded-2xl p-6">
                    <h2 className="text-xl font-semibold text-white font-['Outfit'] mb-6">Course Lessons</h2>
                    
                    <div className="space-y-3">
                        {lessons.map((lesson, index) => {
                            const isCompleted = completedLessons.includes(lesson.id);
                            const isLocked = false; // For now, all lessons are unlocked
                            
                            return (
                                <div 
                                    key={lesson.id}
                                    className={`flex items-center gap-4 p-4 rounded-xl transition-all cursor-pointer ${
                                        isLocked 
                                            ? 'bg-[#09050A]/50 opacity-60 cursor-not-allowed' 
                                            : isCompleted 
                                                ? 'bg-[#E6005C]/10 border border-[#E6005C]/30 hover:border-[#E6005C]/50' 
                                                : 'bg-[#09050A] hover:bg-[#1a1020]'
                                    }`}
                                    onClick={() => !isLocked && viewLesson(lesson.id)}
                                    data-testid={`lesson-${lesson.id}`}
                                >
                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
                                        isCompleted 
                                            ? 'bg-[#E6005C] text-white' 
                                            : isLocked 
                                                ? 'bg-[#2E1E31] text-white/40' 
                                                : 'bg-[#2E1E31] text-white'
                                    }`}>
                                        {isCompleted ? (
                                            <Check className="w-6 h-6" />
                                        ) : isLocked ? (
                                            <Lock className="w-5 h-5" />
                                        ) : (
                                            <span className="text-lg font-bold">{lesson.lesson_number}</span>
                                        )}
                                    </div>
                                    
                                    <div className="flex-1 min-w-0">
                                        <h3 className={`font-semibold mb-1 ${isLocked ? 'text-white/40' : 'text-white'}`}>
                                            {lesson.title}
                                        </h3>
                                        <div className="flex items-center gap-4 text-sm">
                                            <span className={isLocked ? 'text-white/20' : 'text-[#FFB3D1]'}>
                                                {lesson.instructor}
                                            </span>
                                            <span className={isLocked ? 'text-white/20' : 'text-white/40'}>
                                                {lesson.duration_minutes} min
                                            </span>
                                            <span className={isLocked ? 'text-white/20' : 'text-white/40'}>
                                                {lesson.xp_reward} XP
                                            </span>
                                        </div>
                                        
                                        {/* Lesson Type Icons */}
                                        <div className="flex items-center gap-2 mt-2">
                                            {lesson.has_lab && (
                                                <span className="flex items-center gap-1 text-xs text-[#E6005C] bg-[#E6005C]/10 px-2 py-0.5 rounded">
                                                    <FlaskConical className="w-3 h-3" />
                                                    Lab
                                                </span>
                                            )}
                                            {lesson.has_quiz && (
                                                <span className="flex items-center gap-1 text-xs text-[#FFB3D1] bg-[#FFB3D1]/10 px-2 py-0.5 rounded">
                                                    <FileQuestion className="w-3 h-3" />
                                                    Quiz
                                                </span>
                                            )}
                                            {lesson.has_reflection && (
                                                <span className="flex items-center gap-1 text-xs text-purple-400 bg-purple-400/10 px-2 py-0.5 rounded">
                                                    <PenLine className="w-3 h-3" />
                                                    Reflection
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <ChevronRight className={`w-5 h-5 ${isLocked ? 'text-white/20' : 'text-white/40'}`} />
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CourseDetail;
