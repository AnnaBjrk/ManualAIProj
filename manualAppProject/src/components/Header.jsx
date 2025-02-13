import gizmo from "../assets/gizmo.svg";
import { Link } from 'react-router-dom';
// import { Sidebar } from "../components/Sidebar";
import React, { useState } from "react";
import { CircleUserRound } from 'lucide-react';

export default function Header({ onMenuClick, user }) {
    // const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <header className="font-['Roboto']">
            <nav>
                <div className="flex flex-row items-center h-24 bg-sky-800  text-amber-50">
                    <ul className="flex flex-row flex-1 gap-6 p-4 pt-8">
                        <li>
                            <Link to="/">
                                <img className="manual-assistant-logo h-16 w-auto" src={gizmo} alt="Manual Assistant logo" />
                            </Link>
                        </li>
                        <li>
                            <Link to="/query" className="px-4 text-lg font-roboto text-amber-50">
                                Fråga AI
                            </Link>
                        </li>
                        <li>
                            <Link to="/manual" className="px-4 text-lg font-roboto text-amber-50">
                                Sök efter en manual
                            </Link>
                        </li>
                        <li>
                            <Link to="/about" className="px-4 text-lg font-roboto text-amber-50">
                                Om Manual Assistant
                            </Link>
                        </li>
                        <div> {user ? (
                            <li>
                                <Link to="/userspage" className="px-4 text-lg font-roboto text-amber-50">
                                    Min sida
                                </Link>
                            </li>
                        ) : null}
                        </div>

                    </ul>

                    <div className="flex items-end">
                        {user ? (
                            <span className="mr-4">Hej, {user.firstName}</span>
                        ) : null}
                    </div>
                    <div className="pr-4">
                        <button onClick={onMenuClick} className="p-2 text-amber-50 hover:text-amber-300 transition-colors">
                            <CircleUserRound size={30} />
                        </button>
                    </div>
                </div>
            </nav>
        </header>

    );
}