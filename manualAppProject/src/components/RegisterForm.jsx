import { useState } from "react";

export default function RegisterForm({ onLoginSuccess }) {
    const apiUrl = import.meta.env.VITE_API_URL;

    const [firstName, setfirstName] = useState("");
    const [firstNameError, setFirstNameError] = useState([]);

    const [lastName, setlastName] = useState("");
    const [lastNameError, setLastNameError] = useState([]);

    const [email, setEmail] = useState("");
    const [emailError, setEmailError] = useState([]);

    const [password, setPassword] = useState("");
    const [passwordError, setPasswordError] = useState([]);

    const [terms, setTerms] = useState(false);
    const [termsError, setTermsError] = useState("");

    const [serverError, setServerError] = useState("");

    function validatefirstName() {
        if (!firstName.trim()) {
            setFirstNameError(["Skriv förnamn"]);
            return false;
        } else {
            setFirstNameError([]);
            return true;
        }
    }

    function validatelastName() {
        if (!lastName.trim()) {
            setLastNameError(["Skriv efternamn"]);
            return false;
        } else {
            setLastNameError([]);
            return true;
        }
    }

    function validateEmail() {
        let emailErrors = [];
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!Boolean(regex.test(email))) {
            emailErrors.push("Inte en epostadress");
        }
        if (!email) {
            emailErrors.push("Du behöver skriva e-postadress");
        }
        setEmailError(emailErrors);
        return emailErrors.length === 0;
    }

    function validatePassword() {
        let passwordErrors = [];
        if (password.length < 8) {  // Changed from <= to < for proper minimum length check
            passwordErrors.push("Lösenordet måste ha minst 8 tecken");
        }
        if (!password) {
            passwordErrors.push("Skriv ett lösenord");
        }
        setPasswordError(passwordErrors);
        return passwordErrors.length === 0;
    }

    function validateTerms() {
        if (!terms) {
            setTermsError("Du behöver acceptera villkoren");
            return false;
        } else {
            setTermsError("");
            return true;
        }
    }

    async function submitRegister(e) {
        e.preventDefault();

        // Validate all fields
        const isFirstNameValid = validatefirstName();
        const isLastNameValid = validatelastName();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isTermsValid = validateTerms();

        // Check if all validations pass
        if (isFirstNameValid && isLastNameValid && isEmailValid && isPasswordValid && isTermsValid) {
            try {
                console.log("Sending data:", {
                    first_name: firstName,
                    last_name: lastName,
                    email,
                    password,
                    terms_of_agreement: terms
                });

                // Register the user
                const registerResponse = await fetch(`${apiUrl}/v1/auth/register`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        first_name: firstName,
                        last_name: lastName,
                        email,
                        password,
                        terms_of_agreement: terms,
                    }),
                    mode: 'cors',
                    credentials: 'include'
                });

                const registerData = await registerResponse.json();

                if (!registerResponse.ok) {
                    console.log("Validation error:", registerData);

                    // Check for the specific email already registered error
                    if (registerData.detail && registerData.detail === "Email already registered.") {
                        setEmailError(["E-postadressen används redan"]);
                        document.getElementById("email").focus();
                        return;
                    } else {
                        throw new Error(JSON.stringify(registerData));
                    }
                }

                console.log("Registration successful:", registerData);
                setServerError("");

                // After successful registration, log the user in
                const formData = new URLSearchParams();
                formData.append('username', email);  // Note: 'username' not 'email'
                formData.append('password', password);

                const loginResponse = await fetch(`${apiUrl}/v1/auth/token_login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: formData,
                    mode: 'cors',
                    credentials: 'include'
                });

                // Process the login response
                if (!loginResponse.ok) {
                    const loginError = await loginResponse.json();
                    throw new Error(JSON.stringify(loginError));
                }

                // Parse the login response data
                const loginData = await loginResponse.json();
                console.log("Login successful:", loginData);

                // Save the token to localStorage
                localStorage.setItem("access_token", loginData.access_token);

                // Call onLoginSuccess with user data from the login response
                onLoginSuccess({
                    firstName: loginData.first_name,
                    lastName: loginData.last_name,
                    isAdmin: loginData.is_admin,
                    isPartner: loginData.is_partner,
                    userId: "authenticated"
                });

            } catch (error) {
                console.error("Full error:", error);
                setServerError(error.message);
            }
        } else {
            console.log("Form validation failed");
            console.log("First name errors:", firstNameError);
            console.log("Last name errors:", lastNameError);
            console.log("Password errors:", passwordError);
            console.log("Email errors:", emailError);
            console.log("Terms error:", termsError);
        }
    }

    return (
        <>
            <div className="flex flex-col justify-center flex-1 min-h-full px-6 py-6 lg:px-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                    <h1 className="mt-3 text-3xl font-['Neucha'] tracking-tight text-center text-gray-900">
                        Skapa ett konto
                    </h1>
                </div>

                <div className="mt-5 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form onSubmit={submitRegister} className="space-y-6" noValidate>
                        <div>
                            <label
                                htmlFor="firstName"
                                className="block text-sm font-['Barlow_Condensed'] font-medium leading-6 text-gray-900"
                            >
                                Förnamn
                            </label>
                            <div className="mt-2">
                                <input
                                    id="firstName"
                                    name="firstName"
                                    type="text"
                                    autoComplete="given-name"
                                    className="block w-full rounded-md border-0 px-2 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-['Barlow_Condensed']"
                                    value={firstName}
                                    onChange={(e) => setfirstName(e.target.value)}
                                    onBlur={validatefirstName}
                                />
                                {firstNameError.map((error) => (
                                    <p key={error} className="text-amber-700 text-sm">
                                        {error}
                                    </p>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label
                                htmlFor="lastName"
                                className="block text-sm font-['Barlow_Condensed'] font-medium leading-6 text-gray-900"
                            >
                                Efternamn
                            </label>
                            <div className="mt-2">
                                <input
                                    id="lastName"
                                    name="lastName"
                                    type="text"
                                    autoComplete="family-name"
                                    className="block w-full rounded-md border-0 px-2 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-['Barlow_Condensed']"
                                    value={lastName}
                                    onChange={(e) => setlastName(e.target.value)}
                                    onBlur={validatelastName}
                                />
                                {lastNameError.map((error) => (
                                    <p key={error} className="text-amber-700 text-sm">
                                        {error}
                                    </p>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-['Barlow_Condensed'] font-medium leading-6 text-gray-900"
                            >
                                Mejl
                            </label>
                            <div className="mt-2">
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    className="block w-full rounded-md border-0 px-2 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-['Barlow_Condensed']"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onBlur={validateEmail}
                                />
                                {emailError.map((error) => (
                                    <p key={error} className="text-amber-700 text-sm">
                                        {error}
                                    </p>
                                ))}
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between">
                                <label
                                    htmlFor="password"
                                    className="block text-sm font-['Barlow_Condensed'] font-medium leading-6 text-gray-900"
                                >
                                    Lösenord
                                </label>
                            </div>
                            <div className="mt-2">
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    className="block w-full rounded-md border-0 py-1.5 px-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    onBlur={validatePassword}
                                />
                                {passwordError.map((error) => (
                                    <p key={error} className="text-amber-700 text-sm">
                                        {error}
                                    </p>
                                ))}
                            </div>
                        </div>

                        <div className="flex items-center">
                            <div className="items-center justify-between mr-4">
                                <label
                                    htmlFor="terms"
                                    className="block text-sm font-['Barlow_Condensed'] font-medium leading-6 text-gray-900"
                                >
                                    Användarvillkor
                                </label>
                            </div>
                            <div>
                                <input
                                    id="terms"
                                    name="terms"
                                    type="checkbox"
                                    checked={terms}
                                    onChange={(e) => setTerms(e.target.checked)}
                                />
                            </div>
                        </div>
                        {termsError && <p className="text-amber-700 text-sm">{termsError}</p>}

                        <div>
                            <button
                                type="submit"
                                className="flex w-full justify-center font-['Neucha'] rounded-md bg-amber-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-amber-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-amber-900"
                            >
                                Skicka
                            </button>
                        </div>
                        {serverError && (
                            <p className="mt-4 text-center text-amber-700 text-sm">{serverError}</p>
                        )}
                    </form>
                </div>
            </div>
        </>
    );
}