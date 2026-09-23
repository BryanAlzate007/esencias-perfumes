import { useEffect, useState } from "react";
import { Alert, Spinner } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import DashboardChart from "../../components/DashboardChart/DashboardChart";
import { useAuth } from "../../hooks/useAuth";
import { getDashboardStats } from "../../services/dashboard";

const INITIAL_PERIODS = { users: "day", orders: "day", products: "day" };

export default function AdminDashboard() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [status, setStatus] = useState("loading");
  const [periods, setPeriods] = useState(INITIAL_PERIODS);

  useEffect(() => {
    getDashboardStats()
      .then((data) => {
        setStats(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, []);

  function changePeriod(metric, period) {
    setPeriods((current) => ({ ...current, [metric]: period }));
  }

  const charts = [
    { key: "users", title: t("admin.usersChart") },
    { key: "orders", title: t("admin.ordersChart") },
    { key: "products", title: t("admin.productsChart") },
  ];

  return (
    <>
      <h1 className="h2 mb-3">{t("admin.dashboardTitle")}</h1>
      <p className="text-body-secondary">{t("admin.dashboardLead", { name: user?.first_name || user?.username })}</p>
      {status === "loading" && (
        <div className="d-flex align-items-center gap-2 mt-4">
          <Spinner animation="border" size="sm" />
          <span>{t("common.loading")}</span>
        </div>
      )}
      {status === "error" && <Alert variant="warning" className="mt-4">{t("common.error")}</Alert>}
      {status === "ready" && (
        <div className="dashboard-charts">
          {charts.map((chart) => (
            <DashboardChart
              key={chart.key}
              title={chart.title}
              points={stats[chart.key][periods[chart.key]]}
              period={periods[chart.key]}
              onPeriod={(period) => changePeriod(chart.key, period)}
            />
          ))}
        </div>
      )}
    </>
  );
}
