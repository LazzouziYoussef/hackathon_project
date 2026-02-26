import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./Hooks/MainLayout"
import Overview from "./pages/Overview";
import Metrics from "./pages/Metrics";
import Predictions from "./pages/Predictions";
import Recommendations from "./pages/Recommendations";
import Approvals from "./pages/Approvals";
import Simulator from "./pages/Simulator";
import Auditlog from "./pages/Auditlog";
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/metrics" element={<Metrics />} />
          <Route path="/predictions" element={<Predictions />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/approvals" element={<Approvals />} />
          <Route path="/simulator" element={<Simulator />} />
          <Route path="/audit-log" element={<Auditlog />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
