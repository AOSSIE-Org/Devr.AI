import React from 'react';
import { motion } from 'framer-motion';
import {
    Box,
    Container,
    Typography,
    Button,
    Chip,
    Stack
} from '@mui/material';
import {
    People as UsersIcon,
    Explore as ExploreIcon
} from '@mui/icons-material';

const Hero: React.FC = () => {
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2,
            },
        },
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 },
    };

    return (
        <Box
            component="section"
            className="relative min-h-screen flex items-center justify-center pt-32 pb-20 overflow-hidden"
            sx={{
                position: 'relative',
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                paddingTop: { xs: 8, md: 16 },
                paddingBottom: { xs: 5, md: 10 },
                overflow: 'hidden',
            }}
        >
            {/* Simplified Background - Modern & Clean */}
            <Box
                className="absolute inset-0 pointer-events-none"
                sx={{
                    position: 'absolute',
                    inset: 0,
                    pointerEvents: 'none',
                }}
            >
                {/* Base gradient */}
                <Box
                    className="absolute inset-0 bg-gradient-to-br from-dark via-dark to-gray-900"
                    sx={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(to bottom right, #09090b, #09090b, #111827)',
                    }}
                />

                {/* Subtle accent gradients with blue */}
                <Box
                    className="absolute top-0 left-0 w-[800px] h-[800px] rounded-full bg-green-600/10 blur-[120px] -translate-x-1/2 -translate-y-1/2"
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '800px',
                        height: '800px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(22, 163, 74, 0.1)',
                        filter: 'blur(120px)',
                        transform: 'translate(-50%, -50%)',
                    }}
                />
                <Box
                    className="absolute bottom-0 right-0 w-[600px] h-[600px] rounded-full bg-blue-500/8 blur-[100px] translate-x-1/3 translate-y-1/3"
                    sx={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                        width: '600px',
                        height: '600px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(59, 130, 246, 0.08)',
                        filter: 'blur(100px)',
                        transform: 'translate(33%, 33%)',
                    }}
                />
                {/* Additional blue accent */}
                <Box
                    sx={{
                        position: 'absolute',
                        top: '30%',
                        right: '10%',
                        width: '400px',
                        height: '400px',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(37, 99, 235, 0.06)',
                        filter: 'blur(80px)',
                    }}
                />

                {/* Grid pattern for texture */}
                <Box
                    className="absolute inset-0 bg-grid-pattern opacity-40"
                    sx={{
                        position: 'absolute',
                        inset: 0,
                        backgroundImage: `
                            linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px)
                        `,
                        backgroundSize: '40px 40px',
                        opacity: 0.4,
                    }}
                />

                {/* Top gradient fade with blue */}
                <Box
                    className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-green-500/5 to-transparent"
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        height: '8rem',
                        background: 'linear-gradient(to bottom, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.03), transparent)',
                    }}
                />
            </Box>

            {/* Bottom fade for smooth transition */}
            <Box
                className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-b from-transparent to-dark pointer-events-none"
                sx={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '10rem',
                    background: 'linear-gradient(to bottom, transparent, #09090b)',
                    pointerEvents: 'none',
                }}
            />

            <Container maxWidth="lg" className="z-10" sx={{ position: 'relative', zIndex: 10 }}>
                <Box
                    component={motion.div}
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="max-w-6xl mx-auto text-center"
                    sx={{
                        maxWidth: '72rem',
                        margin: '0 auto',
                        textAlign: 'center',
                    }}
                >
                    {/* Badge */}
                    <Box
                        component={motion.div}
                        variants={item}
                        sx={{ mb: 4 }}
                    >
                        <Chip
                            label="Developer Experience Reimagined"
                            sx={{
                                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(59, 130, 246, 0.08))',
                                color: '#4ade80',
                                fontSize: '1rem',
                                fontWeight: 600,
                                padding: '12px 24px',
                                height: 'auto',
                                border: '1px solid rgba(59, 130, 246, 0.3)',
                                borderRadius: '9999px',
                                boxShadow: '0 0 20px rgba(59, 130, 246, 0.1)',
                                '& .MuiChip-label': {
                                    padding: 0,
                                },
                            }}
                        />
                    </Box>

                    {/* Hero Heading - Larger, Bolder */}
                    <Typography
                        component={motion.h1}
                        variants={item}
                        variant="h1"
                        className="font-extrabold mb-8 tracking-tight"
                        sx={{
                            fontSize: { xs: '3rem', md: '4.5rem', lg: '6rem' },
                            fontWeight: 800,
                            mb: 4,
                            letterSpacing: '-0.03em',
                            lineHeight: 1.1,
                        }}
                    >
                        AI-Powered{' '}
                        <Box
                            component="span"
                            className="gradient-text"
                            sx={{
                                background: 'linear-gradient(to right, #4ade80, #3b82f6, #22d3ee, #2563eb, #10b981)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                            }}
                        >
                            Developer Relations
                        </Box>{' '}
                        Assistant
                    </Typography>

                    {/* Description - Better spacing and readability */}
                    <Typography
                        component={motion.p}
                        variants={item}
                        variant="h6"
                        className="text-gray-300 mb-10 max-w-4xl mx-auto leading-relaxed"
                        sx={{
                            fontSize: { xs: '1.125rem', md: '1.25rem', lg: '1.5rem' },
                            color: 'rgba(209, 213, 219, 1)',
                            mb: 5,
                            maxWidth: '56rem',
                            marginX: 'auto',
                            lineHeight: 1.75,
                        }}
                    >
                        Devr.AI revolutionizes open-source community management by automating engagement,
                        streamlining onboarding, and delivering real-time project updates across Discord,
                        Slack, GitHub, CLI, Web Widget, and more.
                        <br />
                        <Box
                            component="span"
                            className="text-primary font-semibold mt-2 inline-block"
                            sx={{
                                color: '#22c55e',
                                fontWeight: 600,
                                marginTop: '0.5rem',
                                display: 'inline-block',
                            }}
                        >
                            Personalized, multi-platform, and analytics-driven.
                        </Box>
                    </Typography>

                    {/* CTAs - Enhanced styling */}
                    <Stack
                        component={motion.div}
                        variants={item}
                        direction={{ xs: 'column', sm: 'row' }}
                        spacing={3}
                        justifyContent="center"
                        sx={{ mb: 8 }}
                    >
                        <Button
                            component="a"
                            href="#waitlist"
                            variant="contained"
                            startIcon={<UsersIcon />}
                            className="btn-primary"
                            sx={{
                                background: 'linear-gradient(135deg, #22c55e 0%, #3b82f6 50%, #16a34a 100%)',
                                backgroundSize: '200% auto',
                                color: 'white',
                                fontWeight: 600,
                                fontSize: '1.125rem',
                                padding: '16px 32px',
                                borderRadius: '12px',
                                textTransform: 'none',
                                boxShadow: '0 4px 14px 0 rgba(34, 197, 94, 0.3), 0 1px 3px 0 rgba(0, 0, 0, 0.1)',
                                border: '1px solid rgba(34, 197, 94, 0.4)',
                                textDecoration: 'none',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                    backgroundPosition: 'right center',
                                    boxShadow: '0 12px 32px 0 rgba(59, 130, 246, 0.4), 0 6px 16px 0 rgba(34, 197, 94, 0.3)',
                                    transform: 'translateY(-3px) scale(1.02)',
                                    borderColor: 'rgba(59, 130, 246, 0.5)',
                                },
                            }}
                        >
                            Join the Waitlist
                        </Button>
                        <Button
                            component="a"
                            href="#features"
                            variant="outlined"
                            startIcon={<ExploreIcon />}
                            className="btn-secondary"
                            sx={{
                                background: 'linear-gradient(135deg, rgba(39, 39, 42, 1) 0%, rgba(24, 24, 27, 1) 100%)',
                                color: 'white',
                                fontWeight: 600,
                                fontSize: '1.125rem',
                                padding: '16px 32px',
                                borderRadius: '12px',
                                textTransform: 'none',
                                border: '1px solid rgba(63, 63, 70, 1)',
                                boxShadow: '0 2px 8px 0 rgba(0, 0, 0, 0.15), inset 0 1px 0 0 rgba(255, 255, 255, 0.05)',
                                textDecoration: 'none',
                                '&:hover': {
                                    background: 'linear-gradient(135deg, rgba(63, 63, 70, 1) 0%, rgba(39, 39, 42, 1) 100%)',
                                    borderColor: 'rgba(82, 82, 91, 1)',
                                    boxShadow: '0 6px 20px 0 rgba(0, 0, 0, 0.25), inset 0 1px 0 0 rgba(255, 255, 255, 0.1)',
                                    transform: 'translateY(-3px) scale(1.02)',
                                },
                            }}
                        >
                            Explore Features
                        </Button>
                    </Stack>

                    {/* Dashboard Preview - Enhanced presentation */}
                    <Box
                        component={motion.div}
                        variants={item}
                        className="max-w-6xl mx-auto"
                        sx={{
                            maxWidth: '72rem',
                            marginX: 'auto',
                        }}
                    >
                        <Box
                            className="relative rounded-2xl overflow-hidden border border-gray-700 shadow-2xl elevation-xl interactive-lift"
                            sx={{
                                position: 'relative',
                                borderRadius: '16px',
                                overflow: 'hidden',
                                border: '1px solid rgba(63, 63, 70, 1)',
                                boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                                },
                            }}
                        >
                            {/* Subtle glow effect with blue */}
                            <Box
                                className="absolute inset-0 bg-gradient-to-t from-green-500/5 via-transparent to-transparent pointer-events-none"
                                sx={{
                                    position: 'absolute',
                                    inset: 0,
                                    background: 'linear-gradient(to top, rgba(34, 197, 94, 0.05), rgba(59, 130, 246, 0.03), transparent)',
                                    pointerEvents: 'none',
                                }}
                            />

                            {/* Bottom fade */}
                            <Box
                                className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-dark via-dark/50 to-transparent z-10"
                                sx={{
                                    position: 'absolute',
                                    left: 0,
                                    right: 0,
                                    bottom: 0,
                                    height: '8rem',
                                    background: 'linear-gradient(to top, #09090b, rgba(9, 9, 11, 0.5), transparent)',
                                    zIndex: 10,
                                }}
                            />

                            <Box
                                component="img"
                                src="/dashboard_preview.png"
                                alt="Devr.AI Dashboard Preview"
                                className="w-full h-auto"
                                sx={{
                                    width: '100%',
                                    height: 'auto',
                                    display: 'block',
                                }}
                            />
                        </Box>
                    </Box>
                </Box>
            </Container>
        </Box>
    );
};

export default Hero;