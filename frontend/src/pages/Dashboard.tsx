import React from "react";

interface Stat {
  title: string;
  value: string;
}

interface Project {
  name: string;
  needed: string;
  urgency: "High" | "Medium" | "Low";
}

const stats: Stat[] = [
  { title: "Total Donations", value: "124,500 MAD" },
  { title: "Active Projects", value: "18" },
  { title: "High Urgency", value: "5" },
  { title: "AI Confidence", value: "92%" },
];

const urgentProjects: Project[] = [
  { name: "Food Aid - Casablanca", needed: "25,000 MAD", urgency: "High" },
  { name: "Winter Blankets - Atlas", needed: "12,000 MAD", urgency: "High" },
  { name: "Medical Support - Rabat", needed: "18,500 MAD", urgency: "Medium" },
];

const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-linear-to-br from-[#0f172a] via-[#111827] to-black text-white flex">
      {/* Main Content */}
      <main className="flex-1 p-10 space-y-10">

        {/* Title */}
        <div>
          <h1 className="text-3xl font-bold mb-2">AI Impact Dashboard</h1>
          <p className="text-gray-400">Smart donation allocation overview</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-lg backdrop-blur-md hover:scale-105 transition"
            >
              <p className="text-gray-400 text-sm">{stat.title}</p>
              <h3 className="text-2xl font-bold mt-2">{stat.value}</h3>
            </div>
          ))}
        </div>

        {/* Chart Section */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 shadow-lg backdrop-blur-md">
          <h2 className="text-xl font-semibold mb-6">Donation Trends</h2>

          <div className="h-64 bg-linear-to-r from-indigo-500/20 to-purple-500/20 rounded-xl flex items-center justify-center text-gray-400">
            Chart Component Goes Here
          </div>
        </div>

        {/* Urgent Projects */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 shadow-lg backdrop-blur-md">
          <h2 className="text-xl font-semibold mb-6">High Urgency Projects</h2>

          <div className="space-y-4">
            {urgentProjects.map((project, index) => (
              <div
                key={index}
                className="flex justify-between items-center bg-white/5 p-4 rounded-xl border border-white/10"
              >
                <div>
                  <h3 className="font-semibold">{project.name}</h3>
                  <p className="text-gray-400 text-sm">
                    Needed: {project.needed}
                  </p>
                </div>

                <span
                  className={`px-3 py-1 text-sm rounded-full ${
                    project.urgency === "High"
                      ? "bg-red-500/20 text-red-400"
                      : project.urgency === "Medium"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-green-500/20 text-green-400"
                  }`}
                >
                  {project.urgency}
                </span>
              </div>
            ))}
          </div>
        </div>

      </main>
    </div>
  );
};

export default Dashboard;