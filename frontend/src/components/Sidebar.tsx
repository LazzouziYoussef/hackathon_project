import { NavLink } from "react-router-dom";
import { 
  LayoutDashboard, 
  BarChart3, 
  TrendingUp, 
  Lightbulb, 
  CheckCircle2, 
  PlayCircle, 
  History 
} from "lucide-react";

const navItems = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Metrics', to: '/metrics', icon: BarChart3 },
  { label: 'Predictions', to: '/predictions', icon: TrendingUp },
  { label: 'Recommendations', to: '/recommendations', icon: Lightbulb },
  { label: 'Approvals', to: '/approvals', icon: CheckCircle2 },
  { label: 'Simulator', to: '/simulator', icon: PlayCircle },
  { label: 'Audit Log', to: '/audit-log', icon: History },
];

const Sidebar = () => {
  return (
    <aside className="fixed w-64 h-screen bg-slate-950 border-r border-slate-800/50 flex flex-col">
      {/* Brand Header */}
      <div className="p-6 mb-2">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-900/20">
            <span className="text-white font-bold">S</span>
          </div>
          <h2 className="text-xl font-bold tracking-tight text-slate-100">
            Sadaqa <span className="text-blue-400">Tech</span>
          </h2>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-1 overflow-y-auto" aria-label="Main Navigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${
                isActive 
                  ? 'bg-blue-600/10 text-blue-400 font-medium' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span className="text-sm">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Optional: User/Footer area for balance */}
      <div className="p-4 border-t border-slate-800/50">
        <div className="flex items-center gap-3 px-2 py-2 text-slate-500 text-xs">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          System Operational
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;