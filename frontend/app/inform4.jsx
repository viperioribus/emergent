import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { storage } from '../utils/storage';
import { Ionicons } from '@expo/vector-icons';
import DateTimePicker from '@react-native-community/datetimepicker';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function Inform4Screen() {
  const router = useRouter();
  const [beachName, setBeachName] = useState('');
  const [date, setDate] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [hour, setHour] = useState('');
  const [minute, setMinute] = useState('');
  const [windSpeed, setWindSpeed] = useState('');
  const [temperature, setTemperature] = useState('');
  const [waveHeight, setWaveHeight] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBeachName();
  }, []);

  const loadBeachName = async () => {
    try {
      const savedBeach = await storage.getItem('selected_beach');
      const savedBeachPost = await storage.getItem('selected_beach_post');
      if (savedBeach && savedBeachPost) {
        const beach = JSON.parse(savedBeach);
        const post = JSON.parse(savedBeachPost);
        setBeachName(`${beach.name} - ${post.name}`);
      } else {
        Alert.alert(
          'No Beach Selected',
          'Please select a beach and beach post in Settings first',
          [
            { text: 'Go to Settings', onPress: () => router.push('/settings') },
            { text: 'Cancel', onPress: () => router.back() },
          ]
        );
      }
    } catch (error) {
      console.error('Error loading beach name:', error);
    }
  };

  const handleSubmit = async () => {
    // Validation
    if (!beachName || !hour || !minute || !windSpeed || !temperature || !waveHeight) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    const hourNum = parseInt(hour);
    const minuteNum = parseInt(minute);
    const windSpeedNum = parseFloat(windSpeed);
    const temperatureNum = parseFloat(temperature);
    const waveHeightNum = parseFloat(waveHeight);

    if (isNaN(hourNum) || hourNum < 0 || hourNum > 23) {
      Alert.alert('Error', 'Hour must be between 0 and 23');
      return;
    }

    if (isNaN(minuteNum) || minuteNum < 0 || minuteNum > 59) {
      Alert.alert('Error', 'Minute must be between 0 and 59');
      return;
    }

    if (isNaN(windSpeedNum) || windSpeedNum < 0) {
      Alert.alert('Error', 'Please enter a valid wind speed');
      return;
    }

    if (isNaN(temperatureNum)) {
      Alert.alert('Error', 'Please enter a valid temperature');
      return;
    }

    if (isNaN(waveHeightNum) || waveHeightNum < 0) {
      Alert.alert('Error', 'Please enter a valid wave height');
      return;
    }

    setLoading(true);
    try {
      const token = await storage.getItem('auth_token');
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/inform4`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          date: date.toISOString().split('T')[0],
          beach_name: beachName,
          hour: hourNum,
          minute: minuteNum,
          wind_speed: windSpeedNum,
          temperature: temperatureNum,
          wave_height: waveHeightNum,
        }),
      });

      if (response.ok) {
        Alert.alert('Success', 'Inform 4 submitted successfully', [
          { text: 'OK', onPress: () => router.back() },
        ]);
      } else {
        const data = await response.json();
        Alert.alert('Error', data.detail || 'Failed to submit inform');
      }
    } catch (error) {
      console.error('Submit error:', error);
      Alert.alert('Error', 'Unable to connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Inform 4</Text>
        <View style={{ width: 24 }} />
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <ScrollView style={styles.content} keyboardShouldPersistTaps="handled">
          {/* Date */}
          <View style={styles.field}>
            <Text style={styles.label}>Date *</Text>
            <TouchableOpacity
              style={styles.dateButton}
              onPress={() => setShowDatePicker(true)}
            >
              <Text style={styles.dateText}>{date.toLocaleDateString()}</Text>
              <Ionicons name="calendar-outline" size={20} color="#007AFF" />
            </TouchableOpacity>
            {showDatePicker && (
              <DateTimePicker
                value={date}
                mode="date"
                display="default"
                onChange={(event, selectedDate) => {
                  setShowDatePicker(false);
                  if (selectedDate) {
                    setDate(selectedDate);
                  }
                }}
              />
            )}
          </View>

          {/* Beach Name */}
          <View style={styles.field}>
            <Text style={styles.label}>Beach Name *</Text>
            <TextInput
              style={[styles.input, styles.inputDisabled]}
              value={beachName}
              editable={false}
            />
          </View>

          {/* Time */}
          <View style={styles.row}>
            <View style={[styles.field, styles.flex]}>
              <Text style={styles.label}>Hour (0-23) *</Text>
              <TextInput
                style={styles.input}
                value={hour}
                onChangeText={setHour}
                keyboardType="number-pad"
                placeholder="HH"
                maxLength={2}
              />
            </View>
            <View style={{ width: 16 }} />
            <View style={[styles.field, styles.flex]}>
              <Text style={styles.label}>Minute (0-59) *</Text>
              <TextInput
                style={styles.input}
                value={minute}
                onChangeText={setMinute}
                keyboardType="number-pad"
                placeholder="MM"
                maxLength={2}
              />
            </View>
          </View>

          {/* Wind Speed */}
          <View style={styles.field}>
            <Text style={styles.label}>Wind Speed (km/h) *</Text>
            <TextInput
              style={styles.input}
              value={windSpeed}
              onChangeText={setWindSpeed}
              keyboardType="decimal-pad"
              placeholder="Enter wind speed"
            />
          </View>

          {/* Temperature */}
          <View style={styles.field}>
            <Text style={styles.label}>Temperature (°C) *</Text>
            <TextInput
              style={styles.input}
              value={temperature}
              onChangeText={setTemperature}
              keyboardType="decimal-pad"
              placeholder="Enter temperature"
            />
          </View>

          {/* Wave Height */}
          <View style={styles.field}>
            <Text style={styles.label}>Wave Height (m) *</Text>
            <TextInput
              style={styles.input}
              value={waveHeight}
              onChangeText={setWaveHeight}
              keyboardType="decimal-pad"
              placeholder="Enter wave height"
            />
          </View>

          {/* Submit Button */}
          <TouchableOpacity
            style={[styles.submitButton, loading && styles.submitButtonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.submitButtonText}>Submit Inform 4</Text>
            )}
          </TouchableOpacity>

          <View style={{ height: 32 }} />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  flex: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  field: {
    marginBottom: 16,
  },
  row: {
    flexDirection: 'row',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  inputDisabled: {
    backgroundColor: '#f9f9f9',
    color: '#999',
  },
  dateButton: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  dateText: {
    fontSize: 16,
    color: '#333',
  },
  submitButton: {
    backgroundColor: '#007AFF',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonDisabled: {
    backgroundColor: '#999',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});
