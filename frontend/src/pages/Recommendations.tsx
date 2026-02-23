const Recommendations = () => {
  return (
    <div className="space-y-6">

      <h1 className="text-2xl font-semibold">
        Guarded Scaling Recommendations
      </h1>

      <div className="bg-[#1f2937] border border-gray-800 rounded-xl p-6">
        <p className="text-sm text-gray-400">
          Rule: R-HighLoad-01
        </p>

        <h3 className="text-lg mt-2">
          Predicted capacity breach at 19:45
        </h3>

        <p className="text-sm text-gray-400 mt-2">
          Current margin: 12%  
          Confidence: 74%
        </p>

        <div className="mt-4 flex gap-4">
          <button className="px-4 py-2 bg-green-600 rounded-md">
            Approve
          </button>
          <button className="px-4 py-2 bg-red-600 rounded-md">
            Reject
          </button>
        </div>
      </div>

    </div>
  );
};

export default Recommendations;