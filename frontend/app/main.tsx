import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { storage } from '../utils/storage';
import { Ionicons } from '@expo/vector-icons';

export default function MainScreen() {
  const router = useRouter();

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await storage.deleteItem('auth_token');
            await storage.deleteItem('username');
            router.replace('/');
          },
        },
      ]
    );
  };

  const handleInformPress = (informNumber: number) => {
    if (informNumber === 2) {
      router.push('/inform2');
    } else if (informNumber === 4) {
      router.push('/inform4');
    } else {
      Alert.alert('Coming Soon', `Inform ${informNumber} is not yet implemented`);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Beach Informs</Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={() => router.push('/settings')}
          >
            <Ionicons name="settings-outline" size={24} color="#007AFF" />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.headerButton}
            onPress={handleLogout}
          >
            <Ionicons name="log-out-outline" size={24} color="#FF3B30" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        <Text style={styles.subtitle}>Select an inform to fill</Text>
        
        <View style={styles.grid}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((num) => (
            <TouchableOpacity
              key={num}
              style={[
                styles.informButton,
                (num === 2 || num === 4) && styles.informButtonActive,
              ]}
              onPress={() => handleInformPress(num)}
            >
              <Text style={styles.informButtonNumber}>{num}</Text>
              <Text style={styles.informButtonText}>Inform {num}</Text>
              {(num === 2 || num === 4) && (
                <View style={styles.activeBadge} />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
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
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 16,
  },
  headerButton: {
    padding: 4,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 24,
    textAlign: 'center',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  informButton: {
    width: '48%',
    aspectRatio: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#e0e0e0',
  },
  informButtonActive: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  informButtonNumber: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 8,
  },
  informButtonText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  activeBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#34C759',
  },
});
