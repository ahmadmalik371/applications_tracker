"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { 
  ArrowLeft, GripVertical, CheckCircle2, User, Clock, Star
} from "lucide-react";
import { 
  DndContext, 
  closestCorners, 
  KeyboardSensor, 
  PointerSensor, 
  useSensor, 
  useSensors,
  DragOverlay
} from "@dnd-kit/core";
import { 
  SortableContext, 
  arrayMove, 
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const STAGES = ["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected"];

interface Application {
  id: string;
  status: string;
  score: number | null;
  candidate: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  job_id: string;
  created_at: string;
}

// Sortable Application Card component
function SortableAppCard({ app }: { app: Application }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: app.id });
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <div 
      ref={setNodeRef} 
      style={style} 
      {...attributes} 
      {...listeners}
      className="bg-white p-4 rounded-lg border border-zinc-200 shadow-sm cursor-grab active:cursor-grabbing hover:border-indigo-300 transition-colors"
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-zinc-900 truncate pr-2">
          {app.candidate?.first_name} {app.candidate?.last_name}
        </h4>
        <GripVertical className="h-4 w-4 text-zinc-400 shrink-0 mt-0.5" />
      </div>
      <div className="flex items-center gap-1.5 text-xs text-zinc-500 mb-3">
        <Clock className="h-3 w-3" /> {new Date(app.created_at).toLocaleDateString()}
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-600 bg-zinc-100 px-2 py-1 rounded-md">
          {app.score ? `${Math.round(app.score * 100)}% Match` : "Pending AI"}
        </span>
        <Link href={`/dashboard/candidates/${app.candidate?.id}`} className="text-xs text-indigo-600 font-medium hover:underline flex items-center">
          <User className="h-3 w-3 mr-1" /> Profile
        </Link>
      </div>
    </div>
  );
}

// Column component
function PipelineColumn({ stage, applications }: { stage: string, applications: Application[] }) {
  return (
    <div className="flex-shrink-0 w-80 flex flex-col bg-zinc-50/80 rounded-xl border border-zinc-200 h-full max-h-full">
      <div className="p-4 border-b border-zinc-200/80 flex items-center justify-between bg-white/50 rounded-t-xl shrink-0">
        <h3 className="font-semibold text-zinc-800">{stage}</h3>
        <span className="bg-zinc-200 text-zinc-700 text-xs font-bold px-2 py-1 rounded-full">
          {applications.length}
        </span>
      </div>
      
      <div className="p-3 flex-1 overflow-y-auto min-h-[150px]">
        <SortableContext 
          id={stage}
          items={applications.map(a => a.id)} 
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-3 min-h-[100px]">
            {applications.map(app => (
              <SortableAppCard key={app.id} app={app} />
            ))}
          </div>
        </SortableContext>
      </div>
    </div>
  );
}

export default function PipelinePage() {
  const params = useParams();
  const { getToken } = useAuth();
  
  const [job, setJob] = useState<any>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeId, setActiveId] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = await getToken();
        if (!token) return;

        // Fetch Job
        const jobRes = await fetch(`${API_BASE}/jobs/${params.id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!jobRes.ok) throw new Error("Job not found");
        const jobData = await jobRes.json();
        setJob(jobData);

        // Fetch Applications for this job
        const appsRes = await fetch(`${API_BASE}/applications?job_id=${params.id}&limit=100`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (appsRes.ok) {
          const appsData = await appsRes.json();
          setApplications(Array.isArray(appsData) ? appsData : []);
        }
      } catch (err) {
        setError("Failed to load pipeline data.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [params.id, getToken]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragStart = (event: any) => {
    setActiveId(event.active.id);
  };

  const updateAppStatus = async (appId: string, newStatus: string) => {
    try {
      const token = await getToken();
      await fetch(`${API_BASE}/applications/${appId}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ status: newStatus })
      });
    } catch (e) {
      console.error("Failed to update status", e);
    }
  };

  const handleDragEnd = (event: any) => {
    setActiveId(null);
    const { active, over } = event;
    
    if (!over) return;
    
    const activeApp = applications.find(a => a.id === active.id);
    if (!activeApp) return;

    // Find what container we dropped it into
    const overId = over.id;
    let targetContainer = STAGES.find(s => s === overId);
    
    // If dropped on an item instead of the container directly, find that item's container
    if (!targetContainer) {
      const overItem = applications.find(a => a.id === overId);
      if (overItem) {
        targetContainer = overItem.status;
      }
    }
    
    if (targetContainer && targetContainer !== activeApp.status) {
      // Optimistic UI update
      setApplications(prev => 
        prev.map(app => app.id === active.id ? { ...app, status: targetContainer as string } : app)
      );
      
      // Persist to backend
      updateAppStatus(active.id, targetContainer as string);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-900" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="p-8 text-center text-rose-600">
        <p>{error || "Job not found"}</p>
        <Link href="/dashboard/jobs"><Button className="mt-4">Back to Jobs</Button></Link>
      </div>
    );
  }

  const activeApplication = activeId ? applications.find(a => a.id === activeId) : null;

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 shrink-0">
        <div>
          <Link href="/dashboard/jobs" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 mb-2 transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Jobs
          </Link>
          <h1 className="text-3xl font-bold text-zinc-900">{job.title}</h1>
          <p className="text-zinc-500 mt-1 flex items-center gap-2">
            Hiring Pipeline <span className="bg-zinc-200 w-1 h-1 rounded-full inline-block"></span> {applications.length} total candidates
          </p>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto min-h-0 pb-4">
        <DndContext 
          sensors={sensors} 
          collisionDetection={closestCorners} 
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-6 h-full items-start">
            {STAGES.map(stage => (
              <PipelineColumn 
                key={stage} 
                stage={stage} 
                applications={applications.filter(a => a.status === stage)} 
              />
            ))}
          </div>
          
          <DragOverlay>
            {activeApplication ? (
              <div className="bg-white p-4 rounded-lg border-2 border-indigo-500 shadow-xl opacity-90 scale-105 transform">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-semibold text-zinc-900">
                    {activeApplication.candidate?.first_name} {activeApplication.candidate?.last_name}
                  </h4>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <span className="text-xs font-medium text-zinc-600 bg-zinc-100 px-2 py-1 rounded-md">
                    {activeApplication.score ? `${Math.round(activeApplication.score * 100)}% Match` : "Pending AI"}
                  </span>
                </div>
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
}
