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
        if (password.length < 8) {
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
                // Get form values
                const formValues = {
                    username: email, // API expects 'username', but we're using 'email' in the UI
                    password: password
                };

                // Create URLSearchParams for x-www-form-urlencoded format
                // This is what OAuth2PasswordRequestForm in FastAPI expects
                const formData = new URLSearchParams();
                for (const [key, value] of Object.entries(formValues)) {
                    formData.append(key, value);
                }

                console.log("Sending form data with username:", email);
                //console.log("Sending data:", { email, password });

                const response = await fetch(`${apiUrl}/v1/auth/token_login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    body: formData

                });

                const data = await response.json();
                if (!response.ok) {
                    console.log("Validation error:", data);
                    throw new Error(data.detail || "Login failed");
                }

                // Store token in local storage
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('token_type', data.token_type);



                // Success case - use the data from response
                onLoginSuccess({
                    firstName: data.first_name,
                    lastName: data.last_name,
                    userId: "authenticated",
                    isAdmin: Boolean(data.is_admin),
                    isPartner: Boolean(data.is_partner)
                });

                console.log("Successfull login", data);
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
                        name="email" //kolla denna
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="mt-1 px-2 block w-full rounded-md border-gray-300 shadow-sm focus:border-amber-500 focus:ring-amber-500 font-['Barlow_Condensed']"
                    />
                    {emailError.map((error, index) => (
                        <p key={index} className="text-amber-700 text-sm mt-1">{error}</p>
                    ))}
                </div>
                <div>
                    <label htmlFor="password" className="block font-['Barlow_Condensed'] text-sm font-medium text-amber-950">
                        Password
                    </label>
                    <input
                        type="password"
                        id="password"
                        name="password" //kolla denna
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="mt-1 px-2 block w-full rounded-md border-gray-300 shadow-sm focus:border-amber-500 focus:ring-amber-500 font-['Barlow_Condensed']"
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
                    className="w-full bg-amber-600 font-['Neucha'] text-white py-2 px-4 rounded-md hover:bg-amber-700 transition-colors"
                >
                    Skicka
                </button>
            </form>
        </div>
    );
};

export default LoginForm;