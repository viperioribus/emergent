import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { storage } from '../utils/storage';
import { Ionicons } from '@expo/vector-icons';

const EXPO_PUBLIC_BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Beach {
  id: string;
  name: string;
}

interface BeachPost {
  id: string;
  beach_id: string;
  name: string;
}

export default function SettingsScreen() {
  const router = useRouter();
  const [beaches, setBeaches] = useState<Beach[]>([]);
  const [beachPosts, setBeachPosts] = useState<BeachPost[]>([]);
  const [selectedBeach, setSelectedBeach] = useState<Beach | null>(null);
  const [selectedBeachPost, setSelectedBeachPost] = useState<BeachPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingPosts, setLoadingPosts] = useState(false);

  useEffect(() => {
    loadBeaches();
    loadSavedSettings();
  }, []);

  const loadSavedSettings = async () => {
    try {
      const savedBeach = await storage.getItem('selected_beach');
      const savedBeachPost = await storage.getItem('selected_beach_post');
      if (savedBeach) {
        setSelectedBeach(JSON.parse(savedBeach));
        if (savedBeachPost) {
          setSelectedBeachPost(JSON.parse(savedBeachPost));
        }
      }
    } catch (error) {
      console.error('Error loading saved settings:', error);
    }
  };

  const loadBeaches = async () => {
    try {
      const token = await storage.getItem('auth_token');
      const response = await fetch(`${EXPO_PUBLIC_BACKEND_URL}/api/beaches`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBeaches(data);
      } else {
        Alert.alert('Error', 'Failed to load beaches');
      }
    } catch (error) {
      console.error('Error loading beaches:', error);
      Alert.alert('Error', 'Unable to connect to server');
    } finally {
      setLoading(false);
    }
  };

  const loadBeachPosts = async (beachId: string) => {
    setLoadingPosts(true);
    try {
      const token = await storage.getItem('auth_token');
      const response = await fetch(
        `${EXPO_PUBLIC_BACKEND_URL}/api/beach-posts/${beachId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setBeachPosts(data);
      } else {
        Alert.alert('Error', 'Failed to load beach posts');
      }
    } catch (error) {
      console.error('Error loading beach posts:', error);
      Alert.alert('Error', 'Unable to connect to server');
    } finally {
      setLoadingPosts(false);
    }
  };

  const handleBeachSelect = async (beach: Beach) => {
    setSelectedBeach(beach);
    setSelectedBeachPost(null);
    setBeachPosts([]);
    await storage.setItem('selected_beach', JSON.stringify(beach));
    await storage.deleteItem('selected_beach_post');
    loadBeachPosts(beach.id);
  };

  const handleBeachPostSelect = async (post: BeachPost) => {
    setSelectedBeachPost(post);
    await storage.setItem('selected_beach_post', JSON.stringify(post));
    Alert.alert('Success', 'Beach post selected successfully');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* Beach Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Beach</Text>
          {beaches.map((beach) => (
            <TouchableOpacity
              key={beach.id}
              style={[
                styles.listItem,
                selectedBeach?.id === beach.id && styles.listItemSelected,
              ]}
              onPress={() => handleBeachSelect(beach)}
            >
              <Text
                style={[
                  styles.listItemText,
                  selectedBeach?.id === beach.id && styles.listItemTextSelected,
                ]}
              >
                {beach.name}
              </Text>
              {selectedBeach?.id === beach.id && (
                <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
              )}
            </TouchableOpacity>
          ))}
        </View>

        {/* Beach Post Selection */}
        {selectedBeach && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Select Beach Post</Text>
            {loadingPosts ? (
              <ActivityIndicator color="#007AFF" style={{ marginVertical: 16 }} />
            ) : beachPosts.length > 0 ? (
              beachPosts.map((post) => (
                <TouchableOpacity
                  key={post.id}
                  style={[
                    styles.listItem,
                    selectedBeachPost?.id === post.id && styles.listItemSelected,
                  ]}
                  onPress={() => handleBeachPostSelect(post)}
                >
                  <Text
                    style={[
                      styles.listItemText,
                      selectedBeachPost?.id === post.id && styles.listItemTextSelected,
                    ]}
                  >
                    {post.name}
                  </Text>
                  {selectedBeachPost?.id === post.id && (
                    <Ionicons name="checkmark-circle" size={24} color="#007AFF" />
                  )}
                </TouchableOpacity>
              ))
            ) : (
              <Text style={styles.emptyText}>No beach posts available</Text>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
  },
  section: {
    marginTop: 24,
    paddingHorizontal: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  listItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  listItemSelected: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  listItemText: {
    fontSize: 16,
    color: '#333',
  },
  listItemTextSelected: {
    color: '#007AFF',
    fontWeight: '600',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginTop: 16,
  },
});
