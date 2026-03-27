import React, { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { Toaster } from "./components/ui/sonner";

// Components
import Header from "./components/Header";
import Footer from "./components/Footer";
import AgeVerification from "./components/AgeVerification";
import AIAdvisor from "./components/AIAdvisor";

// Pages
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CoursesPage from "./pages/CoursesPage";
import CourseDetail from "./pages/CourseDetail";

function App() {
    const [ageVerified, setAgeVerified] = useState(
        localStorage.getItem('fleshsesh_age_verified') === 'true'
    );

    return (
        <AuthProvider>
            <div className="App min-h-screen bg-[#09050A]">
                {!ageVerified && (
                    <AgeVerification onVerified={() => setAgeVerified(true)} />
                )}
                
                {ageVerified && (
                    <BrowserRouter>
                        <Header />
                        <main>
                            <Routes>
                                <Route path="/" element={<LandingPage />} />
                                <Route path="/dashboard" element={<Dashboard />} />
                                <Route path="/courses" element={<CoursesPage />} />
                                <Route path="/courses/:courseId" element={<CourseDetail />} />
                            </Routes>
                        </main>
                        <Footer />
                        <AIAdvisor />
                    </BrowserRouter>
                )}
                <Toaster />
            </div>
        </AuthProvider>
    );
}

export default App;
