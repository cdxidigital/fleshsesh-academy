import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Users, Clock, ArrowRight, Filter, Search } from 'lucide-react';
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
                {/* Header */}
                <div className="text-center mb-12">
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                        Course Catalog
                    </h1>
                    <p className="text-white/60 text-lg max-w-2xl mx-auto">
                        Explore all 10 levels of intimacy mastery. Each level builds on the previous, 
                        creating a comprehensive journey to confident connection.
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
                            {[1,2,3,4,5,6,7,8,9,10].map(level => (
                                <option key={level} value={level}>Level {level}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Course Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {filteredCourses.map((course) => (
                        <Link 
                            key={course.id}
                            to={isAuthenticated ? `/courses/${course.id}` : '#'}
                            onClick={(e) => {
                                if (!isAuthenticated) {
                                    e.preventDefault();
                                    // Could trigger auth modal here
                                }
                            }}
                            className="glass-card rounded-2xl overflow-hidden card-hover group"
                            data-testid={`course-card-${course.id}`}
                        >
                            <div className="flex flex-col md:flex-row">
                                <div className="relative w-full md:w-48 h-48 md:h-auto overflow-hidden shrink-0">
                                    <img 
                                        src={course.image_url} 
                                        alt={course.title}
                                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[#140C16] md:block hidden" />
                                    <div className="absolute inset-0 bg-gradient-to-t from-[#140C16] to-transparent md:hidden" />
                                    <div className="absolute top-4 left-4 bg-[#E6005C] text-white text-sm font-bold px-3 py-1 rounded-full">
                                        Level {course.level}
                                    </div>
                                </div>
                                
                                <div className="p-6 flex-1">
                                    <h3 className="text-xl font-semibold text-white mb-2 font-['Outfit'] group-hover:text-[#FFB3D1] transition-colors">
                                        {course.title}
                                    </h3>
                                    <p className="text-white/60 text-sm mb-4 line-clamp-2">
                                        {course.description}
                                    </p>
                                    
                                    <div className="flex flex-wrap gap-2 mb-4">
                                        {course.skills.slice(0, 3).map((skill, i) => (
                                            <span 
                                                key={i}
                                                className="text-xs bg-[#2E1E31] text-white/70 px-2 py-1 rounded"
                                            >
                                                {skill}
                                            </span>
                                        ))}
                                    </div>
                                    
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4 text-sm text-white/40">
                                            <span className="flex items-center gap-1">
                                                <BookOpen className="w-4 h-4" />
                                                {course.lessons} lessons
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Users className="w-4 h-4" />
                                                {course.instructor}
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
