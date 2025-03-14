import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
// import logo from './logo.svg';
import '../../App.css';
import { createClient } from '@supabase/supabase-js';
import { supabase } from '../../App.js';



function HomePage() {
    return (
        <div className="App">
            <header className="App-header">
                <h1>Welcome to HomePage</h1>
                <p>
                    This is the main landing page of the application.
                </p>
                <a
                    className="App-link"
                    href="https://yourwebsite.com"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Visit Website
                </a>
            </header>
        </div>
    );
}

export default HomePage;
