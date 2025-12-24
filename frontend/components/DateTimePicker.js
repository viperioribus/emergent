// Simple polyfill for DateTimePicker on web
import { Platform } from 'react-native';

let RealDateTimePicker = null;

if (Platform.OS !== 'web') {
  RealDateTimePicker = require('@react-native-community/datetimepicker').default;
}

export default RealDateTimePicker || (() => null);
