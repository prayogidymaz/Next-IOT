import type { ReactNode } from "react";

type Props = {
  action?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
};

export function HqPageShell({ action, actions, children }: Props) {
  const headerAction = action ?? actions;
  return (
    <div className="container mx-auto space-y-6 px-4 py-6 md:px-6 lg:px-8">
      {headerAction ? <div className="flex justify-end">{headerAction}</div> : null}
      {children}
    </div>
  );
}
