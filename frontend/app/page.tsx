"use client";

import React, { useState, useEffect, useCallback } from "react";
import confetti from "canvas-confetti";
import { Header } from "@/components/Header";
import { ArchitectureCanvas } from "@/components/ArchitectureCanvas";
import { EngineerStation, AgentCardData } from "@/components/EngineerStation";
import { EventTimeline } from "@/components/EventTimeline";
import { TelemetryBar } from "@/components/TelemetryBar";
import { ArtifactModal } from "@/components/ArtifactModal";
import { CreateMissionModal } from "@/components/CreateMissionModal";
import { FinalReportModal } from "@/components/FinalReportModal";
import {
  fetchMissions,
  fetchMission,
  runMission,
  fetchMissionEvents,
  fetchMissionArtifacts,
  fetchMissionReport,
  Mission,
  MissionEvent,
  Artifact,
} from "@/lib/api";
import { MissionWebSocket } from "@/lib/websocket";

const INITIAL_AGENTS: AgentCardData[] = [
  { id: "architect",      name: "Solution Architect",    role: "AWS System Topology & Cost",       status: "WAITING" },
  { id: "database",       name: "Database Specialist",   role: "PostgreSQL Schema & Indexing",      status: "WAITING" },
  { id: "application",    name: "Backend Engineer",       role: "FastAPI & Non-Root Docker",         status: "WAITING" },
  { id: "infrastructure", name: "DevOps Engineer",        role: "Terraform Modules & IaC Plan",      status: "WAITING" },
  { id: "devsecops",      name: "DevSecOps Officer",      role: "Semgrep / Trivy / Syft / Cosign",  status: "WAITING" },
  { id: "sre",            name: "SRE Lead",               role: "k6 Benchmark & Remediation",        status: "WAITING" },
];

export default function Home() {
  const [mission, setMission] = useState<Mission | null>(null);
  const [agents, setAgents] = useState<AgentCardData[]>(INITIAL_AGENTS);
  const [events, setEvents] = useState<MissionEvent[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [telemetry, setTelemetry] = useState<any>(null);
  const [diagram, setDiagram] = useState<any>(null);

  // Modals
  const [isArtifactModalOpen, setIsArtifactModalOpen] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [reportData, setReportData] = useState<{
    report_json: any;
    report_markdown: string;
  } | null>(null);

  // 1. Initial Load
  const loadInitialMission = useCallback(async () => {
    try {
      const list = await fetchMissions();
      if (list.length > 0) {
        const active = list[0];
        setMission(active);
        syncFromMission(active);
        const [evts, arts] = await Promise.all([
          fetchMissionEvents(active.id),
          fetchMissionArtifacts(active.id),
        ]);
        setEvents(evts);
        setArtifacts(arts);
      }
    } catch {
      // Backend not yet responding
    }
  }, []);

  useEffect(() => {
    loadInitialMission();
  }, [loadInitialMission]);

  // Sync state from mission
  const syncFromMission = (m: Mission) => {
    if (m.stages) {
      setAgents((prev) =>
        prev.map((agent) => {
          const stageInfo = m.stages[agent.id];
          if (!stageInfo) return agent;
          return {
            ...agent,
            status: stageInfo.status as AgentCardData["status"],
            summary: stageInfo.summary,
            durationSeconds: stageInfo.duration_seconds,
            artifactsCount: stageInfo.artifacts?.length || 0,
          };
        })
      );
    }
    if (m.telemetry) setTelemetry(m.telemetry);
  };

  // 2. WebSocket Streaming
  useEffect(() => {
    if (!mission?.id) return;

    const ws = new MissionWebSocket(mission.id, async (msg: any) => {
      const newEvent: MissionEvent = {
        id: Math.random().toString(),
        mission_id: mission.id,
        event_type: msg.event_type || msg.event,
        stage: msg.stage,
        status: msg.status || "info",
        message: msg.message || "",
        timestamp: new Date().toISOString(),
      };
      setEvents((prev) => [...prev, newEvent]);

      if (msg.stage) {
        setAgents((prev) =>
          prev.map((agent) => {
            if (agent.id === msg.stage) {
              const isDone =
                msg.status === "passed" || msg.event_type?.includes("COMPLETED");
              const isFailed = msg.status === "failed";
              return {
                ...agent,
                status: isDone ? "COMPLETED" : isFailed ? "FAILED" : "RUNNING",
                summary: msg.message,
                artifactsCount:
                  (agent.artifactsCount || 0) + (msg.metadata?.artifacts?.length || 0),
              };
            }
            return agent;
          })
        );
      }

      if (msg.event_type === "ARCHITECT_COMPLETED" && msg.metadata?.diagram) {
        setDiagram(msg.metadata.diagram);
      }

      if (msg.event_type === "BENCHMARK_COMPLETED" && msg.metadata?.telemetry) {
        setTelemetry(msg.metadata.telemetry);
      }

      if (msg.event_type === "MISSION_COMPLETED") {
        setMission((prev) => (prev ? { ...prev, status: "COMPLETED" } : null));
        confetti({
          particleCount: 150,
          spread: 80,
          origin: { y: 0.6 },
          colors: ["#00d4ff", "#818cf8", "#34d399", "#c084fc"],
        });
        fetchMissionArtifacts(mission.id).then(setArtifacts);
      }
    });

    return () => ws.destroy();
  }, [mission?.id]);

  // 3. Launch
  const handleLaunchMission = async () => {
    if (!mission?.id) return;
    try {
      setMission((prev) => (prev ? { ...prev, status: "PLANNING" } : null));
      setAgents(INITIAL_AGENTS.map((a) => ({ ...a, status: "WAITING" })));
      setEvents([]);
      await runMission(mission.id);
    } catch (err: any) {
      alert("Error starting mission: " + err.message);
    }
  };

  // 4. View Report
  const handleViewReport = async () => {
    if (!mission?.id) return;
    try {
      const data = await fetchMissionReport(mission.id);
      setReportData(data);
      setIsReportModalOpen(true);
    } catch (err: any) {
      alert("Report not ready yet: " + err.message);
    }
  };

  const isRunning =
    mission?.status !== undefined &&
    mission.status !== "CREATED" &&
    mission.status !== "COMPLETED" &&
    mission.status !== "FAILED";

  // Polling fallback when mission is running to ensure UI always stays in sync
  useEffect(() => {
    if (!mission?.id || !isRunning) return;

    const interval = setInterval(async () => {
      try {
        const updated = await fetchMission(mission.id);
        if (updated) {
          setMission(updated);
          syncFromMission(updated);
          if (updated.status === "COMPLETED" || updated.status === "FAILED") {
            const [evts, arts] = await Promise.all([
              fetchMissionEvents(updated.id),
              fetchMissionArtifacts(updated.id),
            ]);
            setEvents(evts);
            setArtifacts(arts);
          }
        }
      } catch {
        // ignore polling network errors
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [mission?.id, isRunning]);

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: "#03060f", color: "#f0f4ff" }}
    >
      {/* Header */}
      <Header
        missionName={mission?.name || "E-Commerce Flash Sale Platform"}
        missionStatus={mission?.status || "CREATED"}
        region={mission?.requirements?.region || "ap-southeast-1"}
        currentStage={mission?.current_stage}
        estimatedCost={mission?.cost_estimate?.total_monthly_usd || 207.0}
        isRunning={isRunning}
        onLaunch={handleLaunchMission}
        onCreateNew={() => setIsCreateModalOpen(true)}
        onViewReport={handleViewReport}
        canViewReport={mission?.status === "COMPLETED"}
      />

      {/* Main */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-5 py-5 space-y-4">
        {/* Squad */}
        <EngineerStation
          agents={agents}
          onInspectArtifacts={() => setIsArtifactModalOpen(true)}
        />

        {/* Canvas + Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <ArchitectureCanvas architectureDiagram={diagram} />
          </div>
          <div className="lg:col-span-1">
            <EventTimeline events={events} />
          </div>
        </div>

        {/* Telemetry */}
        <TelemetryBar
          telemetry={telemetry}
          costMonthly={mission?.cost_estimate?.total_monthly_usd || 207.0}
        />
      </main>

      {/* Footer */}
      <footer
        className="text-center py-3 text-[10px] font-mono text-[#2d3748]"
        style={{ borderTop: "1px solid rgba(148,163,184,0.04)" }}
      >
        AWS CloudSquad · Autonomous Multi-Agent DevOps Platform · Built with Next.js 16
      </footer>

      {/* Modals */}
      <ArtifactModal
        isOpen={isArtifactModalOpen}
        onClose={() => setIsArtifactModalOpen(false)}
        artifacts={artifacts}
      />

      <CreateMissionModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreated={(newMission) => {
          setMission(newMission);
          syncFromMission(newMission);
          setEvents([]);
          setArtifacts([]);
          setTelemetry(null);
          setDiagram(null);
        }}
      />

      <FinalReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        reportJson={reportData?.report_json}
        reportMarkdown={reportData?.report_markdown}
        missionName={mission?.name || "Mission"}
      />
    </div>
  );
}
