import { useState, useCallback } from 'react';
import { View, Text, FlatList, Image, TouchableOpacity, StyleSheet, Linking } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useFocusEffect } from 'expo-router';

type TrackedProduct = {
  url: string;
  image_url: string | null;
  name: string;
  site: string;
  price: number;
  original_price: number | null;
  in_stock: boolean;
  trackedPrice: number;
  trackedAt: string;
};

export default function TrackScreen() {
  const [items, setItems] = useState<TrackedProduct[]>([]);

  const load = async () => {
    const keys = await AsyncStorage.getAllKeys();
    const stores = await AsyncStorage.multiGet(keys);
    const parsed = stores.map(([_, val]) => val ? JSON.parse(val) : null).filter(Boolean);
    setItems(parsed);
  };

  useFocusEffect(useCallback(() => { load(); }, []));

  const remove = async (url: string) => {
    await AsyncStorage.removeItem(url);
    setItems(prev => prev.filter(i => i.url !== url));
  };

  if (items.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyIcon}>☆</Text>
        <Text style={styles.emptyText}>Henüz takip edilen ürün yok.</Text>
        <Text style={styles.emptySubText}>Arama sonuçlarında ★ ikonuna bas.</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>★ Takip Edilenler</Text>
      <FlatList
        data={items}
        keyExtractor={(item) => item.url}
        renderItem={({ item }) => {
          const priceDiff = item.price - item.trackedPrice;
          const addedDate = new Date(item.trackedAt).toLocaleDateString('tr-TR');
          return (
            <TouchableOpacity style={styles.card} onPress={() => Linking.openURL(item.url)}>
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
                  {priceDiff !== 0 && (
                    <Text style={priceDiff < 0 ? styles.priceDown : styles.priceUp}>
                      {priceDiff < 0 ? '▼' : '▲'} {Math.abs(priceDiff).toFixed(2)} ₺
                    </Text>
                  )}
                </View>
                <Text style={styles.trackedInfo}>Eklendiğinde: {item.trackedPrice} ₺ · {addedDate}</Text>
              </View>
              <TouchableOpacity style={styles.removeBtn} onPress={() => remove(item.url)}>
                <Text style={styles.removeBtnText}>✕</Text>
              </TouchableOpacity>
            </TouchableOpacity>
          );
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f0f', paddingTop: 60, paddingHorizontal: 16 },
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 16, color: '#ffffff' },
  empty: { flex: 1, backgroundColor: '#0f0f0f', justifyContent: 'center', alignItems: 'center' },
  emptyIcon: { fontSize: 48, color: '#555', marginBottom: 12 },
  emptyText: { fontSize: 16, color: '#555', marginBottom: 4 },
  emptySubText: { fontSize: 13, color: '#333' },
  card: { flexDirection: 'row', backgroundColor: '#1a1a1a', borderRadius: 12, padding: 12, marginBottom: 10, borderWidth: 1, borderColor: '#2a2a2a', alignItems: 'center' },
  image: { width: 70, height: 70, borderRadius: 8, marginRight: 12 },
  imagePlaceholder: { backgroundColor: '#2a2a2a' },
  info: { flex: 1 },
  name: { fontSize: 13, fontWeight: '600', color: '#ffffff', marginBottom: 4 },
  site: { fontSize: 12, color: '#6366f1', marginBottom: 4 },
  priceRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 2 },
  price: { fontSize: 16, fontWeight: 'bold', color: '#22c55e' },
  priceDown: { fontSize: 12, color: '#22c55e', fontWeight: 'bold' },
  priceUp: { fontSize: 12, color: '#ef4444', fontWeight: 'bold' },
  trackedInfo: { fontSize: 11, color: '#555' },
  removeBtn: { padding: 8, borderRadius: 8, backgroundColor: '#2a2a2a', marginLeft: 8 },
  removeBtnText: { fontSize: 14, color: '#ef4444' },
});