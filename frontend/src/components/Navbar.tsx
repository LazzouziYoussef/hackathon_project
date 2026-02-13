import React from 'react'
import Dashboard from '../pages/Dashboard'

export const Navbar = () => {
  return (
    <>
 <nav className="bg-indigo-950 text-2xl text-white font-bold h-20 w-full">
            <div className='navbar flex p-5'>
            <div className=' logo'>
                <h1>Sadaqa tech</h1>
            </div>
            <div className='links relative '>    
            <ul className='list-group'>
                <li><a href="../pages/Dashboard.tsx">Dashboard</a></li>
                <li></li>
                <li></li>
            </ul>
            </div>
        </div>
        </nav>
        </>
  )
}
