import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  FlatList, Image, ActivityIndicator,
  StyleSheet, Linking
} from 'react-native';

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

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/search?q=${encodeURIComponent(query)}`);
      const data = await res.json();
      setResults(data.results);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔍 SmartScan</Text>
      <View style={styles.searchRow}>
        <TextInput
          style={styles.input}
          placeholder="Ürün ara..."
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={search}
        />
        <TouchableOpacity style={styles.button} onPress={search}>
          <Text style={styles.buttonText}>Ara</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 20 }} />}

      {!loading && searched && results.length === 0 && (
        <Text style={styles.empty}>Sonuç bulunamadı.</Text>
      )}

      <FlatList
        data={results}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item, index }) => (
          <TouchableOpacity style={styles.card} onPress={() => Linking.openURL(item.url)}>
            <Text style={styles.rank}>#{index + 1}</Text>
            {item.image_url ? (
              <Image source={{ uri: item.image_url }} style={styles.image} />
            ) : null}
            <View style={styles.info}>
              <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
              <Text style={styles.site}>{item.site}</Text>
              <Text style={styles.price}>{item.price} ₺</Text>
              {item.original_price && item.original_price > item.price && (
                <Text style={styles.oldPrice}>{item.original_price} ₺</Text>
              )}
              {!item.in_stock && <Text style={styles.outOfStock}>Stok yok</Text>}
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc', paddingTop: 60, paddingHorizontal: 16 },
  title: { fontSize: 28, fontWeight: 'bold', marginBottom: 16, color: '#1e293b' },
  searchRow: { flexDirection: 'row', gap: 8, marginBottom: 16 },
  input: { flex: 1, backgroundColor: '#fff', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 16, borderWidth: 1, borderColor: '#e2e8f0' },
  button: { backgroundColor: '#6366f1', borderRadius: 12, paddingHorizontal: 20, justifyContent: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  empty: { textAlign: 'center', marginTop: 40, color: '#94a3b8', fontSize: 16 },
  card: { flexDirection: 'row', backgroundColor: '#fff', borderRadius: 12, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: '#e2e8f0' },
  rank: { fontSize: 12, color: '#94a3b8', marginRight: 8, marginTop: 2 },
  image: { width: 70, height: 70, borderRadius: 8, marginRight: 12 },
  info: { flex: 1 },
  name: { fontSize: 14, fontWeight: '600', color: '#1e293b', marginBottom: 4 },
  site: { fontSize: 12, color: '#6366f1', marginBottom: 4 },
  price: { fontSize: 16, fontWeight: 'bold', color: '#16a34a' },
  oldPrice: { fontSize: 12, color: '#94a3b8', textDecorationLine: 'line-through' },
  outOfStock: { fontSize: 12, color: '#ef4444', marginTop: 2 },
});