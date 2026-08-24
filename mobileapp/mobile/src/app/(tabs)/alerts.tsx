import { useQuery } from '@tanstack/react-query';
import { FlatList, Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Skeleton } from '@/components/Skeleton';
import { Colors, FontSize, MarketplaceColors, Spacing } from '@/constants/design';
import { getAlerts } from '@/lib/products';
import { useRouter } from 'expo-router';

function relativeTime(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
}

export default function AlertsScreen() {
  const router = useRouter();
  const { data, isFetching, isError } = useQuery({
    queryKey: ['alerts'],
    queryFn: getAlerts,
  });

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <View style={styles.container}>
        <Text style={styles.title}>Alerts</Text>
        <Text style={styles.subtitle}>Latest price drops we've seen across marketplaces.</Text>

        {isFetching && !data ? (
          <View style={styles.skeletonList}>
            {[0, 1, 2, 3].map((i) => (
              <View key={i} style={styles.skeletonCard}>
                <Skeleton style={styles.skeletonLine} />
                <Skeleton style={styles.skeletonShort} />
              </View>
            ))}
          </View>
        ) : (
          <FlatList
            style={styles.list}
            data={data ?? []}
            keyExtractor={(item) => `${item.product_id}-${item.marketplace_slug}`}
            ListEmptyComponent={
              isError ? (
                <Text style={styles.error}>Could not load alerts.</Text>
              ) : (
                <Text style={styles.empty}>No price drops recorded yet.</Text>
              )
            }
            renderItem={({ item }) => {
              const dotColor = MarketplaceColors[item.marketplace_slug] ?? Colors.primary;
              return (
                <Pressable
                  style={({ pressed }) => [styles.card, pressed && styles.pressed]}
                  onPress={() =>
                    router.push({
                      pathname: '/product/[id]',
                      params: { id: String(item.product_id) },
                    })
                  }>
                  <View style={styles.cardHeader}>
                    <View style={styles.source}>
                      <View style={[styles.dot, { backgroundColor: dotColor }]} />
                      <Text style={styles.sourceName}>{item.marketplace_name}</Text>
                    </View>
                    <Text style={styles.time}>{relativeTime(item.dropped_at)}</Text>
                  </View>
                  <Text style={styles.cardName} numberOfLines={2}>
                    {item.product_name}
                  </Text>
                  <View style={styles.cardFooter}>
                    <Text style={styles.oldPrice}>
                      ₹{item.old_price.toLocaleString('en-IN')}
                    </Text>
                    <Text style={styles.newPrice}>
                      ₹{item.new_price.toLocaleString('en-IN')}
                    </Text>
                    <View style={styles.badge}>
                      <Text style={styles.badgeText}>
                        −₹{item.drop_amount.toLocaleString('en-IN')} ({item.percent_drop}%)
                      </Text>
                    </View>
                  </View>
                </Pressable>
              );
            }}
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
  subtitle: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
  },
  list: {
    flex: 1,
  },
  card: {
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
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  source: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  sourceName: {
    fontSize: FontSize.caption,
    fontWeight: '600',
    color: Colors.textSecondary,
  },
  time: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
  },
  cardName: {
    fontSize: FontSize.subhead,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  oldPrice: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
    textDecorationLine: 'line-through',
    fontVariant: ['tabular-nums'],
  },
  newPrice: {
    fontSize: FontSize.subhead,
    fontWeight: '700',
    color: Colors.textPrimary,
    fontVariant: ['tabular-nums'],
  },
  badge: {
    marginLeft: 'auto',
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
  error: {
    fontSize: FontSize.body,
    color: Colors.error,
    textAlign: 'center',
    marginTop: Spacing.lg,
  },
  empty: {
    fontSize: FontSize.body,
    color: Colors.textSecondary,
    textAlign: 'center',
    marginTop: Spacing.lg,
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
  skeletonLine: {
    height: 16,
    width: '85%',
  },
  skeletonShort: {
    height: 12,
    width: '50%',
  },
});