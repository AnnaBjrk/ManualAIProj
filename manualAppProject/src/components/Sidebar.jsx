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
      className={`fixed inset-y-0 right-0 w-96 h-full bg-amber-50 shadow-lg transform transition-transform duration-300 ease-in-out overflow-y-auto ${isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
    >
      <div className="p-4 overflow-y-auto max-h-full">
        <div className="flex justify-end sticky top-0 bg-amber-50 z-10 py-2">
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="mt-8 overflow-y-auto">
          {user ? (
            <div className="flex flex-col items-center space-y-6">
              <div className="text-center">
                <h2 className="text-xl font-['Barlow_Condensed'] font-semibold text-gray-800">
                  Välkommen, {user.firstName}!
                </h2>
                <p className="mt-2 text-gray-600 font-['Barlow_Condensed']">
                  Du är nu inloggad. Sök och ställ frågor om dina tekniska prylar.
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="px-6 py-2 font-['Neucha'] bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors"
              >
                Logga ut
              </button>
            </div>
          ) : (
            <>
              <div className="flex justify-center space-x-4 mb-6">
                <button
                  onClick={() => setShowLogin(false)}
                  className={`px-4 py-2 font-['Neucha'] rounded-md transition-colors ${!showLogin
                      ? 'bg-amber-600 text-white'
                      : 'bg-transparent text-amber-700 hover:bg-amber-700 hover:text-white'
                    }`}
                >
                  Bli medlem
                </button>
                <button
                  onClick={() => setShowLogin(true)}
                  className={`px-4 py-2 font-['Neucha'] rounded-md transition-colors ${showLogin
                      ? 'bg-amber-600 text-white'
                      : 'bg-transparent text-amber-700 hover:bg-amber-700 hover:text-white'
                    }`}
                >
                  Logga in
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