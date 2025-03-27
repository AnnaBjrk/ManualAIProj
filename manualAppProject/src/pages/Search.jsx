import React, { useState, useEffect } from "react";
import { Download } from 'lucide-react';

export default function Search() {
    const [activeTab, setActiveTab] = useState("image");

    // Text search state
    const [formData, setFormData] = useState({
        brand_id: "",
        device_type_id: "",
        modelnumber: "",
        modelname: ""
    });

    // Image search state
    const [imageFormData, setImageFormData] = useState({
        brand_id: "",
        device_type_id: "",
        image: null
    });

    // Dropdown options state
    const [brands, setBrands] = useState([]);
    const [deviceTypes, setDeviceTypes] = useState([]);
    const [isLoadingOptions, setIsLoadingOptions] = useState(false);
    const [optionsError, setOptionsError] = useState(null);

    // Shared state
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validationError, setValidationError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    // Add state for the save to list modal
    const [showSaveModal, setShowSaveModal] = useState(false);
    const [selectedManual, setSelectedManual] = useState(null);
    const [customName, setCustomName] = useState("");
    const [isSaving, setIsSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(null);
    const [saveError, setSaveError] = useState(null);

    const handleDownload = async (fileId) => {
        try {
            // Use correct endpoint with underscores instead of hyphens
            const baseUrl = import.meta.env.VITE_API_URL;

            // Get token from localStorage for authentication
            const token = localStorage.getItem('access_token');

            const response = await fetch(`${baseUrl}/v1/gen/get_download_url/${fileId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            // Parse the JSON response
            const data = await response.json();
            console.log("Received download URL:", data);

            // open in new tab
            window.open(data.downloadUrl, '_blank');

        } catch (error) {
            console.error('Failed to get download URL:', error);
        }
    };

    // Fetch brands and device types on component mount
    useEffect(() => {
        const fetchOptions = async () => {
            setIsLoadingOptions(true);
            setOptionsError(null);

            try {
                const baseUrl = import.meta.env.VITE_API_URL;

                // Get token from localStorage
                const token = localStorage.getItem('access_token');

                const headers = {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                };

                // Fetch brands
                const brandsResponse = await fetch(`${baseUrl}/v1/gen/list_all_brands`, {
                    method: 'GET',
                    headers: headers,
                    credentials: 'include',
                });

                // Fetch device types
                const deviceTypesResponse = await fetch(`${baseUrl}/v1/gen/list_all_device_types`, {
                    method: 'GET',
                    headers: headers,
                    credentials: 'include',
                });

                if (!brandsResponse.ok) {
                    throw new Error(`Error fetching brands: ${brandsResponse.statusText}`);
                }

                if (!deviceTypesResponse.ok) {
                    throw new Error(`Error fetching device types: ${deviceTypesResponse.statusText}`);
                }

                const brandsData = await brandsResponse.json();
                const deviceTypesData = await deviceTypesResponse.json();

                console.log("Brands data:", brandsData);
                console.log("Device types data:", deviceTypesData);

                // Handle the data - check to make sure it's in the expected format
                const brandsArray = brandsData.brands || [];
                const deviceTypesArray = deviceTypesData.device_types || [];

                setBrands(brandsArray);
                setDeviceTypes(deviceTypesArray);

                // Set default selected values if there are options available
                if (brandsArray.length > 0) {
                    setFormData(prev => ({ ...prev, brand_id: brandsArray[0].id }));
                    setImageFormData(prev => ({ ...prev, brand_id: brandsArray[0].id }));
                }

                if (deviceTypesArray.length > 0) {
                    setFormData(prev => ({ ...prev, device_type_id: deviceTypesArray[0].id }));
                    setImageFormData(prev => ({ ...prev, device_type_id: deviceTypesArray[0].id }));
                }
            } catch (err) {
                console.error("Error fetching dropdown options:", err);
                setOptionsError(err.message);

                // Fallback to mock data if API calls fail
                fallbackToMockData();
            } finally {
                setIsLoadingOptions(false);
            }
        };

        // Add a fallback function to use mock data if API calls fail
        const fallbackToMockData = () => {
            console.warn("Falling back to mock data due to API error");

            const mockBrands = [
                { id: "123e4567-e89b-12d3-a456-426614174000", name: "Samsung" },
                { id: "223e4567-e89b-12d3-a456-426614174001", name: "Electrolux" },
                { id: "323e4567-e89b-12d3-a456-426614174002", name: "Apple" },
                { id: "423e4567-e89b-12d3-a456-426614174003", name: "LG" },
                { id: "523e4567-e89b-12d3-a456-426614174004", name: "Bosch" }
            ];

            const mockDeviceTypes = [
                { id: "623e4567-e89b-12d3-a456-426614174005", type: "Diskmaskin" },
                { id: "723e4567-e89b-12d3-a456-426614174006", type: "Tvättmaskin" },
                { id: "823e4567-e89b-12d3-a456-426614174007", type: "Kylskåp" },
                { id: "923e4567-e89b-12d3-a456-426614174008", type: "Mobiltelefon" }
            ];

            setBrands(mockBrands);
            setDeviceTypes(mockDeviceTypes);

            // Set default selected values
            setFormData(prev => ({
                ...prev,
                brand_id: mockBrands[0].id,
                device_type_id: mockDeviceTypes[0].id
            }));

            setImageFormData(prev => ({
                ...prev,
                brand_id: mockBrands[0].id,
                device_type_id: mockDeviceTypes[0].id
            }));
        };

        // Call the fetch function
        fetchOptions();
    }, []);

    // Text search handlers
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));

        // Clear validation error when user starts typing in either field
        if ((name === 'modelnumber' || name === 'modelname') && validationError) {
            setValidationError(null);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Check if both modelnumber and modelname are empty
        if (!formData.modelnumber.trim() && !formData.modelname.trim()) {
            setValidationError("Antingen Modellnummer eller Modellnamn måste anges");
            return;
        }

        setIsLoading(true);
        setError(null);
        setValidationError(null);

        console.log('Submitting form data:', formData);

        // For debugging - show what dropdown values are selected
        console.log('Selected brand_id:', formData.brand_id);
        console.log('Selected device_type_id:', formData.device_type_id);
        console.log('Available brands:', brands);
        console.log('Available device types:', deviceTypes);

        try {
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/search/words_only`;
            console.log("Making request to:", apiUrl);

            // Create URL with query parameters
            const params = new URLSearchParams();
            for (const key in formData) {
                if (formData[key]) {
                    params.append(key, formData[key]);
                }
            }

            const response = await fetch(`${apiUrl}?${params.toString()}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                // Include credentials if authentication is required
                credentials: 'include',
            });

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod vid sökningen';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    // If parsing JSON fails, use status text or a generic message
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            try {
                const text = await response.text();
                console.log("Raw response:", text);

                if (text.trim()) {
                    const data = JSON.parse(text);
                    console.log("Parsed data:", data);

                    // Simplified handling of the response structure
                    if (data && data.manuals && Array.isArray(data.manuals)) {
                        setSearchResults(data.manuals);
                        console.log("Setting search results to:", data.manuals);
                    } else {
                        console.error("Unexpected data structure:", data);
                        setError('Oväntad datastruktur från servern');
                        setSearchResults([]);
                    }
                } else {
                    setSearchResults([]);
                }
            } catch (jsonError) {
                console.error('Error parsing response:', jsonError);
                throw new Error('Kunde inte tolka svaret från servern');
            }
        } catch (err) {
            console.error('Search error:', err);
            setError(err.message);
            setSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    // Image search handlers
    const handleImageFormChange = (e) => {
        const { name, value } = e.target;
        setImageFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleImageChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setImageFormData(prevState => ({
                ...prevState,
                image: e.target.files[0]
            }));
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const file = e.dataTransfer.files[0];
            if (file.type.startsWith('image/')) {
                setImageFormData(prevState => ({
                    ...prevState,
                    image: file
                }));
            } else {
                setError("Endast bildfiler kan laddas upp");
            }
        }
    };

    const handleImageSubmit = async (e) => {
        e.preventDefault();

        // Validate form fields
        if (!imageFormData.brand_id.trim()) {
            setValidationError("Märke måste anges");
            return;
        }

        if (!imageFormData.device_type_id.trim()) {
            setValidationError("Enhetstyp måste anges");
            return;
        }

        if (!imageFormData.image) {
            setValidationError("En bild måste laddas upp");
            return;
        }

        setIsLoading(true);
        setError(null);
        setValidationError(null);

        try {
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/gen/search/with_image`;
            console.log("Making image search request to:", apiUrl);

            const formData = new FormData();
            formData.append('image', imageFormData.image);
            formData.append('brand_id', imageFormData.brand_id);
            formData.append('device_type_id', imageFormData.device_type_id);

            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
                // Include credentials if authentication is required
                credentials: 'include',
            });

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod vid bildsökningen';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Image search response:", data);

            if (data && data.manuals && Array.isArray(data.manuals)) {
                setSearchResults(data.manuals);
            } else {
                console.error("Unexpected data structure:", data);
                setError('Oväntad datastruktur från servern');
                setSearchResults([]);
            }
        } catch (err) {
            console.error('Image search error:', err);
            setError(err.message);
            setSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    // Save manual to user list handlers
    const openSaveModal = (manual) => {
        // Pre-fill the custom name field with the model name if available
        setCustomName(manual.modelname || "");
        setSelectedManual(manual);
        setShowSaveModal(true);
        // Reset any previous save messages
        setSaveSuccess(null);
        setSaveError(null);
    };

    const closeSaveModal = () => {
        setShowSaveModal(false);
        setSelectedManual(null);
        setCustomName("");
    };

    const handleSaveToList = async () => {
        if (!selectedManual || !selectedManual.file_id) {
            setSaveError("Ingen manual vald");
            return;
        }

        if (!customName.trim()) {
            setSaveError("Du måste ange ett namn");
            return;
        }

        setIsSaving(true);
        setSaveError(null);

        try {
            const baseUrl = import.meta.env.VITE_API_URL;
            const token = localStorage.getItem('access_token');

            const response = await fetch(`${baseUrl}/v1/uploads/add_manual_to_user_list`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    file_id: selectedManual.file_id,
                    users_own_naming: customName
                }),
                credentials: 'include',
            });

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod när manualen skulle sparas';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Save response:", data);

            setSaveSuccess(data.message || "Manualen har sparats i din lista");

            // Close the modal after a delay
            setTimeout(() => {
                closeSaveModal();
            }, 2000);

        } catch (err) {
            console.error('Error saving manual:', err);
            setSaveError(err.message);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Hitta din apparat eller hemelektronik</h1>
            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Sök efter din hushållsapparat eller hemelektronik. Spara till listan på din sida - så blir det enklare nästa gång du ska göra en sökning.
                Klicka vidare till Gizmo vår AI - agent om du vill ha hjälp att lösa ett problem.
            </p>

            {/* Error message for dropdown options */}
            {optionsError && (
                <div className="p-4 bg-amber-50 text-amber-700 rounded-md my-4">
                    <p>Kunde inte hämta alla alternativ: {optionsError}</p>
                    <p className="text-sm">Använder fördefinierade alternativ istället.</p>
                </div>
            )}

            {/* Tab Navigation */}
            <div className="border-b border-gray-200 mt-6">
                <nav className="flex -mb-px">
                    <button
                        className={`py-4 px-6 font-['Neucha'] font-medium border-b-2 text-base focus:outline-none ${activeTab === "image"
                            ? "border-sky-700 text-sky-700"
                            : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                            }`}
                        onClick={() => setActiveTab("image")}
                    >
                        Bildsökning
                    </button>
                    <button
                        className={`py-4 px-6 font-['Neucha'] font-medium border-b-2 text-base focus:outline-none ${activeTab === "text"
                            ? "border-sky-700 text-sky-700"
                            : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                            }`}
                        onClick={() => setActiveTab("text")}
                    >
                        Textsökning
                    </button>
                </nav>
            </div>

            {/* Text Search Form */}
            {activeTab === "text" && (
                <form onSubmit={handleSubmit} className="my-6 p-6 bg-gray-50 rounded-lg shadow-sm">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="flex flex-col relative">
                            <label htmlFor="brand_id" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Märke</label>
                            <div className="relative">
                                <select
                                    id="brand_id"
                                    name="brand_id"
                                    value={formData.brand_id}
                                    onChange={handleChange}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none"
                                    disabled={isLoadingOptions}
                                >
                                    <option value="">Välj märke</option>
                                    {brands.map(brand => (
                                        <option key={brand.id} value={brand.id}>
                                            {brand.name}
                                        </option>
                                    ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col relative">
                            <label htmlFor="device_type_id" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Enhetstyp</label>
                            <div className="relative">
                                <select
                                    id="device_type_id"
                                    name="device_type_id"
                                    value={formData.device_type_id}
                                    onChange={handleChange}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none"
                                    disabled={isLoadingOptions}
                                >
                                    <option value="">Välj enhetstyp</option>
                                    {deviceTypes.map(deviceType => (
                                        <option key={deviceType.id} value={deviceType.id}>
                                            {deviceType.type}
                                        </option>
                                    ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col">
                            <label htmlFor="modelnumber" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Modellnummer</label>
                            <input
                                type="text"
                                id="modelnumber"
                                name="modelnumber"
                                value={formData.modelnumber}
                                onChange={handleChange}
                                className={`px-3 py-2 border ${validationError ? 'border-amber-500' : 'border-gray-300'} rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500`}
                                placeholder="T.ex. ESF5545LOX, SM-G998B"
                            />
                        </div>

                        <div className="flex flex-col">
                            <label htmlFor="modelname" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Modellnamn</label>
                            <input
                                type="text"
                                id="modelname"
                                name="modelname"
                                value={formData.modelname}
                                onChange={handleChange}
                                className={`px-3 py-2 border ${validationError ? 'border-amber-500' : 'border-gray-300'} rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500`}
                                placeholder="T.ex. Galaxy S21 Ultra"
                            />
                        </div>
                    </div>

                    {validationError && (
                        <div className="mt-2 text-amber-600 text-sm">
                            {validationError}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="mt-4 px-1 py-1 ml-4 mb-2 w-30 bg-sky-900 text-base border rounded-sm text-white hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                        disabled={isLoading || isLoadingOptions}
                    >
                        {isLoading ? 'Söker...' : 'Sök'}
                    </button>
                </form>
            )}

            {/* Image Search Form */}
            {activeTab === "image" && (
                <form
                    onSubmit={handleImageSubmit}
                    className="my-6 p-6 bg-gray-50 rounded-lg shadow-sm"
                >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="flex flex-col relative">
                            <label htmlFor="image-brand_id" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Märke</label>
                            <div className="relative">
                                <select
                                    id="image-brand_id"
                                    name="brand_id"
                                    value={imageFormData.brand_id}
                                    onChange={handleImageFormChange}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none"
                                    disabled={isLoadingOptions}
                                >
                                    <option value="">Välj märke</option>
                                    {brands.map(brand => (
                                        <option key={brand.id} value={brand.id}>
                                            {brand.name}
                                        </option>
                                    ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <div className="flex flex-col relative">
                            <label htmlFor="image-device_type_id" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Enhetstyp</label>
                            <div className="relative">
                                <select
                                    id="image-device_type_id"
                                    name="device_type_id"
                                    value={imageFormData.device_type_id}
                                    onChange={handleImageFormChange}
                                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white appearance-none"
                                    disabled={isLoadingOptions}
                                >
                                    <option value="">Välj enhetstyp</option>
                                    {deviceTypes.map(deviceType => (
                                        <option key={deviceType.id} value={deviceType.id}>
                                            {deviceType.type}
                                        </option>
                                    ))}
                                </select>
                                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Image Upload Area */}
                    <div
                        className={`mt-4 p-6 border-2 border-dashed rounded-lg ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300'} ${imageFormData.image ? 'bg-gray-100' : ''}`}
                        onDragEnter={handleDrag}
                        onDragOver={handleDrag}
                        onDragLeave={handleDrag}
                        onDrop={handleDrop}
                    >
                        {imageFormData.image ? (
                            <div className="flex flex-col items-center">
                                <img
                                    src={URL.createObjectURL(imageFormData.image)}
                                    alt="Förhandsgranskning"
                                    className="max-h-48 max-w-full mb-2 rounded"
                                />
                                <p className="text-sm text-gray-600">
                                    {imageFormData.image.name} ({Math.round(imageFormData.image.size / 1024)} KB)
                                </p>
                                <button
                                    type="button"
                                    onClick={() => setImageFormData(prev => ({ ...prev, image: null }))}
                                    className="mt-2 text-sm text-amber-600 hover:text-amber-800"
                                >
                                    Ta bort bild
                                </button>
                            </div>
                        ) : (
                            <div className="text-center">
                                <svg className="mx-auto h-12 w-12 text-amber-500" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                                    <path
                                        d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4h-12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                                        strokeWidth="2"
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                    />
                                </svg>
                                <div className="flex flex-col items-center mt-4">
                                    <label htmlFor="image-upload" className="cursor-pointer bg-gray-100 px-4 py-2 text-sm font-['Neucha'] font-medium text-amber-500 border-2 border-amber-500 rounded-md hover:bg-blue-50">
                                        Välj en bild
                                        <input
                                            id="image-upload"
                                            name="image"
                                            type="file"
                                            className="hidden"
                                            accept="image/*"
                                            onChange={handleImageChange}
                                        />
                                    </label>
                                    <p className="mt-2 text-sm font-['Barlow_Condensed'] text-gray-500">eller dra och släpp en bild här</p>
                                </div>
                                <p className="text-xs font-['Barlow_Condensed'] text-gray-500 mt-2">
                                    Endast bildfiler (PNG, JPG, JPEG, GIF)
                                </p>
                            </div>
                        )}
                    </div>

                    {validationError && (
                        <div className="mt-2 text-amber-600 text-sm">
                            {validationError}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="mt-4 px-1 py-1 ml-4 mb-2 w-30 bg-sky-900 text-base border rounded-sm text-white hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                        disabled={isLoading || isLoadingOptions}
                    >
                        {isLoading ? 'Söker...' : 'Sök med bild'}
                    </button>
                </form>
            )}

            {/* Results Section */}
            <div className="my-6">
                {error && (
                    <div className="p-4 bg-amber-50 text-amber-700 rounded-md mb-4">
                        {error}
                    </div>
                )}

                {searchResults.length > 0 && (
                    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                        <h2 className="font-['Neucha'] text-2xl p-4 bg-gray-50 border-b">Sökresultat</h2>
                        <div className="overflow-x-auto">
                            <table className="min-w-full bg-white">
                                <thead>
                                    <tr className="bg-gray-50 border-b">
                                        <th className="py-3 px-4 text-left text-sm font-medium text-gray-700">Modellnamn</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium text-gray-700">Märke/Modellnummer</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium text-gray-700">Enhetstyp</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium text-gray-700">Match</th>
                                        <th className="py-3 px-4 text-left text-sm font-medium text-gray-700">Hantera</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200">
                                    {searchResults.map((manual, index) => (
                                        <tr key={index} className="hover:bg-gray-50 transition-colors duration-150">
                                            <td className="py-3 px-4 text-base text-gray-700 font-medium font-['Barlow_Condensed']">
                                                {manual && manual.modelname ? manual.modelname : 'Manual'}
                                            </td>
                                            <td className="py-3 px-4 text-base text-gray-700 font-['Barlow_Condensed']">
                                                {manual && manual.brand ? manual.brand : ''} {manual && manual.model_numbers ? manual.model_numbers : (manual && manual.modelnumber ? manual.modelnumber : '')}
                                            </td>
                                            <td className="py-3 px-4 text-base text-gray-700 font-['Barlow_Condensed']">
                                                {manual && manual.device_type ? manual.device_type : '-'}
                                            </td>
                                            <td className="py-3 px-4 text-base text-gray-700 italic font-['Barlow_Condensed']">
                                                {manual && manual.match ? manual.match : '-'}
                                            </td>
                                            <td className="py-3 px-4 text-left">
                                                <div className="flex justify-left items-center gap-6">
                                                    <button
                                                        className="bg-amber-600 hover:bg-amber-700 h-8 transition-colors font-medium text-white py-1 px-3 rounded text-sm font-['Neucha']"
                                                        onClick={() => openSaveModal(manual)}
                                                    >
                                                        Spara i min lista
                                                    </button>
                                                    <button
                                                        onClick={() => handleDownload(manual.file_id)}
                                                        className="text-sky-800 hover:text-amber-900 inline-flex items-center justify-center h-8 relative group"
                                                        title="Ladda ner"
                                                    >
                                                        <Download size={18} />
                                                        <span className="absolute top-full right-0 whitespace-nowrap bg-sky-800 text-white font-['Barlow_Condensed'] text-xs rounded px-2 py-1 opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200">
                                                            Ladda ner manual
                                                        </span>
                                                    </button>

                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {searchResults.length === 0 && !isLoading && !error && (
                    <p className="text-gray-500 italic font-['Barlow_Condensed']">
                        Inga resultat att visa. Försök med en annan sökning.
                    </p>
                )}
            </div>

            {/* Save to My List Modal */}
            {showSaveModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full">
                        <h3 className="text-xl font-['Neucha'] mb-4">Spara i min lista</h3>

                        <div className="mb-4">
                            <p className="text-sm text-gray-600 mb-2">
                                Du sparar nu:
                            </p>
                            <p className="font-medium">
                                {selectedManual?.modelname || 'Enhet'}
                                {selectedManual?.brand ? ` (${selectedManual.brand})` : ''}
                            </p>
                        </div>

                        <div className="mb-4">
                            <label htmlFor="custom-name" className="block mb-1 text-gray-700 font-['Barlow_Condensed']">
                                Ge enheten ett eget namn (t.ex. "TV i vardagsrummet")
                            </label>
                            <input
                                type="text"
                                id="custom-name"
                                value={customName}
                                onChange={(e) => setCustomName(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="Ange namn på din enhet"
                            />
                        </div>

                        {saveError && (
                            <div className="p-3 bg-amber-50 text-amber-700 rounded-md mb-4 text-sm">
                                {saveError}
                            </div>
                        )}

                        {saveSuccess && (
                            <div className="p-3 bg-green-50 text-green-700 rounded-md mb-4 text-sm">
                                {saveSuccess}
                            </div>
                        )}

                        <div className="flex justify-end gap-3">
                            <button
                                type="button"
                                onClick={closeSaveModal}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors duration-300"
                                disabled={isSaving}
                            >
                                Avbryt
                            </button>
                            <button
                                type="button"
                                onClick={handleSaveToList}
                                className="px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors duration-300 font-['Neucha']"
                                disabled={isSaving}
                            >
                                {isSaving ? 'Sparar...' : 'Spara'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Olika gör oss vidsträckt rot som på det blivit, ingalunda miljoner trevnadens se ingalunda träutensilierna bäckasiner kanske lax, söka från bra sax ordningens faktor verkligen. Kanske groda om regn rännil vidsträckt färdväg dag ta denna flera själv, kan så där inom samtidigt erfarenheter räv där precis bland, dag miljoner från bland och kunde ingalunda bland groda äng. Hela stora dock om kanske och stig varit sista, träutensilierna annat hans verkligen år åker dimma, smultron flera hwila träutensilierna kanske både som.
            </p>
        </div>
    );
}