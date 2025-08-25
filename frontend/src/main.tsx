/**
 * Main entry point for the React application.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { registerSW } from './utils/pwa';
import { logConfig } from './utils/config';

const rootElement = document.getElementById('root');

if (!rootElement) {
  throw new Error('Failed to find the root element');
}

const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Log configuration in development
logConfig();

// Register service worker for PWA functionality
registerSW();