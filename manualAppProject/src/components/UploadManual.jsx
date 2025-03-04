import React, { useState } from 'react';
import { Upload } from 'lucide-react';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const [progress, setProgress] = useState(0);

    const handleFileSelect = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile && selectedFile.type === 'application/pdf') {
            setFile(selectedFile);
            setError('');
        } else {
            setError('Please select a PDF file');
            setFile(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        try {
            setUploading(true);
            setProgress(0);

            // First, get the presigned URL from your backend
            const response = await fetch('/api/get-upload-url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: file.name,
                    contentType: file.type,
                }),
            });

            if (!response.ok) throw new Error('Failed to get upload URL');

            const { uploadUrl, fileId } = await response.json();

            // Upload to S3 using the presigned URL
            const uploadResponse = await fetch(uploadUrl, {
                method: 'PUT',
                body: file,
                headers: {
                    'Content-Type': file.type,
                },
            });

            if (!uploadResponse.ok) throw new Error('Upload failed');

            // Notify backend that upload is complete
            await fetch('/api/confirm-upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ fileId }),
            });

            setProgress(100);
            setFile(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow">
            <div className="flex items-center justify-center w-full">
                <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="w-10 h-10 mb-3 text-gray-400" />
                        <p className="mb-2 text-sm text-gray-500">
                            <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-gray-500">PDF files only</p>
                    </div>
                    <input
                        type="file"
                        className="hidden"
                        accept="application/pdf"
                        onChange={handleFileSelect}
                        disabled={uploading}
                    />
                </label>
            </div>

            {file && (
                <div className="mt-4">
                    <p className="text-sm text-gray-600">Selected: {file.name}</p>
                    <button
                        onClick={handleUpload}
                        disabled={uploading}
                        className="mt-2 w-full px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600 disabled:bg-blue-300"
                    >
                        {uploading ? 'Uploading...' : 'Upload PDF'}
                    </button>
                </div>
            )}

            {error && (
                <div className="mt-4 text-sm text-red-500">
                    {error}
                </div>
            )}

            {uploading && (
                <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                        <div
                            className="bg-blue-600 h-2.5 rounded-full"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileUpload;