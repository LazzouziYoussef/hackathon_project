import { NavLink } from "react-router-dom";

export const Navbar = () => {
  const pages = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "About", path: "/about" },
  ];

  return (
    <nav className="relative w-full text-white overflow-hidden">
      
      {/* Animated Background Layer */}
      <div className="absolute inset-0 bg-gradient-to-r 
                      from-indigo-900 via-blue-800 to-indigo-900 
                      bg-[length:200%_200%] animate-gradient">
      </div>

      {/* Content Layer */}
      <div className="relative flex items-center justify-between px-8 py-4">
        
        <h1 className="text-2xl font-bold">
          Sadaqa Tech
        </h1>

        <div className="flex gap-8 text-lg box-border">
          {pages.map((page) => (
            <NavLink
              key={page.path}
              to={page.path}
              className={({ isActive }) =>
                ` opacity-50 relative pb-1 transition-all duration-300
                 after:content-[''] after:absolute after:left-0 after:bottom-0
                 after:h-[2px] after:bg-white after:transition-all after:duration-300 hover:opacity-100
                 ${
                   isActive
                     ? "after:w-full opacity-100"
                     : "after:w-0 hover:after:w-full " 
                 }`
              }
            >
              {page.name}
            </NavLink>
          ))}
        </div>

      </div>
    </nav>
  );
};
