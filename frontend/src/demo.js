



import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import { createClient } from '@supabase/supabase-js';

// Supabase setup
const supabase_url = process.env.REACT_APP_SUPABASE_URL;
const anon_key = process.env.REACT_APP_SUPABASE_KEY;

console.log('Supabase URL:', supabase_url);
console.log('Supabase Key:', anon_key);
console.log('ENV Check:', process.env);

const supabase = createClient(supabase_url, anon_key);

// Navbar Component
function Navbar() {
    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    DevrAI
                </Link>
                <div>
                    <Link to="/login" className="login-button">
                        Login
                    </Link>
                </div>
            </div>
        </nav>
    );
}

// Login Page Component
function LoginPage() {
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            });
            if (error) throw error;
            // Redirect to home page on successful login
            window.location.href = '/';
        } catch (error) {
            alert(error.message);
        }
    };

    const handleGoogleLogin = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
            });
            if (error) throw error;
        } catch (error) {
            alert(error.message);
        }
    };

    const handleGithubLogin = async () => {
        try {
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'github',
            });
            if (error) throw error;
        } catch (error) {
            alert(error.message);
        }
    };
    const handleOtpLogin = async () => {
        try {
            const email = prompt('Enter your email for OTP login:');
            if (!email) return;

            const { data, error } = await supabase.auth.signInWithOtp({
                email,
                options: {
                    emailRedirectTo: 'http://localhost:6543/',
                },
            });

            if (error) throw error;

            alert('OTP sent! Check your email.');
        } catch (error) {
            alert(error.message);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-form-container">
                <h2 className="auth-title">Login to DevrAI</h2>

                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="email">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            className="form-input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="password">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            className="form-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="auth-button primary-button"
                    >
                        Login
                    </button>
                </form>

                <div className="auth-link-container">
                    <Link to="/reset-password" className="auth-link">
                        Reset Password
                    </Link>
                </div>

                <div className="social-login-container">
                    <p className="social-login-text">Or login with</p>
                    <div className="social-buttons">
                        <button
                            onClick={handleGoogleLogin}
                            className="social-button google-button"
                        >
                            Google
                        </button>
                        <button
                            onClick={handleGithubLogin}
                            className="social-button github-button"
                        >
                            GitHub
                        </button>
                        <button
                            onClick={handleOtpLogin}
                            className="social-button otp-button"
                        >
                            Login with OTP
                        </button>
                    </div>
                </div>

                <div className="auth-link-container">
                    <p>
                        Don't have an account?{' '}
                        <Link to="/signup" className="auth-link">
                            Sign up
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

// SignUp Page Component
function SignUpPage() {
    const [email, setEmail] = React.useState('');
    const [password, setPassword] = React.useState('');
    const [confirmPassword, setConfirmPassword] = React.useState('');

    const handleSignUp = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            alert("Passwords don't match");
            return;
        }

        try {
            const { error } = await supabase.auth.signUp({
                email,
                password,
            });
            if (error) throw error;
            alert(
                'Sign up successful! Please check your email for verification.'
            );
            window.location.href = '/';
        } catch (error) {
            alert(error.message);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-form-container">
                <h2 className="auth-title">Sign Up for DevrAI</h2>

                <form onSubmit={handleSignUp}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="email">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            className="form-input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="password">
                            Password
                        </label>
                        <input
                            id="password"
                            type="password"
                            className="form-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label
                            className="form-label"
                            htmlFor="confirm-password"
                        >
                            Confirm Password
                        </label>
                        <input
                            id="confirm-password"
                            type="password"
                            className="form-input"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="auth-button primary-button"
                    >
                        Sign Up
                    </button>
                </form>

                <div className="auth-link-container">
                    <p>
                        Already have an account?{' '}
                        <Link to="/login" className="auth-link">
                            Login
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

// Reset Password Page Component
function ResetPasswordPage() {
    const [email, setEmail] = React.useState('');

    const handleResetPassword = async (e) => {
        e.preventDefault();
        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email);
            if (error) throw error;
            alert('Password reset email sent. Please check your inbox.');
        } catch (error) {
            alert(error.message);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-form-container">
                <h2 className="auth-title">Reset Password</h2>

                <form onSubmit={handleResetPassword}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="email">
                            Email
                        </label>
                        <input
                            id="email"
                            type="email"
                            className="form-input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className="auth-button primary-button"
                    >
                        Send Reset Link
                    </button>
                </form>

                <div className="auth-link-container">
                    <Link to="/login" className="auth-link">
                        Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}

// Home Page Component
function HomePage() {
    return (
        <div className="App">
            <header className="App-header">
                <img src={logo} className="App-logo" alt="logo" />
                <p>
                    Edit <code>src/App.js</code> and save to reload.
                </p>
                <a
                    className="App-link"
                    href="https://reactjs.org"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Learn React
                </a>
            </header>
        </div>
    );
}

function App() {
    return (
        <Router>
            <div>
                <Navbar />
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route
                        path="/reset-password"
                        element={<ResetPasswordPage />}
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;

