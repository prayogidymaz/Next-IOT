import { useCallback, useEffect, useState } from "react";
import { RefreshControl, ScrollView, StyleSheet, Text, View } from "react-native";

import { useAlertStore } from "@/stores/alertStore";
import { useAuthStore } from "@/stores/authStore";
import { useDeviceStore } from "@/stores/deviceStore";

function KpiCard({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.kpi}>
      <Text style={styles.kpiValue}>{value}</Text>
      <Text style={styles.kpiLabel}>{label}</Text>
    </View>
  );
}

export function DashboardScreen() {
  const user = useAuthStore((s) => s.user);
  const devices = useDeviceStore((s) => s.devices);
  const fetchDevices = useDeviceStore((s) => s.fetch);
  const alerts = useAlertStore((s) => s.alerts);
  const fetchAlerts = useAlertStore((s) => s.fetch);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    await Promise.all([fetchDevices(), fetchAlerts()]);
  }, [fetchAlerts, fetchDevices]);

  useEffect(() => {
    void load();
  }, [load]);

  const online = devices.filter((d) => d.online).length;

  return (
    <ScrollView
      contentContainerStyle={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => {
            setRefreshing(true);
            void load().finally(() => setRefreshing(false));
          }}
        />
      }
    >
      <Text style={styles.greeting}>Halo, {user?.email ?? "operator"}</Text>
      <Text style={styles.sub}>Tenant {user?.tenant_id?.slice(0, 8) ?? "—"}</Text>
      <View style={styles.kpiRow}>
        <KpiCard label="Devices online" value={`${online}/${devices.length}`} />
        <KpiCard label="Active alerts" value={String(alerts.length)} />
      </View>
      <View style={styles.kpiRow}>
        <KpiCard label="Workflows fired" value="—" />
        <KpiCard label="Savings IDR" value="—" />
      </View>
      <Text style={styles.section}>Recent alerts</Text>
      {alerts.slice(0, 5).map((a) => (
        <View key={a.id} style={styles.alertRow}>
          <Text style={styles.alertTitle}>{a.title}</Text>
          <Text style={styles.alertMeta}>{a.severity}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16, paddingTop: 48 },
  greeting: { fontSize: 22, fontWeight: "700" },
  sub: { color: "#666", marginBottom: 16 },
  kpiRow: { flexDirection: "row", gap: 12, marginBottom: 12 },
  kpi: { flex: 1, backgroundColor: "#fff", borderRadius: 12, padding: 12, borderWidth: 1, borderColor: "#e5e7eb" },
  kpiValue: { fontSize: 20, fontWeight: "700" },
  kpiLabel: { fontSize: 12, color: "#666", marginTop: 4 },
  section: { marginTop: 20, fontWeight: "600", marginBottom: 8 },
  alertRow: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#eee" },
  alertTitle: { fontWeight: "500" },
  alertMeta: { fontSize: 12, color: "#888" },
});
