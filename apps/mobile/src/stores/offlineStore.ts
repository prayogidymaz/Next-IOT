import { create } from "zustand";

import { peekOfflineActions } from "@/features/offline/offlineQueue";

type OfflineState = {
  isOnline: boolean;
  pendingActions: number;
  lastSyncAt: number | null;
  setOnline: (online: boolean) => void;
  setLastSyncAt: (ts: number) => void;
  refreshPendingCount: () => Promise<void>;
};

export const useOfflineStore = create<OfflineState>((set) => ({
  isOnline: true,
  pendingActions: 0,
  lastSyncAt: null,
  setOnline(online) {
    set({ isOnline: online });
  },
  setLastSyncAt(ts) {
    set({ lastSyncAt: ts });
  },
  async refreshPendingCount() {
    const items = await peekOfflineActions(500);
    set({ pendingActions: items.length });
  },
}));
