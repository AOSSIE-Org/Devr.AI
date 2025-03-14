// Login Page Component
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
// import logo from './logo.svg';
import '../../App.css';
import { createClient } from '@supabase/supabase-js';

import { supabase } from '../../App.js';


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
          const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'google'
          })
          
            if (error) throw error;
        } catch (error) {
            alert(error.message);
        }
    };

    const handleGithubLogin = async () => {
        try {
          const { data, error } = await supabase.auth.signInWithOAuth({
            provider: 'github'
          })
          
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

export default LoginPage;