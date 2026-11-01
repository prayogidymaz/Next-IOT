import { useState } from "react";
import { Pressable, StyleSheet, Switch, Text, View } from "react-native";

import { useAuthStore } from "@/stores/authStore";

export function ProfileScreen() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profil</Text>
      <Text style={styles.row}>Email: {user?.email ?? "—"}</Text>
      <Text style={styles.row}>Tenant: {user?.tenant_id ?? "—"}</Text>
      <Text style={styles.row}>Role: {user?.role ?? "—"}</Text>
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
  setting: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 16 },
  logout: { marginTop: 32, backgroundColor: "#b91c1c", padding: 14, borderRadius: 10, alignItems: "center" },
  logoutText: { color: "#fff", fontWeight: "600" },
});
