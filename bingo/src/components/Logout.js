import React from 'react';
import { useNavigate } from 'react-router-dom';

function Logout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear any stored authentication tokens or user data
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    sessionStorage.clear();
    
    // Redirect to login/home page
    navigate('/');
  };

  return (
    <div className="flex-1 p-6">
      <div className="max-w-md mx-auto mt-20 bg-gray-800 p-8 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Logout</h2>
        <p className="text-gray-300 mb-6 text-center">
          Are you sure you want to logout from your admin account?
        </p>
        <div className="flex space-x-4">
          <button
            onClick={handleLogout}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
          >
            Yes, Logout
          </button>
          <button
            onClick={() => window.history.back()}
            className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-4 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default Logout;
