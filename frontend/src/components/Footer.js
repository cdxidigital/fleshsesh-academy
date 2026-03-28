import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, Instagram, Twitter, Youtube } from 'lucide-react';

const Footer = () => {
    return (
        <footer className="bg-[#09050A] border-t border-[#2E1E31]" data-testid="main-footer">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="md:col-span-2">
                        <Link to="/" className="inline-block mb-4">
                            <img 
                                src="https://customer-assets.emergentagent.com/job_body-training-lab/artifacts/22p6smrp_82bcdafd-9834-4c0f-b899-cc5eb2810f81-removebg-preview.png"
                                alt="Fleshsesh Academy"
                                className="h-16 object-contain"
                            />
                        </Link>
                        <p className="text-white/60 max-w-md mb-6">
                            AI-powered intimacy education that transforms how you connect, attract, and build lasting relationships. Learn at your own pace with expert guidance.
                        </p>
                        <div className="flex gap-4">
                            <a href="#" className="text-white/40 hover:text-[#E6005C] transition-colors">
                                <Instagram className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-white/40 hover:text-[#E6005C] transition-colors">
                                <Twitter className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-white/40 hover:text-[#E6005C] transition-colors">
                                <Youtube className="w-5 h-5" />
                            </a>
                        </div>
                    </div>

                    {/* Quick Links */}
                    <div>
                        <h4 className="text-white font-semibold mb-4 font-['Outfit']">Academy</h4>
                        <ul className="space-y-2">
                            <li>
                                <Link to="/courses" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    All Courses
                                </Link>
                            </li>
                            <li>
                                <Link to="/#instructors" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Our Instructors
                                </Link>
                            </li>
                            <li>
                                <Link to="/#pricing" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Pricing
                                </Link>
                            </li>
                            <li>
                                <Link to="/dashboard" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    My Dashboard
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Support */}
                    <div>
                        <h4 className="text-white font-semibold mb-4 font-['Outfit']">Support</h4>
                        <ul className="space-y-2">
                            <li>
                                <a href="#" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Help Center
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Privacy Policy
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Terms of Service
                                </a>
                            </li>
                            <li>
                                <a href="#" className="text-white/60 hover:text-[#E6005C] transition-colors text-sm">
                                    Contact Us
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-[#2E1E31] mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="text-white/40 text-sm">
                        © 2024 Fleshsesh Academy. All rights reserved.
                    </p>
                    <p className="text-white/40 text-sm flex items-center gap-1">
                        Made with <Heart className="w-4 h-4 text-[#E6005C]" /> for deeper connections
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
