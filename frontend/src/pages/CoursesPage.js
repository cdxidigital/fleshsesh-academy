import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Clock, ArrowRight, Filter, Search } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CoursesPage = () => {
    const { isAuthenticated } = useAuth();
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedLevel, setSelectedLevel] = useState('all');

    useEffect(() => {
        const fetchCourses = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/courses`);
                setCourses(response.data);
            } catch (error) {
                console.error('Error fetching courses:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchCourses();
    }, []);

    const filteredCourses = courses.filter(course => {
        const matchesSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             course.description.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesLevel = selectedLevel === 'all' || course.level === parseInt(selectedLevel);
        return matchesSearch && matchesLevel;
    });

    if (loading) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">Loading courses...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="courses-page">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-12">
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                        The Intimacy Course
                    </h1>
                    <p className="text-white/60 text-lg max-w-2xl mx-auto">
                        A complete human education in the art of connection. 4 progressive levels, 
                        28 transformative lessons, guided by 8 expert AI faculty.
                    </p>
                </div>

                {/* Filters */}
                <div className="flex flex-col sm:flex-row gap-4 mb-8">
                    <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                        <input
                            type="text"
                            placeholder="Search courses..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-[#140C16] border border-[#2E1E31] rounded-xl pl-12 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent"
                            data-testid="course-search-input"
                        />
                    </div>
                <div className="relative">
                        <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                        <select
                            value={selectedLevel}
                            onChange={(e) => setSelectedLevel(e.target.value)}
                            className="appearance-none bg-[#140C16] border border-[#2E1E31] rounded-xl pl-12 pr-12 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent"
                            data-testid="level-filter"
                        >
                            <option value="all">All Levels</option>
                            {[1,2,3,4].map(level => (
                                <option key={level} value={level}>Level {level}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Course Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {filteredCourses.map((course) => (
                        <Link 
                            key={course.id}
                            to={isAuthenticated ? `/courses/${course.id}` : '#'}
                            onClick={(e) => {
                                if (!isAuthenticated) {
                                    e.preventDefault();
                                }
                            }}
                            className="glass-card rounded-2xl overflow-hidden card-hover group"
                            data-testid={`course-card-${course.id}`}
                        >
                            <div className="flex flex-col">
                                <div className="relative h-56 overflow-hidden">
                                    <img 
                                        src={course.image_url} 
                                        alt={course.title}
                                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-[#140C16] via-[#140C16]/60 to-transparent" />
                                    <div className="absolute top-4 left-4 bg-[#E6005C] text-white text-sm font-bold px-4 py-1.5 rounded-full">
                                        Level {course.level}
                                    </div>
                                    <div className="absolute bottom-4 left-4 right-4">
                                        <p className="text-[#FFB3D1] text-sm font-medium mb-1">{course.theme}</p>
                                        <h3 className="text-2xl font-bold text-white font-['Outfit'] group-hover:text-[#FFB3D1] transition-colors">
                                            {course.title}
                                        </h3>
                                    </div>
                                </div>
                                
                                <div className="p-6">
                                    <p className="text-white/60 text-sm mb-4 line-clamp-2">
                                        {course.description}
                                    </p>
                                    
                                    <div className="bg-[#09050A] rounded-xl p-4 mb-4">
                                        <p className="text-xs text-white/40 uppercase tracking-wider mb-1">Transformation</p>
                                        <p className="text-[#E6005C] font-semibold">{course.transformation}</p>
                                    </div>
                                    
                                    <div className="flex flex-wrap gap-2 mb-4">
                                        {course.skills.slice(0, 4).map((skill, i) => (
                                            <span 
                                                key={i}
                                                className="text-xs bg-[#2E1E31] text-white/70 px-3 py-1 rounded-full"
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                    
                                    <div className="flex items-center justify-between pt-4 border-t border-[#2E1E31]">
                                        <div className="flex items-center gap-4 text-sm text-white/40">
                                            <span className="flex items-center gap-1">
                                                <BookOpen className="w-4 h-4" />
                                                {course.lessons} lessons
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Clock className="w-4 h-4" />
                                                {course.duration}
                                            </span>
                                        </div>
                                        <ArrowRight className="w-5 h-5 text-white/40 group-hover:text-[#E6005C] transition-colors" />
                                    </div>
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>

                {filteredCourses.length === 0 && (
                    <div className="text-center py-12">
                        <p className="text-white/60">No courses found matching your criteria.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default CoursesPage;
