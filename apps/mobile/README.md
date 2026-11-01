# Next-IOT Field (React Native / Expo)

Aplikasi field operator — dashboard, perangkat, alert, workflow trigger, dan scan QR.

## Setup

```bash
npm install -g expo-cli
cd apps/mobile
npm install
npx expo start
```

Scan QR di terminal dengan **Expo Go** di HP (Android/iOS).

## Environment

```bash
# Android emulator → API host
EXPO_PUBLIC_API_URL=http://10.0.2.2:8000
```

## Build preview APK

```bash
eas build --platform android --profile preview
```

## Offline & push

- SQLite queue: `src/features/offline/offlineQueue.ts`
- Background flush: `src/features/offline/syncManager.ts` (60s foreground + NetInfo)
- Push token: `POST /api/v1/users/me/push-token` (requires migration **046**)

## Paket terkait

| Path | Role |
| --- | --- |
| `apps/mobile/field_app` | Flutter field app (legacy BLE/HUD) |
| `apps/mobile` | **Expo React Native** field app (Combo F) |
