import { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { DatabaseSelection } from './components/DatabaseSelection';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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