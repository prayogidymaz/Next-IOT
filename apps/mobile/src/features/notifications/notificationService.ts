import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

import { registerPushToken } from "@/lib/api/endpoints";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function initNotificationService(onNavigateAlert: (alertId: string) => void): Promise<void> {
  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;
  if (existing !== "granted") {
    const requested = await Notifications.requestPermissionsAsync();
    finalStatus = requested.status;
  }
  if (finalStatus !== "granted") {
    return;
  }

  const expoToken = await Notifications.getExpoPushTokenAsync();
  const platform = Platform.OS === "ios" ? "ios" : "android";
  await registerPushToken(expoToken.data, platform);

  Notifications.addNotificationReceivedListener(() => {
    /* foreground — OS banner via handler */
  });

  Notifications.addNotificationResponseReceivedListener((response) => {
    const alertId = response.notification.request.content.data?.alertId;
    if (typeof alertId === "string") {
      onNavigateAlert(alertId);
    }
  });
}
