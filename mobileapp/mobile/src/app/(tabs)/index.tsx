import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'expo-router';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Skeleton } from '@/components/Skeleton';
import { Colors, FontSize, Spacing } from '@/constants/design';
import { getTrending } from '@/lib/products';

const CATEGORIES = [
  { slug: 'laptops', label: 'Laptops', icon: 'laptop-outline' },
  { slug: 'smartphones', label: 'Smartphones', icon: 'phone-portrait-outline' },
  { slug: 'televisions', label: 'Televisions', icon: 'tv-outline' },
  { slug: 'audio', label: 'Audio', icon: 'headset-outline' },
  { slug: 'wearables', label: 'Wearables', icon: 'watch-outline' },
] as const;

export default function HomeScreen() {
  const router = useRouter();
  const { data, isFetching, isError } = useQuery({
    queryKey: ['trending'],
    queryFn: getTrending,
  });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <FlatList
        style={styles.screen}
        contentContainerStyle={styles.content}
        data={data ?? []}
        keyExtractor={(item) => String(item.id)}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.title}>GeM Price Compare</Text>

            <Pressable
              style={({ pressed }) => [styles.searchEntry, pressed && styles.pressed]}
              onPress={() => router.push('/search')}>
              <Ionicons name="search-outline" size={18} color={Colors.textMuted} />
              <Text style={styles.searchPlaceholder}>Search products…</Text>
            </Pressable>

            <Text style={styles.sectionLabel}>Categories</Text>
            <View style={styles.categoryGrid}>
              {CATEGORIES.map((cat) => (
                <Pressable
                  key={cat.slug}
                  style={({ pressed }) => [styles.categoryCell, pressed && styles.pressed]}
                  onPress={() =>
                    router.push({ pathname: '/search', params: { category: cat.slug } })
                  }>
                  <View style={styles.categoryIcon}>
                    <Ionicons name={cat.icon} size={22} color={Colors.accentTintIcon} />
                  </View>
                  <Text style={styles.categoryLabel}>{cat.label}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.sectionLabel}>Trending savings</Text>
            {isFetching && !data ? <TrendingSkeleton /> : null}
            {isError ? (
              <Text style={styles.errorText}>Could not load trending savings.</Text>
            ) : null}
          </View>
        }
        renderItem={({ item }) => (
          <Pressable
            style={({ pressed }) => [styles.card, pressed && styles.pressed]}
            onPress={() =>
              router.push({ pathname: '/product/[id]', params: { id: String(item.id) } })
            }>
            <Text style={styles.cardName} numberOfLines={2}>
              {item.name}
            </Text>
            {item.brand ? <Text style={styles.cardBrand}>{item.brand}</Text> : null}
            <View style={styles.cardFooter}>
              <Text style={styles.cardPrice}>
                ₹{item.best_price?.toLocaleString('en-IN')}
                <Text style={styles.cardMarketplace}> at {item.best_marketplace}</Text>
              </Text>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>
                  Save ₹{item.savings?.toLocaleString('en-IN')} ({item.savings_pct}%)
                </Text>
              </View>
            </View>
          </Pressable>
        )}
      />
    </SafeAreaView>
  );
}

function TrendingSkeleton() {
  return (
    <View style={styles.skeletonList}>
      {[0, 1, 2, 3].map((i) => (
        <View key={i} style={styles.skeletonCard}>
          <Skeleton style={styles.skeletonLine} />
          <Skeleton style={styles.skeletonShort} />
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  screen: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.md,
    paddingBottom: Spacing.xl,
    gap: Spacing.sm,
  },
  header: {
    gap: Spacing.md,
  },
  title: {
    fontSize: FontSize.title,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  searchEntry: {
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
  searchPlaceholder: {
    fontSize: FontSize.body,
    color: Colors.textMuted,
  },
  pressed: {
    opacity: 0.7,
  },
  sectionLabel: {
    fontSize: FontSize.subhead,
    fontWeight: '700',
    color: Colors.textPrimary,
    marginTop: Spacing.sm,
  },
  categoryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.md,
    justifyContent: 'space-between',
  },
  categoryCell: {
    width: '18%',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  categoryIcon: {
    width: 52,
    height: 52,
    borderRadius: Spacing.md,
    backgroundColor: Colors.accentTintBg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  categoryLabel: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  card: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  cardName: {
    fontSize: FontSize.subhead,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  cardBrand: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: Spacing.sm,
    flexWrap: 'wrap',
  },
  cardPrice: {
    fontSize: FontSize.subhead,
    fontWeight: '700',
    color: Colors.textPrimary,
    fontVariant: ['tabular-nums'],
  },
  cardMarketplace: {
    fontSize: FontSize.caption,
    fontWeight: '400',
    color: Colors.textSecondary,
  },
  badge: {
    backgroundColor: Colors.savingsBadgeBg,
    borderRadius: Spacing.xs,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
  },
  badgeText: {
    fontSize: FontSize.caption,
    fontWeight: '700',
    color: Colors.savingsBadgeText,
  },
  errorText: {
    fontSize: FontSize.body,
    color: Colors.error,
  },
  skeletonList: {
    gap: Spacing.sm,
  },
  skeletonCard: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  skeletonLine: {
    height: 16,
    width: '90%',
  },
  skeletonShort: {
    height: 12,
    width: '40%',
  },
});
