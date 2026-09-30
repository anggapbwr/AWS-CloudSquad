"use client";

import React, { useState, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  NodeProps,
  Edge,
  Node,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  Globe,
  Layers,
  Server,
  Database,
  Zap,
  HardDrive,
  Shield,
  Activity,
  X,
  Network,
} from "lucide-react";

interface NodeData extends Record<string, unknown> {
  label: string;
  service: string;
  type: string;
  status: string;
  cost?: string;
  config?: Record<string, any>;
}

const SERVICE_CONFIG: Record<
  string,
  { icon: React.ElementType; color: string; bg: string }
> = {
  CloudFront: { icon: Globe,     color: "#fbbf24", bg: "rgba(251,191,36,0.1)" },
  Internet:   { icon: Globe,     color: "#fbbf24", bg: "rgba(251,191,36,0.1)" },
  ALB:        { icon: Layers,    color: "#818cf8", bg: "rgba(129,140,248,0.1)" },
  ECS:        { icon: Server,    color: "#00d4ff", bg: "rgba(0,212,255,0.1)" },
  ElastiCache:{ icon: Zap,       color: "#fb7185", bg: "rgba(251,113,133,0.1)" },
  RDS:        { icon: Database,  color: "#60a5fa", bg: "rgba(96,165,250,0.1)" },
  S3:         { icon: HardDrive, color: "#34d399", bg: "rgba(52,211,153,0.1)" },
  WAF:        { icon: Shield,    color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
};

const CustomNodeComponent = ({ data }: NodeProps<Node<NodeData>>) => {
  const svc = SERVICE_CONFIG[data.service] || {
    icon: Activity,
    color: "#c084fc",
    bg: "rgba(192,132,252,0.1)",
  };
  const Icon = svc.icon;

  return (
    <div
      style={{
        background: "linear-gradient(145deg, rgba(10,20,44,0.97) 0%, rgba(4,8,20,0.99) 100%)",
        border: `1px solid ${svc.color}30`,
        borderRadius: 12,
        padding: "10px 12px",
        minWidth: 160,
        boxShadow: `0 4px 24px rgba(0,0,0,0.4), 0 0 0 1px ${svc.color}10`,
        cursor: "pointer",
        transition: "all 0.2s",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* top accent */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: "20%",
          right: "20%",
          height: 1,
          background: `linear-gradient(90deg, transparent, ${svc.color}60, transparent)`,
        }}
      />
      <Handle
        type="target"
        position={Position.Top}
        style={{ width: 8, height: 8, background: svc.color, border: "2px solid #03060f" }}
      />
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 8,
            background: svc.bg,
            border: `1px solid ${svc.color}25`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <Icon size={13} style={{ color: svc.color }} />
        </div>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, color: "#f0f4ff", letterSpacing: "0.01em" }}>
            {data.label}
          </div>
          <div style={{ fontSize: 9, color: "#4a5568", fontFamily: "JetBrains Mono" }}>
            {data.service}
          </div>
        </div>
      </div>
      {data.cost && (
        <div
          style={{
            marginTop: 6,
            paddingTop: 6,
            borderTop: "1px solid rgba(148,163,184,0.06)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: 9, color: "#4a5568", fontFamily: "JetBrains Mono" }}>
            Est. Cost
          </span>
          <span style={{ fontSize: 10, color: "#34d399", fontWeight: 700, fontFamily: "JetBrains Mono" }}>
            {data.cost}
          </span>
        </div>
      )}
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ width: 8, height: 8, background: svc.color, border: "2px solid #03060f" }}
      />
    </div>
  );
};

interface ArchitectureCanvasProps {
  architectureDiagram?: {
    nodes: Node<NodeData>[];
    edges: Edge[];
  } | null;
}

export const ArchitectureCanvas: React.FC<ArchitectureCanvasProps> = ({
  architectureDiagram,
}) => {
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);

  const nodeTypes = useMemo(() => ({ custom: CustomNodeComponent }), []);

  const defaultNodes: Node<NodeData>[] = [
    { id: "node-users",  type: "custom", position: { x: 230, y: 15  }, data: { label: "Internet Clients",          service: "Internet",    type: "client",   status: "active" } },
    { id: "node-cf",     type: "custom", position: { x: 230, y: 105 }, data: { label: "CloudFront + WAF",           service: "CloudFront",  type: "edge",     status: "active", cost: "$15/mo" } },
    { id: "node-alb",    type: "custom", position: { x: 230, y: 195 }, data: { label: "Application Load Balancer",  service: "ALB",         type: "lb",       status: "active", cost: "$22/mo" } },
    { id: "node-ecs",    type: "custom", position: { x: 230, y: 285 }, data: { label: "ECS Fargate (FastAPI)",       service: "ECS",         type: "compute",  status: "active", cost: "$45/mo" } },
    { id: "node-redis",  type: "custom", position: { x: 50,  y: 385 }, data: { label: "ElastiCache Redis",           service: "ElastiCache", type: "cache",    status: "active", cost: "$32/mo" } },
    { id: "node-rds",    type: "custom", position: { x: 230, y: 385 }, data: { label: "RDS PostgreSQL",              service: "RDS",         type: "database", status: "active", cost: "$65/mo" } },
    { id: "node-s3",     type: "custom", position: { x: 410, y: 385 }, data: { label: "Amazon S3",                   service: "S3",          type: "storage",  status: "active", cost: "$6/mo"  } },
  ];

  const defaultEdges: Edge[] = [
    { id: "e1", source: "node-users", target: "node-cf",    animated: true,  style: { stroke: "#00d4ff", strokeWidth: 1.5 } },
    { id: "e2", source: "node-cf",    target: "node-alb",   animated: true,  style: { stroke: "#00d4ff", strokeWidth: 1.5 } },
    { id: "e3", source: "node-alb",   target: "node-ecs",   animated: true,  style: { stroke: "#00d4ff", strokeWidth: 1.5 } },
    { id: "e4", source: "node-ecs",   target: "node-redis",              style: { stroke: "#4a5568",  strokeWidth: 1, strokeDasharray: "4 3" } },
    { id: "e5", source: "node-ecs",   target: "node-rds",                style: { stroke: "#4a5568",  strokeWidth: 1, strokeDasharray: "4 3" } },
    { id: "e6", source: "node-ecs",   target: "node-s3",                 style: { stroke: "#4a5568",  strokeWidth: 1, strokeDasharray: "4 3" } },
  ];

  const nodes = architectureDiagram?.nodes || defaultNodes;
  const edges = architectureDiagram?.edges || defaultEdges;

  return (
    <div
      className="panel flex flex-col h-[520px]"
      style={{ boxShadow: "0 0 0 1px rgba(129,140,248,0.08), 0 4px 40px rgba(0,0,0,0.4)" }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 pt-4 pb-3"
        style={{ borderBottom: "1px solid rgba(148,163,184,0.06)" }}
      >
        <div className="flex items-center gap-2.5">
          <Network size={14} className="text-[#818cf8]" />
          <div>
            <h2 className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#f0f4ff]">
              Architecture Topology
            </h2>
            <p className="text-[10px] font-mono text-[#4a5568]">
              React Flow · Multi-AZ VPC Fabric
            </p>
          </div>
        </div>
        <span className="text-[9px] font-mono text-[#4a5568]">Click nodes to inspect</span>
      </div>

      {/* Canvas */}
      <div className="flex-1 overflow-hidden rounded-b-2xl" style={{ background: "#03060f" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodeClick={(_, node) => setSelectedNode(node.data as unknown as NodeData)}
          fitView
          minZoom={0.4}
          maxZoom={1.8}
          proOptions={{ hideAttribution: true }}
        >
          <Background
            color="rgba(148,163,184,0.04)"
            gap={28}
            size={1}
          />
          <Controls />
        </ReactFlow>
      </div>

      {/* Node Inspector */}
      {selectedNode && (
        <div
          className="absolute bottom-5 right-5 w-72 rounded-2xl p-4 animate-in"
          style={{
            background: "linear-gradient(145deg, rgba(9,18,38,0.98), rgba(4,8,20,0.99))",
            border: "1px solid rgba(0,212,255,0.2)",
            boxShadow: "0 20px 60px rgba(0,0,0,0.7), 0 0 0 1px rgba(0,212,255,0.05)",
            backdropFilter: "blur(24px)",
            zIndex: 50,
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-[11px] font-bold text-white">{selectedNode.label}</p>
              <p className="text-[9px] font-mono text-[#4a5568] mt-0.5">{selectedNode.service}</p>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-[#4a5568] hover:text-white transition-colors cursor-pointer p-1 rounded-lg hover:bg-white/5"
            >
              <X size={14} />
            </button>
          </div>

          <div className="space-y-2">
            {[
              ["Role / Type", selectedNode.type, "#8892aa"],
              ["Monthly Cost", selectedNode.cost || "Included in VPC", "#34d399"],
              ["Redundancy", "Multi-AZ (AZ-a, AZ-b)", "#818cf8"],
              ["Encryption", "KMS AES-256", "#fbbf24"],
            ].map(([k, v, c]) => (
              <div
                key={k}
                className="flex items-center justify-between text-[11px] font-mono py-1.5"
                style={{ borderBottom: "1px solid rgba(148,163,184,0.05)" }}
              >
                <span style={{ color: "#4a5568" }}>{k}</span>
                <span style={{ color: c, fontWeight: 600 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
