interface Props {
  title: string;
  value: string;
  subtitle?: string;
}

const MetricCard: React.FC<Props> = ({ title, value, subtitle }) => {
  return (
    <div className="bg-[#1f2937] border border-gray-800 rounded-xl p-6">
      <p className="text-sm text-gray-400">{title}</p>
      <h3 className="text-2xl font-semibold mt-2">{value}</h3>
      {subtitle && (
        <p className="text-xs text-gray-500 mt-2">{subtitle}</p>
      )}
    </div>
  );
};

export default MetricCard;