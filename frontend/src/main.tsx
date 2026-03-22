import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
<<<<<<< HEAD
import { RouterProvider } from 'react-router-dom'
import {router} from "./router"
createRoot(document.getElementById('root')!).render(
  <StrictMode>
     <RouterProvider router={router}></RouterProvider>
 </StrictMode>
=======

import { RouterProvider } from 'react-router-dom'
import { router } from './router'
createRoot(document.getElementById('root')!).render(
  <StrictMode>
     <RouterProvider router={router}></RouterProvider>
  </StrictMode>
>>>>>>> 32b7af7 (Add routing)
)
