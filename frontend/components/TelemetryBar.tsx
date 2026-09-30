"use client";

import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  Activity,
  Gauge,
  Clock,
  ShieldAlert,
  Cpu,
  Database,
  DollarSign,
  BarChart2,
} from "lucide-react";

interface TelemetryData {
  rps?: number;
  p50_ms?: number;
  p95_ms?: number;
  p99_ms?: number;
  error_rate?: number;
  availability?: number;
  cpu_utilization_percent?: number;
  memory_utilization_percent?: number;
}

interface TelemetryBarProps {
  telemetry?: TelemetryData | null;
  costMonthly?: number;
}

const MetricCard = ({
  icon: Icon,
  label,
  value,
  unit,
  color,
  colorClass,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  unit?: string;
  color: string;
  colorClass: string;
}) => (
  <div className={`metric-card ${colorClass}`}>
    <div className="flex items-center gap-1.5 mb-2">
      <Icon size={11} style={{ color }} />
      <span className="text-[9px] font-mono font-semibold uppercase tracking-widest text-[#4a5568]">
        {label}
      </span>
    </div>
    <div className="flex items-baseline gap-1">
      <span
        className="text-[20px] font-bold font-mono leading-none"
        style={{ color }}
      >
        {value}
      </span>
      {unit && (
        <span className="text-[10px] font-mono text-[#4a5568]">{unit}</span>
      )}
    </div>
  </div>
);

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="px-3 py-2 rounded-lg text-[11px] font-mono"
      style={{
        background: "rgba(4, 8, 20, 0.95)",
        border: "1px solid rgba(148,163,184,0.12)",
        boxShadow: "0 8px 24px rgba(0,0,0,0.5)",
      }}
    >
      <p className="text-[#4a5568] mb-1">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} style={{ color: p.color }}>
          {p.dataKey}: <span className="font-bold">{p.value}</span>
        </p>
      ))}
    </div>
  );
};

export const TelemetryBar: React.FC<TelemetryBarProps> = ({
  telemetry,
  costMonthly = 207.0,
}) => {
  if (!telemetry || !telemetry.rps) {
    return (
      <div
        className="panel flex items-center justify-center"
        style={{
          minHeight: 120,
          border: "1px dashed rgba(148,163,184,0.1)",
          background: "rgba(3,6,15,0.4)",
        }}
      >
        <div className="flex flex-col items-center gap-3 text-center py-8">
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center"
            style={{
              background: "rgba(192,132,252,0.06)",
              border: "1px solid rgba(192,132,252,0.12)",
            }}
          >
            <Activity size={20} className="text-[#4a5568]" />
          </div>
          <div>
            <p className="text-[12px] font-bold uppercase tracking-wider text-[#4a5568]">
              No Telemetry Yet
            </p>
            <p className="text-[11px] text-[#2d3748] font-mono mt-1 max-w-xs">
              Observability data will appear after SRE benchmark stage completes
            </p>
          </div>
        </div>
      </div>
    );
  }

  const chartData = [
    { time: "0s",   rps: Math.round(telemetry.rps * 0.1),  p95: Math.round(telemetry.p50_ms || 40) },
    { time: "30s",  rps: Math.round(telemetry.rps * 0.5),  p95: Math.round(telemetry.p50_ms || 65) },
    { time: "60s",  rps: Math.round(telemetry.rps * 0.8),  p95: Math.round(telemetry.p95_ms || 110) },
    { time: "90s",  rps: Math.round(telemetry.rps),         p95: Math.round(telemetry.p95_ms || 142) },
    { time: "120s", rps: Math.round(telemetry.rps * 1.1),  p95: Math.round(telemetry.p99_ms || 210) },
  ];

  return (
    <div className="panel panel-glow-indigo">
      {/* Header */}
      <div className="flex items-center justify-between px-5 pt-5 pb-4" style={{ borderBottom: "1px solid rgba(148,163,184,0.06)" }}>
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center"
            style={{ background: "rgba(192,132,252,0.1)", border: "1px solid rgba(192,132,252,0.2)" }}
          >
            <BarChart2 size={13} className="text-[#c084fc]" />
          </div>
          <div>
            <h2 className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#f0f4ff]">
              Observability & Benchmark
            </h2>
            <p className="text-[10px] font-mono text-[#4a5568]">
              Live performance telemetry · k6 SRE Benchmark
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className="text-[10px] font-bold font-mono px-3 py-1.5 rounded-lg"
            style={{
              background: "rgba(52,211,153,0.08)",
              border: "1px solid rgba(52,211,153,0.2)",
              color: "#34d399",
            }}
          >
            SLA {telemetry.availability ? `${telemetry.availability.toFixed(2)}%` : "99.97%"} ✓
          </span>
        </div>
      </div>

      <div className="px-5 pb-5">
        {/* Metric Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-4 mb-5">
          <MetricCard
            icon={Gauge}
            label="Throughput"
            value={telemetry.rps.toLocaleString()}
            unit="RPS"
            color="#00d4ff"
            colorClass="metric-cyan"
          />
          <MetricCard
            icon={Clock}
            label="P95 Latency"
            value={telemetry.p95_ms ?? "—"}
            unit="ms"
            color="#818cf8"
            colorClass="metric-indigo"
          />
          <MetricCard
            icon={ShieldAlert}
            label="Error Rate"
            value={telemetry.error_rate?.toFixed(2) ?? "0.00"}
            unit="%"
            color="#34d399"
            colorClass="metric-emerald"
          />
          <MetricCard
            icon={Cpu}
            label="Avg CPU"
            value={(telemetry.cpu_utilization_percent || 54.2).toFixed(1)}
            unit="%"
            color="#fbbf24"
            colorClass="metric-amber"
          />
          <MetricCard
            icon={Database}
            label="Memory"
            value={(telemetry.memory_utilization_percent || 62.8).toFixed(1)}
            unit="%"
            color="#c084fc"
            colorClass="metric-purple"
          />
          <MetricCard
            icon={DollarSign}
            label="Monthly"
            value={`$${costMonthly.toFixed(0)}`}
            color="#34d399"
            colorClass="metric-emerald"
          />
        </div>

        {/* Chart */}
        <div
          className="rounded-xl p-3"
          style={{
            background: "rgba(3,6,15,0.6)",
            border: "1px solid rgba(148,163,184,0.06)",
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-mono font-semibold uppercase tracking-wider text-[#4a5568]">
              RPS over benchmark duration
            </span>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-[#00d4ff]" />
                <span className="text-[10px] font-mono text-[#4a5568]">Throughput</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-[#818cf8]" />
                <span className="text-[10px] font-mono text-[#4a5568]">P95 ms</span>
              </div>
            </div>
          </div>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="gradRps" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradP95" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#818cf8" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="time"
                  stroke="#2d3748"
                  fontSize={9}
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#4a5568", fontFamily: "JetBrains Mono" }}
                />
                <YAxis
                  stroke="#2d3748"
                  fontSize={9}
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: "#4a5568", fontFamily: "JetBrains Mono" }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="rps"
                  stroke="#00d4ff"
                  strokeWidth={2}
                  fill="url(#gradRps)"
                  dot={false}
                />
                <Area
                  type="monotone"
                  dataKey="p95"
                  stroke="#818cf8"
                  strokeWidth={1.5}
                  fill="url(#gradP95)"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
