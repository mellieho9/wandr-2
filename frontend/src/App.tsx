import { useState, useEffect } from "react";
import { LandingPage } from "./components/LandingPage";
import { DatabaseSelection } from "./components/DatabaseSelection";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    // Check if user just completed OAuth (success=true in URL)
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get("success");
    const userId = urlParams.get("user_id");

    if (success === "true" && userId) {
      // OAuth successful, clean up URL
      window.history.replaceState({}, document.title, "/");
      setIsAuthenticated(true);
      setIsCheckingAuth(false);
    } else {
      // Check if user is already authenticated (has session)
      checkAuthStatus();
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Try to fetch databases to check if user is authenticated
      const apiUrl = import.meta.env.DEV
        ? "http://localhost:8080/api/databases"
        : "/api/databases";
      const response = await fetch(apiUrl, {
        credentials: "include",
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error("Error checking auth status:", error);
      setIsAuthenticated(false);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-[#F7F6F3] flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F7F6F3]">
      {!isAuthenticated ? (
        <LandingPage onAuthenticate={() => setIsAuthenticated(true)} />
      ) : (
        <DatabaseSelection />
      )}
    </div>
  );
}
