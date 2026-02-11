import React from 'react';
import { motion } from 'framer-motion';
import { 
    Box, 
    Container, 
    Typography, 
    Link as MuiLink, 
    IconButton, 
    Divider,
    Stack
} from '@mui/material';
import { 
    GitHub as GitHubIcon, 
    Twitter as TwitterIcon, 
    LinkedIn as LinkedInIcon, 
    KeyboardArrowUp as ArrowUpIcon 
} from '@mui/icons-material';
import { useLocation, Link, useNavigate } from 'react-router-dom';

const Footer: React.FC = () => {
    const currentYear = new Date().getFullYear();
    const location = useLocation();
    const isHomePage = location.pathname === '/';

    const navigate = useNavigate();

    // QuickLink component to handle hash navigation/smooth scroll via router
    const QuickLink: React.FC<{ link: { label: string; href: string }; isHomePage: boolean }> = ({ link, isHomePage }) => {
        const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
            e.preventDefault();

            // Construct target href (preserve hash). On non-home pages we prefix with '/'
            const target = isHomePage ? link.href : `/${link.href}`;

            // Navigate so location.hash updates; scrolling is handled by Navbar's useEffect
            navigate(target);
        };

        return (
            <MuiLink
                href={link.href}
                onClick={(e) => handleClick(e)}
                className="text-gray-400 hover:text-green-400 text-sm transition-colors duration-300 inline-flex items-center gap-2 group"
                sx={{
                    color: 'rgba(161, 161, 170, 1)',
                    fontSize: '0.875rem',
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px',
                    position: 'relative',
                    transition: 'color 0.3s ease',
                    '&:hover': {
                        color: 'rgba(34, 197, 94, 1)',
                    },
                    '&::before': {
                        content: '""',
                        width: 0,
                        height: '2px',
                        background: 'linear-gradient(to right, #4ade80, #22d3ee)',
                        transition: 'width 0.3s ease',
                        position: 'absolute',
                        left: 0,
                        bottom: '-2px',
                    },
                    '&:hover::before': {
                        width: '16px',
                    },
                }}
            >
                {link.label}
            </MuiLink>
        );
    };

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
                delayChildren: 0.2,
            },
        },
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
    };

    const socialLinks = [
        {
            icon: <GitHubIcon />,
            href: 'https://github.com/AOSSIE-Org/Devr.AI/',
            label: 'GitHub',
            color: 'hover:text-green-400'
        },
        {
            icon: <TwitterIcon />,
            href: 'https://x.com/aossie_org?lang=en',
            label: 'Twitter',
            color: 'hover:text-cyan-400'
        },
        {
            icon: <LinkedInIcon />,
            href: 'https://www.linkedin.com/company/aossie/?originalSubdomain=au',
            label: 'LinkedIn',
            color: 'hover:text-green-400'
        },
    ];

    const quickLinks = [
        { label: 'Features', href: '#features' },
        { label: 'How It Works', href: '#how-it-works' },
        { label: 'Integrations', href: '#integrations' },
        { label: 'Join Waitlist', href: '#waitlist' },
    ];

    const legalLinks = [
        { label: 'Privacy Policy', to: '/privacy-policy' },
        { label: 'Terms of Service', to: '/terms-of-service' },
    ];

    return (
        <Box
            component="footer"
            className="relative bg-gradient-to-br from-dark via-dark-lighter to-gray-900 py-16 overflow-hidden border-t border-gray-800"
            sx={{
                position: 'relative',
            }}
        >
            {/* Enhanced Background Effects */}
            <Box
                className="absolute inset-0 pointer-events-none"
                sx={{
                    position: 'absolute',
                    inset: 0,
                    pointerEvents: 'none',
                }}
            >
                <Box
                    className="absolute top-0 left-0 w-96 h-96 rounded-full bg-green-500/5 blur-3xl -translate-x-1/2 -translate-y-1/2"
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '24rem',
                        height: '24rem',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(34, 197, 94, 0.05)',
                        filter: 'blur(64px)',
                        transform: 'translate(-50%, -50%)',
                    }}
                />
                <Box
                    className="absolute bottom-0 right-0 w-96 h-96 rounded-full bg-blue-500/6 blur-3xl translate-x-1/2 translate-y-1/2"
                    sx={{
                        position: 'absolute',
                        bottom: 0,
                        right: 0,
                        width: '24rem',
                        height: '24rem',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(59, 130, 246, 0.06)',
                        filter: 'blur(64px)',
                        transform: 'translate(50%, 50%)',
                    }}
                />
                <Box
                    sx={{
                        position: 'absolute',
                        top: '30%',
                        right: '20%',
                        width: '16rem',
                        height: '16rem',
                        borderRadius: '50%',
                        backgroundColor: 'rgba(37, 99, 235, 0.05)',
                        filter: 'blur(60px)',
                    }}
                />
                <Box
                    className="absolute inset-0 bg-grid-pattern opacity-20"
                    sx={{
                        position: 'absolute',
                        inset: 0,
                        backgroundImage: `
                            linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                            linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px)
                        `,
                        backgroundSize: '40px 40px',
                        opacity: 0.2,
                    }}
                />
            </Box>

            <Container 
                maxWidth="xl" 
                className="relative z-10"
                sx={{ position: 'relative', zIndex: 10 }}
            >
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                >
                    <Box
                        className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12"
                        sx={{ mb: 6 }}
                    >
                        {/* Brand Section */}
                        <Box className="md:col-span-2">
                            <motion.div variants={itemVariants}>
                                <Typography
                                    variant="h4"
                                    className="gradient-text mb-4"
                                    sx={{
                                        fontWeight: 700,
                                        mb: 2,
                                        background: 'linear-gradient(to right, #4ade80, #3b82f6, #22d3ee, #2563eb, #10b981)',
                                        WebkitBackgroundClip: 'text',
                                        WebkitTextFillColor: 'transparent',
                                        backgroundClip: 'text',
                                    }}
                                >
                                    Devr.AI
                                </Typography>
                                <Typography
                                    variant="body1"
                                    className="text-gray-400 max-w-md leading-relaxed mb-6"
                                    sx={{
                                        color: 'rgba(161, 161, 170, 1)',
                                        maxWidth: '28rem',
                                        lineHeight: 1.75,
                                        mb: 4,
                                    }}
                                >
                                    Revolutionizing developer relations with AI-powered community management.
                                    Automate engagement, streamline onboarding, and deliver real-time updates.
                                </Typography>
                                <Stack direction="row" spacing={2}>
                                    {socialLinks.map((social) => (
                                        <motion.div
                                            key={social.label}
                                            whileHover={{ scale: 1.1, y: -2 }}
                                            whileTap={{ scale: 0.95 }}
                                        >
                                            <IconButton
                                                component="a"
                                                href={social.href}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                aria-label={social.label}
                                                className={`text-gray-400 ${social.color} transition-all duration-300 bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-gray-600`}
                                                sx={{
                                                    color: 'rgba(161, 161, 170, 1)',
                                                    backgroundColor: 'rgba(39, 39, 42, 0.5)',
                                                    border: '1px solid rgba(63, 63, 70, 1)',
                                                    borderRadius: '12px',
                                                    padding: '12px',
                                                    '&:hover': {
                                                        backgroundColor: 'rgba(39, 39, 42, 1)',
                                                        borderColor: 'rgba(82, 82, 91, 1)',
                                                        color: social.label === 'Twitter' 
                                                            ? 'rgba(6, 182, 212, 1)' 
                                                            : 'rgba(34, 197, 94, 1)',
                                                    },
                                                    transition: 'all 0.3s ease',
                                                }}
                                            >
                                                {social.icon}
                                            </IconButton>
                                        </motion.div>
                                    ))}
                                </Stack>
                            </motion.div>
                        </Box>

                        {/* Quick Links Section */}
                        <Box>
                            <motion.div variants={itemVariants}>
                                <Typography
                                    variant="h6"
                                    className="font-bold mb-4 text-white"
                                    sx={{
                                        fontWeight: 700,
                                        mb: 2,
                                        color: 'white',
                                    }}
                                >
                                    Quick Links
                                </Typography>
                                <Stack spacing={1.5}>
                                    {quickLinks.map((link) => (
                                        <QuickLink
                                            key={link.label}
                                            link={link}
                                            isHomePage={isHomePage}
                                        />
                                    ))}
                                </Stack>
                            </motion.div>
                        </Box>

                        {/* Legal Section */}
                        <Box>
                            <motion.div variants={itemVariants}>
                                <Typography
                                    variant="h6"
                                    className="font-bold mb-4 text-white"
                                    sx={{
                                        fontWeight: 700,
                                        mb: 2,
                                        color: 'white',
                                    }}
                                >
                                    Legal
                                </Typography>
                                <Stack spacing={1.5}>
                                    {legalLinks.map((link) => (
                                        <MuiLink
                                            key={link.label}
                                            component={Link}
                                            to={link.to}
                                            className="text-gray-400 hover:text-cyan-400 text-sm transition-colors duration-300 inline-flex items-center gap-2 group"
                                            sx={{
                                                color: 'rgba(161, 161, 170, 1)',
                                                fontSize: '0.875rem',
                                                textDecoration: 'none',
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '8px',
                                                position: 'relative',
                                                transition: 'color 0.3s ease',
                                                '&:hover': {
                                                    color: 'rgba(6, 182, 212, 1)',
                                                },
                                                '&::before': {
                                                    content: '""',
                                                    width: 0,
                                                    height: '2px',
                                                    background: 'linear-gradient(to right, #22d3ee, #4ade80)',
                                                    transition: 'width 0.3s ease',
                                                    position: 'absolute',
                                                    left: 0,
                                                    bottom: '-2px',
                                                },
                                                '&:hover::before': {
                                                    width: '16px',
                                                },
                                            }}
                                        >
                                            {link.label}
                                        </MuiLink>
                                    ))}
                                </Stack>
                            </motion.div>
                        </Box>
                    </Box>

                    {/* Bottom Bar */}
                    <motion.div
                        variants={itemVariants}
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                    >
                        <Divider 
                            sx={{ 
                                mb: 4, 
                                borderColor: 'rgba(39, 39, 42, 1)',
                            }} 
                        />
                        <Box
                            className="flex flex-col md:flex-row justify-between items-center gap-4"
                            sx={{
                                display: 'flex',
                                flexDirection: { xs: 'column', md: 'row' },
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                gap: 2,
                            }}
                        >
                            <Typography
                                variant="body2"
                                className="text-gray-500"
                                sx={{
                                    color: 'rgba(113, 113, 122, 1)',
                                    fontSize: '0.875rem',
                                }}
                            >
                                © {currentYear} Devr.AI. All rights reserved.
                            </Typography>

                            {/* Scroll to Top Button */}
                            <motion.div
                                whileHover={{ y: -2 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                <MuiLink
                                    component="button"
                                    onClick={scrollToTop}
                                    className="flex items-center gap-2 text-gray-400 hover:text-green-400 text-sm transition-colors duration-300 group"
                                    sx={{
                                        color: 'rgba(161, 161, 170, 1)',
                                        fontSize: '0.875rem',
                                        textDecoration: 'none',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        background: 'none',
                                        border: 'none',
                                        cursor: 'pointer',
                                        padding: 0,
                                        fontFamily: 'inherit',
                                        transition: 'color 0.3s ease',
                                        '&:hover': {
                                            color: 'rgba(34, 197, 94, 1)',
                                        },
                                    }}
                                >
                                    <Typography
                                        component="span"
                                        variant="body2"
                                        sx={{ fontSize: '0.875rem' }}
                                    >
                                        Back to top
                                    </Typography>
                                    <ArrowUpIcon 
                                        sx={{ 
                                            fontSize: '16px',
                                        }} 
                                    />
                                </MuiLink>
                            </motion.div>
                        </Box>
                    </motion.div>
                </motion.div>
            </Container>
        </Box>
    );
};

export default Footer;