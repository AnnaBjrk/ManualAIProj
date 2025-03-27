import React, { useState, useEffect } from "react";
import { Trash2 } from 'lucide-react';
import { Download } from 'lucide-react';

const handleDownload = (fileId) => {
    // Get authentication token
    const accessToken = localStorage.getItem('access_token');
    const tokenType = localStorage.getItem('token_type');

    if (!accessToken) {
        console.error("No authentication token found in localStorage");
        return;
    }

    const authHeader = `${tokenType} ${accessToken}`;

    // Call the API to get the download URL - use the actual backend endpoint path
    fetch(`${import.meta.env.VITE_API_URL}/v1/gen/get_download_url/${fileId}`, {
        method: 'GET',
        headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Open in new tab or start download directly
            window.open(data.downloadUrl, '_blank');
        })
        .catch(error => {
            console.error('Failed to get download URL:', error);
        });
};

const UserManualsTable = () => {
    const [manuals, setManuals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isDeleting, setIsDeleting] = useState(false);

    const fetchManuals = () => {
        setLoading(true);

        // Get token from localStorage
        const accessToken = localStorage.getItem('access_token');
        const tokenType = localStorage.getItem('token_type');

        if (!accessToken) {
            setError("No authentication token found in localStorage");
            setLoading(false);
            return;
        }

        // Use token_type (bearer) + access_token for the Authorization header
        const authHeader = `${tokenType} ${accessToken}`;



        const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/list_user_manuals`;
        console.log("Making request to:", apiUrl);



        fetch(apiUrl, {
            method: "POST",
            headers: {
                "Authorization": authHeader,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        })
            .then(response => {
                console.log("API response status:", response.status);

                // Handle 404 as an empty result, not an error
                if (response.status === 404) {
                    console.log("No manuals found (404 response)");
                    setManuals([]);
                    setError(null);
                    setLoading(false);
                    return null;
                }

                if (!response.ok) {
                    return response.text().then(errorText => {
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
                    });
                }

                return response.json();
            })
            .then(data => {
                if (data) {
                    console.log("API response data:", data);

                    if (!data.manuals) {
                        console.warn("Response doesn't contain a 'manuals' property:", data);
                        setManuals([]);
                    } else {
                        setManuals(data.manuals);
                    }

                    setError(null);
                }
            })
            .catch(err => {
                console.error("Error fetching manuals:", err);
                setError(err.message || "Failed to fetch manuals");
            })
            .finally(() => {
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchManuals();
    }, []);

    const handleDelete = (fileId) => {
        if (window.confirm("Är du säker på att du vill ta bort denna manual?")) {
            setIsDeleting(true);

            // Get authentication token
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                setError("No authentication token found in localStorage");
                setIsDeleting(false);
                return;
            }

            const authHeader = `${tokenType} ${accessToken}`;

            // Use query parameters instead of a request body
            const url = `${import.meta.env.VITE_API_URL}/v1/gen/delete_user_manual_favourite?file_id=${fileId}&hard_delete=false`;
            console.log("Sending delete request to:", url);

            // Call delete endpoint with query parameters
            fetch(url, {
                method: 'DELETE',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json'
                }
                // No body needed - parameters are in the URL
            })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(errorText => {
                            let errorMessage = `Error: ${response.status} ${response.statusText}`;

                            try {
                                // Try to parse error as JSON
                                const errorData = JSON.parse(errorText);
                                if (errorData.detail) {
                                    errorMessage = errorData.detail;
                                }
                            } catch (e) {
                                // If not JSON, use the text
                                if (errorText) {
                                    errorMessage = errorText;
                                }
                            }

                            throw new Error(errorMessage);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("Delete successful:", data);
                    // On success, refresh the list
                    fetchManuals();
                })
                .catch(error => {
                    console.error('Error deleting manual:', error);
                    // Improved error handling
                    setError(`Failed to delete manual: ${error.message || 'Unknown error'}`);
                })
                .finally(() => {
                    setIsDeleting(false);
                });
        }
    };

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
                                    <td className="py-3 px-4 text-base text-gray-700 font-black font-['Barlow_Condensed']">{manual.users_own_naming || "-"}</td>
                                    <td className="py-3 px-4 text-base text-gray-700 font-['Barlow_Condensed']">{manual.brand || "-"}</td>
                                    <td className="py-3 px-4 text-base text-gray-700 font-['Barlow_Condensed']">{manual.device_type || "-"}</td>

                                    <td className="py-3 px-4 text-base text-amber-900 hover:text-indigo-900 font-['Roboto']">

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
                                            onClick={() => handleDelete(manual.file_id)}
                                            className="text-sky-800 hover:text-amber-900 inline-flex items-center relative group"
                                            disabled={isDeleting}
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