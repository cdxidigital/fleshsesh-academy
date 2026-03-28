import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';

const AgeVerification = ({ onVerified }) => {
    const [isVerified, setIsVerified] = useState(false);

    useEffect(() => {
        const verified = localStorage.getItem('fleshsesh_age_verified');
        if (verified === 'true') {
            setIsVerified(true);
            onVerified();
        }
    }, [onVerified]);

    const handleVerify = () => {
        localStorage.setItem('fleshsesh_age_verified', 'true');
        setIsVerified(true);
        onVerified();
    };

    const handleDeny = () => {
        window.location.href = 'https://www.google.com';
    };

    if (isVerified) return null;

    return (
        <div className="fixed inset-0 z-[100] bg-[#09050A] flex items-center justify-center p-4" data-testid="age-verification">
            <div className="max-w-lg w-full text-center">
                {/* Logo */}
                <div className="mb-8">
                    <img 
                        src="https://customer-assets.emergentagent.com/job_body-training-lab/artifacts/8iwd4um5_82bcdafd-9834-4c0f-b899-cc5eb2810f81.jpg"
                        alt="Fleshsesh Academy"
                        className="h-32 mx-auto"
                    />
                </div>

                {/* Warning Card */}
                <div className="bg-[#140C16] border border-[#2E1E31] rounded-2xl p-8 mb-6">
                    <div className="w-16 h-16 rounded-full bg-[#E6005C]/10 flex items-center justify-center mx-auto mb-6">
                        <ShieldCheck className="w-8 h-8 text-[#E6005C]" />
                    </div>
                    
                    <h2 className="text-2xl font-bold text-white font-['Outfit'] mb-4">
                        Age Verification Required
                    </h2>
                    
                    <p className="text-white/70 mb-6 leading-relaxed">
                        This website contains adult-oriented educational content about intimacy, relationships, and sexuality. 
                        You must be <span className="text-[#E6005C] font-semibold">18 years or older</span> to enter.
                    </p>

                    <div className="bg-[#09050A] rounded-xl p-4 mb-6 flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-[#FFB3D1] shrink-0 mt-0.5" />
                        <p className="text-white/60 text-sm text-left">
                            By entering, you confirm that you are at least 18 years old and consent to viewing adult educational content. 
                            This site uses cookies to remember your verification.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <button
                            onClick={handleVerify}
                            className="flex-1 bg-[#E6005C] hover:bg-[#E6005C]/90 text-white font-semibold py-4 px-6 rounded-full transition-all duration-300 hover:shadow-lg hover:shadow-[#E6005C]/25"
                            data-testid="verify-age-btn"
                        >
                            I am 18 or older — Enter
                        </button>
                        <button
                            onClick={handleDeny}
                            className="flex-1 bg-transparent border-2 border-[#2E1E31] text-white/60 font-semibold py-4 px-6 rounded-full transition-all duration-300 hover:bg-[#2E1E31]/50"
                            data-testid="deny-age-btn"
                        >
                            I am under 18 — Exit
                        </button>
                    </div>
                </div>

                <p className="text-white/40 text-xs">
                    By continuing, you agree to our Terms of Service and Privacy Policy.
                </p>
            </div>
        </div>
    );
};

export default AgeVerification;
