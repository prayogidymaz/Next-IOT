import { Card } from "@next-iot/ui";
import Link from "next/link";

import { APP_URL, PRICING_PLANS } from "@/lib/site";

type PricingTableProps = {
  compact?: boolean;
};

export function PricingTable({ compact = false }: PricingTableProps) {
  return (
    <div className={`grid gap-6 ${compact ? "md:grid-cols-2 lg:grid-cols-4" : "md:grid-cols-2 lg:grid-cols-4"}`}>
      {PRICING_PLANS.map((plan) => (
        <Card
          key={plan.code}
          className={`flex flex-col p-6 ${plan.highlight ? "ring-2 ring-sky-500" : ""}`}
          shadow="sm"
        >
          <p className="text-sm font-medium text-slate-500">{plan.name}</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">
            {plan.price}
            <span className="text-base font-normal text-slate-500">{plan.period}</span>
          </p>
          <p className="mt-2 text-sm text-slate-600">{plan.devices}</p>
          <Link
            href={`${APP_URL}/register`}
            className={`mt-6 block rounded-md py-2.5 text-center text-sm font-semibold ${
              plan.highlight ? "bg-sky-600 text-white hover:bg-sky-700" : "border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {plan.code === "enterprise" ? "Contact sales" : "Start trial"}
          </Link>
        </Card>
      ))}
    </div>
  );
}
