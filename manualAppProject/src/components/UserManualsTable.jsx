import React, { useState, useEffect } from "react";
import { Trash2 } from 'lucide-react';
import { Download } from 'lucide-react';

const handleDownload = async (fileId) => {
    try {
        // Optional: Show loading state
        // setIsLoading(true);

        // Call the API to get the download URL
        const response = await fetch(`/api/get-download-url/${fileId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                // Include authentication headers if needed
                // 'Authorization': `Bearer ${yourAuthToken}`
            },
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // open in new tab
        window.open(data.downloadUrl, '_blank');

    } catch (error) {
        console.error('Failed to get download URL:', error);
        // Handle the error - show a notification to the user
        // setError('Failed to download the manual');
    } finally {
        // setIsLoading(false);
    }
};

const UserManualsTable = () => {
    const [manuals, setManuals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [apiResponse, setApiResponse] = useState(null);



    useEffect(() => {
        const fetchManuals = async () => {
            try {
                setLoading(true);

                // Get token from localStorage
                const accessToken = localStorage.getItem('access_token');
                const tokenType = localStorage.getItem('token_type');

                if (!accessToken) {
                    throw new Error("No authentication token found in localStorage");
                }

                // Use token_type (bearer) + access_token for the Authorization header
                const authHeader = `${tokenType} ${accessToken}`;

                // Use the correct path based on your API structure
                // The router is defined with prefix="/gen" and the app includes the router with prefix="/v1"
                const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/list_user_manuals`;
                console.log("Making request to:", apiUrl);

                const response = await fetch(apiUrl, {
                    method: "POST",
                    headers: {
                        "Authorization": authHeader,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({})
                });

                console.log("API response status:", response.status);

                console.log("Authentication:", authHeader.replace(/^Bearer (.{5}).*$/, 'Bearer $1...'));
                console.log("Response headers:", Object.fromEntries([...response.headers.entries()]));

                // Handle 404 as an empty result, not an error
                if (response.status === 404) {
                    console.log("No manuals found (404 response)");
                    setManuals([]);
                    setError(null);
                    setLoading(false);
                    return;
                }

                if (!response.ok) {
                    const errorText = await response.text();
                    let errorMessage = `Error: ${response.status} ${response.statusText}`;

                    try {
                        const errorData = JSON.parse(errorText);
                        if (errorData.detail) {
                            errorMessage = errorData.detail;
                        }
                    } catch (e) {
                        // If the error response isn't JSON, use the text as is
                        if (errorText) {
                            errorMessage = errorText;
                        }
                    }

                    throw new Error(errorMessage);
                }

                const data = await response.json();
                console.log("API response data:", data);

                if (!data.manuals) {
                    console.warn("Response doesn't contain a 'manuals' property:", data);
                    setManuals([]);
                } else {
                    setManuals(data.manuals);
                }

                setError(null);
            } catch (err) {
                console.error("Error fetching manuals:", err);
                setError(err.message || "Failed to fetch manuals");
            } finally {
                setLoading(false);
            }
        };

        fetchManuals();
    }, []);

    if (loading) {
        return (
            <div className="mt-8 mb-10">
                <h2 className="font-['Roboto'] text-2xl mb-4">Sparade manualer</h2>
                <div className="w-full flex justify-center items-center py-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-700"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-8 mb-10">
            <h2 className="font-['Neucha'] text-2xl mb-4">Sparade manualer</h2>

            {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-md mb-4">
                    <p>{error}</p>
                </div>
            )}

            {!error && manuals.length === 0 ? (
                <div className="p-6 bg-gray-50 rounded-lg text-center">
                    <svg
                        className="w-12 h-12 text-gray-400 mx-auto mb-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        ></path>
                    </svg>
                    <p className="text-gray-600 font-['Barlow_Condensed']">Det finns inga sparade manualer</p>
                    <p className="text-gray-500 text-sm mt-1">Du har inte lagt till några manualer än</p>
                </div>
            ) : (
                <div className="overflow-x-auto shadow-md rounded-lg">
                    <table className="min-w-full bg-white">
                        <tbody className="divide-y divide-gray-200">
                            {manuals.map((manual, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                    <td className="py-3 px-4 text-sm text-gray-700 font-black font-['Barlow_Condensed']">{manual.users_own_naming || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.brand || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.device_type || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                        <button
                                            onClick={() => handleDownload(manual.file_id)}
                                            // className="bg-sky-800 text-white text-sm font-['Roboto'] hover:bg-amber-900 rounded-full px-4 py-2 inline-flex items-center mr-3 transition-colors duration-200"
                                            className=" px-1 py-1 ml-4 mb-2 w-20 font-['Neucha'] bg-sky-900 text-sm rounded-sm border-sky-700 text-amber-50 items-center hover:bg-amber-900 transition-colors duration-200"
                                            title="Lös ett problem"
                                        >
                                            <span>Lös ett problem</span>
                                        </button>

                                    </td>
                                    <td className="py-3 px-4 text-sm text-amber-900 hover:text-indigo-900 font-['Roboto']">

                                        <button
                                            onClick={() => handleDownload(manual.file_id)}
                                            className="text-sky-800 hover:text-amber-900  inline-flex items-center mr-3 relative group"
                                            title="Ladda ner" // Keep for screen readers
                                        >
                                            <Download size={18} />
                                            <span className="absolute top-full ml-2 whitespace-nowrap bg-sky-800 text-white font-['Barlow_Condensed'] text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200">
                                                Ladda ner
                                            </span>
                                        </button>

                                        <button
                                            onClick={() => console.log(`Remove manual ${manual.file_id}`)}
                                            className="text-sky-800 hover:text-amber-900 inline-flex items-center relative group"
                                            title="Ta bort" // Keep for screen readers
                                        >
                                            <Trash2 size={18} />
                                            <span className="absolute top-full ml-2 whitespace-nowrap bg-sky-800 text-white font-['Barlow_Condensed'] text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200">
                                                Ta bort
                                            </span>
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default UserManualsTable;