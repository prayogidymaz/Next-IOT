import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { initNotificationService } from "./src/features/notifications/notificationService";
import { initOfflineSync } from "./src/features/offline/syncManager";
import { RootNavigator } from "./src/navigation/RootNavigator";

const queryClient = new QueryClient();

function AppBootstrap() {
  useEffect(() => {
    void initNotificationService(() => {
      /* deep link to alerts tab — navigation ref can be added later */
    });
    return initOfflineSync();
  }, []);

  return <RootNavigator />;
}

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <QueryClientProvider client={queryClient}>
          <AppBootstrap />
          <StatusBar style="auto" />
        </QueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
