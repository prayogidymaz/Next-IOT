import { StyleSheet, View } from "react-native";

import { BarcodeRegistration } from "@/features/scanner/BarcodeRegistration";

export function AddDeviceScreen() {
  return (
    <View style={styles.container}>
      <BarcodeRegistration />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
});
