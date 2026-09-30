"use client";

import React, { useState } from "react";
import { X, Download, Copy, Check, FileCode, Folder, ChevronRight } from "lucide-react";
import { Artifact } from "@/lib/api";

interface ArtifactModalProps {
  isOpen: boolean;
  onClose: () => void;
  artifacts: Artifact[];
  initialSelectedAgent?: string | null;
}

const AGENT_COLORS: Record<string, string> = {
  architect: "#00d4ff",
  database: "#818cf8",
  application: "#60a5fa",
  infrastructure: "#fbbf24",
  devsecops: "#34d399",
  sre: "#c084fc",
};

const getFileExt = (name: string) => name.split(".").pop()?.toLowerCase() || "";

const EXT_COLORS: Record<string, string> = {
  tf: "#7b68ee",
  py: "#4ec9b0",
  sql: "#569cd6",
  yml: "#f0e68c",
  yaml: "#f0e68c",
  json: "#ce9178",
  md: "#9cdcfe",
  sh: "#dcdcaa",
  dockerfile: "#00d4ff",
};

export const ArtifactModal: React.FC<ArtifactModalProps> = ({
  isOpen,
  onClose,
  artifacts,
}) => {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<string>(artifacts[0]?.name || "");

  if (!isOpen) return null;

  const currentArtifact = artifacts.find((a) => a.name === activeTab) || artifacts[0];

  const handleCopy = () => {
    if (currentArtifact?.content) {
      navigator.clipboard.writeText(currentArtifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    if (currentArtifact?.content) {
      const blob = new Blob([currentArtifact.content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = currentArtifact.name;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // Group artifacts by agent
  const grouped = artifacts.reduce(
    (acc, art) => {
      const key = art.agent || "other";
      if (!acc[key]) acc[key] = [];
      acc[key].push(art);
      return acc;
    },
    {} as Record<string, Artifact[]>
  );

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        className="modal-content w-full flex flex-col animate-in"
        style={{ maxWidth: "900px", height: "82vh", maxHeight: "700px" }}
      >
        {/* Header */}
        <div
          className="px-5 py-4 flex items-center justify-between flex-shrink-0"
          style={{ borderBottom: "1px solid rgba(148,163,184,0.08)" }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: "rgba(0,212,255,0.08)", border: "1px solid rgba(0,212,255,0.2)" }}
            >
              <FileCode size={14} className="text-[#00d4ff]" />
            </div>
            <div>
              <h3 className="text-[13px] font-bold text-white tracking-tight">
                Artifact Inspector
              </h3>
              <p className="text-[10px] font-mono text-[#4a5568]">
                {artifacts.length} production artifacts generated
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="btn btn-ghost text-xs py-1.5 px-3"
            >
              {copied ? (
                <><Check size={12} className="text-[#34d399]" /> Copied</>
              ) : (
                <><Copy size={12} /> Copy</>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="btn btn-indigo text-xs py-1.5 px-3"
            >
              <Download size={12} /> Download
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg flex items-center justify-center text-[#4a5568] hover:text-white hover:bg-white/5 transition-all cursor-pointer"
            >
              <X size={15} />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div
            className="w-56 flex-shrink-0 overflow-y-auto p-3 space-y-3"
            style={{ borderRight: "1px solid rgba(148,163,184,0.06)", background: "rgba(3,6,15,0.4)" }}
          >
            {Object.entries(grouped).map(([agent, arts]) => (
              <div key={agent}>
                <div className="flex items-center gap-1.5 px-2 mb-1.5">
                  <Folder
                    size={10}
                    style={{ color: AGENT_COLORS[agent] || "#64748b" }}
                  />
                  <span
                    className="text-[9px] font-bold uppercase tracking-widest font-mono"
                    style={{ color: AGENT_COLORS[agent] || "#4a5568" }}
                  >
                    {agent}
                  </span>
                </div>
                <div className="space-y-0.5">
                  {arts.map((art) => {
                    const ext = getFileExt(art.name);
                    const extColor = EXT_COLORS[ext] || "#94a3b8";
                    const isActive = currentArtifact?.name === art.name;
                    return (
                      <button
                        key={art.name}
                        onClick={() => setActiveTab(art.name)}
                        className="w-full text-left px-2.5 py-2 rounded-lg text-[11px] font-mono flex items-center gap-2 transition-all cursor-pointer group"
                        style={{
                          background: isActive ? "rgba(0,212,255,0.06)" : "transparent",
                          border: isActive
                            ? "1px solid rgba(0,212,255,0.2)"
                            : "1px solid transparent",
                          color: isActive ? "#f0f4ff" : "#4a5568",
                        }}
                      >
                        <ChevronRight
                          size={10}
                          style={{
                            color: isActive ? "#00d4ff" : "transparent",
                            flexShrink: 0,
                          }}
                        />
                        <span
                          className="text-[9px] font-bold px-1.5 py-0.5 rounded"
                          style={{
                            background: `${extColor}15`,
                            color: extColor,
                            flexShrink: 0,
                          }}
                        >
                          .{ext}
                        </span>
                        <span className="truncate group-hover:text-[#8892aa] transition-colors">
                          {art.name.replace(`.${ext}`, "")}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Code viewer */}
          <div className="flex-1 overflow-auto code-viewer p-6">
            {currentArtifact ? (
              <pre className="whitespace-pre-wrap break-words select-text leading-relaxed">
                {currentArtifact.content || "Loading artifact content..."}
              </pre>
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
                <FileCode size={32} className="text-[#2d3748]" />
                <div>
                  <p className="text-[12px] font-semibold text-[#4a5568]">No artifacts yet</p>
                  <p className="text-[11px] font-mono text-[#2d3748] mt-1">
                    Run the mission pipeline to generate files
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
