import { Search } from "lucide-react";
import { useMatches } from "react-router-dom"

interface RouteHandle{
  title? : string;
}
const Header = () => {
  const matches = useMatches();
  const current = matches[matches.length - 1];
 const handle = current?.handle as RouteHandle | undefined;
 const title = handle?.title || "Sadaqa Tech";
  return (
    <div className="  flex  bg-slate-950 h-15 pt-3 pl-4   space-x-5">
      <div className=" font-bold text-2xl">
       <h1>
  {title}
       </h1>
       </div>
       <div className=" flex pl-100 space-x-2">
        <Search className="pt-1"></Search><input type="text" className="border-1 bg-transparent rounded-2xl h-7 w-50 pl-2 text-white" placeholder="/search"/>
   </div>
   </div>
  )
}

export default Header