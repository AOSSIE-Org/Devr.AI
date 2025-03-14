import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import { createClient } from '@supabase/supabase-js';
import LoginPage from './components/auth/signin.js';
import SignUpPage from './components/auth/signup.js';
import ResetPasswordPage from './components/auth/reset.js';
import HomePage from './components/home/home.js';
import MainHomePage from './components/home/mainhomepage.js';
import Navbar from './components/navbar/navbar.js';

// Supabase setup
const supabase_url = process.env.REACT_APP_SUPABASE_URL;
const anon_key = process.env.REACT_APP_SUPABASE_KEY;

console.log('Supabase URL:', supabase_url);
console.log('Supabase Key:', anon_key);
console.log('ENV Check:', process.env);

export const supabase = createClient(supabase_url, anon_key);

function App() {
    return (
        <Router>
            <div>
                <Navbar />
                <Routes>
                    <Route path="/" element={<MainHomePage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/signup" element={<SignUpPage />} />
                    <Route path="/home" element={<HomePage />} />
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