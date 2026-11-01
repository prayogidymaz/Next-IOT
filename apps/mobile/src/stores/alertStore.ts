import { create } from "zustand";

import { fetchAlarms, type AlarmRecord } from "@/lib/api/endpoints";

type AlertState = {
  alerts: AlarmRecord[];
  unreadCount: number;
  fetch: () => Promise<void>;
  markAsRead: (id: string) => void;
  clearAll: () => void;
};

export const useAlertStore = create<AlertState>((set, get) => ({
  alerts: [],
  unreadCount: 0,
  async fetch() {
    const alerts = await fetchAlarms("active");
    set({ alerts, unreadCount: alerts.length });
  },
  markAsRead(id) {
    const alerts = get().alerts.filter((a) => a.id !== id);
    set({ alerts, unreadCount: alerts.length });
  },
  clearAll() {
    set({ alerts: [], unreadCount: 0 });
  },
}));
