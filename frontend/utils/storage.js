import { Platform } from 'react-native';

const isWeb = Platform.OS === 'web';

// Lazy load SecureStore only on native platforms
let SecureStore = null;
if (!isWeb) {
  SecureStore = require('expo-secure-store');
}

export const storage = {
  async setItem(key, value) {
    if (isWeb) {
      localStorage.setItem(key, value);
    } else {
      await SecureStore.setItemAsync(key, value);
    }
  },

  async getItem(key) {
    if (isWeb) {
      return localStorage.getItem(key);
    } else {
      return await SecureStore.getItemAsync(key);
    }
  },

  async deleteItem(key) {
    if (isWeb) {
      localStorage.removeItem(key);
    } else {
      await SecureStore.deleteItemAsync(key);
    }
  },
};
