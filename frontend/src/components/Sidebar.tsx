import { NavLink } from "react-router-dom";

const Sidebar = () => {
  return (
    <aside className="fixed w-64 h-screen bg-[#111827] border-r border-gray-800 p-6">
      <h2 className="text-xl font-semibold mb-10">
        Sadaqa Tech
      </h2>

      <nav className="space-y-4 text-sm">
        <NavLink to="/" className="block hover:text-white">Overview</NavLink>
        <NavLink to="/metrics" className="block hover:text-white">Metrics</NavLink>
        <NavLink to="/predictions" className="block hover:text-white">Predictions</NavLink>
        <NavLink to="/recommendations" className="block hover:text-white">Recommendations</NavLink>
        <NavLink to="/approvals" className="block hover:text-white">Approvals</NavLink>
        <NavLink to="/simulator" className="block hover:text-white">Simulator</NavLink>
        <NavLink to="/audit-log" className="block hover:text-white">Audit Log</NavLink>
        <NavLink to="/tenants" className="block hover:text-white">Tenants</NavLink>
      </nav>
    </aside>
  );
};

export default Sidebar;