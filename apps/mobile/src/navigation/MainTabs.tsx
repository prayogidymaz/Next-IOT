import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";

import { AlertFeedScreen } from "@/screens/alerts/AlertFeedScreen";
import { DashboardScreen } from "@/screens/dashboard/DashboardScreen";
import { ProfileScreen } from "@/screens/profile/ProfileScreen";
import { WorkflowListScreen } from "@/screens/workflows/WorkflowListScreen";
import { useAlertStore } from "@/stores/alertStore";

import { DeviceStack } from "./DeviceStack";
import type { MainTabParamList } from "./types";

const Tab = createBottomTabNavigator<MainTabParamList>();

export function MainTabs() {
  const unread = useAlertStore((s) => s.unreadCount);
  return (
    <Tab.Navigator screenOptions={{ headerShown: false }}>
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: "Home" }} />
      <Tab.Screen name="Devices" component={DeviceStack} options={{ title: "Devices" }} />
      <Tab.Screen
        name="Alerts"
        component={AlertFeedScreen}
        options={{ title: "Alerts", tabBarBadge: unread > 0 ? unread : undefined }}
      />
      <Tab.Screen name="Workflows" component={WorkflowListScreen} options={{ title: "Workflows" }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: "Profile" }} />
    </Tab.Navigator>
  );
}
