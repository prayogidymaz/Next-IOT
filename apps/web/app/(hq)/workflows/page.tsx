import Link from "next/link";

export default function WorkflowsListPage() {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-stone-900">Workflows</h1>
        <Link
          href="/workflows/new"
          className="rounded-lg bg-stone-900 px-4 py-2 text-sm text-white hover:bg-stone-800"
        >
          New workflow
        </Link>
      </div>
      <p className="text-sm text-stone-600">
        Visual mesh workflows with AI copilot. Open an existing workflow or create a blank canvas.
      </p>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          href="/workflows/new"
          className="flex h-32 flex-col justify-end rounded-xl border border-dashed border-stone-300 bg-stone-50 p-4 hover:border-stone-400"
        >
          <span className="text-sm font-medium text-stone-800">Blank canvas</span>
          <span className="text-xs text-stone-500">Drag triggers, conditions, actions</span>
        </Link>
      </div>
    </div>
  );
}
