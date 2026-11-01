import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useState } from "react";
import { ActivityIndicator, StyleSheet, Text, TextInput, View } from "react-native";

import { BarcodeScanner } from "@/features/scanner/BarcodeScanner";
import { registerDevice } from "@/lib/api/endpoints";
import type { DeviceStackParamList } from "@/navigation/types";

export function BarcodeRegistration() {
  const navigation = useNavigation<NativeStackNavigationProp<DeviceStackParamList>>();
  const [token, setToken] = useState("");
  const [nickname, setNickname] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function submit(deviceToken: string) {
    setLoading(true);
    setMessage(null);
    try {
      const result = await registerDevice({
        device_token: deviceToken,
        device_type: "sensor",
        name: nickname || undefined,
        capabilities: ["telemetry"],
      });
      setMessage("Perangkat terdaftar");
      navigation.navigate("DeviceDetail", { deviceId: result.id });
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Gagal mendaftar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <BarcodeScanner
        onScan={(value) => {
          setToken(value);
          void submit(value);
        }}
      />
      <View style={styles.form}>
        <TextInput style={styles.input} placeholder="Nickname (opsional)" value={nickname} onChangeText={setNickname} />
        <Text style={styles.token} numberOfLines={2}>
          Token: {token || "—"}
        </Text>
        {loading ? <ActivityIndicator /> : null}
        {message ? <Text style={styles.message}>{message}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  form: { padding: 16, backgroundColor: "#fff" },
  input: { borderWidth: 1, borderColor: "#ddd", borderRadius: 8, padding: 10, marginBottom: 8 },
  token: { fontSize: 12, color: "#666" },
  message: { marginTop: 8, color: "#1a3d2e", fontWeight: "600" },
});
