"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

export default function SiteMembersPage() {
  const params = useParams<{ id: string }>();
  return (
    <div className="container mx-auto space-y-4 px-4 py-6">
      <Link href={`/sites/${params.id}`} className="text-sm text-muted-foreground hover:text-foreground">
        ← Site
      </Link>
      <p className="text-sm text-muted-foreground">
        Site-level members: use <code className="text-foreground">POST /api/v1/sites/{params.id}/members</code> with user_id and role
        (owner/manager/viewer). UI form mirrors tenant invite — wire user picker in a follow-up.
      </p>
    </div>
  );
}
