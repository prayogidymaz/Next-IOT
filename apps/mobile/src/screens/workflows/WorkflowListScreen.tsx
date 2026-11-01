import { useEffect, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

import { fetchWorkflows, triggerWorkflow, type WorkflowRecord } from "@/lib/api/endpoints";

export function WorkflowListScreen() {
  const [items, setItems] = useState<WorkflowRecord[]>([]);
  const [loadingId, setLoadingId] = useState<string | null>(null);

  useEffect(() => {
    void fetchWorkflows().then(setItems).catch(() => setItems([]));
  }, []);

  async function fire(id: string) {
    setLoadingId(id);
    try {
      await triggerWorkflow(id);
    } finally {
      setLoadingId(null);
    }
  }

  return (
    <FlatList
      contentContainerStyle={{ padding: 16, paddingTop: 48 }}
      data={items}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.meta}>{item.enabled ? "Active" : "Disabled"}</Text>
          <Pressable style={styles.button} onPress={() => void fire(item.id)} disabled={loadingId === item.id}>
            <Text style={styles.buttonText}>{loadingId === item.id ? "Firing…" : "Fire Now"}</Text>
          </Pressable>
        </View>
      )}
      ListEmptyComponent={<Text style={styles.empty}>Belum ada workflow</Text>}
    />
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: "#fff", borderRadius: 12, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: "#e5e7eb" },
  name: { fontWeight: "600" },
  meta: { color: "#666", fontSize: 12, marginTop: 4 },
  button: { marginTop: 10, alignSelf: "flex-start", backgroundColor: "#1a3d2e", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8 },
  buttonText: { color: "#fff", fontWeight: "600" },
  empty: { textAlign: "center", color: "#888" },
});
