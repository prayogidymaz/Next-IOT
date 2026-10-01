import { HqAppShell } from "@/components/hq/HqAppShell";

export default function HqRouteGroupLayout({ children }: { children: React.ReactNode }) {
  return <HqAppShell>{children}</HqAppShell>;
}
