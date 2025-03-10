import React, { useState, useEffect } from "react";

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
                <h2 className="font-['Roboto'] text-2xl mb-4">Dina sparade manualer</h2>
                <div className="w-full flex justify-center items-center py-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-700"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-8 mb-10">
            <h2 className="font-['Roboto'] text-2xl mb-4">Dina sparade manualer</h2>

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
                    <p className="text-gray-600 font-['Roboto']">Inga manualer hittades</p>
                    <p className="text-gray-500 text-sm mt-1">Du har inte lagt till några manualer än</p>
                </div>
            ) : (
                <div className="overflow-x-auto shadow-md rounded-lg">
                    <table className="min-w-full bg-white">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider font-['Roboto']">Kommentar</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider font-['Roboto']">Märke</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider font-['Roboto']">Enhetstyp</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider font-['Roboto']">Modellnummer</th>
                                <th className="py-3 px-4 text-left text-xs font-medium text-gray-700 uppercase tracking-wider font-['Roboto']">Åtgärder</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {manuals.map((manual, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Roboto']">{manual.users_own_naming || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Roboto']">{manual.brand || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Roboto']">{manual.device_type || "-"}</td>
                                    <td className="py-3 px-4 text-sm text-gray-700 font-['Roboto']">
                                        {manual.model_numbers && Array.isArray(manual.model_numbers)
                                            ? manual.model_numbers.filter(num => num).join(", ")
                                            : "-"}
                                    </td>
                                    <td className="py-3 px-4 text-sm text-indigo-600 hover:text-indigo-900 font-['Roboto']">
                                        <a href={`/view/${manual.file_id}`} className="mr-3">Visa</a>
                                        <button
                                            onClick={() => console.log(`Remove manual ${manual.file_id}`)}
                                            className="text-red-600 hover:text-red-900"
                                        >
                                            Ta bort
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