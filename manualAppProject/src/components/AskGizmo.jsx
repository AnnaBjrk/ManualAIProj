import React, { useState, useEffect } from "react";

export default function AskGizmo() {
    const [userFiles, setUserFiles] = useState([]);
    const [selectedFileId, setSelectedFileId] = useState("");
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);
    const [filesError, setFilesError] = useState(null);

    // Check authentication status
    const [isAuthenticated, setIsAuthenticated] = useState(true);

    // Check if user is authenticated on component mount
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setIsAuthenticated(false);
            console.log("User is not authenticated - no token found");
        }
    }, []);

    // Fetch the user's saved files on component mount
    useEffect(() => {
        if (!isAuthenticated) {
            console.log("Skipping file fetch - user not authenticated");
            return;
        }

        const fetchUserFiles = async () => {
            setIsLoadingFiles(true);
            setFilesError(null);

            try {
                const baseUrl = import.meta.env.VITE_API_URL;
                const token = localStorage.getItem('access_token');

                const response = await fetch(`${baseUrl}/v1/uploads/get_user_file_list`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    credentials: 'include',
                });

                if (response.status === 401) {
                    // User is unauthorized - update auth state and return
                    setIsAuthenticated(false);
                    localStorage.removeItem('access_token');
                    console.log("User session expired or invalid");
                    return;
                }

                if (!response.ok) {
                    throw new Error('Failed to fetch user files');
                }

                const data = await response.json();
                console.log("User files data:", data);

                // Filter out files that are marked as remove_from_view
                const filteredFiles = data.files.filter(file => !file.remove_from_view);

                // Add additional file info for display
                const enhancedFiles = filteredFiles.map(file => ({
                    ...file,
                    displayName: `${file.users_own_naming} (${file.brand} ${file.model_numbers})`
                }));

                setUserFiles(enhancedFiles);

                // Set default selected file if files exist
                if (enhancedFiles.length > 0) {
                    setSelectedFileId(enhancedFiles[0].file_id);
                }
            } catch (err) {
                console.error('Error fetching user files:', err);
                setFilesError(err.message);

                // Fallback to mock data if API call fails
                fallbackToMockData();
            } finally {
                setIsLoadingFiles(false);
            }
        };

        // Fallback function for mock data
        const fallbackToMockData = () => {
            console.warn("Falling back to mock file data due to API error");

            const mockFiles = [
                {
                    file_id: "123e4567-e89b-12d3-a456-426614174000",
                    users_own_naming: "TV i vardagsrummet",
                    brand: "Samsung",
                    device_type: "TV",
                    model_numbers: "UE55TU7105",
                    remove_from_view: false,
                    displayName: "TV i vardagsrummet (Samsung UE55TU7105)"
                },
                {
                    file_id: "223e4567-e89b-12d3-a456-426614174001",
                    users_own_naming: "Diskmaskin i köket",
                    brand: "Bosch",
                    device_type: "Diskmaskin",
                    model_numbers: "SMV4HCX48E",
                    remove_from_view: false,
                    displayName: "Diskmaskin i köket (Bosch SMV4HCX48E)"
                },
                {
                    file_id: "323e4567-e89b-12d3-a456-426614174002",
                    users_own_naming: "Min mobil",
                    brand: "Samsung",
                    device_type: "Mobiltelefon",
                    model_numbers: "Galaxy S21",
                    remove_from_view: false,
                    displayName: "Min mobil (Samsung Galaxy S21)"
                }
            ];

            setUserFiles(mockFiles);
            setSelectedFileId(mockFiles[0].file_id);
        };

        fetchUserFiles();
    }, []);

    const handleFileChange = (e) => {
        setSelectedFileId(e.target.value);
    };

    const handleQuestionChange = (e) => {
        setQuestion(e.target.value);
        // Clear any previous errors when user starts typing
        if (error) setError(null);
    };

    const handleDownloadManual = async (fileId) => {
        try {
            setIsLoading(true);
            setError(null);

            const baseUrl = import.meta.env.VITE_API_URL;
            const token = localStorage.getItem('access_token');

            console.log(`Calling download URL endpoint: ${baseUrl}/v1/gen/get_download_url/${fileId}`);

            // Call the download URL endpoint
            const response = await fetch(`${baseUrl}/v1/gen/get_download_url/${fileId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                credentials: 'include',
            });

            console.log("Download URL response status:", response.status);

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod vid hämtning av manualen';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Download URL response data:", data);

            if (data && data.downloadUrl) {
                // Open the download URL in a new tab
                window.open(data.downloadUrl, '_blank');
            } else {
                setError("Kunde inte hämta nedladdningslänk för manualen");
            }
        } catch (err) {
            console.error('Error getting download URL:', err);
            setError(`Kunde inte ladda ner manualen: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate inputs
        if (!selectedFileId) {
            setError("Du måste välja en manual");
            return;
        }

        if (!question.trim()) {
            setError("Du måste ställa en fråga");
            return;
        }

        setIsLoading(true);
        setError(null);
        setAnswer("");

        try {
            const baseUrl = import.meta.env.VITE_API_URL;
            const token = localStorage.getItem('access_token');

            // Create URL with query parameters for the LLM endpoint
            const params = new URLSearchParams();
            params.append('user_question', question.trim());
            params.append('file_id', selectedFileId);

            // Log the parameters for debugging
            console.log("Query parameters:", {
                user_question: question.trim(),
                file_id: selectedFileId
            });

            console.log("Making request to LLM endpoint with params:", {
                user_question: question,
                file_id: selectedFileId
            });

            console.log(`Calling LLM endpoint: ${baseUrl}/v1/llm/llm_request_full_text?${params.toString()}`);

            const response = await fetch(`${baseUrl}/v1/llm/llm_request_full_text?${params.toString()}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                credentials: 'include',
            });

            console.log("Response status:", response.status);

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod vid frågehanteringen';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("LLM response:", data);

            // Check if the response has a specific format
            if (data && data.response) {
                setAnswer(data.response);
            } else if (typeof data === 'string') {
                setAnswer(data);
            } else {
                // If we can't determine the structure, display the raw JSON
                setAnswer(JSON.stringify(data, null, 2));
            }
        } catch (err) {
            console.error('Error getting answer:', err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="mt-8 mb-10">
            {!isAuthenticated ? (
                <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-md p-6 my-6">
                    <h2 className="font-['Neucha'] text-2xl mb-2">Du måste logga in</h2>
                    <p className="font-['Barlow_Condensed']">Du måste vara inloggad för att kunna ställa frågor om dina manualer.</p>
                    <div className="mt-4">
                        <a href="/login" className="inline-block px-4 py-2 bg-sky-700 text-white rounded-md hover:bg-sky-800 transition-colors duration-300 font-['Neucha']">
                            Gå till inloggning
                        </a>
                    </div>
                </div>
            ) : (
                <>
                    <h1 className="font-['Neucha'] text-2xl mb-6">Ställ en fråga</h1>
                    <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed mb-6">
                        Här kan du ställa frågor om dina manualer. Välj den manual du vill fråga om och ställ din fråga.
                        Gizmo hjälper dig att hitta svaret.
                        <br /><br />
                        Du måste vara inloggad för att göra en sökning. Och du kan bara göra en sökning om du har sparat manualen till din lista.
                    </p>

                    {/* File selection and question form */}
                    <form onSubmit={handleSubmit} className="my-6 p-6 bg-gray-50 rounded-lg shadow-sm">
                        {/* File dropdown */}
                        <div className="mb-4">
                            <label htmlFor="file-select" className="block mb-2 text-gray-700 font-['Barlow_Condensed']">
                                Välj manual
                            </label>
                            <div className="relative">
                                <select
                                    id="file-select"
                                    value={selectedFileId}
                                    onChange={handleFileChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none"
                                    disabled={isLoadingFiles || userFiles.length === 0}
                                >
                                    {userFiles.length === 0 ? (
                                        <option value="">Inga manualer tillgängliga - har du loggat in?</option>
                                    ) : (
                                        userFiles.map((file) => (
                                            <option key={file.file_id} value={file.file_id}>
                                                {file.displayName || file.users_own_naming}
                                            </option>
                                        ))
                                    )}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                            {filesError && (
                                <p className="mt-1 text-amber-600 text-sm">
                                    {filesError}
                                </p>
                            )}
                        </div>

                        {/* Question input */}
                        <div className="mb-4">
                            <label htmlFor="question-input" className="block mb-2 text-gray-700 font-['Barlow_Condensed']">
                                Din fråga
                            </label>
                            <textarea
                                id="question-input"
                                value={question}
                                onChange={handleQuestionChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. Hur ställer jag in tiden på min mikrovågsugn?"
                                rows="3"
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-amber-50 text-amber-700 rounded-md mb-4 text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="mt-4 px-1 py-1 ml-4 mb-2 w-30 bg-sky-900 text-base border rounded-sm text-white hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                            disabled={isLoading || isLoadingFiles || userFiles.length === 0}
                        >
                            {isLoading ? 'Hämtar svar...' : 'Fråga Gizmo'}
                        </button>
                    </form>

                    {/* Answer section */}
                    {answer && (
                        <div className="bg-white rounded-lg shadow-sm p-6 my-6">
                            <h2 className="font-['Neucha'] text-2xl mb-4">Svar från Gizmo</h2>

                            <div className="prose max-w-none">
                                {/* Display which manual was used for the answer */}
                                {selectedFileId && (
                                    <div className="mb-4 p-3 bg-gray-50 rounded-md">
                                        <p className="text-sm text-gray-600 font-['Barlow_Condensed']">
                                            Svar baserat på: <strong>{userFiles.find(f => f.file_id === selectedFileId)?.displayName || 'Vald manual'}</strong>
                                        </p>
                                    </div>
                                )}

                                {/* Answer content with simple formatting */}
                                {answer.split('\n').map((paragraph, index) => (
                                    <p key={index} className="mb-2 font-['Barlow_Condensed']">
                                        {paragraph}
                                    </p>
                                ))}

                                {/* Download manual button */}
                                {selectedFileId && (
                                    <div className="mt-6 pt-4 border-t border-gray-200">
                                        <button
                                            onClick={() => handleDownloadManual(selectedFileId)}
                                            className="flex items-center px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors duration-300 font-['Neucha']"
                                        >
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                            </svg>
                                            Ladda ner manualen
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Loading indicator */}
                    {isLoading && (
                        <div className="flex justify-center my-6">
                            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-sky-700"></div>
                        </div>
                    )}

                    <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed mt-6">
                        Gizmo hjälper dig att hitta information i dina manualer. För att få bästa möjliga svar, försök vara
                        specifik i din fråga. Om Gizmo inte kan hitta svaret i manualen kommer du få veta det.
                    </p>
                </>
            )}
        </div>
    );
}