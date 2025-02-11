import React, { useState } from 'react';
import { X } from 'lucide-react';
import RegisterForm from '../components/RegisterForm';
import LoginForm from '../components/LoginForm';

export default function Sidebar({ isOpen, onClose, onLogin, onLogout, user }) {
  const [showLogin, setShowLogin] = useState(false);

  const handleLoginSuccess = (userData) => {
    onLogin(userData);
    onClose();
  };

  const handleLogout = () => {
    onLogout();
    onClose();
  };

  return (
    <div
      className={`fixed inset-y-0 right-0 w-96 bg-amber-50 shadow-lg transform transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
    >
      <div className="p-4">
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="mt-8">
          {user ? (
            <div className="flex flex-col items-center space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-800">
                  Välkommen, {user.firstName}!
                </h2>
                <p className="mt-2 text-gray-600">
                  Du är nu inloggad. Sök och ställ frågor om dina tekniska prylar.
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="px-6 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition-colors"
              >
                Logga ut
              </button>
            </div>
          ) : (
            <>
              <div className="flex justify-center space-x-4 mb-6">
                <button
                  onClick={() => setShowLogin(false)}
                  className={`px-4 py-2 rounded-md transition-colors ${!showLogin
                    ? 'bg-sky-600 text-white'
                    : 'bg-transparent text-sky-600 hover:bg-sky-50'
                    }`}
                >
                  Register
                </button>
                <button
                  onClick={() => setShowLogin(true)}
                  className={`px-4 py-2 rounded-md transition-colors ${showLogin
                    ? 'bg-sky-600 text-white'
                    : 'bg-transparent text-sky-600 hover:bg-sky-50'
                    }`}
                >
                  Login
                </button>
              </div>

              {showLogin ? (
                <LoginForm onLoginSuccess={handleLoginSuccess} />
              ) : (
                <RegisterForm onLoginSuccess={handleLoginSuccess} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}