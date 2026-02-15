import React from 'react'

const About = () => {
  return (
    <>
    <div className="relative w-full min-h-screen px-10 pt-6 ">  
           <div className="absolute left-[500px] top-0 w-[2px] h-[90%] bg-white slide-line-up z-[-10] "></div>

      <div className="absolute left-0 top-[100px]  w-[90%] h-[1px] bg-white slide-line-left"></div>
      <div className="absolute  top-[500px]  w-[90%] h-[1px] bg-white slide-line-right"></div>

        <h1 className='text-5xl text-white font-bold left animate-slide-left '>About <span className=''>us</span></h1>
    </div>
    </>
  )
}

export default About;