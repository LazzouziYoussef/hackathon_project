import MetricCard from "../components/MetricCard";
import Header from "../components/Header";
const Dashboard = () => {
  return (
    <>
    
        <div className="space-y-8">
            
          

      <div>
        <h1 className="text-2xl font-semibold">Operational Overview</h1>
        <p className="text-gray-400 text-sm ">
          Real-time observability with short-term prediction.
        </p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        
      </div>

      <div className="bg-[#1f2937] border border-gray-800 rounded-xl p-6 h-80">
        <p className="text-sm text-gray-400 mb-4">
          Actual vs Predicted Traffic
        </p>

        {/* PredictionChart goes here */}

      </div>

    </div>
    </>
  );
};

export default Dashboard;