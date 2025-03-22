import { useState, useEffect } from 'react';

const AdminTableUsers = () => {
    const [users, setUsers] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchUsers(currentPage, searchQuery);
    }, [currentPage, searchQuery]);

    const fetchUsers = async (page, search = '') => {
        setIsLoading(true);
        try {
            // Get authentication token from localStorage
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            // Create authentication header
            const authHeader = `${tokenType} ${accessToken}`;

            // Use the correct API endpoint
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/auth/users_for_admin`;

            // Add search parameter if provided
            const queryParams = new URLSearchParams({
                page: page.toString(),
                page_size: '20'
            });

            if (search) {
                queryParams.append('search', search);
            }

            console.log("Making request to:", `${apiUrl}?${queryParams.toString()}`);

            const response = await fetch(`${apiUrl}?${queryParams.toString()}`, {
                method: "GET",
                headers: {
                    "Authorization": authHeader,
                    "Content-Type": "application/json"
                }
            });

            console.log("API response status:", response.status);
            console.log("Authentication:", authHeader.replace(/^Bearer (.{5}).*$/, 'Bearer $1...'));

            // Handle 404 as an empty result, not an error
            if (response.status === 404) {
                console.log("No users found (404 response)");
                setUsers([]);
                setError(null);
                setTotalPages(1);
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

            // Debug: Check user objects structure
            if (data.users && data.users.length > 0) {
                console.log("First user object structure:", data.users[0]);
                console.log("User ID type and value:",
                    typeof data.users[0].id,
                    data.users[0].id);
            }

            // Handle different response structures
            if (Array.isArray(data)) {
                // If data is directly an array
                setUsers(data.map(user => ({
                    ...user,
                    id: user.id || user.user_id // Ensure id is set
                })));
                setTotalPages(Math.ceil(data.length / 20));
            } else if (data.users) {
                // If data contains a users property and possibly total_pages
                setUsers(data.users.map(user => ({
                    ...user,
                    id: user.id || user.user_id // Ensure id is set
                })));
                setTotalPages(data.total_pages || Math.ceil(data.users.length / 20));
            } else {
                console.warn("Response doesn't contain users array:", data);
                setUsers([]);
                setTotalPages(1);
            }

            setError(null);
        } catch (error) {
            console.error("Error fetching users:", error);
            setError(error.message || "Failed to fetch users");
            setUsers([]);
        } finally {
            setIsLoading(false);
        }
    };

    const toggleAdminStatus = async (userId, currentStatus) => {
        try {
            // Log the userId being sent
            console.log("Toggling admin status for user ID:", userId);

            // Validate userId
            if (!userId || userId === "undefined") {
                throw new Error("Invalid user ID. Cannot update admin status.");
            }

            // Get authentication token
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            const authHeader = `${tokenType} ${accessToken}`;
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/auth/users/${userId}/admin-status`;

            console.log("Making request to:", apiUrl);

            const response = await fetch(apiUrl, {
                method: 'PATCH',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    is_admin: !currentStatus
                })
            });

            console.log("Toggle response status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response:", errorText);
                throw new Error(`Failed to update admin status: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Toggle result:", result);

            // Update local state after successful API call
            setUsers(users.map(user =>
                user.id === userId ? { ...user, is_admin: !user.is_admin } : user
            ));
        } catch (error) {
            console.error('Error updating admin status:', error);
            setError(error.message || "Failed to update admin status");
        }
    };

    const togglePartnerStatus = async (userId, currentStatus) => {
        try {
            // Log the userId being sent
            console.log("Toggling partner status for user ID:", userId);

            // Validate userId
            if (!userId || userId === "undefined") {
                throw new Error("Invalid user ID. Cannot update partner status.");
            }

            // Get authentication token
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            const authHeader = `${tokenType} ${accessToken}`;
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/auth/users/${userId}/partner-status`;

            console.log("Making request to:", apiUrl);

            const response = await fetch(apiUrl, {
                method: 'PATCH',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    is_partner: !currentStatus
                })
            });

            console.log("Toggle response status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response:", errorText);
                throw new Error(`Failed to update partner status: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Toggle result:", result);

            setUsers(users.map(user =>
                user.id === userId ? { ...user, is_partner: !user.is_partner } : user
            ));
        } catch (error) {
            console.error('Error updating partner status:', error);
            setError(error.message || "Failed to update partner status");
        }
    };

    const toggleDeletedStatus = async (userId, currentStatus) => {
        try {
            // Log the userId being sent
            console.log("Toggling delete status for user ID:", userId);

            // Validate userId
            if (!userId || userId === "undefined") {
                throw new Error("Invalid user ID. Cannot update delete status.");
            }

            // Get authentication token
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type');

            if (!accessToken) {
                throw new Error("No authentication token found in localStorage");
            }

            const authHeader = `${tokenType} ${accessToken}`;
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/auth/users/${userId}/delete-status`;

            console.log("Making request to:", apiUrl);

            const response = await fetch(apiUrl, {
                method: 'PATCH',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    deleted: !currentStatus
                })
            });

            console.log("Toggle response status:", response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response:", errorText);
                throw new Error(`Failed to update delete status: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Toggle result:", result);

            setUsers(users.map(user =>
                user.id === userId ? { ...user, deleted: !user.deleted } : user
            ));
        } catch (error) {
            console.error('Error updating delete status:', error);
            setError(error.message || "Failed to update delete status");
        }
    };

    const handleNextPage = () => {
        if (currentPage < totalPages) {
            setCurrentPage(currentPage + 1);
        }
    };

    const handlePrevPage = () => {
        if (currentPage > 1) {
            setCurrentPage(currentPage - 1);
        }
    };

    const handleSearch = (e) => {
        e.preventDefault();
        setSearchQuery(searchTerm);
        setCurrentPage(1); // Reset to first page when searching
    };

    const clearSearch = () => {
        setSearchTerm('');
        setSearchQuery('');
        setCurrentPage(1);
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-black font-['Barlow_Condensed'] mb-6">Ändra behörigheter och ta bort användare</h1>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="mb-6 flex items-end">
                <div className="flex-grow mr-2">
                    <label htmlFor="search-users" className="block text-sm font-medium text-gray-700 mb-1 font-['Barlow_Condensed']">
                        Sök användare
                    </label>
                    <input
                        type="text"
                        id="search-users"
                        placeholder="Sök på för- eller efternamn..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-sky-500 focus:border-sky-500 font-['Barlow_Condensed']"
                    />
                </div>
                <button
                    type="submit"
                    className="px-4 py-2 bg-sky-900 text-white text-sm font-['Neucha'] rounded-sm hover:bg-amber-900 transition-colors duration-200"
                >
                    Sök
                </button>
                {searchQuery && (
                    <button
                        type="button"
                        onClick={clearSearch}
                        className="px-4 py-2 ml-2 bg-gray-300 text-gray-700 text-sm font-['Neucha'] rounded-sm hover:bg-gray-400 transition-colors duration-200"
                    >
                        Rensa
                    </button>
                )}
            </form>

            {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-md mb-4">
                    <p>{error}</p>
                </div>
            )}

            {/* Search status message */}
            {searchQuery && (
                <div className="mb-4 text-sm text-gray-600 font-['Barlow_Condensed']">
                    Visar resultat för: <span className="font-semibold">"{searchQuery}"</span>
                </div>
            )}

            <div className="overflow-x-auto shadow-md rounded-lg">
                <table className="min-w-full bg-white">
                    <thead>
                        <tr className="bg-gray-100 border-b">
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Namn</th>
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Uppladdade Manualer</th>
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Valda Manualer</th>
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Admin</th>
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Partner</th>
                            <th className="py-3 px-4 text-left text-sm font-black font-['Barlow_Condensed']">Radera Användare*</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {isLoading ? (
                            <tr>
                                <td colSpan="6" className="py-4 px-4 text-center text-gray-500">
                                    <div className="w-full flex justify-center items-center py-6">
                                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-700"></div>
                                    </div>
                                </td>
                            </tr>
                        ) : users.length === 0 ? (
                            <tr>
                                <td colSpan="6" className="py-4 px-4 text-center text-gray-500">Inga användare hittades</td>
                            </tr>
                        ) : (
                            users.map((user, index) => {
                                // Add debug logging for each user when rendering
                                console.log(`User ${index} ID:`, user.id);

                                return (
                                    <tr key={user.id || `user-${index}`} className="hover:bg-gray-50">
                                        <td className="py-3 px-4 text-sm text-gray-700 font-black font-['Barlow_Condensed']">
                                            {`${user.first_name || ''} ${user.last_name || ''}`}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {user.manual_count || 0}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            {user.display_count || 0}
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            <button
                                                onClick={() => toggleAdminStatus(user.id, user.is_admin)}
                                                className={`px-1 py-1 ml-4 mb-2 w-20 font-['Neucha'] ${user.is_admin
                                                    ? 'bg-sky-900 text-amber-50'
                                                    : 'bg-gray-200 text-gray-700'
                                                    } text-sm rounded-sm border-sky-700 items-center hover:bg-amber-900 transition-colors duration-200`}
                                            >
                                                {user.is_admin ? 'Admin' : 'Ej Admin'}
                                            </button>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            <button
                                                onClick={() => togglePartnerStatus(user.id, user.is_partner)}
                                                className={`px-1 py-1 ml-4 mb-2 w-20 font-['Neucha'] ${user.is_partner
                                                    ? 'bg-sky-900 text-amber-50'
                                                    : 'bg-gray-200 text-gray-700'
                                                    } text-sm rounded-sm border-sky-700 items-center hover:bg-amber-900 transition-colors duration-200`}
                                            >
                                                {user.is_partner ? 'Partner' : 'Ej Partner'}
                                            </button>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 font-['Barlow_Condensed']">
                                            <button
                                                onClick={() => toggleDeletedStatus(user.id, user.deleted)}
                                                className={`px-1 py-1 ml-4 mb-2 w-20 font-['Neucha'] ${user.deleted
                                                    ? 'bg-amber-700 text-white'
                                                    : 'bg-gray-200 text-gray-700'
                                                    } text-sm rounded-sm items-center hover:bg-amber-700 transition-colors duration-200`}
                                            >
                                                {user.deleted ? 'Raderas' : 'Aktiv'}
                                            </button>
                                        </td>
                                    </tr>
                                )
                            })
                        )}
                    </tbody>
                </table>

            </div>
            <p className="text-sm  text-gray-600 font-['Barlow_Condensed']">* användare som markeras med "Raderas", tas bort från systemet efter 30 dagar</p>

            {/* Pagination controls */}
            <div className="flex justify-between items-center mt-6">
                <div className="text-sm text-gray-700 font-['Barlow_Condensed']">
                    Visar sida {currentPage} av {totalPages}
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={handlePrevPage}
                        disabled={currentPage === 1}
                        className="px-3 py-1 bg-sky-900 text-white text-sm font-['Neucha'] rounded-sm disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-amber-900 transition-colors duration-200"
                    >
                        Föregående
                    </button>
                    <button
                        onClick={handleNextPage}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 bg-sky-900 text-white text-sm font-['Neucha'] rounded-sm disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-amber-900 transition-colors duration-200"
                    >
                        Nästa
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdminTableUsers;