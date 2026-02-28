import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./Hooks/MainLayout";
import Metrics from "./pages/Metrics";
import Predictions from "./pages/Predictions";
import Recommendations from "./pages/Recommendations";
import Approvals from "./pages/Approvals";
import Simulator from "./pages/Simulator";
import AuditLog from "./pages/Auditlog";
import Dashboard from "./pages/Dashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
        handle:{title : "Dashboard"}
      },
      {
        path: "metrics",
        element: <Metrics />,
        handle:{title : "Metrics"}

      },
      {
        path: "predictions",
        element: <Predictions />,
        handle:{title : "Predictions"}

      },
      {
        path: "recommendations",
        element: <Recommendations />,
        handle:{title : "Recommendations"}

      },
      {
        path: "approvals",
        element: <Approvals />,
        handle:{title : "Aprrovals"}

      },
      {
        path: "simulator",
        element: <Simulator />,
        handle:{title : "Simulator"}

      },
      {
        path: "audit-log",
        element: <AuditLog></AuditLog>,
        handle:{ title : "AuditLog"},

      },
      
    ],
  },
]);
