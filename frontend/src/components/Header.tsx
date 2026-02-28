import { Search } from "lucide-react";
import { useMatches } from "react-router-dom";

interface RouteHandle {
  title?: string;
}

const Header = () => {
  const matches = useMatches();
  const current = matches[matches.length - 1];
  const handle = current?.handle as RouteHandle | undefined;
  const title = handle?.title || "Sadaqa Tech";

  return (
    // Changed bg-slate-950 to bg-slate-900 for softer contrast
    <header className="flex items-center justify-between bg-slate-900 h-16 px-8 border-b border-slate-800">
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
    </header>
  );
};

export default Header;