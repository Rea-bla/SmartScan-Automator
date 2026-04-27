import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  FlatList, Image, ActivityIndicator,
  StyleSheet, Linking, StatusBar
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = process.env.EXPO_PUBLIC_API_URL;

type Product = {
  url: string;
  image_url: string | null;
  name: string;
  site: string;
  price: number;
  original_price: number | null;
  in_stock: boolean;
};

export default function HomeScreen() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [tracked, setTracked] = useState<string[]>([]);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const url = `${API_URL}/api/v1/search?q=${encodeURIComponent(query)}&limit=20`;
      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();
      setResults(data.results || []);
      const keys = await AsyncStorage.getAllKeys();
      setTracked([...keys]);
    } catch (e) {
      console.error("Bağlantı Hatası:", e);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrack = async (item: Product) => {
    const key = item.url;
    const existing = await AsyncStorage.getItem(key);
    if (existing) {
      await AsyncStorage.removeItem(key);
      setTracked(prev => prev.filter(k => k !== key));
    } else {
      await AsyncStorage.setItem(key, JSON.stringify({ ...item, trackedPrice: item.price, trackedAt: new Date().toISOString() }));
      setTracked(prev => [...prev, key]);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f0f0f" />
      <Text style={styles.title}>⚡ SmartScan</Text>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.input}
          placeholder="Ürün ara..."
          placeholderTextColor="#555"
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={search}
        />
        <TouchableOpacity style={styles.button} onPress={search}>
          <Text style={styles.buttonText}>Ara</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 30 }} />}

      {!loading && searched && results.length === 0 && (
        <Text style={styles.empty}>Sonuç bulunamadı.</Text>
      )}

      <FlatList
        data={results}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item, index }) => {
          const isTracked = tracked.includes(item.url);
          return (
            <View style={styles.card}>
              <TouchableOpacity style={styles.cardMain} onPress={() => Linking.openURL(item.url)}>
                <Text style={styles.rank}>#{index + 1}</Text>
                {item.image_url ? (
                  <Image source={{ uri: item.image_url }} style={styles.image} />
                ) : (
                  <View style={[styles.image, styles.imagePlaceholder]} />
                )}
                <View style={styles.info}>
                  <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
                  <Text style={styles.site}>{item.site}</Text>
                  <View style={styles.priceRow}>
                    <Text style={styles.price}>{item.price} ₺</Text>
                    {item.original_price && item.original_price > item.price && (
                      <Text style={styles.oldPrice}>{item.original_price} ₺</Text>
                    )}
                  </View>
                  {!item.in_stock && <Text style={styles.outOfStock}>Stok yok</Text>}
                </View>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.trackBtn, isTracked && styles.trackBtnActive]} onPress={() => toggleTrack(item)}>
                <Text style={styles.trackBtnText}>{isTracked ? '★' : '☆'}</Text>
              </TouchableOpacity>
            </View>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f0f', paddingTop: 60, paddingHorizontal: 16 },
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 16, color: '#ffffff' },
  searchRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  input: { flex: 1, backgroundColor: '#1a1a1a', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 16, borderWidth: 1, borderColor: '#2a2a2a', color: '#fff' },
  button: { backgroundColor: '#6366f1', borderRadius: 12, paddingHorizontal: 20, justifyContent: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  empty: { textAlign: 'center', marginTop: 40, color: '#555', fontSize: 16 },
  card: { flexDirection: 'row', backgroundColor: '#1a1a1a', borderRadius: 12, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: '#2a2a2a', alignItems: 'center' },
  cardMain: { flexDirection: 'row', flex: 1 },
  rank: { fontSize: 12, color: '#555', marginRight: 8, marginTop: 2 },
  image: { width: 70, height: 70, borderRadius: 8, marginRight: 12 },
  imagePlaceholder: { backgroundColor: '#2a2a2a' },
  info: { flex: 1 },
  name: { fontSize: 13, fontWeight: '600', color: '#ffffff', marginBottom: 4 },
  site: { fontSize: 12, color: '#6366f1', marginBottom: 4 },
  priceRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  price: { fontSize: 16, fontWeight: 'bold', color: '#22c55e' },
  oldPrice: { fontSize: 12, color: '#555', textDecorationLine: 'line-through' },
  outOfStock: { fontSize: 12, color: '#ef4444', marginTop: 2 },
  trackBtn: { padding: 8, borderRadius: 8, backgroundColor: '#2a2a2a', marginLeft: 8 },
  trackBtnActive: { backgroundColor: '#6366f1' },
  trackBtnText: { fontSize: 18, color: '#fff' },
});