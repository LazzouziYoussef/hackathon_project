
import { useState, useRef, useEffect } from "react"; // Added hooks
import { Search, User2Icon, LogIn, UserPlus } from "lucide-react";
import { useMatches, useNavigate } from "react-router-dom";


interface RouteHandle {
  title?: string;
}
const Header = () => {
  const navigate =  useNavigate();

  const [isMenuOpen, setIsMenuOpen] = useState(false); // State to track the menu
  const menuRef = useRef<HTMLDivElement>(null); // To help close menu when clicking outside

  const matches = useMatches();
  const current = matches[matches.length - 1];
  const handle = current?.handle as RouteHandle | undefined;
  const title = handle?.title || "Sadaqa Tech";

  // Close menu if user clicks anywhere else on the screen
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="flex items-center justify-between bg-slate-900 h-16 px-8 border-b border-slate-800 relative">
      <div className="flex items-center">
        <h1 className="text-xl font-semibold text-slate-100 tracking-tight">
          {title}
        </h1>
      </div>

      <div className="relative flex items-center group">
        <Search className="absolute left-3 w-4 h-4 text-slate-400 group-focus-within:text-blue-400 transition-colors" />
        <input 
          type="text" 
          className="bg-slate-800 border border-slate-700 rounded-lg h-10 w-64 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" 
          placeholder="Search..."
        />
      </div>

      {/* User Icon Container */}
      <div className="relative" ref={menuRef}>
        <button 
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className={`p-2 rounded-full transition-all duration-200 ${
            isMenuOpen ? 'bg-slate-800 text-blue-400' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800'
          }`}
        >
          <User2Icon className="w-6 h-6" />
        </button>

        {/* Dropdown Menu */}
        {isMenuOpen && (
          <div className="absolute right-0 mt-2 w-48 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl py-2 z-50 animate-in fade-in zoom-in duration-150">
            <button className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors hover:cursor-pointer" onClick={()=>{navigate('/Login')}}>
              <LogIn className="w-4 h-4" />
              Log In
            </button>
            <button className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors hover:cursor-pointer">
              <UserPlus className="w-4 h-4" />
              Sign Up
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;