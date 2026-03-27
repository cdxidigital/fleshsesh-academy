import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { Toaster } from "./components/ui/sonner";

// Components
import Header from "./components/Header";
import Footer from "./components/Footer";

// Pages
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CoursesPage from "./pages/CoursesPage";
import CourseDetail from "./pages/CourseDetail";

function App() {
    return (
        <AuthProvider>
            <div className="App min-h-screen bg-[#09050A]">
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
                </BrowserRouter>
                <Toaster />
            </div>
        </AuthProvider>
    );
}

export default App;
