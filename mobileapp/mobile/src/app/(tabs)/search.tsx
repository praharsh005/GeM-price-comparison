import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Skeleton } from '@/components/Skeleton';
import { Colors, FontSize, Spacing } from '@/constants/design';
import { searchProducts } from '@/lib/products';

function useDebouncedValue(value: string, delay = 400) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

export default function SearchScreen() {
  const router = useRouter();
  const { category } = useLocalSearchParams<{ category?: string }>();
  const [query, setQuery] = useState('');
  const debounced = useDebouncedValue(query);
  const activeCategory = typeof category === 'string' ? category : undefined;

  const { data, isFetching, isError, error } = useQuery({
    queryKey: ['search', debounced.trim(), activeCategory ?? ''],
    queryFn: () => searchProducts(debounced, activeCategory),
    enabled: debounced.trim().length > 0 || Boolean(activeCategory),
  });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        <Text style={styles.title}>Search</Text>
        <View style={styles.searchBar}>
          <TextInput
            style={styles.input}
            placeholder="Search products…"
            placeholderTextColor={Colors.textMuted}
            value={query}
            onChangeText={setQuery}
            autoCorrect={false}
          />
        </View>

        {activeCategory ? (
          <Pressable
            style={styles.chip}
            onPress={() => router.setParams({ category: undefined })}>
            <Text style={styles.chipText}>Category: {activeCategory}</Text>
            <Text style={styles.chipX}>✕</Text>
          </Pressable>
        ) : null}

        {isError && <Text style={styles.error}>Failed to load: {String(error)}</Text>}

        {isFetching && !data ? (
          <View style={styles.skeletonList}>
            {[0, 1, 2, 3, 4].map((i) => (
              <View key={i} style={styles.skeletonCard}>
                <Skeleton style={styles.skeletonName} />
                <Skeleton style={styles.skeletonMeta} />
              </View>
            ))}
          </View>
        ) : (
          <FlatList
            data={data ?? []}
            keyExtractor={(item) => String(item.id)}
            keyboardShouldPersistTaps="handled"
            ListEmptyComponent={
              (debounced.trim().length > 0 || activeCategory) && !isFetching && !isError ? (
                <Text style={styles.empty}>
                  No products found{debounced.trim() ? ` for "${debounced}"` : ''}.
                </Text>
              ) : (
                <Text style={styles.empty}>Search above to find products.</Text>
              )
            }
            renderItem={({ item }) => (
              <Pressable
                style={({ pressed }) => [styles.resultCard, pressed && styles.pressed]}
                onPress={() =>
                  router.push({ pathname: '/product/[id]', params: { id: String(item.id) } })
                }>
                <View style={styles.resultHeader}>
                  <Text style={styles.resultName} numberOfLines={2}>
                    {item.name}
                  </Text>
                  {item.brand ? <Text style={styles.resultBrand}>{item.brand}</Text> : null}
                </View>
                <View style={styles.resultFooter}>
                  {item.lowest_price !== null ? (
                    <Text style={styles.resultPrice}>
                      ₹{item.lowest_price.toLocaleString('en-IN')}
                    </Text>
                  ) : null}
                  <Text style={styles.resultMeta}>
                    Compare across {item.marketplace_count}{' '}
                    {item.marketplace_count === 1 ? 'store' : 'stores'}
                  </Text>
                </View>
              </Pressable>
            )}
          />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  container: {
    flex: 1,
    padding: Spacing.md,
    gap: Spacing.md,
  },
  title: {
    fontSize: FontSize.title,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minHeight: 44,
    gap: Spacing.sm,
  },
  input: {
    flex: 1,
    fontSize: FontSize.subhead,
    color: Colors.textPrimary,
  },
  error: {
    fontSize: FontSize.body,
    color: Colors.error,
  },
  empty: {
    fontSize: FontSize.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: Spacing.lg,
  },
  chip: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: Colors.accentTintBg,
    borderRadius: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minHeight: 36,
    gap: Spacing.sm,
  },
  chipText: {
    fontSize: FontSize.caption,
    fontWeight: '600',
    color: Colors.accentTintIcon,
  },
  chipX: {
    fontSize: FontSize.body,
    color: Colors.accentTintIcon,
  },
  skeletonList: {
    flex: 1,
  },
  skeletonCard: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
    gap: Spacing.sm,
  },
  skeletonName: {
    height: 16,
    width: '85%',
  },
  skeletonMeta: {
    height: 12,
    width: '45%',
  },
  resultCard: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
    gap: Spacing.sm,
  },
  pressed: {
    opacity: 0.7,
  },
  resultHeader: {
    gap: 2,
  },
  resultName: {
    fontSize: FontSize.subhead,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  resultBrand: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
  },
  resultFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  resultPrice: {
    fontSize: FontSize.subhead,
    fontWeight: '700',
    color: Colors.savingsGreen,
    fontVariant: ['tabular-nums'],
  },
  resultMeta: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
  },
});
