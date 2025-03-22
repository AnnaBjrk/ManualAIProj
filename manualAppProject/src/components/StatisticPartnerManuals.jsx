import React, { useState, useEffect } from 'react';
import { RefreshCw, Users, FileText, Activity } from 'lucide-react';

const StatisticPartnerManuals = () => {
    const [stats, setStats] = useState({
        users_selected_count: 0,
        manuals_uploaded_count: 0,
        total_selections_count: 0,
        most_popular_manuals: []
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Load user data from localStorage
        const userString = localStorage.getItem('user');
        if (userString) {
            try {
                const userData = JSON.parse(userString);
                setUser(userData);
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }

        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Get token from localStorage, following your UserManualsTable pattern
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            // Use token_type (bearer) + access_token for the Authorization header
            const authHeader = `${tokenType} ${accessToken}`;

            // Use the VITE_API_URL from environment, like in your other components
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/dashboard/statistics`;
            console.log("Making request to:", apiUrl);

            const response = await fetch(apiUrl, {
                method: "GET",
                headers: {
                    "Authorization": authHeader,
                    "Content-Type": "application/json"
                }
            });

            console.log("API response status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response body:", errorText);

                let errorMessage = `Error: ${response.status} ${response.statusText}`;

                try {
                    const errorData = JSON.parse(errorText);
                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    }
                } catch (e) {
                    if (errorText) {
                        errorMessage = errorText;
                    }
                }

                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Dashboard stats data:", data);
            setStats(data);
            setError(null);
        } catch (err) {
            console.error("Error fetching dashboard data:", err);
            setError(err.message || "Failed to fetch dashboard data");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="mt-8 mb-10">
                <h2 className="font-['Neucha'] text-2xl mb-4">Manualstatistik</h2>
                <div className="w-full flex justify-center items-center py-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-700"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-8 mb-10">
            <div className="flex justify-between items-center mb-6">
                <h2 className="font-['Neucha'] text-2xl">Manualstatistik</h2>
                <button
                    onClick={fetchDashboardData}
                    className="bg-sky-800 hover:bg-amber-900 text-white py-2 px-4 rounded flex items-center font-['Barlow_Condensed']"
                >
                    <RefreshCw size={16} className="mr-2" />
                    Uppdatera
                </button>
            </div>

            {error && (
                <div className="p-4 bg-amber-50 text-amber-700 rounded-md mb-4">
                    <p>{error}</p>
                </div>
            )}

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Card 1: Users */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-blue-100 text-sky-800">
                            <Users size={24} />
                        </div>
                        <div className="ml-4">
                            <p className="text-gray-500 text-sm font-['Barlow_Condensed']">Användare som valt dina manualer</p>
                            <p className="text-2xl font-semibold text-gray-800 font-['Neucha']">{stats.users_selected_count}</p>
                        </div>
                    </div>
                </div>

                {/* Card 2: Manuals */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-green-100 text-green-600">
                            <FileText size={24} />
                        </div>
                        <div className="ml-4">
                            <p className="text-gray-500 text-sm font-['Barlow_Condensed']">Uppladdade manualer</p>
                            <p className="text-2xl font-semibold text-gray-800 font-['Neucha']">{stats.manuals_uploaded_count}</p>
                        </div>
                    </div>
                </div>

                {/* Card 3: Selections */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex items-center">
                        <div className="p-3 rounded-full bg-amber-100 text-amber-600">
                            <Activity size={24} />
                        </div>
                        <div className="ml-4">
                            <p className="text-gray-500 text-sm font-['Barlow_Condensed']">Totalt antal val</p>
                            <p className="text-2xl font-semibold text-gray-800 font-['Neucha']">{stats.total_selections_count}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Popular Manuals Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="px-6 py-4 border-b">
                    <h2 className="font-['Neucha'] text-lg">Mest populära av era manualer</h2>
                </div>
                <div className="overflow-x-auto">
                    {stats.most_popular_manuals && stats.most_popular_manuals.length > 0 ? (
                        <table className="min-w-full bg-white">
                            <thead>
                                <tr className="bg-gray-100">
                                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Märke</th>
                                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Modell</th>
                                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Typ</th>
                                    <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Antal val</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200">
                                {stats.most_popular_manuals.map((manual) => (
                                    <tr key={manual.id} className="hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {manual.brand || "-"}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {manual.modelname || "-"}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {manual.device_type || "-"}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {manual.selection_count}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="p-6 text-center text-gray-500 font-['Barlow_Condensed']">
                            Inga manualer har valts av användare ännu.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default StatisticPartnerManuals;