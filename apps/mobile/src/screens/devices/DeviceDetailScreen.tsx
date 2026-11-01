import { RouteProp, useRoute } from "@react-navigation/native";
import { useEffect, useState } from "react";
import { StyleSheet, Switch, Text, View } from "react-native";

import type { DeviceStackParamList } from "@/navigation/types";
import { useDeviceStore } from "@/stores/deviceStore";

export function DeviceDetailScreen() {
  const route = useRoute<RouteProp<DeviceStackParamList, "DeviceDetail">>();
  const devices = useDeviceStore((s) => s.devices);
  const device = devices.find((d) => d.id === route.params.deviceId);
  const [actuatorOn, setActuatorOn] = useState(false);

  useEffect(() => {
    void useDeviceStore.getState().fetch();
  }, []);

  if (!device) {
    return (
      <View style={styles.container}>
        <Text>Memuat perangkat…</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{device.name}</Text>
      <Text style={styles.meta}>Type: {device.device_type}</Text>
      <Text style={styles.meta}>Status: {device.online ? "Online" : "Offline"}</Text>
      <View style={styles.chartPlaceholder}>
        <Text style={styles.chartText}>Sensor history chart (victory-native / Recharts RN)</Text>
      </View>
      <View style={styles.row}>
        <Text>Actuator</Text>
        <Switch value={actuatorOn} onValueChange={setActuatorOn} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: "700" },
  meta: { color: "#666", marginTop: 4 },
  chartPlaceholder: { marginTop: 24, height: 160, borderRadius: 12, backgroundColor: "#f3f4f6", alignItems: "center", justifyContent: "center" },
  chartText: { color: "#888", fontSize: 12, paddingHorizontal: 16, textAlign: "center" },
  row: { marginTop: 24, flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
});
