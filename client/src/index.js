import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// React 18+ createRoot API
const root = ReactDOM.createRoot(document.getElementById('root'));
// Render the main application component
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
