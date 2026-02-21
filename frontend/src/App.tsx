
import { Outlet } from "react-router-dom";
import Sidebar from "./components/Sidebar";

const App: React.FC = () => {
  return (
   <>
    <Sidebar></Sidebar>
    <Outlet></Outlet>

  </>
  );
};

export default App;