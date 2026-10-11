import { BillingPanel } from "@/components/billing/BillingPanel";
import { HqPageContent } from "@/components/hq/HqPageContent";

export default function BillingPage() {
  return (
    <HqPageContent description="Subscription, usage limits, invoices, and payment methods.">
      <BillingPanel />
    </HqPageContent>
  );
}
