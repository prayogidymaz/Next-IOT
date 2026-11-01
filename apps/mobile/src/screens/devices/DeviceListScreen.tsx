import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useEffect, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

import type { DeviceStackParamList } from "@/navigation/types";
import { useDeviceStore } from "@/stores/deviceStore";

export function DeviceListScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<DeviceStackParamList>>();
  const { devices, fetch, select } = useDeviceStore();
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    void fetch();
  }, [fetch]);

  const filtered = filter === "all" ? devices : devices.filter((d) => d.device_type === filter);

  return (
    <View style={styles.container}>
      <View style={styles.filters}>
        {["all", "sensor", "actuator", "camera"].map((f) => (
          <Pressable key={f} style={[styles.chip, filter === f && styles.chipActive]} onPress={() => setFilter(f)}>
            <Text>{f}</Text>
          </Pressable>
        ))}
      </View>
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() => {
              select(item);
              navigation.navigate("DeviceDetail", { deviceId: item.id });
            }}
          >
            <Text style={styles.name}>{item.name}</Text>
            <Text style={styles.meta}>
              {item.device_type} · {item.online ? "online" : "offline"}
            </Text>
          </Pressable>
        )}
      />
      <Pressable style={styles.fab} onPress={() => navigation.navigate("AddDevice")}>
        <Text style={styles.fabText}>+ Add Device</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  filters: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 12 },
  chip: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 999, backgroundColor: "#eee" },
  chipActive: { backgroundColor: "#cdebd8" },
  card: { padding: 14, borderRadius: 10, backgroundColor: "#fff", marginBottom: 8, borderWidth: 1, borderColor: "#e5e7eb" },
  name: { fontWeight: "600" },
  meta: { color: "#666", marginTop: 4, fontSize: 12 },
  fab: { position: "absolute", right: 16, bottom: 16, backgroundColor: "#1a3d2e", paddingHorizontal: 16, paddingVertical: 12, borderRadius: 999 },
  fabText: { color: "#fff", fontWeight: "600" },
});
