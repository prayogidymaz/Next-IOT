import { CameraView, useCameraPermissions } from "expo-camera";
import * as Haptics from "expo-haptics";
import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

type Props = {
  onScan: (value: string) => void;
};

export function BarcodeScanner({ onScan }: Props) {
  const [permission, requestPermission] = useCameraPermissions();
  const [locked, setLocked] = useState(false);

  if (!permission) {
    return <Text style={styles.center}>Memuat kamera…</Text>;
  }

  if (!permission.granted) {
    return (
      <View style={styles.centerBox}>
        <Text style={styles.center}>Izin kamera diperlukan untuk scan QR</Text>
        <Pressable style={styles.button} onPress={() => void requestPermission()}>
          <Text style={styles.buttonText}>Izinkan kamera</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        barcodeScannerSettings={{
          barcodeTypes: ["qr", "code128", "ean13"],
        }}
        onBarcodeScanned={(event) => {
          if (locked) return;
          setLocked(true);
          void Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
          onScan(event.data);
          setTimeout(() => setLocked(false), 1500);
        }}
      />
      <View style={styles.overlay}>
        <Text style={styles.hint}>Scan QR code device</Text>
        <View style={styles.crosshair} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, minHeight: 280 },
  overlay: { flex: 1, alignItems: "center", justifyContent: "center" },
  crosshair: { width: 180, height: 180, borderWidth: 2, borderColor: "#fff", borderRadius: 12 },
  hint: { position: "absolute", top: 24, color: "#fff", fontWeight: "600", textShadowColor: "#000", textShadowRadius: 4 },
  center: { textAlign: "center", padding: 16 },
  centerBox: { flex: 1, justifyContent: "center", padding: 24 },
  button: { marginTop: 12, alignSelf: "center", backgroundColor: "#1a3d2e", paddingHorizontal: 16, paddingVertical: 10, borderRadius: 8 },
  buttonText: { color: "#fff", fontWeight: "600" },
});
