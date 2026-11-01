"use client";

import { Download } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  downloadAuditLogsCsv,
  fetchAuditLogs,
  parseResourceTarget,
  type AuditLogItem,
} from "@/lib/api/auditLogs";
import { Card, CardContent } from "@/src/components/ui/card";
import { DataTable, type DataTableColumn } from "@/src/components/ui/DataTable";
import { EmptyState } from "@/src/components/ui/EmptyState";
import { Input } from "@/src/components/ui/input";
import { Label } from "@/src/components/ui/label";

const ACTION_OPTIONS = [
  { value: "all", label: "All actions" },
  { value: "LOGIN", label: "Login" },
  { value: "DEVICE_REGISTER", label: "Create device" },
  { value: "DEVICE_COMMAND", label: "Device command" },
  { value: "RULE_MUTATION", label: "Rule update" },
  { value: "OTA_UPLOAD", label: "OTA upload" },
  { value: "TENANT_UPDATE", label: "Tenant update" },
] as const;

const RESOURCE_OPTIONS = [
  { value: "all", label: "All resources" },
  { value: "device", label: "Device" },
  { value: "rule", label: "Rule" },
  { value: "tenant", label: "Tenant" },
  { value: "firmware", label: "Firmware" },
] as const;

function toIsoStart(date: string): string | undefined {
  if (!date) return undefined;
  return new Date(`${date}T00:00:00`).toISOString();
}

function toIsoEnd(date: string): string | undefined {
  if (!date) return undefined;
  return new Date(`${date}T23:59:59.999`).toISOString();
}

function DetailsRow({ row }: { row: AuditLogItem }) {
  const [open, setOpen] = useState(false);
  const payload = useMemo(
    () =>
      JSON.stringify(
        {
          id: row.id,
          timestamp: row.timestamp,
          actor_id: row.actor_id,
          actor_email: row.actor_email,
          tenant_id: row.tenant_id,
          action: row.action,
          resource_target: row.resource_target,
          ip_address: row.ip_address,
          status: row.status,
        },
        null,
        2,
      ),
    [row],
  );

  return (
    <div className="text-xs">
      <button type="button" className="text-accent-cobalt hover:underline" onClick={() => setOpen((v) => !v)}>
        {open ? "Hide" : "Details"}
      </button>
      {open ? (
        <pre className="mt-2 max-h-48 overflow-auto rounded-lg border border-border bg-muted/30 p-2 text-left text-[11px] text-foreground">
          {payload}
        </pre>
      ) : null}
    </div>
  );
}

export function AuditLogPanel() {
  const [action, setAction] = useState("all");
  const [resourceType, setResourceType] = useState("all");
  const [actor, setActor] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState<AuditLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLogs({
        action,
        actor,
        start_time: toIsoStart(dateFrom),
        end_time: toIsoEnd(dateTo),
        page,
        page_size: 50,
      });
      let items = data.items;
      if (resourceType !== "all") {
        items = items.filter((r) => {
          const { type } = parseResourceTarget(r.resource_target);
          return type.toLowerCase().includes(resourceType.toLowerCase());
        });
      }
      setRows(items);
      setTotal(data.total);
    } catch (e) {
      setRows([]);
      setTotal(0);
      setError(e instanceof Error ? e.message : "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  }, [action, actor, dateFrom, dateTo, page, resourceType]);

  useEffect(() => {
    void load();
  }, [load]);

  const columns = useMemo<Array<DataTableColumn<AuditLogItem>>>(
    () => [
      {
        id: "timestamp",
        header: "Timestamp",
        render: (row) => new Date(row.timestamp).toLocaleString(),
      },
      {
        id: "user",
        header: "User",
        render: (row) => (
          <div>
            <div className="font-medium text-foreground">{row.actor_email}</div>
            <div className="text-xs text-muted-foreground">{row.status}</div>
          </div>
        ),
      },
      {
        id: "action",
        header: "Action",
        render: (row) => row.action,
      },
      {
        id: "resource",
        header: "Resource",
        render: (row) => parseResourceTarget(row.resource_target).type,
      },
      {
        id: "resource_id",
        header: "Resource ID",
        render: (row) => {
          const { id } = parseResourceTarget(row.resource_target);
          return <span className="font-mono text-xs">{id.length > 12 ? `${id.slice(0, 8)}…` : id}</span>;
        },
      },
      {
        id: "ip",
        header: "IP address",
        render: (row) => row.ip_address ?? "—",
      },
      {
        id: "details",
        header: "Details",
        render: (row) => <DetailsRow row={row} />,
      },
    ],
    [],
  );

  const pageCount = Math.max(1, Math.ceil(total / 50));

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="space-y-4 pt-6">
          <div className="flex flex-wrap items-end gap-4">
            <div className="space-y-2">
              <Label htmlFor="audit-from">From</Label>
              <Input id="audit-from" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="audit-to">To</Label>
              <Input id="audit-to" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
            </div>
            <div className="min-w-[180px] space-y-2">
              <Label htmlFor="audit-user">Search user</Label>
              <Input
                id="audit-user"
                placeholder="Email or resource"
                value={actor}
                onChange={(e) => {
                  setActor(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="audit-action">Action</Label>
              <select
                id="audit-action"
                className="h-10 rounded-lg border border-border bg-background px-3 text-sm text-foreground"
                value={action}
                onChange={(e) => {
                  setAction(e.target.value);
                  setPage(1);
                }}
              >
                {ACTION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="audit-resource">Resource</Label>
              <select
                id="audit-resource"
                className="h-10 rounded-lg border border-border bg-background px-3 text-sm text-foreground"
                value={resourceType}
                onChange={(e) => {
                  setResourceType(e.target.value);
                  setPage(1);
                }}
              >
                {RESOURCE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <Button
              variant="outline"
              className="ml-auto"
              disabled={exporting}
              onClick={() => {
                setExporting(true);
                void downloadAuditLogsCsv({
                  action,
                  actor,
                  start_time: toIsoStart(dateFrom),
                  end_time: toIsoEnd(dateTo),
                })
                  .catch((e: unknown) => setError(e instanceof Error ? e.message : "Export failed"))
                  .finally(() => setExporting(false));
              }}
            >
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <Card>
        <CardContent className="p-0 pt-2">
          {!loading && rows.length === 0 ? (
            <div className="p-6">
              <EmptyState
                title="No audit logs"
                description="Audit entries will appear here as users take actions"
              />
            </div>
          ) : (
            <>
              <DataTable columns={columns} rows={rows} rowKey={(r) => r.id} loading={loading} pageSize={50} />
              <div className="flex items-center justify-between border-t border-border px-4 py-3 text-sm text-muted-foreground">
                <span>
                  Page {page} / {pageCount} · {total} total
                </span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={page <= 1 || loading} onClick={() => setPage((p) => p - 1)}>
                    Prev
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= pageCount || loading}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
