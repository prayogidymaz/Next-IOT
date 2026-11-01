export type AuthStackParamList = {
  Login: undefined;
  RegisterTenant: undefined;
};

export type DeviceStackParamList = {
  DeviceList: undefined;
  DeviceDetail: { deviceId: string };
  AddDevice: undefined;
};

export type MainTabParamList = {
  Dashboard: undefined;
  Devices: undefined;
  Alerts: undefined;
  Workflows: undefined;
  Profile: undefined;
};
