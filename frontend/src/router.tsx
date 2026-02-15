import { createBrowserRouter } from 'react-router-dom'
import App from './App';
import About from './pages/About';
import Login from './pages/Login';
import Register from './pages/Register';
import { Dashboard } from './pages/Dashboard';
export const router = createBrowserRouter([
    {
        path:"/",
        element: <App></App>,
        children:[
            {path:'/Dashboard',element: <Dashboard></Dashboard>},
            {path:'/about',element:<About></About>},
            {path:'/Login',element:<Login></Login>},
            {path:'/Register',element:<Register></Register>}
        ]
    },

]);

