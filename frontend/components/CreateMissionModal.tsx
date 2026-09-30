"use client";

import React, { useState } from "react";
import { X, Sparkles, Rocket, ChevronDown } from "lucide-react";
import { createMission, Mission } from "@/lib/api";

interface CreateMissionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: (mission: Mission) => void;
}

const PRESETS = [
  {
    label: "E-Commerce Flash Sale",
    description: "High concurrency e-commerce order processing API with PostgreSQL and ECS Fargate",
    rps: 1000,
    budget: 300,
  },
  {
    label: "SaaS Multi-Tenant API",
    description: "Multi-tenant SaaS REST API with row-level security, Redis caching, and CDN",
    rps: 2500,
    budget: 600,
  },
  {
    label: "Microservices Platform",
    description: "Event-driven microservices with SQS, Lambda, and API Gateway on ECS",
    rps: 5000,
    budget: 800,
  },
];

const FormField = ({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) => (
  <div>
    <label className="flex items-center justify-between mb-1.5">
      <span className="text-[11px] font-semibold text-[#8892aa] font-mono uppercase tracking-wider">
        {label}
      </span>
      {hint && <span className="text-[10px] font-mono text-[#4a5568]">{hint}</span>}
    </label>
    {children}
  </div>
);

export const CreateMissionModal: React.FC<CreateMissionModalProps> = ({
  isOpen,
  onClose,
  onCreated,
}) => {
  const [name, setName] = useState("E-Commerce Flash Sale Platform");
  const [description, setDescription] = useState(
    "High concurrency e-commerce order processing API with PostgreSQL and ECS Fargate"
  );
  const [targetRps, setTargetRps] = useState(1000);
  const [budget, setBudget] = useState(300);
  const [availability, setAvailability] = useState(0.9995);
  const [region, setRegion] = useState("ap-southeast-1");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const applyPreset = (preset: (typeof PRESETS)[0]) => {
    setName(preset.label + " Platform");
    setDescription(preset.description);
    setTargetRps(preset.rps);
    setBudget(preset.budget);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const mission = await createMission({
        name,
        description,
        requirements: {
          raw_input: description,
          target_rps: targetRps,
          availability_target: availability,
          monthly_budget_usd: budget,
          region,
          database: "postgresql",
          deployment: "ecs_fargate",
          performance_testing: true,
          security_validation: true,
        },
      });
      onCreated(mission);
      onClose();
    } catch (err: any) {
      alert("Failed to create mission: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="modal-content w-full animate-in" style={{ maxWidth: 540 }}>
        {/* Header */}
        <div
          className="px-6 py-4 flex items-center justify-between"
          style={{ borderBottom: "1px solid rgba(148,163,184,0.08)" }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-xl flex items-center justify-center"
              style={{ background: "rgba(0,212,255,0.08)", border: "1px solid rgba(0,212,255,0.2)" }}
            >
              <Sparkles size={14} className="text-[#00d4ff]" />
            </div>
            <div>
              <h3 className="text-[13px] font-bold text-white">New Engineering Mission</h3>
              <p className="text-[10px] font-mono text-[#4a5568]">
                Configure your autonomous DevOps pipeline
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[#4a5568] hover:text-white hover:bg-white/5 transition-all cursor-pointer"
          >
            <X size={15} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 pt-5 pb-6 space-y-5">
          {/* Presets */}
          <div>
            <p className="text-[10px] font-mono font-semibold uppercase tracking-widest text-[#4a5568] mb-2">
              Quick Presets
            </p>
            <div className="flex gap-2 flex-wrap">
              {PRESETS.map((p) => (
                <button
                  key={p.label}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className="text-[10px] font-mono px-2.5 py-1.5 rounded-lg transition-all cursor-pointer"
                  style={{
                    background: "rgba(0,212,255,0.05)",
                    border: "1px solid rgba(0,212,255,0.15)",
                    color: "#8892aa",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = "rgba(0,212,255,0.1)";
                    e.currentTarget.style.color = "#00d4ff";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = "rgba(0,212,255,0.05)";
                    e.currentTarget.style.color = "#8892aa";
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div
            style={{ height: 1, background: "rgba(148,163,184,0.06)" }}
          />

          {/* Mission Name */}
          <FormField label="Mission Name">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="form-input"
              placeholder="e.g. E-Commerce Flash Sale Platform"
              required
            />
          </FormField>

          {/* Description */}
          <FormField label="Workload Requirements">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="form-input resize-none"
              placeholder="Describe the technical requirements..."
              required
            />
          </FormField>

          {/* Sliders */}
          <div className="grid grid-cols-2 gap-5">
            <FormField label="Target Throughput" hint={`${targetRps.toLocaleString()} RPS`}>
              <input
                type="range"
                min={100}
                max={10000}
                step={100}
                value={targetRps}
                onChange={(e) => setTargetRps(Number(e.target.value))}
                className="w-full mt-2"
              />
              <div className="flex justify-between text-[9px] font-mono text-[#2d3748] mt-1">
                <span>100</span>
                <span>10K</span>
              </div>
            </FormField>

            <FormField label="Monthly Budget" hint={`$${budget} USD`}>
              <input
                type="range"
                min={50}
                max={1000}
                step={25}
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full mt-2"
              />
              <div className="flex justify-between text-[9px] font-mono text-[#2d3748] mt-1">
                <span>$50</span>
                <span>$1K</span>
              </div>
            </FormField>
          </div>

          {/* Selects */}
          <div className="grid grid-cols-2 gap-4">
            <FormField label="Availability SLA">
              <div className="relative">
                <select
                  value={availability}
                  onChange={(e) => setAvailability(Number(e.target.value))}
                  className="form-input"
                >
                  <option value={0.999}>99.9% — Three Nines</option>
                  <option value={0.9995}>99.95% — High Concurrency</option>
                  <option value={0.9999}>99.99% — Mission Critical</option>
                </select>
              </div>
            </FormField>

            <FormField label="AWS Region">
              <div className="relative">
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  className="form-input"
                >
                  <option value="ap-southeast-1">ap-southeast-1 · Singapore</option>
                  <option value="us-east-1">us-east-1 · N. Virginia</option>
                  <option value="eu-west-1">eu-west-1 · Ireland</option>
                  <option value="ap-northeast-1">ap-northeast-1 · Tokyo</option>
                </select>
              </div>
            </FormField>
          </div>

          {/* Actions */}
          <div
            className="flex items-center justify-end gap-3 pt-1"
            style={{ borderTop: "1px solid rgba(148,163,184,0.06)" }}
          >
            <button
              type="button"
              onClick={onClose}
              className="btn btn-ghost text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              id="btn-initialize-mission"
              className="btn btn-primary text-xs"
            >
              <Rocket size={13} />
              {isSubmitting ? "Initializing..." : "Initialize Mission"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
