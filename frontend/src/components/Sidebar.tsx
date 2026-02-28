import { NavLink } from "react-router-dom";
  const navItems = [
  { label: 'Dashboard', to: '/' },
  { label: 'Metrics', to: '/metrics' },
  { label: 'Predictions', to: '/predictions' },
  { label: 'Recommendations', to: '/recommendations' },
  { label: 'Approvals', to: '/approvals' },
  { label: 'Simulator', to: '/simulator' },
  { label: 'Audit Log', to: '/audit-log' },
];
const Sidebar = () => {
  return (
    <aside className="fixed w-64 h-screen bg-[#111827] border-r border-gray-800 p-6">
      <div className="pl-3 py- bg-linear-to-br from-slate-900 to-slate-800 rounded-2xl shadow-xl border border-slate-700">
  <h2 className="text-3xl font-extrabold tracking-tight text-white">
    Sadaqa <span className="text-blue-400">Tech</span>
  </h2>
</div>
      

  
    <nav className="flex flex-col gap-y-4 text-md font-medium pt-4" aria-label="Main Navigation">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          className={({ isActive }) =>
            `block transition-colors duration-200 hover:text-white hover:bg-slate-800 rounded-[5px] ${
              isActive ? 'text-white font-semibold' : 'text-gray-400'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  

    </aside>
  );
};


export default Sidebar;