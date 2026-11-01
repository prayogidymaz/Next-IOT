import { useState } from "react";
import { StyleSheet, Switch, Text, View } from "react-native";

const CATEGORIES = ["pest", "irrigation", "sensor_offline", "yield"] as const;

export function NotificationPreferences() {
  const [enabled, setEnabled] = useState<Record<string, boolean>>({
    pest: true,
    irrigation: true,
    sensor_offline: true,
    yield: true,
  });
  const [quietHours, setQuietHours] = useState(true);
  const [minPriority, setMinPriority] = useState<"low" | "medium" | "high">("medium");

  return (
    <View style={styles.box}>
      <Text style={styles.title}>Preferensi notifikasi</Text>
      {CATEGORIES.map((cat) => (
        <View key={cat} style={styles.row}>
          <Text>{cat}</Text>
          <Switch value={enabled[cat]} onValueChange={(v) => setEnabled((s) => ({ ...s, [cat]: v }))} />
        </View>
      ))}
      <View style={styles.row}>
        <Text>Quiet hours (22:00–06:00)</Text>
        <Switch value={quietHours} onValueChange={setQuietHours} />
      </View>
      <Text style={styles.meta}>Priority minimum: {minPriority}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: { marginTop: 16, padding: 12, borderRadius: 12, backgroundColor: "#fff", borderWidth: 1, borderColor: "#e5e7eb" },
  title: { fontWeight: "600", marginBottom: 8 },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 6 },
  meta: { marginTop: 8, fontSize: 12, color: "#666" },
});
