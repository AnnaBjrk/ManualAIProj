import gizmo from "../assets/gizmo.svg";
import { Link } from 'react-router-dom';
// import { Sidebar } from "../components/Sidebar";
import React, { useState } from "react";
import { CircleUserRound } from 'lucide-react';

export default function Header({ onMenuClick, user }) {
    // const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    return (
        <header className="font-['Neucha']">
            <nav>
                <div className="flex flex-row items-center h-20 border-b border-b-4 border-b-amber-50 border-double bg-sky-900  text-amber-50">
                    <ul className="flex flex-row items-center flex-1 gap-6 p-4">
                        <li>
                            <div className="">
                                <Link to="/">
                                    <img className="manual-assistant-logo h-12 w-auto" src={gizmo} alt="Manual Assistant logo" />
                                </Link>
                            </div>
                        </li>
                        <li>
                            <Link to="/query" className="px-4 text-base font-['Neucha'] text-amber-50">
                                Fråga AI
                            </Link>
                        </li>
                        <li>
                            <Link to="/search" className="px-4 text-base font-['Neucha'] text-amber-50">
                                Sök
                            </Link>
                        </li>
                        <li>
                            <Link to="/about" className="px-4 text-base font-['Neucha'] text-amber-50">
                                Våra partners
                            </Link>
                        </li>
                        <div> {user ? (
                            <li>
                                <Link to="/userspage" className="px-4 text-base font-['Neucha'] text-amber-50">
                                    Min sida
                                </Link>
                            </li>
                        ) : null}
                        </div>
                        <div> {user && user.isAdmin ? (
                            <li>
                                <Link to="/adminpage" className="px-4 text-base font-['Neucha'] text-amber-50">
                                    Admin
                                </Link>
                            </li>
                        ) : null}
                        </div>
                        <div> {user && user.isPartner ? (
                            <li>
                                <Link to="/partnerpage" className="px-4 text-base font-['Neucha'] text-amber-50">
                                    Partner
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
                            <CircleUserRound strokeWidth={1.5} size={30} />
                        </button>
                    </div>
                </div>
            </nav>
        </header>

    );
}