import { StyleSheet, Text, View } from "react-native";

export function RegisterTenantScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Register tenant</Text>
      <Text style={styles.body}>Gunakan portal web Next-IOT untuk registrasi tenant baru, lalu login di aplikasi field.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: "center" },
  title: { fontSize: 20, fontWeight: "700", marginBottom: 12 },
  body: { fontSize: 15, lineHeight: 22, color: "#444" },
});
