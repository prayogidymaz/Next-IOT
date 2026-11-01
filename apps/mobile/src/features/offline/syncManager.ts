import NetInfo from "@react-native-community/netinfo";

import { apiFetch } from "@/lib/api/client";
import { enqueueOfflineAction, peekOfflineActions, removeOfflineAction } from "@/features/offline/offlineQueue";
import { useOfflineStore } from "@/stores/offlineStore";

const FLUSH_INTERVAL_MS = 60_000;

let interval: ReturnType<typeof setInterval> | null = null;

async function flushQueue(): Promise<void> {
  const items = await peekOfflineActions(10);
  for (const item of items) {
    try {
      const payload = JSON.parse(item.payload_json) as { path?: string; method?: string; body?: string };
      if (!payload.path) {
        await removeOfflineAction(item.id);
        continue;
      }
      const res = await apiFetch(payload.path, {
        method: payload.method ?? "POST",
        body: payload.body,
      });
      if (res.ok) {
        await removeOfflineAction(item.id);
      }
    } catch {
      break;
    }
  }
  useOfflineStore.getState().setLastSyncAt(Date.now());
  useOfflineStore.getState().refreshPendingCount();
}

export function initOfflineSync(): () => void {
  const unsubNet = NetInfo.addEventListener((state) => {
    const online = Boolean(state.isConnected && state.isInternetReachable !== false);
    useOfflineStore.getState().setOnline(online);
    if (online) {
      void flushQueue();
    }
  });

  interval = setInterval(() => {
    if (useOfflineStore.getState().isOnline) {
      void flushQueue();
    }
  }, FLUSH_INTERVAL_MS);

  return () => {
    unsubNet();
    if (interval) clearInterval(interval);
  };
}

export async function queueOrExecute(path: string, method: string, body?: string): Promise<void> {
  if (!useOfflineStore.getState().isOnline) {
    await enqueueOfflineAction("api", { path, method, body });
    await useOfflineStore.getState().refreshPendingCount();
    return;
  }
  await apiFetch(path, { method, body });
}
