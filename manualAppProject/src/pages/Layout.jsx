import { Outlet } from "react-router-dom";
import Footer from "../components/Footer";
import Header from "../components/Header";
import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";

export default function Layout() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [user, setUser] = useState(null);  // Add state for user

    //sparar användaren i local storage under 24 timmar. 
    useEffect(() => {
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            const userData = JSON.parse(savedUser);
            const now = new Date().getTime();

            if (userData.expiryTime && now > userData.expiryTime) {
                // Data has expired
                localStorage.removeItem('user');
            } else {
                setUser(userData);
            }
        }
    }, []);

    const handleLogin = (userData) => {
        const userDataWithExpiry = {
            ...userData,
            expiryTime: new Date().getTime() + (24 * 60 * 60 * 1000) // 24 hours from now
        };
        setUser(userDataWithExpiry);
        setIsSidebarOpen(false);
        localStorage.setItem('user', JSON.stringify(userDataWithExpiry));
    };

    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('user');
    };

    return (
        <div className="flex flex-col min-h-screen bg-amber-50">
            <Header
                onMenuClick={() => setIsSidebarOpen(true)}
                user={user}  // Pass user data to Header
            />

            <main className="flex-1">
                <Sidebar
                    isOpen={isSidebarOpen}
                    onClose={() => setIsSidebarOpen(false)}
                    onLogin={handleLogin}  // Pass login handler to Sidebar
                    onLogout={handleLogout}
                    user={user}
                />

                <Outlet />
            </main>

            <Footer />
        </div>
    );
}