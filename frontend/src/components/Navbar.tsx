import React from "react"
import { Link } from "react-router-dom"
export const Navbar = () => {
  return (
    <>
 <nav className="bg-indigo-950 text-2xl text-white  h-20 w-full">
            <div className='navbar flex p-5'>
            <div className=' logo'>
                <h1>Sadaqa tech</h1>
            </div>
            <div >    
                <nav className=" text-[20px] font-sans grid gap-4">
                 <Link to={"/"}>Dashboard</Link>
                 <Link to={"/about"}>About us</Link>    

                </nav>        

            </div>
        </div>
        </nav>
        </>
  )
}
