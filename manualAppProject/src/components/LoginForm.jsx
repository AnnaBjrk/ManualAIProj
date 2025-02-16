import React, { useState } from 'react';

const LoginForm = ({ onLoginSuccess }) => {
    const apiUrl = import.meta.env.VITE_API_URL;

    const [email, setEmail] = useState("");
    const [emailError, setEmailError] = useState([]);
    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState([]);
    const [serverError, setServerError] = useState(""); // Added missing state

    function validateEmail() {
        let emailErrors = [];
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!Boolean(regex.test(email))) {
            emailErrors.push("It must be a correct email");
        }
        if (!email) {
            emailErrors.push("Email is required");
        }
        setEmailError(emailErrors);
        return emailErrors.length === 0;
    }

    function validatePassword() {
        let passwordErrors = [];
        if (password.length <= 8) {
            passwordErrors.push("Password length must be greater than 8");
        }
        if (!password) {
            passwordErrors.push("Password is required");
        }
        setPasswordError(passwordErrors);
        return passwordErrors.length === 0;
    }

    async function submitLogin(e) {  // renamed from submitRegister
        e.preventDefault();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();

        if (isEmailValid && isPasswordValid) {
            try {
                console.log("Sending data:", { email, password });

                const response = await fetch(`${apiUrl}/validate_user`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email,
                        password
                    }),
                });

                const data = await response.json();
                if (!response.ok) {
                    console.log("Validation error:", data);
                    throw new Error(JSON.stringify(data));
                }

                // Success case - use the data from response
                onLoginSuccess({
                    firstName: data.first_name,
                    userId: data.user_id
                });

                console.log("Success", data);
                setServerError("");
            } catch (error) {
                console.log("Full error:", error);
                setServerError(error.message);
            }
        } else {
            console.log(passwordError);
            console.log(emailError);
            console.log("Error in form");
        }
    }

    return (
        <div className="p-4">
            <h2 className="flex justify-center text-3xl font-['Neucha'] font-bold mb-4 text-amber-950">Logga in</h2>
            <form className="space-y-4" onSubmit={submitLogin}>
                <div>
                    <label htmlFor="email" className="block font-['Barlow_Condensed'] text-sm font-medium text-amber-950">
                        Email
                    </label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-amber-500 focus:ring-amber-500"
                    />
                    {emailError.map((error, index) => (
                        <p key={index} className="text-red-700 text-sm mt-1">{error}</p>
                    ))}
                </div>
                <div>
                    <label htmlFor="password" className="block font-['Barlow_Condensed'] text-sm font-medium text-amber-950">
                        Password
                    </label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-amber-500 focus:ring-amber-500"
                    />
                    {passwordError.map((error, index) => (
                        <p key={index} className="text-red-700 text-sm mt-1">{error}</p>
                    ))}
                </div>
                {serverError && (
                    <p className="text-red-700 text-sm">{serverError}</p>
                )}
                <button
                    type="submit"
                    className="w-full bg-amber-700 font-['Neucha'] text-white py-2 px-4 rounded-md hover:bg-amber-600 transition-colors"
                >
                    Skicka
                </button>
            </form>
        </div>
    );
};

export default LoginForm;