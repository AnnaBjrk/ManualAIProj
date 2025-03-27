import React, { useState, useEffect } from "react";
import { Trash2, RefreshCw } from 'lucide-react';
import { Download } from 'lucide-react';

const handleDownload = async (fileId) => {
    try {
        // Call the API to get the download URL
        const response = await fetch(`/api/get-download-url/${fileId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
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
    }
};

const UserManualsTable = () => {
    const [manuals, setManuals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [user, setUser] = useState(null);
    const [deletedItems, setDeletedItems] = useState({});

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

        fetchManuals();
    }, []);

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

            // Updated to use the correct endpoint and HTTP method
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/list_user_uploaded_manuals`;
            console.log("Making request to:", apiUrl);

            const response = await fetch(apiUrl, {
                method: "GET", // Changed from POST to GET
                headers: {
                    "Authorization": authHeader,
                    "Content-Type": "application/json"
                },
                // Important: Add query parameter to include deleted manuals
                // Add this parameter to the URL if the API supports it
            });

            console.log("API response status:", response.status);

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
                // Important: Save all manuals, including those with "deleted" status
                console.log("All manuals from API:", data.manuals);
                setManuals(data.manuals);

                // Initialize deleted status based on manual status if available
                const initialDeletedState = {};
                data.manuals.forEach(manual => {
                    // Check for "deleted" status or any other indicator that the manual is deleted
                    if (manual.status === "deleted" || manual.deleted === true) {
                        initialDeletedState[manual.id] = true;
                    }
                });
                console.log("Initial deleted state:", initialDeletedState);
                setDeletedItems(initialDeletedState);
            }

            setError(null);
        } catch (err) {
            console.error("Error fetching manuals:", err);
            setError(err.message || "Failed to fetch manuals");
        } finally {
            setLoading(false);
        }
    };

    // This function is critical for handling the UI state for deleted items
    const toggleDeleteStatus = async (manualId, isCurrentlyDeleted) => {
        try {
            // Get token from localStorage
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            // Use token_type (bearer) + access_token for the Authorization header
            const authHeader = `${tokenType} ${accessToken}`;

            // Choose the appropriate endpoint based on current status
            const endpoint = isCurrentlyDeleted ? 'unmark_manual_deleted' : 'mark_manual_deleted';

            // Return to using the ID in the URL path
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/${endpoint}/${manualId}`;

            console.log("Calling API endpoint:", apiUrl);

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Authorization": authHeader,
                    "Content-Type": "application/json"
                },
                // Send an empty body for the POST request
                body: JSON.stringify({})
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

            // Important: Update the local UI state immediately
            // This ensures the user sees the change without waiting for a server refresh
            setDeletedItems(prev => {
                const newState = { ...prev };
                newState[manualId] = !isCurrentlyDeleted;
                return newState;
            });

            // Also update the manual's status in the manuals array to ensure consistency
            setManuals(prev => {
                return prev.map(manual => {
                    if (manual.id === manualId) {
                        return {
                            ...manual,
                            status: !isCurrentlyDeleted ? "deleted" : "active"
                        };
                    }
                    return manual;
                });
            });

            // Optionally refresh the manual list to ensure we're in sync with server
            // Comment this out if you want to rely purely on local state changes
            // await fetchManuals();

        } catch (error) {
            console.error("Error toggling delete status:", error);
            setError("Kunde inte uppdatera manualen: " + error.message);
        }
    };

    if (loading) {
        return (
            <div className="mt-8 mb-10">
                <h2 className="font-['Neucha'] text-2xl mb-4">Mina manualer</h2>
                <div className="w-full flex justify-center items-center py-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-700"></div>
                </div>
            </div>
        );
    }

    // Debug: Log all manuals before rendering
    console.log("Rendering manuals:", manuals);
    console.log("Deleted items state:", deletedItems);

    // Make sure we have manuals to display
    const manualsToDisplay = manuals || [];

    return (
        <div className="mt-8 mb-10">
            <h2 className="font-['Neucha'] text-2xl mb-4">Hantera dina manualer</h2>

            {error && (
                <div className="p-4 bg-amber-50 text-amber-600 rounded-md mb-4">
                    <p>{error}</p>
                </div>
            )}

            {!error && manualsToDisplay.length === 0 ? (
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
                    <p className="text-gray-600 font-['Barlow_Condensed']">Du har inga manualer att visa</p>
                </div>
            ) : (
                <div className="overflow-x-auto shadow-md rounded-lg">
                    <table className="min-w-full bg-white">
                        <thead>
                            <tr className="bg-gray-100">
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Märke</th>
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Typ</th>
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Modellnummer</th>
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Modellnamn</th>
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Status</th>
                                <th className="py-3 px-4 text-left text-sm font-medium text-gray-600">Åtgärder</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {manualsToDisplay.map((manual, index) => {
                                // Check for deletion status from both sources
                                const isDeleted = deletedItems[manual.id] === true ||
                                    manual.status === "deleted" ||
                                    manual.deleted === true;

                                return (
                                    <tr key={index} className={`hover:bg-gray-50 ${isDeleted ? 'bg-gray-100' : ''}`}>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.brand || "-"}</td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.device_type || "-"}</td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.modelnumber || "-"}</td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">{manual.modelname || "-"}</td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {isDeleted ? (
                                                <span className="text-amber-600">Raderas</span>
                                            ) : (
                                                <span className="text-amber-500">Aktiv</span>
                                            )}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            <button
                                                onClick={() => handleDownload(manual.id)}
                                                className="text-sky-800 hover:text-amber-900 inline-flex items-center mr-3 relative group"
                                                title="Ladda ner"
                                            >
                                                <Download size={18} />
                                                <span className="absolute top-full ml-6 whitespace-nowrap bg-sky-800 text-white font-['Barlow_Condensed'] text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200">
                                                    Ladda ner
                                                </span>
                                            </button>

                                            {user && user.isPartner && (
                                                <button
                                                    onClick={() => toggleDeleteStatus(manual.id, isDeleted)}

                                                    className={`${isDeleted ? 'bg-amber-700 hover:bg-amber-500 ' : 'bg-amber-600 hover:bg-amber-700 transition-colors'} text-white py-1 px-3 mr-4 rounded text-sm font-['Neucha']`}
                                                >
                                                    {isDeleted ? "Ångra radering" : "Radera"}
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default UserManualsTable;