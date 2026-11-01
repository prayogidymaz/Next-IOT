import { create } from "zustand";

import { fetchDevices, type DeviceRecord } from "@/lib/api/endpoints";

type DeviceState = {
  devices: DeviceRecord[];
  selectedDevice: DeviceRecord | null;
  loading: boolean;
  fetch: () => Promise<void>;
  refresh: () => Promise<void>;
  select: (device: DeviceRecord | null) => void;
};

export const useDeviceStore = create<DeviceState>((set) => ({
  devices: [],
  selectedDevice: null,
  loading: false,
  async fetch() {
    set({ loading: true });
    try {
      const devices = await fetchDevices();
      set({ devices });
    } finally {
      set({ loading: false });
    }
  },
  async refresh() {
    await useDeviceStore.getState().fetch();
  },
  select(device) {
    set({ selectedDevice: device });
  },
}));
