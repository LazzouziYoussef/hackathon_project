import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

const MainLayout = () => {
  return (
    <div className="flex min-h-screen bg-[#0f172a] text-gray-200">
      
      <Sidebar />

      <div className="ml-64 flex-1 flex flex-col">
        <Header />
        <main className="p-8 flex-1 overflow-y-auto">
       <Outlet></Outlet>
        </main>
      </div>

    </div>
  );
};

export default MainLayout;