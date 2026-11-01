import { StyleSheet, Text, View } from "react-native";

export function AddDeviceScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.hint}>Arahkan kamera ke QR code perangkat (scanner di tab Devices → FAB)</Text>
      <View style={styles.placeholder}>
        <Text>Modul kamera akan aktif setelah konfigurasi Expo Camera.</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  hint: { padding: 16, textAlign: "center", color: "#444" },
  placeholder: { flex: 1, alignItems: "center", justifyContent: "center", padding: 24 },
});
