import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="index" />
      <Stack.Screen name="main" />
      <Stack.Screen name="settings" />
      <Stack.Screen name="inform2" />
      <Stack.Screen name="inform4" />
    </Stack>
  );
}
