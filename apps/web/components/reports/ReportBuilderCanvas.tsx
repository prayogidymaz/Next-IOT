"use client";

import { DndContext, type DragEndEvent, useDraggable, useDroppable } from "@dnd-kit/core";
import { useState } from "react";

type Widget = { id: string; type: string; title: string };

const PALETTE: Widget[] = [
  { id: "chart", type: "chart", title: "Chart" },
  { id: "table", type: "table", title: "Table" },
  { id: "text", type: "text", title: "Text" },
  { id: "kpi", type: "kpi", title: "KPI" },
  { id: "image", type: "image", title: "Image" },
];

function PaletteItem({ widget }: { widget: Widget }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({ id: `palette-${widget.type}`, data: widget });
  const style = transform ? { transform: `translate(${transform.x}px, ${transform.y}px)` } : undefined;
  return (
    <button
      type="button"
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="w-full rounded-lg border border-border bg-card px-3 py-2 text-left text-sm text-foreground"
    >
      {widget.title}
    </button>
  );
}

function CanvasDrop({ widgets, selectedId, onSelect }: { widgets: Widget[]; selectedId: string | null; onSelect: (id: string) => void }) {
  const { setNodeRef, isOver } = useDroppable({ id: "canvas" });
  return (
    <div ref={setNodeRef} className={`min-h-[320px] rounded-xl border border-dashed p-4 ${isOver ? "border-primary bg-muted/30" : "border-border"}`}>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {widgets.map((w) => (
          <button
            key={w.id}
            type="button"
            onClick={() => onSelect(w.id)}
            className={`rounded-lg border p-4 text-left text-sm ${selectedId === w.id ? "border-primary bg-muted/40" : "border-border bg-card"}`}
          >
            {w.type.toUpperCase()} — {w.title}
          </button>
        ))}
      </div>
    </div>
  );
}

export function ReportBuilderCanvas({ onChange }: { onChange: (sections: Widget[]) => void }) {
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = widgets.find((w) => w.id === selectedId) ?? null;

  function onDragEnd(event: DragEndEvent) {
    const data = event.active.data.current as Widget | undefined;
    if (event.over?.id === "canvas" && data) {
      const next = [...widgets, { ...data, id: `${data.type}-${Date.now()}` }];
      setWidgets(next);
      onChange(next);
    }
  }

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="grid gap-4 lg:grid-cols-[220px_1fr_240px]">
        <aside className="space-y-2 rounded-xl border border-border bg-card p-3">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Widgets</p>
          {PALETTE.map((w) => (
            <PaletteItem key={w.id} widget={w} />
          ))}
        </aside>
        <CanvasDrop widgets={widgets} selectedId={selectedId} onSelect={setSelectedId} />
        <aside className="rounded-xl border border-border bg-card p-3 text-sm">
          <p className="text-xs font-semibold uppercase text-muted-foreground">Properties</p>
          {selected ? (
            <div className="mt-2 space-y-2">
              <label className="block text-xs text-muted-foreground">
                Title
                <input
                  className="mt-1 w-full rounded border border-border bg-background px-2 py-1"
                  value={selected.title}
                  onChange={(e) => {
                    const next = widgets.map((w) => (w.id === selected.id ? { ...w, title: e.target.value } : w));
                    setWidgets(next);
                    onChange(next);
                  }}
                />
              </label>
              <p className="text-muted-foreground">Type: {selected.type}</p>
            </div>
          ) : (
            <p className="mt-2 text-muted-foreground">Select a widget</p>
          )}
        </aside>
      </div>
    </DndContext>
  );
}
