import React, { useState } from "react";

export default function Search() {
    const [activeTab, setActiveTab] = useState("image");

    // Text search state
    const [formData, setFormData] = useState({
        brand: "",
        device_type: "",
        modelnumber: "",
        modelname: ""
    });

    // Image search state
    const [imageFormData, setImageFormData] = useState({
        brand: "",
        device_type: "",
        image: null
    });

    // Shared state
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validationError, setValidationError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

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
        if (!imageFormData.brand.trim()) {
            setValidationError("Märke måste anges");
            return;
        }

        if (!imageFormData.device_type.trim()) {
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
            formData.append('brand', imageFormData.brand);
            formData.append('device_type', imageFormData.device_type);

            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
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

    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Hitta din apparat eller hemelektronik</h1>
            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Sök efter din hushållsapparat eller hemelektronik. Spara till listan på din sida - så blir det enklare nästa gång du ska göra en sökning.
                Klicka vidare till Gizmo vår AI - agent om du vill ha hjälp att lösa ett problem.
            </p>

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
                        <div className="flex flex-col">
                            <label htmlFor="brand" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Märke</label>
                            <input
                                type="text"
                                id="brand"
                                name="brand"
                                value={formData.brand}
                                onChange={handleChange}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. Samsung, Electrolux"
                            />
                        </div>

                        <div className="flex flex-col">
                            <label htmlFor="device_type" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Enhetstyp</label>
                            <input
                                type="text"
                                id="device_type"
                                name="device_type"
                                value={formData.device_type}
                                onChange={handleChange}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. Diskmaskin, Mobiltelefon"
                            />
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
                        className="mt-4 px-4 py-2 bg-sky-700 text-white rounded-md hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                        disabled={isLoading}
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
                        <div className="flex flex-col">
                            <label htmlFor="image-brand" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Märke</label>
                            <input
                                type="text"
                                id="image-brand"
                                name="brand"
                                value={imageFormData.brand}
                                onChange={handleImageFormChange}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. Samsung, Electrolux"
                            />
                        </div>

                        <div className="flex flex-col">
                            <label htmlFor="image-device_type" className="mb-1 text-gray-700 font-['Barlow_Condensed']">Enhetstyp</label>
                            <input
                                type="text"
                                id="image-device_type"
                                name="device_type"
                                value={imageFormData.device_type}
                                onChange={handleImageFormChange}
                                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                placeholder="T.ex. Diskmaskin, Mobiltelefon"
                            />
                        </div>
                    </div>

                    {/* Image Upload Area */}
                    <div
                        className={`mt-4 p-6 border-2 border-dashed rounded-lg ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300'
                            } ${imageFormData.image ? 'bg-gray-100' : ''}`}
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
                        className="mt-4 px-4 py-2 bg-sky-700 text-white rounded-md hover:bg-sky-800 transition-colors duration-300 font-['Neucha']"
                        disabled={isLoading}
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
                        <ul className="divide-y divide-gray-200">
                            {searchResults.map((manual, index) => (
                                <li key={index} className="p-4 hover:bg-gray-50 transition-colors duration-150">
                                    <div className="flex flex-col md:flex-row md:justify-between">
                                        <div>
                                            <h3 className="font-medium">{manual && manual.modelname ? manual.modelname : 'Manual'}</h3>
                                            <p className="text-gray-600 text-sm">
                                                {manual && manual.brand ? manual.brand : ''} {manual && manual.model_numbers ? manual.model_numbers : (manual && manual.modelnumber ? manual.modelnumber : '')}
                                            </p>
                                            <p className="text-gray-600 text-sm">
                                                {manual && manual.device_type ? manual.device_type : ''}
                                            </p>
                                            {manual && manual.match && (
                                                <p className="text-gray-600 text-sm italic">
                                                    {manual.match}
                                                </p>
                                            )}
                                        </div>
                                        <div className="mt-2 md:mt-0">
                                            <button
                                                className="text-sky-700 hover:text-sky-800 font-medium"
                                                onClick={() => console.log(`Viewing manual ID: ${manual && manual.file_id ? manual.file_id : 'unknown'}`)}
                                            >
                                                Visa manual
                                            </button>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {searchResults.length === 0 && !isLoading && !error && (
                    <p className="text-gray-500 italic font-['Barlow_Condensed']">
                        Inga resultat att visa. Försök med en annan sökning.
                    </p>
                )}
            </div>

            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Olika gör oss vidsträckt rot som på det blivit, ingalunda miljoner trevnadens se ingalunda träutensilierna bäckasiner kanske lax, söka från bra sax ordningens faktor verkligen. Kanske groda om regn rännil vidsträckt färdväg dag ta denna flera själv, kan så där inom samtidigt erfarenheter räv där precis bland, dag miljoner från bland och kunde ingalunda bland groda äng. Hela stora dock om kanske och stig varit sista, träutensilierna annat hans verkligen år åker dimma, smultron flera hwila träutensilierna kanske både som.
            </p>
        </div>
    );
}