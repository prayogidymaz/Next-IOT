import { createNativeStackNavigator } from "@react-navigation/native-stack";

import { AddDeviceScreen } from "@/screens/devices/AddDeviceScreen";
import { DeviceDetailScreen } from "@/screens/devices/DeviceDetailScreen";
import { DeviceListScreen } from "@/screens/devices/DeviceListScreen";

import type { DeviceStackParamList } from "./types";

const Stack = createNativeStackNavigator<DeviceStackParamList>();

export function DeviceStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="DeviceList" component={DeviceListScreen} options={{ title: "Perangkat" }} />
      <Stack.Screen name="DeviceDetail" component={DeviceDetailScreen} options={{ title: "Detail" }} />
      <Stack.Screen name="AddDevice" component={AddDeviceScreen} options={{ title: "Scan QR" }} />
    </Stack.Navigator>
  );
}
