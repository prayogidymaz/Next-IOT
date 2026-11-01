import { useEffect } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

import { useAlertStore } from "@/stores/alertStore";

function severityColor(severity: string): string {
  if (severity === "critical" || severity === "high") return "#fecaca";
  if (severity === "medium") return "#fed7aa";
  return "#fef9c3";
}

export function AlertFeedScreen() {
  const { alerts, fetch, markAsRead } = useAlertStore();

  useEffect(() => {
    void fetch();
  }, [fetch]);

  return (
    <FlatList
      style={styles.list}
      contentContainerStyle={{ padding: 16, paddingTop: 48 }}
      data={alerts}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <Pressable style={[styles.card, { backgroundColor: severityColor(item.severity) }]} onPress={() => markAsRead(item.id)}>
          <Text style={styles.title}>{item.title}</Text>
          <Text style={styles.body}>{item.message ?? "—"}</Text>
          <Text style={styles.meta}>{item.severity} · tap to acknowledge</Text>
        </Pressable>
      )}
      ListEmptyComponent={<Text style={styles.empty}>Tidak ada alert aktif</Text>}
    />
  );
}

const styles = StyleSheet.create({
  list: { flex: 1 },
  card: { borderRadius: 12, padding: 14, marginBottom: 10 },
  title: { fontWeight: "700" },
  body: { marginTop: 4, color: "#333" },
  meta: { marginTop: 8, fontSize: 11, color: "#555" },
  empty: { textAlign: "center", color: "#888", marginTop: 40 },
});
