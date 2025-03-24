// Reset Password Page Component
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
// import logo from './logo.svg';
import '../../App.css';
import { createClient } from '@supabase/supabase-js';
import { supabase } from '../../App.js';



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

export default ResetPasswordPage;