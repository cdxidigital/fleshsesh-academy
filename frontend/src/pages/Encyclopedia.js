import React, { useState, useEffect } from 'react';
import { 
    Search, 
    BookOpen, 
    Bookmark, 
    BookmarkCheck,
    ChevronRight,
    Filter,
    Sparkles,
    GraduationCap,
    Shield,
    Heart,
    Users,
    Flame,
    Globe,
    Zap
} from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const categoryIcons = {
    'Anatomy and Physiology': Heart,
    'Communication and Consent': Shield,
    'Pleasure Practices': Flame,
    'Kink and BDSM': Zap,
    'Relational Structures': Users,
    'default': BookOpen
};

const depthColors = {
    'beginner': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    'intermediate': 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    'advanced': 'bg-rose-500/10 text-rose-400 border-rose-500/30'
};

const Encyclopedia = () => {
    const { isAuthenticated, token, user, updateUser } = useAuth();
    const [entries, setEntries] = useState([]);
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [selectedEntry, setSelectedEntry] = useState(null);
    const [bookmarkedEntries, setBookmarkedEntries] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [entriesRes] = await Promise.all([
                    axios.get(`${API_URL}/api/encyclopedia`)
                ]);
                setEntries(entriesRes.data);
                
                // Extract unique categories
                const uniqueCategories = [...new Set(entriesRes.data.map(e => e.category))];
                setCategories(uniqueCategories);
                
                // Get user bookmarks if authenticated
                if (isAuthenticated && user) {
                    setBookmarkedEntries(user.bookmarked_entries || []);
                }
            } catch (error) {
                console.error('Error fetching encyclopedia:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [isAuthenticated, user]);

    const filteredEntries = entries.filter(entry => {
        const matchesSearch = entry.term.toLowerCase().includes(searchQuery.toLowerCase()) ||
                             entry.definition.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesCategory = selectedCategory === 'all' || entry.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    const handleBookmark = async (entryId) => {
        if (!isAuthenticated) {
            toast.error('Please login to bookmark entries');
            return;
        }

        try {
            const response = await axios.post(
                `${API_URL}/api/encyclopedia/${entryId}/bookmark`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setBookmarkedEntries(response.data.bookmarked_entries);
            updateUser({ ...user, bookmarked_entries: response.data.bookmarked_entries });
            toast.success(response.data.message);
        } catch (error) {
            toast.error('Failed to update bookmark');
        }
    };

    const getCategoryIcon = (category) => {
        return categoryIcons[category] || categoryIcons['default'];
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-[#09050A] flex items-center justify-center pt-20">
                <div className="animate-pulse text-[#E6005C]">
                    <Sparkles className="w-12 h-12 animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#09050A] pt-24 pb-12" data-testid="encyclopedia-page">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 bg-[#E6005C]/10 border border-[#E6005C]/30 rounded-full px-4 py-2 mb-6">
                        <BookOpen className="w-4 h-4 text-[#E6005C]" />
                        <span className="text-sm text-[#FFB3D1]">A-Z Reference</span>
                    </div>
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 font-['Outfit']">
                        Intimacy <span className="text-gradient">Encyclopedia</span>
                    </h1>
                    <p className="text-white/60 text-lg max-w-2xl mx-auto">
                        Your comprehensive reference guide to intimacy education. Explore terms, concepts, 
                        and practices with expert insights from our AI Faculty.
                    </p>
                </div>

                <div className="flex flex-col lg:flex-row gap-8">
                    {/* Sidebar - Categories */}
                    <div className="lg:w-64 shrink-0">
                        <div className="glass-card rounded-2xl p-4 sticky top-24">
                            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                                <Filter className="w-4 h-4 text-[#E6005C]" />
                                Categories
                            </h3>
                            <div className="space-y-2">
                                <button
                                    onClick={() => setSelectedCategory('all')}
                                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors text-sm ${
                                        selectedCategory === 'all' 
                                            ? 'bg-[#E6005C] text-white' 
                                            : 'text-white/60 hover:bg-[#2E1E31] hover:text-white'
                                    }`}
                                    data-testid="category-all"
                                >
                                    All Entries ({entries.length})
                                </button>
                                {categories.map((category) => {
                                    const Icon = getCategoryIcon(category);
                                    const count = entries.filter(e => e.category === category).length;
                                    return (
                                        <button
                                            key={category}
                                            onClick={() => setSelectedCategory(category)}
                                            className={`w-full text-left px-4 py-2 rounded-lg transition-colors text-sm flex items-center gap-2 ${
                                                selectedCategory === category 
                                                    ? 'bg-[#E6005C] text-white' 
                                                    : 'text-white/60 hover:bg-[#2E1E31] hover:text-white'
                                            }`}
                                            data-testid={`category-${category.toLowerCase().replace(/\s+/g, '-')}`}
                                        >
                                            <Icon className="w-4 h-4" />
                                            <span className="truncate">{category}</span>
                                            <span className="ml-auto text-xs opacity-60">({count})</span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1">
                        {/* Search */}
                        <div className="relative mb-6">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
                            <input
                                type="text"
                                placeholder="Search terms, definitions..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-[#140C16] border border-[#2E1E31] rounded-xl pl-12 pr-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#E6005C] focus:border-transparent"
                                data-testid="encyclopedia-search"
                            />
                        </div>

                        {/* Entry List */}
                        {!selectedEntry ? (
                            <div className="space-y-4">
                                {filteredEntries.map((entry) => {
                                    const Icon = getCategoryIcon(entry.category);
                                    const isBookmarked = bookmarkedEntries.includes(entry.id);
                                    
                                    return (
                                        <div 
                                            key={entry.id}
                                            className="glass-card rounded-xl p-5 card-hover cursor-pointer group"
                                            onClick={() => setSelectedEntry(entry)}
                                            data-testid={`entry-card-${entry.id}`}
                                        >
                                            <div className="flex items-start justify-between gap-4">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-3 mb-2">
                                                        <div className="w-10 h-10 rounded-lg bg-[#E6005C]/10 flex items-center justify-center">
                                                            <Icon className="w-5 h-5 text-[#E6005C]" />
                                                        </div>
                                                        <div>
                                                            <h3 className="text-lg font-semibold text-white font-['Outfit'] group-hover:text-[#FFB3D1] transition-colors">
                                                                {entry.term}
                                                            </h3>
                                                            <p className="text-xs text-white/40">{entry.category}</p>
                                                        </div>
                                                        <span className={`text-xs px-2 py-0.5 rounded-full border ${depthColors[entry.depth_level]}`}>
                                                            {entry.depth_level}
                                                        </span>
                                                    </div>
                                                    <p className="text-white/60 text-sm line-clamp-2 ml-13">
                                                        {entry.definition}
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            handleBookmark(entry.id);
                                                        }}
                                                        className={`p-2 rounded-lg transition-colors ${
                                                            isBookmarked 
                                                                ? 'text-[#E6005C]' 
                                                                : 'text-white/40 hover:text-white'
                                                        }`}
                                                        data-testid={`bookmark-${entry.id}`}
                                                    >
                                                        {isBookmarked ? (
                                                            <BookmarkCheck className="w-5 h-5" />
                                                        ) : (
                                                            <Bookmark className="w-5 h-5" />
                                                        )}
                                                    </button>
                                                    <ChevronRight className="w-5 h-5 text-white/40 group-hover:text-[#E6005C] transition-colors" />
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                                
                                {filteredEntries.length === 0 && (
                                    <div className="text-center py-12 glass-card rounded-2xl">
                                        <BookOpen className="w-12 h-12 text-white/20 mx-auto mb-4" />
                                        <p className="text-white/60">No entries found matching your search.</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            /* Entry Detail View */
                            <div className="glass-card rounded-2xl overflow-hidden" data-testid="entry-detail">
                                <div className="bg-gradient-to-r from-[#E6005C]/20 to-transparent p-6 border-b border-[#2E1E31]">
                                    <button
                                        onClick={() => setSelectedEntry(null)}
                                        className="text-white/60 hover:text-white text-sm mb-4 flex items-center gap-1"
                                    >
                                        <ChevronRight className="w-4 h-4 rotate-180" />
                                        Back to list
                                    </button>
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className={`text-xs px-2 py-0.5 rounded-full border ${depthColors[selectedEntry.depth_level]}`}>
                                                    {selectedEntry.depth_level}
                                                </span>
                                                <span className="text-xs text-white/40">{selectedEntry.category}</span>
                                            </div>
                                            <h2 className="text-3xl font-bold text-white font-['Outfit']">
                                                {selectedEntry.term}
                                            </h2>
                                        </div>
                                        <button
                                            onClick={() => handleBookmark(selectedEntry.id)}
                                            className={`p-2 rounded-lg transition-colors ${
                                                bookmarkedEntries.includes(selectedEntry.id) 
                                                    ? 'text-[#E6005C] bg-[#E6005C]/10' 
                                                    : 'text-white/40 hover:text-white hover:bg-white/10'
                                            }`}
                                        >
                                            {bookmarkedEntries.includes(selectedEntry.id) ? (
                                                <BookmarkCheck className="w-6 h-6" />
                                            ) : (
                                                <Bookmark className="w-6 h-6" />
                                            )}
                                        </button>
                                    </div>
                                </div>
                                
                                <div className="p-6 space-y-6">
                                    <div>
                                        <h3 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">Definition</h3>
                                        <p className="text-white/80 leading-relaxed">{selectedEntry.definition}</p>
                                    </div>
                                    
                                    <div>
                                        <h3 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-2">Context</h3>
                                        <p className="text-white/70 leading-relaxed">{selectedEntry.context}</p>
                                    </div>
                                    
                                    {selectedEntry.science && (
                                        <div className="bg-[#09050A] rounded-xl p-5 border-l-4 border-blue-500">
                                            <h3 className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                                                <GraduationCap className="w-4 h-4" />
                                                The Science
                                            </h3>
                                            <p className="text-white/70 leading-relaxed">{selectedEntry.science}</p>
                                        </div>
                                    )}
                                    
                                    {selectedEntry.practice && (
                                        <div className="bg-[#09050A] rounded-xl p-5 border-l-4 border-emerald-500">
                                            <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                                                <Sparkles className="w-4 h-4" />
                                                In Practice
                                            </h3>
                                            <p className="text-white/70 leading-relaxed">{selectedEntry.practice}</p>
                                        </div>
                                    )}
                                    
                                    {selectedEntry.safety && (
                                        <div className="bg-[#09050A] rounded-xl p-5 border-l-4 border-amber-500">
                                            <h3 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                                                <Shield className="w-4 h-4" />
                                                Safety Note
                                            </h3>
                                            <p className="text-white/70 leading-relaxed">{selectedEntry.safety}</p>
                                        </div>
                                    )}
                                    
                                    {selectedEntry.lecturer_note && Object.keys(selectedEntry.lecturer_note).length > 0 && (
                                        <div className="bg-gradient-to-r from-[#E6005C]/10 to-transparent rounded-xl p-5 border border-[#E6005C]/20">
                                            <h3 className="text-sm font-semibold text-[#E6005C] uppercase tracking-wider mb-3">Faculty Insight</h3>
                                            {Object.entries(selectedEntry.lecturer_note).map(([lecturer, note]) => (
                                                <div key={lecturer} className="flex items-start gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-[#E6005C]/20 flex items-center justify-center shrink-0">
                                                        <Users className="w-5 h-5 text-[#E6005C]" />
                                                    </div>
                                                    <div>
                                                        <p className="text-[#FFB3D1] font-medium text-sm">{lecturer}</p>
                                                        <p className="text-white/70 italic">"{note}"</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    
                                    {selectedEntry.related_entries && selectedEntry.related_entries.length > 0 && (
                                        <div>
                                            <h3 className="text-sm font-semibold text-[#FFB3D1] uppercase tracking-wider mb-3">Related Entries</h3>
                                            <div className="flex flex-wrap gap-2">
                                                {selectedEntry.related_entries.map((related, i) => (
                                                    <span 
                                                        key={i}
                                                        className="text-sm bg-[#2E1E31] text-white/70 px-3 py-1.5 rounded-full hover:bg-[#E6005C]/20 hover:text-white cursor-pointer transition-colors"
                                                    >
                                                        {related}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Encyclopedia;
