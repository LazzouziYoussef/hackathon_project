import { createBrowserRouter } from 'react-router-dom'
import App from './App';

import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
export const router = createBrowserRouter([
    {
        path:"/",
        element: <App></App>,
        children:[
            {path:'/Dashboard',element: <Dashboard></Dashboard>},
            {path:'/Projects',element:<Projects></Projects>}
        ]
    },

]);

