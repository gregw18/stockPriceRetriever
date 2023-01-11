import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
console.log(new Date().toTimeString(), ", starting index.js");

const container = document.getElementById("root");
console.log(new Date().toTimeString(), "index.js, after getElementById");
const root = createRoot(container);
console.log(new Date().toTimeString(), "index.js, after createRoot");
root.render(<StrictMode><App /></StrictMode>);
console.log(new Date().toTimeString(), "index.js, after root.render");
