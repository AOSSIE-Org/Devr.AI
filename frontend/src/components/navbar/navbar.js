import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../../App.css";
import { supabase } from "../../App.js"; // Ensure this path is correct

function Navbar() {
    const navigate = useNavigate();

    const handleLogout = async () => {
        await supabase.auth.signOut();
        navigate("/login"); // Redirect to login page after logout
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    DevrAI
                </Link>
                <div className="nav-buttons">
                    <Link to="/login" className="login-button">
                        Login
                    </Link>
                    <button onClick={handleLogout} className="login-button">
                        Logout
                    </button>
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
