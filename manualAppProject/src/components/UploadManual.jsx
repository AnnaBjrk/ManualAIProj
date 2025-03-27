import React, { useState, useEffect } from "react";

export default function UploadManual() {
    // Upload form state
    const [formData, setFormData] = useState({
        brand_id: "",
        device_type_id: "",
        modelnumber: "",
        modelname: "",
        file: null
    });

    // Dropdown options state
    const [brands, setBrands] = useState([]);
    const [deviceTypes, setDeviceTypes] = useState([]);
    const [isLoadingOptions, setIsLoadingOptions] = useState(false);
    const [optionsError, setOptionsError] = useState(null);

    // UI state
    const [isUploading, setIsUploading] = useState(false);
    const [error, setError] = useState(null);
    const [validationError, setValidationError] = useState(null);
    const [uploadSuccess, setUploadSuccess] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    // State for adding to personal list
    const [uploadedFileId, setUploadedFileId] = useState(null);
    const [deviceName, setDeviceName] = useState("");
    const [showAddToListForm, setShowAddToListForm] = useState(false);
    const [isAddingToList, setIsAddingToList] = useState(false);
    const [addToListSuccess, setAddToListSuccess] = useState(null);

    // Fetch brands and device types on component mount
    useEffect(() => {
        const fetchOptions = async () => {
            setIsLoadingOptions(true);
            setOptionsError(null);

            try {
                const baseUrl = import.meta.env.VITE_API_URL;

                // Get token from localStorage with correct key
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
                }

                if (deviceTypesArray.length > 0) {
                    setFormData(prev => ({ ...prev, device_type_id: deviceTypesArray[0].id }));
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
        };

        // Call the fetch function
        fetchOptions();
    }, []);

    // Form handlers
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));

        // Clear validation error when user starts typing
        if (validationError) {
            setValidationError(null);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFormData(prevState => ({
                ...prevState,
                file: e.target.files[0]
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
            // Check if file type is allowed
            const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

            if (allowedTypes.includes(file.type)) {
                setFormData(prevState => ({
                    ...prevState,
                    file: file
                }));
            } else {
                setError("Endast PDF och Word-dokument kan laddas upp");
            }
        }
    };

    const handleAddToList = async () => {
        if (!deviceName.trim()) {
            setValidationError("Du måste ange ett namn för enheten");
            return;
        }

        setIsAddingToList(true);
        setError(null);
        setValidationError(null);

        try {
            const accessToken = localStorage.getItem('access_token');
            const tokenType = localStorage.getItem('token_type') || 'bearer';

            if (!accessToken) {
                throw new Error("No authentication token found");
            }

            const authHeader = `${tokenType} ${accessToken}`;
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/uploads/add_manual_to_user_list`;

            console.log("Making add to list request to:", apiUrl);
            console.log("Request payload:", {
                file_id: uploadedFileId,
                users_own_naming: deviceName
            });

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: uploadedFileId,
                    users_own_naming: deviceName
                }),
                credentials: 'include'
            });

            console.log("Response status:", response.status);

            if (!response.ok) {
                let errorMessage = 'Failed to add manual to your list';
                const responseText = await response.text();
                console.error("Error response body:", responseText);

                try {
                    if (responseText) {
                        const errorData = JSON.parse(responseText);
                        errorMessage = errorData.detail || errorMessage;
                    }
                } catch (jsonError) {
                    console.error("Failed to parse error response:", jsonError);
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Added manual to list:", data);

            // Reset form
            setDeviceName("");
            setShowAddToListForm(false);
            setAddToListSuccess("Manual har lagts till i din lista");

            // Could trigger a refresh of the UserManualsTable component here
            // if it's on the same page, perhaps via context or a passed callback

        } catch (err) {
            console.error('Error adding to list:', err);
            setError(err.message);
        } finally {
            setIsAddingToList(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Validate form fields
        if (!formData.brand_id.trim()) {
            setValidationError("Märke måste anges");
            return;
        }

        if (!formData.device_type_id.trim()) {
            setValidationError("Enhetstyp måste anges");
            return;
        }

        // Either modelnumber or modelname must be provided
        if (!formData.modelnumber.trim() && !formData.modelname.trim()) {
            setValidationError("Antingen Modellnummer eller Modellnamn måste anges");
            return;
        }

        if (!formData.file) {
            setValidationError("En manuell fil måste laddas upp");
            return;
        }

        setIsUploading(true);
        setError(null);
        setValidationError(null);
        setUploadSuccess(null);

        try {
            const apiUrl = `${import.meta.env.VITE_API_URL}/v1/uploads/upload-manual`;
            console.log("Making upload request to:", apiUrl);

            // Create FormData object
            const uploadFormData = new FormData();

            // Make sure the file is the first field (some implementations are sensitive to order)
            uploadFormData.append('file', formData.file);

            // Convert UUID strings to ensure they're properly formatted
            uploadFormData.append('brand_id', formData.brand_id.toString());
            uploadFormData.append('device_type_id', formData.device_type_id.toString());
            uploadFormData.append('modelnumber', formData.modelnumber.trim());
            uploadFormData.append('modelname', formData.modelname.trim());

            // Get token from localStorage with the correct key
            const token = localStorage.getItem('access_token');

            const headers = {};
            if (token && token !== 'null') {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(apiUrl, {
                method: 'POST',
                body: uploadFormData,
                headers: headers,
                credentials: 'include',
            });

            if (!response.ok) {
                let errorMessage = 'Ett fel uppstod vid uppladdningen';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (jsonError) {
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log("Upload response:", data);

            // Reset form after successful upload
            setFormData({
                brand_id: brands.length > 0 ? brands[0].id : "",
                device_type_id: deviceTypes.length > 0 ? deviceTypes[0].id : "",
                modelnumber: "",
                modelname: "",
                file: null
            });

            // Show success message and save fileId for adding to list
            setUploadSuccess("Manual har laddats upp framgångsrikt");

            // Store the uploaded file ID to use for adding to personal list
            console.log("Upload successful, file ID:", data.fileId);
            setUploadedFileId(data.fileId);
        } catch (err) {
            console.error('Upload error:', err);
            setError(err.message);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="mt-8 mb-10">
            <h1 className="font-['Neucha'] text-2xl mb-6">Ladda upp manual</h1>
            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Ladda upp en manual för en enhet. Fyll i alla fält nedan och välj en fil i PDF- eller Word-format.
                Ladda bara upp manualer som du har rätt att dela.
            </p>

            {/* Error message for dropdown options */}
            {optionsError && (
                <div className="p-4 bg-amber-50 text-amber-700 rounded-md my-4">
                    <p>Kunde inte hämta alla alternativ: {optionsError}</p>
                    <p className="text-sm">Använder fördefinierade alternativ istället.</p>
                </div>
            )}

            {/* Upload Form */}
            <form
                onSubmit={handleSubmit}
                className="my-6 p-6 bg-gray-50 rounded-lg shadow-sm"
            >
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

                {/* File Upload Area */}
                <div
                    className={`mt-6 p-6 border-2 border-dashed rounded-lg ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300'
                        } ${formData.file ? 'bg-gray-100' : ''}`}
                    onDragEnter={handleDrag}
                    onDragOver={handleDrag}
                    onDragLeave={handleDrag}
                    onDrop={handleDrop}
                >
                    {formData.file ? (
                        <div className="flex flex-col items-center">
                            <div className="flex items-center justify-center w-16 h-16 bg-gray-200 rounded mb-2">
                                <svg className="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                            <p className="text-sm text-gray-600 font-medium">
                                {formData.file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                                ({Math.round(formData.file.size / 1024)} KB)
                            </p>
                            <button
                                type="button"
                                onClick={() => setFormData(prev => ({ ...prev, file: null }))}
                                className="mt-2 text-sm text-amber-600 hover:text-amber-800"
                            >
                                Ta bort fil
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
                                <label htmlFor="file-upload" className="cursor-pointer bg-gray-100 px-4 py-2 text-sm font-['Neucha'] font-medium text-amber-500 border-2 border-amber-500 rounded-md hover:bg-blue-50">
                                    Välj en fil
                                    <input
                                        id="file-upload"
                                        name="file"
                                        type="file"
                                        className="hidden"
                                        accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                        onChange={handleFileChange}
                                    />
                                </label>
                                <p className="mt-2 text-sm font-['Barlow_Condensed'] text-gray-500">eller dra och släpp en fil här</p>
                            </div>
                            <p className="text-xs font-['Barlow_Condensed'] text-gray-500 mt-2">
                                Endast PDF och Word-dokument (.pdf, .doc, .docx)
                            </p>
                        </div>
                    )}
                </div>

                {validationError && (
                    <div className="mt-2 text-amber-600 text-sm">
                        {validationError}
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-3 bg-amber-50 text-amber-700 rounded-md">
                        {error}
                    </div>
                )}

                {uploadSuccess && (
                    <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-md">
                        {uploadSuccess}
                    </div>
                )}

                {addToListSuccess && (
                    <div className="mt-4 p-3 bg-green-50 text-green-700 rounded-md">
                        {addToListSuccess}
                    </div>
                )}

                {/* Add to list form */}
                {uploadedFileId && showAddToListForm && (
                    <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-md">
                        <h3 className="text-lg font-['Neucha'] mb-2">Lägg till i din lista</h3>
                        <p className="text-sm text-gray-600 mb-3 font-['Barlow_Condensed']">
                            Ge denna enhet ett namn som du enkelt känner igen (t.ex. "TV i vardagsrummet")
                        </p>

                        <div className="flex flex-col">
                            <label htmlFor="deviceName" className="mb-1 text-gray-700 font-['Barlow_Condensed']">
                                Enhetsnamn
                            </label>
                            <input
                                type="text"
                                id="deviceName"
                                value={deviceName}
                                onChange={(e) => setDeviceName(e.target.value)}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. TV i vardagsrummet"
                            />
                        </div>

                        <div className="mt-3 flex space-x-3">
                            <button
                                type="button"
                                onClick={handleAddToList}
                                className="px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors duration-300 font-['Neucha']"
                                disabled={isAddingToList}
                            >
                                {isAddingToList ? 'Lägger till...' : 'Lägg till i min lista'}
                            </button>

                            <button
                                type="button"
                                onClick={() => setShowAddToListForm(false)}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors duration-300 font-['Neucha']"
                                disabled={isAddingToList}
                            >
                                Avbryt
                            </button>
                        </div>
                    </div>
                )}

                {/* Show "Add to list" button after successful upload */}
                {uploadedFileId && !showAddToListForm && !addToListSuccess && (
                    <div className="mt-4">
                        <button
                            type="button"
                            onClick={() => setShowAddToListForm(true)}
                            className="px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors duration-300 font-['Neucha']"
                        >
                            Lägg till i min lista
                        </button>
                    </div>
                )}

                <button
                    type="submit"
                    className="mt-4 px-1 py-1 ml-4 mb-2 w-30 bg-sky-900 text-base border rounded-sm text-white hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                    disabled={isUploading || isLoadingOptions || showAddToListForm}
                >
                    {isUploading ? 'Laddar upp...' : 'Ladda upp manual'}
                </button>
            </form>

            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Genom att ladda upp en manual bekräftar du att du har rätt att dela detta dokument. Alla manualer granskas innan de publiceras på plattformen.
            </p>
        </div>
    );
}