import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Dashboard from './pages/Dashboard';
import App from './App';
import about from './pages/About';
import About from './pages/About';
export const router = createBrowserRouter([
    {
        path:"/",
        element: <App></App>,
        children:[
            {path:'/Dashboard',element: <Dashboard></Dashboard>},
            {path:'/about',element:<About></About>}
        ]
    },

]);

