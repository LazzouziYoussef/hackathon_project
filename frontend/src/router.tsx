import { createBrowserRouter } from "react-router-dom";
import MainLayout from "./Hooks/MainLayout";

import Overview from "./pages/Overview";
import Metrics from "./pages/Metrics";
import Predictions from "./pages/Predictions";
import Recommendations from "./pages/Recommendations";
import Approvals from "./pages/Approvals";
import Simulator from "./pages/Simulator";
import AuditLog from "./pages/Auditlog";
import Tenants from "./pages/Tenants";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Overview />,
      },
      {
        path: "metrics",
        element: <Metrics />,
      },
      {
        path: "predictions",
        element: <Predictions />,
      },
      {
        path: "recommendations",
        element: <Recommendations />,
      },
      {
        path: "approvals",
        element: <Approvals />,
      },
      {
        path: "simulator",
        element: <Simulator />,
      },
      {
        path: "audit-log",
        element: <AuditLog />,
      },
      {
        path: "tenants",
        element: <Tenants />,
      },
    ],
  },
]);