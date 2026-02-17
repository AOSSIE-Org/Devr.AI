import React from 'react';
import { Github, Twitter, Linkedin } from 'lucide-react';
import { useLocation, Link } from 'react-router-dom';

const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear();
    const location = useLocation();
    const isHomePage = location.pathname === '/';

    return (
        <footer className="relative bg-gradient-to-t from-dark via-dark-lighter to-dark py-12 overflow-hidden">
            {/* Background gradient overlays */}
            <div className="absolute inset-0 pointer-events-none">
                
                <div className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-blue-500/4 blur-3xl translate-x-1/2 translate-y-1/2"></div>
                <div className="absolute inset-0 bg-gradient-to-t from-transparent via-green-500/5 to-transparent opacity-50"></div>
            </div>

            <div className="container mx-auto px-6 relative z-10">
                <div className="flex flex-col md:flex-row justify-between items-start mb-8">
                    <div className="mb-6 md:mb-0">
                        <h3 className="text-2xl font-bold gradient-text mb-2">Devr.AI</h3>
                        <p className="text-gray-300 text-sm max-w-xs leading-relaxed">
                            Revolutionizing developer relations with AI-powered community management.
                        </p>
                    </div>
                    <div className="flex flex-row gap-12">
                        <div>
                            <h4 className="font-semibold mb-4 text-white bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">Links</h4>
                            <ul className="space-y-3">
                                <li><a href={isHomePage ? "#features" : "/#features"} className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">Features</a></li>
                                <li><a href={isHomePage ? "#how-it-works" : "/#how-it-works"} className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">How It Works</a></li>
                                <li><a href={isHomePage ? "#integrations" : "/#integrations"} className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">Integrations</a></li>
                                <li><a href={isHomePage ? "#waitlist" : "/#waitlist"} className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">Join Waitlist</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-4 text-white bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">Legal</h4>
                            <ul className="space-y-3">
                                <li><Link to="/privacy-policy" className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">Privacy Policy</Link></li>
                                <li><Link to="/terms-of-service" className="text-gray-300 hover:text-transparent hover:bg-gradient-to-r hover:from-green-400 hover:to-blue-500 hover:bg-clip-text text-sm transition-all duration-300 ease-in-out">Terms of Service</Link></li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div className="border-t border-gradient-to-r from-green-500/20 via-blue-500/20 to-green-500/20 pt-8 flex flex-col md:flex-row justify-between items-center" style={{borderImage: 'linear-gradient(90deg, rgba(34, 197, 94, 0.2), rgba(59, 130, 246, 0.2), rgba(34, 197, 94, 0.2)) 1'}}>
                    <p className="text-gray-400 text-sm mb-4 md:mb-0">
                        &copy; {currentYear} Devr.AI. All rights reserved.
                    </p>
                    <div className="flex space-x-6">
                        <a href="https://github.com/AOSSIE-Org/Devr.AI/" 
                           className="text-gray-300 hover:text-white hover:scale-110 transition-all duration-300 ease-in-out p-2 rounded-lg hover:bg-gradient-to-r hover:from-green-500/10 hover:to-blue-500/10 hover:shadow-lg hover:shadow-green-500/20" 
                           target='_blank' 
                           rel="noreferrer">
                            <Github size={20} />
                        </a>
                        <a href="https://x.com/aossie_org?lang=en" 
                           className="text-gray-300 hover:text-white hover:scale-110 transition-all duration-300 ease-in-out p-2 rounded-lg hover:bg-gradient-to-r hover:from-green-500/10 hover:to-blue-500/10 hover:shadow-lg hover:shadow-blue-500/20" 
                           target='_blank'
                           rel="noreferrer">
                            <Twitter size={20} />
                        </a>
                        <a href="https://www.linkedin.com/company/aossie/?originalSubdomain=au" 
                           className="text-gray-300 hover:text-white hover:scale-110 transition-all duration-300 ease-in-out p-2 rounded-lg hover:bg-gradient-to-r hover:from-green-500/10 hover:to-blue-500/10 hover:shadow-lg hover:shadow-green-500/20" 
                           target='_blank'
                           rel="noreferrer">
                            <Linkedin size={20} />
                        </a>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;