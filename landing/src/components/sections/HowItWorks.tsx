import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    BrainCircuit,
    Workflow,
    Database,
    GitMerge,
    ArrowRight,
    Github,
    Slack,
    MessageSquare,
    Users,
    Shield,
    Layers,
    Server,
    Code,
    FileCode,
    BarChart3,
    ShieldCheck,
    KeyRound,
    Brain,
    BookOpen,
    FileText,
    Sparkles,
    GitBranch,
    FileBarChart2,
    TrendingUp,
    Smile,
    GraduationCap,
    Rocket,
    Code2,
    LayoutDashboard,
    Globe,
    Terminal
} from 'lucide-react';

const HowItWorks: React.FC = () => {
    const [isDesktop, setIsDesktop] = useState(false);

    useEffect(() => {
        const checkIfDesktop = () => {
            setIsDesktop(window.innerWidth >= 768);
        };

        checkIfDesktop();

        window.addEventListener('resize', checkIfDesktop);

        return () => window.removeEventListener('resize', checkIfDesktop);
    }, []);

    const steps = [
        {
            icon: <Layers size={32} />,
            title: 'API Gateway',
            description: 'Handles authentication, request routing, rate limiting, and validation for all incoming requests.',
            color: 'from-green-500 to-blue-500',
        },
        {
            icon: <Workflow size={32} />,
            title: 'Workflow Orchestrator',
            description: 'Manages workflows, asynchronous tasks, and context for ongoing conversations.',
            color: 'from-blue-500 to-purple-500',
        },
        {
            icon: <BrainCircuit size={32} />,
            title: 'AI Service Layer',
            description: 'LLM integration, knowledge retrieval, code understanding, documentation assistant, content generation, and personalization.',
            color: 'from-purple-500 to-pink-500',
        },
        {
            icon: <GitMerge size={32} />,
            title: 'Integration Services',
            description: 'Adapters for Discord, Slack, GitHub, Discourse, CLI, and Web Widget. Handles webhooks, events, and authentication.',
            color: 'from-pink-500 to-orange-500',
        },
        {
            icon: <Database size={32} />,
            title: 'Data Storage Layer',
            description: 'Vector DB for semantic search, relational DB for structured data, document store for history, and user profiles.',
            color: 'from-orange-500 to-amber-500',
        },
        {
            icon: <BarChart3 size={32} />,
            title: 'Analytics & Education',
            description: 'Real-time metrics, reporting, trend analysis, sentiment, interactive tutorials, and live code assistance.',
            color: 'from-amber-500 to-rose-500',
        }
    ];

    const TooltipBox = ({ children, tooltip }: { children: React.ReactNode, tooltip: string }) => {
        const [showTooltip, setShowTooltip] = useState(false);

        return (
            <div
                className="relative"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                onTouchStart={() => setShowTooltip(true)}
                onTouchEnd={() => setTimeout(() => setShowTooltip(false), 1500)}
            >
                {children}
                {showTooltip && (
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 mt-1 z-50 bg-gray-900 text-white text-xs p-2 rounded-md shadow-lg w-44 md:w-48">
                        {tooltip}
                    </div>
                )}
            </div>
        );
    };

    const SectionTitle = ({ title, color }: { title: string, color: string }) => (
        <div className="w-full text-center mb-2">
            <span className={`text-xs md:text-sm font-semibold uppercase tracking-wider ${color} border-b border-dashed border-opacity-60 pb-1 px-2 md:px-4`}>
                {title}
            </span>
        </div>
    );

    return (
        <section id="how-it-works" className="section bg-gradient-to-t from-dark via-gray-900 to-dark">
            <div className="container mx-auto px-3 md:px-6">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-12 md:mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        How <span className="gradient-text">It Works</span>
                    </h2>
                    <p className="text-gray-400 max-w-2xl mx-auto text-sm md:text-base">
                        Devr.AI follows a microservices architecture designed for efficiency, scalability, and intelligent operations.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-10 max-w-5xl mx-auto">
                    {steps.map((step, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.6, delay: index * 0.1 }}
                            className="relative"
                        >
                            <div className="flex gap-3 md:gap-4 items-start">
                                <div className={`relative z-10 p-2 md:p-3 rounded-lg bg-gradient-to-br ${step.color} text-white shadow-lg`}>
                                    {step.icon}
                                </div>
                                <div>
                                    <h3 className="text-base md:text-lg font-semibold mb-1">{step.title}</h3>
                                    <p className="text-xs md:text-sm text-gray-400">{step.description}</p>
                                </div>
                            </div>

                            {index < steps.length - 1 && (
                                <>
                                    <div className="hidden md:block">
                                        {step.title !== "Contributor Management" &&
                                            step.title !== "Maintainer Support" &&
                                            step.title !== "Data Storage Layer" && (
                                                <motion.div
                                                    initial={{ opacity: 0, height: 0 }}
                                                    whileInView={{ opacity: 1, height: '100%' }}
                                                    viewport={{ once: true }}
                                                    transition={{ duration: 0.8, delay: 0.4 + index * 0.1 }}
                                                    className={`absolute top-[46px] left-[24px] w-px bg-gradient-to-b ${step.color} opacity-70`}
                                                    style={{ maxHeight: '120px', zIndex: 1 }}
                                                />
                                            )}

                                        {step.title === "Knowledge Retrieval" && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                whileInView={{ opacity: 1, height: '100%' }}
                                                viewport={{ once: true }}
                                                transition={{ duration: 0.8, delay: 0.4 + index * 0.1 }}
                                                className={`absolute top-[46px] left-[24px] w-px bg-gradient-to-b ${step.color} opacity-70`}
                                                style={{ maxHeight: '120px', zIndex: 1 }}
                                            />
                                        )}
                                    </div>

                                    <div className="md:hidden absolute left-[16px] md:left-[24px] top-[38px] md:top-[46px] h-full">
                                        <div className={`h-full w-px bg-gradient-to-b ${step.color} opacity-70`} style={{ zIndex: 1 }}></div>
                                    </div>
                                </>
                            )}
                        </motion.div>
                    ))}
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    className="mt-12 md:mt-16 max-w-4xl mx-auto"
                >
                    <h3 className="text-lg md:text-xl font-semibold text-center mb-4 md:mb-6">System Architecture</h3>

                    <div className="bg-dark-card border border-gray-700 rounded-xl p-3 pb-10 md:p-8 md:pb-16 shadow-lg overflow-hidden">
                        <div className="flex flex-col space-y-3 md:space-y-6">
                            {/* External Platforms */}
                            <SectionTitle title="External Platforms" color="text-teal-400" />
                            <div className="grid grid-cols-3 gap-1 md:gap-3">
                                <TooltipBox tooltip="GitHub platform integration for code, issues, and PRs. Connect repositories for automated workflows.">
                                    <div className="bg-teal-900/40 border border-teal-500/60 rounded-lg p-1.5 md:p-4 flex flex-col items-center justify-center text-center hover:border-teal-400 transition-colors shadow-md">
                                        <Github className="mb-1 md:mb-2 text-teal-400" size={18} />
                                        <span className="text-2xs md:text-sm font-medium text-teal-300">GitHub</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Discord integration for community chat and support. Real-time bot responses and interaction.">
                                    <div className="bg-teal-900/40 border border-teal-500/60 rounded-lg p-1.5 md:p-4 flex flex-col items-center justify-center text-center hover:border-teal-400 transition-colors shadow-md">
                                        <MessageSquare className="mb-1 md:mb-2 text-teal-400" size={18} />
                                        <span className="text-2xs md:text-sm font-medium text-teal-300">Discord</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Slack integration for team and community collaboration. Notifications and command interface.">
                                    <div className="bg-teal-900/40 border border-teal-500/60 rounded-lg p-1.5 md:p-4 flex flex-col items-center justify-center text-center hover:border-teal-400 transition-colors shadow-md">
                                        <Slack className="mb-1 md:mb-2 text-teal-400" size={18} />
                                        <span className="text-2xs md:text-sm font-medium text-teal-300">Slack</span>
                                    </div>
                                </TooltipBox>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-teal-400/70" size={16} />
                            </div>

                            {/* Integration Services */}
                            <SectionTitle title="Integration Services" color="text-pink-400" />
                            {/* Desktop view - all 5 in one row */}
                            <div className="hidden md:grid md:grid-cols-5 gap-3">
                                <TooltipBox tooltip="GitHub Service adapter for repository integration and webhooks.">
                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                        <GitBranch className="mb-2 text-pink-400" size={16} />
                                        <span className="text-xs font-medium text-pink-300">GitHub</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Discord Service adapter for community bot functionality.">
                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                        <MessageSquare className="mb-2 text-pink-400" size={16} />
                                        <span className="text-xs font-medium text-pink-300">Discord</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Slack Service adapter for workspace integration and commands.">
                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                        <Slack className="mb-2 text-pink-400" size={16} />
                                        <span className="text-xs font-medium text-pink-300">Slack</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="CLI integration for command-line developers with local tools.">
                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                        <Terminal className="mb-2 text-pink-400" size={16} />
                                        <span className="text-xs font-medium text-pink-300">CLI</span>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Web widget for embedding on documentation sites and websites.">
                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-4 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                        <Globe className="mb-2 text-pink-400" size={16} />
                                        <span className="text-xs font-medium text-pink-300">Web</span>
                                    </div>
                                </TooltipBox>
                            </div>

                            {/* Mobile view - split into two rows (3+2) */}
                            <div className="md:hidden">
                                <div className="grid grid-cols-3 gap-2 mb-2">
                                    <TooltipBox tooltip="GitHub Service adapter for repository integration and webhooks.">
                                        <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                            <GitBranch className="mb-1 text-pink-400" size={16} />
                                            <span className="text-[10px] font-medium text-pink-300">GitHub</span>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Discord Service adapter for community bot functionality.">
                                        <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                            <MessageSquare className="mb-1 text-pink-400" size={16} />
                                            <span className="text-[10px] font-medium text-pink-300">Discord</span>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Slack Service adapter for workspace integration and commands.">
                                        <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                            <Slack className="mb-1 text-pink-400" size={16} />
                                            <span className="text-[10px] font-medium text-pink-300">Slack</span>
                                        </div>
                                    </TooltipBox>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <TooltipBox tooltip="CLI integration for command-line developers with local tools.">
                                        <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                            <Terminal className="mb-1 text-pink-400" size={16} />
                                            <span className="text-[10px] font-medium text-pink-300">CLI</span>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Web widget for embedding on documentation sites and websites.">
                                        <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 flex flex-col items-center justify-center text-center hover:border-pink-400 transition-colors shadow-md">
                                            <Globe className="mb-1 text-pink-400" size={16} />
                                            <span className="text-[10px] font-medium text-pink-300">Web</span>
                                        </div>
                                    </TooltipBox>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-pink-400/70" size={16} />
                            </div>

                            {/* Frontend & Backend */}
                            <div className="grid grid-cols-2 gap-2 md:gap-4">
                                <div className="space-y-2 md:space-y-3">
                                    <SectionTitle title="React Frontend" color="text-purple-400" />
                                    <TooltipBox tooltip="React-based dashboard for analytics, settings, and management. Visualizes community health metrics.">
                                        <div className="bg-purple-900/40 border border-purple-500/60 rounded-lg p-2 md:p-4 flex flex-col items-center justify-center text-center hover:border-purple-400 transition-colors shadow-md">
                                            <LayoutDashboard className="mb-1 md:mb-2 text-purple-400" size={18} />
                                            <span className="text-2xs md:text-sm font-medium text-purple-300">Dashboard</span>
                                        </div>
                                    </TooltipBox>
                                </div>
                                <div className="space-y-2 md:space-y-3">
                                    <SectionTitle title="Backend API" color="text-green-400" />
                                    <TooltipBox tooltip="FastAPI Gateway handles all backend requests, authentication, and routing.">
                                        <div className="bg-green-900/40 border border-green-500/60 rounded-lg p-2 md:p-4 flex flex-col items-center justify-center text-center hover:border-green-400 transition-colors shadow-md">
                                            <Server className="mb-1 md:mb-2 text-green-400" size={18} />
                                            <span className="text-2xs md:text-sm font-medium text-green-300">FastAPI Gateway</span>
                                        </div>
                                    </TooltipBox>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-green-400/70" size={16} />
                            </div>

                            {/* Authentication */}
                            <SectionTitle title="Authentication" color="text-purple-400" />
                            <div className="grid grid-cols-2 gap-1 md:gap-3">
                                <TooltipBox tooltip="GitHub OAuth authentication for user and repository access.">
                                    <div className="bg-purple-900/40 border border-purple-500/60 rounded-lg p-2 md:p-4 text-center hover:border-purple-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <ShieldCheck className="text-purple-400" size={18} />
                                        </div>
                                        <h4 className="font-medium text-2xs md:text-sm text-purple-300">GitHub Auth</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="OAuth2 authentication for secure user management and permissions.">
                                    <div className="bg-purple-900/40 border border-purple-500/60 rounded-lg p-2 md:p-4 text-center hover:border-purple-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <KeyRound className="text-purple-400" size={18} />
                                        </div>
                                        <h4 className="font-medium text-2xs md:text-sm text-purple-300">OAuth2 Auth</h4>
                                    </div>
                                </TooltipBox>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-purple-400/70" size={16} />
                            </div>

                            {/* Core Processing */}
                            <SectionTitle title="Core Processing Engine" color="text-amber-400" />
                            <div className="grid grid-cols-2 gap-1 md:gap-3">
                                <TooltipBox tooltip="Workflow orchestrator manages tasks and orchestrates service interactions.">
                                    <div className="bg-amber-900/40 border border-amber-500/60 rounded-lg p-1.5 md:p-4 text-center hover:border-amber-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <Workflow className="text-amber-400" size={18} />
                                        </div>
                                        <h4 className="font-medium text-2xs md:text-sm text-amber-300">
                                            <span className="hidden md:inline">Workflow Orchestrator</span>
                                            <span className="md:hidden">Workflow</span>
                                        </h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Task queue for asynchronous processing and job management.">
                                    <div className="bg-amber-900/40 border border-amber-500/60 rounded-lg p-1.5 md:p-4 text-center hover:border-amber-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <Server className="text-amber-400" size={18} />
                                        </div>
                                        <h4 className="font-medium text-2xs md:text-sm text-amber-300">Task Queue</h4>
                                    </div>
                                </TooltipBox>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-amber-400/70" size={16} />
                            </div>

                            {/* AI Service Layer */}
                            <SectionTitle title="AI Service Layer" color="text-blue-400" />
                            {/* Desktop view - all 5 in one row */}
                            <div className="hidden md:grid md:grid-cols-5 gap-3">
                                <TooltipBox tooltip="Large Language Model service powered by LangChain for AI interactions.">
                                    <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-4 text-center hover:border-blue-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <Brain className="text-blue-400" size={20} />
                                        </div>
                                        <h4 className="font-medium text-sm text-blue-300">LLM</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Knowledge retrieval from documentation and code repositories.">
                                    <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-4 text-center hover:border-blue-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <BookOpen className="text-blue-400" size={16} />
                                        </div>
                                        <h4 className="font-medium text-sm text-blue-300">Knowledge</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Code understanding and analysis service for technical assistance.">
                                    <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-4 text-center hover:border-blue-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <Code2 className="text-blue-400" size={16} />
                                        </div>
                                        <h4 className="font-medium text-sm text-blue-300">Code</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Documentation assistant for navigation and content generation.">
                                    <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-4 text-center hover:border-blue-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <FileText className="text-blue-400" size={16} />
                                        </div>
                                        <h4 className="font-medium text-sm text-blue-300">Docs</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Content generator for blogs, docs, and technical materials.">
                                    <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-4 text-center hover:border-blue-400 transition-colors shadow-md">
                                        <div className="flex justify-center mb-1">
                                            <Sparkles className="text-blue-400" size={16} />
                                        </div>
                                        <h4 className="font-medium text-sm text-blue-300">Content</h4>
                                    </div>
                                </TooltipBox>
                            </div>

                            {/* Mobile view - split into two rows (3+2) */}
                            <div className="md:hidden">
                                <div className="grid grid-cols-3 gap-2 mb-2">
                                    <TooltipBox tooltip="Large Language Model service powered by LangChain for AI interactions.">
                                        <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 text-center hover:border-blue-400 transition-colors shadow-md">
                                            <div className="flex justify-center mb-1">
                                                <Brain className="text-blue-400" size={16} />
                                            </div>
                                            <h4 className="font-medium text-[10px] text-blue-300">LLM</h4>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Knowledge retrieval from documentation and code repositories.">
                                        <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 text-center hover:border-blue-400 transition-colors shadow-md">
                                            <div className="flex justify-center mb-1">
                                                <BookOpen className="text-blue-400" size={16} />
                                            </div>
                                            <h4 className="font-medium text-[10px] text-blue-300">Knowledge</h4>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Code understanding and analysis service for technical assistance.">
                                        <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 text-center hover:border-blue-400 transition-colors shadow-md">
                                            <div className="flex justify-center mb-1">
                                                <Code2 className="text-blue-400" size={16} />
                                            </div>
                                            <h4 className="font-medium text-[10px] text-blue-300">Code</h4>
                                        </div>
                                    </TooltipBox>
                                </div>
                                <div className="grid grid-cols-2 gap-2">
                                    <TooltipBox tooltip="Documentation assistant for navigation and content generation.">
                                        <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 text-center hover:border-blue-400 transition-colors shadow-md">
                                            <div className="flex justify-center mb-1">
                                                <FileText className="text-blue-400" size={16} />
                                            </div>
                                            <h4 className="font-medium text-[10px] text-blue-300">Docs</h4>
                                        </div>
                                    </TooltipBox>
                                    <TooltipBox tooltip="Content generator for blogs, docs, and technical materials.">
                                        <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 text-center hover:border-blue-400 transition-colors shadow-md">
                                            <div className="flex justify-center mb-1">
                                                <Sparkles className="text-blue-400" size={16} />
                                            </div>
                                            <h4 className="font-medium text-[10px] text-blue-300">Content</h4>
                                        </div>
                                    </TooltipBox>
                                </div>
                            </div>

                            <div className="flex justify-center">
                                <ArrowRight className="rotate-90 text-blue-400/70" size={16} />
                            </div>

                            {/* Data Storage */}
                            <SectionTitle title="Data Storage Layer" color="text-indigo-400" />
                            <div className="grid grid-cols-3 gap-1 md:gap-3">
                                <TooltipBox tooltip="Supabase provides storage for vectors, relational data, and documents.">
                                    <div className="bg-indigo-900/40 border border-indigo-500/60 rounded-lg p-2 md:p-4 text-center hover:border-indigo-400 transition-colors shadow-md h-[70px] md:h-auto flex flex-col justify-center">
                                        <div className="flex justify-center mb-1">
                                            <Database className="text-indigo-400" size={16} md:size={18} />
                                        </div>
                                        <h4 className="font-medium text-[10px] md:text-sm text-indigo-300">Supabase</h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="Vector and relational database for semantic search and structured data.">
                                    <div className="bg-indigo-900/40 border border-indigo-500/60 rounded-lg p-2 md:p-4 text-center hover:border-indigo-400 transition-colors shadow-md h-[70px] md:h-auto flex flex-col justify-center">
                                        <div className="flex justify-center mb-1">
                                            <Database className="text-indigo-400" size={16} md:size={18} />
                                        </div>
                                        <h4 className="font-medium text-[10px] md:text-sm text-indigo-300">
                                            <span className="hidden md:inline">Vector & Relational DB</span>
                                            <span className="md:hidden">Vector DB</span>
                                        </h4>
                                    </div>
                                </TooltipBox>
                                <TooltipBox tooltip="User profiles and preferences database for personalization.">
                                    <div className="bg-indigo-900/40 border border-indigo-500/60 rounded-lg p-2 md:p-4 text-center hover:border-indigo-400 transition-colors shadow-md h-[70px] md:h-auto flex flex-col justify-center">
                                        <div className="flex justify-center mb-1">
                                            <Users className="text-indigo-400" size={16} md:size={18} />
                                        </div>
                                        <h4 className="font-medium text-[10px] md:text-sm text-indigo-300"> User Profile</h4>
                                    </div>
                                </TooltipBox>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                                {/* Analytics Engine */}
                                <div className="space-y-3">
                                    <SectionTitle title="Analytics Engine" color="text-blue-400" />
                                    <div className="grid grid-cols-2 gap-2">
                                        <TooltipBox tooltip="Metrics calculator for analytics and community insights.">
                                            <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 md:p-3 text-center hover:border-blue-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <BarChart3 className="text-blue-400" size={22} />
                                                </div>
                                                <h4 className="font-medium text-xs text-blue-300">Metrics</h4>
                                            </div>
                                        </TooltipBox>
                                        <TooltipBox tooltip="Report generator creates visualizations and periodic summaries.">
                                            <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 md:p-3 text-center hover:border-blue-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <FileBarChart2 className="text-blue-400" size={22} />
                                                </div>
                                                <h4 className="font-medium text-xs text-blue-300">Reports</h4>
                                            </div>
                                        </TooltipBox>
                                        <TooltipBox tooltip="Trend analyzer identifies patterns and predicts community health.">
                                            <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 md:p-3 text-center hover:border-blue-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <TrendingUp className="text-blue-400" size={22} />
                                                </div>
                                                <h4 className="font-medium text-xs text-blue-300">Trends</h4>
                                            </div>
                                        </TooltipBox>
                                        <TooltipBox tooltip="Sentiment analysis tracks community satisfaction and engagement.">
                                            <div className="bg-blue-900/40 border border-blue-500/60 rounded-lg p-2 md:p-3 text-center hover:border-blue-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <Smile className="text-blue-400" size={22} />
                                                </div>
                                                <h4 className="font-medium text-xs text-blue-300">Sentiment</h4>
                                            </div>
                                        </TooltipBox>
                                    </div>
                                </div>

                                {/* Education & Advocacy */}
                                <div className="space-y-3">
                                    <SectionTitle title="Education & Advocacy" color="text-pink-400" />
                                    {/* Desktop view - split into two rows (2+1) */}
                                    <div className="hidden md:block">
                                        <div className="grid grid-cols-2 gap-3 mb-3">
                                            <TooltipBox tooltip="Interactive tutorials provide guided learning experiences.">
                                                <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-3 text-center hover:border-pink-400 transition-colors shadow-md">
                                                    <div className="flex justify-center mb-1">
                                                        <GraduationCap className="text-pink-400" size={20} />
                                                    </div>
                                                    <h4 className="font-medium text-sm text-pink-300">Tutorials</h4>
                                                </div>
                                            </TooltipBox>
                                            <TooltipBox tooltip="Quickstart generator for personalized onboarding materials.">
                                                <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-3 text-center hover:border-pink-400 transition-colors shadow-md">
                                                    <div className="flex justify-center mb-1">
                                                        <Rocket className="text-pink-400" size={20} />
                                                    </div>
                                                    <h4 className="font-medium text-sm text-pink-300">Quickstart</h4>
                                                </div>
                                            </TooltipBox>
                                        </div>
                                        <div className="flex justify-center">
                                            <div className="w-1/2">
                                                <TooltipBox tooltip="Live code assistance for real-time developer support.">
                                                    <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-3 text-center hover:border-pink-400 transition-colors shadow-md">
                                                        <div className="flex justify-center mb-1">
                                                            <Code2 className="text-pink-400" size={20} />
                                                        </div>
                                                        <h4 className="font-medium text-sm text-pink-300">Live Help</h4>
                                                    </div>
                                                </TooltipBox>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Mobile view - all 3 in one row */}
                                    <div className="md:hidden grid grid-cols-3 gap-2">
                                        <TooltipBox tooltip="Interactive tutorials provide guided learning experiences.">
                                            <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 text-center hover:border-pink-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <GraduationCap className="text-pink-400" size={16} />
                                                </div>
                                                <h4 className="font-medium text-[10px] text-pink-300">Tutorials</h4>
                                            </div>
                                        </TooltipBox>
                                        <TooltipBox tooltip="Quickstart generator for personalized onboarding materials.">
                                            <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 text-center hover:border-pink-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <Rocket className="text-pink-400" size={16} />
                                                </div>
                                                <h4 className="font-medium text-[10px] text-pink-300">Quickstart</h4>
                                            </div>
                                        </TooltipBox>
                                        <TooltipBox tooltip="Live code assistance for real-time developer support.">
                                            <div className="bg-pink-900/40 border border-pink-500/60 rounded-lg p-2 text-center hover:border-pink-400 transition-colors shadow-md">
                                                <div className="flex justify-center mb-1">
                                                    <Code2 className="text-pink-400" size={16} />
                                                </div>
                                                <h4 className="font-medium text-[10px] text-pink-300">Live Help</h4>
                                            </div>
                                        </TooltipBox>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-4 text-center text-[10px] md:text-xs text-gray-400">
                        <p>Hover over components to learn more about their role in the architecture</p>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default HowItWorks;