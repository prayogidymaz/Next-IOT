import { useState } from "react";
import { Pressable, StyleSheet, Switch, Text, View } from "react-native";

import { NotificationPreferences } from "@/features/notifications/NotificationPreferences";
import { useAuthStore } from "@/stores/authStore";
import { useOfflineStore } from "@/stores/offlineStore";

export function ProfileScreen() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const lastSyncAt = useOfflineStore((s) => s.lastSyncAt);
  const pendingActions = useOfflineStore((s) => s.pendingActions);
  const isOnline = useOfflineStore((s) => s.isOnline);
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profil</Text>
      <Text style={styles.row}>Email: {user?.email ?? "—"}</Text>
      <Text style={styles.row}>Tenant: {user?.tenant_id ?? "—"}</Text>
      <Text style={styles.row}>Role: {user?.role ?? "—"}</Text>
      <Text style={styles.syncMeta}>
        {isOnline ? "Online" : "Offline"} · pending {pendingActions}
        {lastSyncAt ? ` · sync ${new Date(lastSyncAt).toLocaleTimeString()}` : ""}
      </Text>
      <NotificationPreferences />
      <View style={styles.setting}>
        <Text>Notifikasi</Text>
        <Switch value={notifications} onValueChange={setNotifications} />
      </View>
      <View style={styles.setting}>
        <Text>Dark mode</Text>
        <Switch value={darkMode} onValueChange={setDarkMode} />
      </View>
      <Pressable style={styles.logout} onPress={() => void logout()}>
        <Text style={styles.logoutText}>Logout</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, paddingTop: 48 },
  title: { fontSize: 22, fontWeight: "700", marginBottom: 16 },
  row: { marginBottom: 8, color: "#333" },
  syncMeta: { fontSize: 12, color: "#666", marginBottom: 8 },
  setting: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 16 },
  logout: { marginTop: 32, backgroundColor: "#b91c1c", padding: 14, borderRadius: 10, alignItems: "center" },
  logoutText: { color: "#fff", fontWeight: "600" },
});
