import React, { useState } from "react";

export default function Search() {
    const [formData, setFormData] = useState({
        brand: "",
        device_type: "",
        modelnumber: "",
        modelname: ""
    });
    const [searchResults, setSearchResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

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

                    // More detailed logging to debug the structure
                    if (data && data.manuals) {
                        console.log("manuals property exists:", typeof data.manuals);
                        console.log("is it an array?", Array.isArray(data.manuals));
                        console.log("length:", Array.isArray(data.manuals) ? data.manuals.length : "not an array");
                        console.log("content:", JSON.stringify(data.manuals, null, 2));
                    }

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

    return (
        <div className="flex flex-col p-4 max-w-4xl mx-10">
            <h1 className="font-['Neucha'] text-5xl mb-6">Hitta din apparat eller hemelektronik</h1>
            <p className="text-gray-700 font-['Barlow_Condensed'] leading-relaxed">
                Sök efter din hushållsapparat eller hemelektronik. Spara till listan på din sida - så blir det enklare nästa gång du ska göra en sökning.
                Klicka vidare till Gizmo vår AI - agent om du vill ha hjälp att lösa ett problem.
            </p>

            {/* Search Form */}
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
                            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="T.ex. Galaxy S21 Ultra"
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors duration-300 font-['Barlow_Condensed']"
                    disabled={isLoading}
                >
                    {isLoading ? 'Söker...' : 'Sök'}
                </button>
            </form>

            {/* Results Section */}
            <div className="my-6">
                {error && (
                    <div className="p-4 bg-red-50 text-red-700 rounded-md mb-4">
                        {error}
                    </div>
                )}

                {searchResults.length > 0 && (
                    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                        <h2 className="font-['Neucha'] text-2xl p-4 bg-gray-50 border-b">Sökresultat</h2>
                        {/* Debug output for troubleshooting */}
                        <div className="p-2 bg-gray-100 text-xs">
                            <p>Debug: {JSON.stringify(searchResults)}</p>
                        </div>
                        <ul className="divide-y divide-gray-200">
                            {searchResults.map((manual, index) => {
                                console.log(`Rendering result #${index}:`, manual);
                                return (
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
                                                    className="text-blue-600 hover:text-blue-800 font-medium"
                                                    onClick={() => console.log(`Viewing manual ID: ${manual && manual.file_id ? manual.file_id : 'unknown'}`)}
                                                >
                                                    Visa manual
                                                </button>
                                            </div>
                                        </div>
                                    </li>
                                )
                            })}
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