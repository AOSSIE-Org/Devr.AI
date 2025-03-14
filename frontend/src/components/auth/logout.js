import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "../supabaseClient"; // Adjust the import based on your project structure

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        const handleLogout = async () => {
            await supabase.auth.signOut();
            navigate("/login"); // Redirect to the login page after logout
        };

        handleLogout();
    }, [navigate]);

    return (
        <div className="App">
            <header className="App-header">
                <h1>Logging Out...</h1>
                <p>You will be redirected shortly.</p>
            </header>
        </div>
    );
}

export default Logout;
