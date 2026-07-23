"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft,
  Plus,
  Mail,
  Eye,
  Pencil,
  Trash2,
  X,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  CheckCircle2,
  Variable,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import apiClient from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { AuthGuard } from "@/components/auth-guard";

// ─── Types ────────────────────────────────────────────────────────────────────

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
  variables: string | null;
  is_active: boolean;
  created_at: string | null;
}

interface TemplateFormData {
  name: string;
  subject: string;
  body: string;
  variables: string; // comma-separated in UI, sent as array to API
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function parseVariables(raw: string | null): string[] {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return raw.split(",").map((v) => v.trim()).filter(Boolean);
  }
}

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// ─── Main Page ────────────────────────────────────────────────────────────────

function EmailTemplatesContent() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<EmailTemplate | null>(null);
  const [successMsg, setSuccessMsg] = useState("");

  const flash = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(""), 3000);
  };

  const { data: templates = [], isLoading, isError } = useQuery<EmailTemplate[]>({
    queryKey: ["email-templates"],
    queryFn: async () => {
      const { data } = await apiClient.get<EmailTemplate[]>("/email-templates");
      return data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async (form: TemplateFormData) => {
      const variables = form.variables
        .split(",")
        .map((v) => v.trim())
        .filter(Boolean);
      await apiClient.post("/email-templates", { ...form, variables });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["email-templates"] });
      setShowForm(false);
      flash("Template created successfully.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/email-templates/${id}`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["email-templates"] });
      flash("Template deleted.");
    },
  });

  const openEdit = (t: EmailTemplate) => {
    setEditingTemplate(t);
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditingTemplate(null);
  };

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Page Header */}
      <header className="border-b border-zinc-200 bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4 sm:px-6 lg:px-8">
          <Link
            href="/dashboard"
            className="mb-1 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-700"
          >
            <ArrowLeft className="h-4 w-4" /> Dashboard
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-zinc-900">
                Email Templates
              </h1>
              <p className="text-sm text-zinc-500">
                Manage reusable email templates with dynamic variable substitution.
              </p>
            </div>
            <Button
              id="create-template-btn"
              onClick={() => { setEditingTemplate(null); setShowForm(true); }}
              className="gap-2 bg-zinc-900 text-white hover:bg-zinc-800"
            >
              <Plus className="h-4 w-4" /> New Template
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
        {/* Success toast */}
        {successMsg && (
          <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            <CheckCircle2 className="h-4 w-4 shrink-0" /> {successMsg}
          </div>
        )}

        {/* Create / Edit Form */}
        {showForm && (
          <TemplateForm
            initial={editingTemplate}
            onSubmit={(form) => createMutation.mutate(form)}
            onClose={closeForm}
            isPending={createMutation.isPending}
            error={createMutation.error as Error | null}
          />
        )}

        {/* Preview modal */}
        {previewTemplate && (
          <PreviewModal
            template={previewTemplate}
            onClose={() => setPreviewTemplate(null)}
          />
        )}

        {/* Template List */}
        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-20 w-full rounded-xl" />
            ))}
          </div>
        ) : isError ? (
          <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4 shrink-0" />
            Failed to load email templates.
          </div>
        ) : templates.length === 0 ? (
          <EmptyState onCreateClick={() => { setEditingTemplate(null); setShowForm(true); }} />
        ) : (
          <div className="space-y-3">
            {templates.map((t) => (
              <TemplateCard
                key={t.id}
                template={t}
                onPreview={() => setPreviewTemplate(t)}
                onEdit={() => openEdit(t)}
                onDelete={() => {
                  if (confirm(`Delete template "${t.name}"?`)) {
                    deleteMutation.mutate(t.id);
                  }
                }}
                isDeleting={deleteMutation.isPending}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

// ─── Template Card ─────────────────────────────────────────────────────────────

function TemplateCard({
  template,
  onPreview,
  onEdit,
  onDelete,
  isDeleting,
}: {
  template: EmailTemplate;
  onPreview: () => void;
  onEdit: () => void;
  onDelete: () => void;
  isDeleting: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const vars = parseVariables(template.variables);

  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-1">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 shrink-0">
                <Mail className="h-4 w-4 text-indigo-600" />
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-zinc-900 truncate">{template.name}</p>
                <p className="text-xs text-zinc-500 truncate">{template.subject}</p>
              </div>
            </div>

            {vars.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5 pl-12">
                {vars.map((v) => (
                  <span
                    key={v}
                    className="inline-flex items-center gap-1 rounded-full bg-violet-50 px-2 py-0.5 text-xs font-mono text-violet-700"
                  >
                    <Variable className="h-2.5 w-2.5" />
                    {`{{${v}}}`}
                  </span>
                ))}
              </div>
            )}

            {expanded && (
              <div className="mt-4 pl-12">
                <pre className="whitespace-pre-wrap rounded-lg bg-zinc-50 border border-zinc-100 p-4 text-xs text-zinc-700 font-mono leading-relaxed max-h-64 overflow-y-auto">
                  {template.body}
                </pre>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Badge
              variant="secondary"
              className={template.is_active ? "bg-emerald-100 text-emerald-700" : "bg-zinc-100 text-zinc-500"}
            >
              {template.is_active ? "Active" : "Inactive"}
            </Badge>
            <span className="text-xs text-zinc-400 hidden sm:block">
              {formatDate(template.created_at)}
            </span>

            <Button
              id={`expand-template-${template.id}`}
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-400 hover:text-zinc-700"
              onClick={() => setExpanded((p) => !p)}
              title={expanded ? "Collapse" : "Expand body"}
            >
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>

            <Button
              id={`preview-template-${template.id}`}
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-400 hover:text-indigo-600"
              onClick={onPreview}
              title="Preview with variables"
            >
              <Eye className="h-4 w-4" />
            </Button>

            <Button
              id={`edit-template-${template.id}`}
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-400 hover:text-zinc-700"
              onClick={onEdit}
              title="Edit template"
            >
              <Pencil className="h-4 w-4" />
            </Button>

            <Button
              id={`delete-template-${template.id}`}
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-zinc-400 hover:text-rose-600"
              onClick={onDelete}
              disabled={isDeleting}
              title="Delete template"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Create / Edit Form ────────────────────────────────────────────────────────

function TemplateForm({
  initial,
  onSubmit,
  onClose,
  isPending,
  error,
}: {
  initial: EmailTemplate | null;
  onSubmit: (form: TemplateFormData) => void;
  onClose: () => void;
  isPending: boolean;
  error: Error | null;
}) {
  const [name, setName] = useState(initial?.name ?? "");
  const [subject, setSubject] = useState(initial?.subject ?? "");
  const [body, setBody] = useState(initial?.body ?? "");
  const [variables, setVariables] = useState(
    initial ? parseVariables(initial.variables).join(", ") : ""
  );

  const isEdit = !!initial;
  const isValid = name.trim() && subject.trim() && body.trim();

  return (
    <Card className="border-zinc-300 shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{isEdit ? "Edit Template" : "New Email Template"}</CardTitle>
            <CardDescription>
              Use <code className="rounded bg-zinc-100 px-1 text-xs">{"{{variable_name}}"}</code> syntax in subject and body for dynamic substitution.
            </CardDescription>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} id="close-template-form">
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error.message || "Failed to save template."}
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="template-name" className="mb-1.5 block text-sm font-medium text-zinc-700">
              Template Name <span className="text-rose-500">*</span>
            </label>
            <input
              id="template-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Application Received"
              className="h-10 w-full rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-100"
            />
          </div>

          <div>
            <label htmlFor="template-variables" className="mb-1.5 block text-sm font-medium text-zinc-700">
              Variables (comma-separated)
            </label>
            <input
              id="template-variables"
              type="text"
              value={variables}
              onChange={(e) => setVariables(e.target.value)}
              placeholder="e.g. candidate_name, job_title"
              className="h-10 w-full rounded-md border border-zinc-200 px-3 text-sm font-mono outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-100"
            />
          </div>
        </div>

        <div>
          <label htmlFor="template-subject" className="mb-1.5 block text-sm font-medium text-zinc-700">
            Email Subject <span className="text-rose-500">*</span>
          </label>
          <input
            id="template-subject"
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g. We received your application for {{job_title}}"
            className="h-10 w-full rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-100"
          />
        </div>

        <div>
          <label htmlFor="template-body" className="mb-1.5 block text-sm font-medium text-zinc-700">
            Email Body <span className="text-rose-500">*</span>
          </label>
          <textarea
            id="template-body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={10}
            placeholder={`Dear {{candidate_name}},\n\nThank you for applying to {{job_title}}...\n\nBest regards,\nThe {{company_name}} Team`}
            className="w-full rounded-md border border-zinc-200 px-3 py-2 text-sm font-mono leading-relaxed outline-none focus:border-zinc-400 focus:ring-2 focus:ring-zinc-100 resize-y"
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="outline" onClick={onClose} disabled={isPending}>
            Cancel
          </Button>
          <Button
            id="save-template-btn"
            onClick={() => onSubmit({ name, subject, body, variables })}
            disabled={!isValid || isPending}
            className="bg-zinc-900 text-white hover:bg-zinc-800"
          >
            {isPending ? "Saving…" : isEdit ? "Save Changes" : "Create Template"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Preview Modal ─────────────────────────────────────────────────────────────

function PreviewModal({
  template,
  onClose,
}: {
  template: EmailTemplate;
  onClose: () => void;
}) {
  const vars = parseVariables(template.variables);
  const [values, setValues] = useState<Record<string, string>>(
    Object.fromEntries(vars.map((v) => [v, ""]))
  );
  const [preview, setPreview] = useState<{ subject: string; body: string } | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  const [renderError, setRenderError] = useState("");

  const render = async () => {
    setIsRendering(true);
    setRenderError("");
    try {
      const { data } = await apiClient.post(
        `/email-templates/${template.id}/render`,
        { variables: values }
      );
      setPreview(data as { subject: string; body: string });
    } catch (e: any) {
      setRenderError(e?.response?.data?.detail || "Render failed.");
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
      <Card className="w-full max-w-2xl shadow-2xl">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-indigo-600" />
                Preview: {template.name}
              </CardTitle>
              <CardDescription>Fill in variables to render the template.</CardDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} id="close-preview-modal">
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4 max-h-[70vh] overflow-y-auto">
          {vars.length > 0 && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {vars.map((v) => (
                <div key={v}>
                  <label className="mb-1 block text-xs font-medium text-zinc-600">
                    <code className="rounded bg-zinc-100 px-1">{`{{${v}}}`}</code>
                  </label>
                  <input
                    id={`var-${v}`}
                    type="text"
                    value={values[v] ?? ""}
                    onChange={(e) =>
                      setValues((prev) => ({ ...prev, [v]: e.target.value }))
                    }
                    placeholder={`Value for ${v}…`}
                    className="h-9 w-full rounded-md border border-zinc-200 px-3 text-sm outline-none focus:border-zinc-400"
                  />
                </div>
              ))}
            </div>
          )}

          {vars.length === 0 && (
            <p className="text-sm text-zinc-500 italic">
              This template has no variables — it will render as-is.
            </p>
          )}

          <Button
            id="render-preview-btn"
            onClick={render}
            disabled={isRendering}
            className="bg-indigo-600 text-white hover:bg-indigo-700"
          >
            {isRendering ? "Rendering…" : "Render Preview"}
          </Button>

          {renderError && (
            <p className="text-sm text-rose-600">{renderError}</p>
          )}

          {preview && (
            <div className="mt-2 space-y-4 rounded-xl border border-zinc-200 p-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-1">
                  Subject
                </p>
                <p className="font-medium text-zinc-900">{preview.subject}</p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-zinc-400 mb-1">
                  Body
                </p>
                <pre className="whitespace-pre-wrap text-sm text-zinc-700 leading-relaxed">
                  {preview.body}
                </pre>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ─── Empty State ───────────────────────────────────────────────────────────────

function EmptyState({ onCreateClick }: { onCreateClick: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-zinc-200 bg-white py-24 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-50 mb-4">
        <Mail className="h-8 w-8 text-indigo-400" />
      </div>
      <h3 className="text-base font-semibold text-zinc-700">No templates yet</h3>
      <p className="mt-1 text-sm text-zinc-400 max-w-xs">
        Create reusable email templates to communicate with candidates efficiently.
      </p>
      <Button
        onClick={onCreateClick}
        className="mt-6 gap-2 bg-zinc-900 text-white hover:bg-zinc-800"
        id="empty-state-create-btn"
      >
        <Plus className="h-4 w-4" /> Create First Template
      </Button>
    </div>
  );
}

// ─── Export ───────────────────────────────────────────────────────────────────

export default function EmailTemplatesPage() {
  return (
    <AuthGuard>
      <EmailTemplatesContent />
    </AuthGuard>
  );
}
