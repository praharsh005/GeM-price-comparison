import { useQuery } from '@tanstack/react-query';
import { Link, useLocalSearchParams, type Href } from 'expo-router';
import { ActivityIndicator, Linking, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Colors, FontSize, MarketplaceColors, Spacing } from '@/constants/design';
import { getProductCompare } from '@/lib/products';

export default function CompareScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const productId = Number(id);

  const { data, isFetching, isError } = useQuery({
    queryKey: ['compare', productId],
    queryFn: () => getProductCompare(productId),
    enabled: Number.isFinite(productId),
  });

  if (isFetching && !data) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  if (isError || !data) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Could not load product.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.name}>{data.name}</Text>
      {data.brand ? <Text style={styles.brand}>{data.brand}</Text> : null}
      <Text style={styles.category}>{data.category}</Text>

      {data.listings.map((listing) => {
        const best = listing.is_cheapest;
        const dotColor = MarketplaceColors[listing.marketplace_slug] ?? Colors.textMuted;
        return (
          <View key={listing.id} style={[styles.row, best && styles.rowBest]}>
            <View style={styles.rowHeader}>
              <View style={styles.marketplace}>
                <View style={[styles.dot, { backgroundColor: dotColor }]} />
                <Text style={styles.marketplaceName}>{listing.marketplace_name}</Text>
              </View>
              {best && (
                <View style={styles.pill}>
                  <Text style={styles.pillText}>Best price</Text>
                </View>
              )}
            </View>
            <Text style={[styles.price, best && styles.priceBest]}>
              ₹{listing.price.toLocaleString('en-IN')}
            </Text>
            {listing.available ? (
              <Text style={styles.available}>In stock</Text>
            ) : (
              <Text style={styles.unavailable}>Out of stock</Text>
            )}
            {best && listing.url ? (
              <Pressable
                style={({ pressed }) => [styles.goSite, pressed && styles.goSitePressed]}
                onPress={() => Linking.openURL(listing.url)}>
                <Text style={styles.goSiteText}>Go to site</Text>
              </Pressable>
            ) : null}
          </View>
        );
      })}

      {data.best_marketplace ? (
        <Text style={styles.bestSummary}>
          Best price at {data.best_marketplace}: ₹{data.best_price?.toLocaleString('en-IN')}
        </Text>
      ) : null}

      <Link href={`/product/${productId}/history` as Href} asChild>
        <Pressable style={({ pressed }) => [styles.historyButton, pressed && styles.historyButtonPressed]}>
          <Text style={styles.historyButtonText}>View price history</Text>
        </Pressable>
      </Link>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  center: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    fontSize: 14,
    color: Colors.error,
  },
  name: {
    fontSize: FontSize.heading,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  brand: {
    fontSize: FontSize.body,
    color: Colors.textSecondary,
  },
  category: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
    textTransform: 'uppercase',
    marginBottom: Spacing.sm,
  },
  row: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  rowBest: {
    borderColor: Colors.savingsGreen,
    backgroundColor: Colors.savingsGreenBg,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  marketplace: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.xs,
  },
  dot: {
    width: 7,
    height: 7,
    borderRadius: 4,
  },
  marketplaceName: {
    fontSize: FontSize.body,
    color: Colors.textSecondary,
  },
  pill: {
    backgroundColor: Colors.savingsGreen,
    borderRadius: Spacing.xs,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
  },
  pillText: {
    color: '#FFFFFF',
    fontSize: FontSize.caption,
    fontWeight: '700',
  },
  price: {
    fontSize: FontSize.heading,
    fontWeight: '700',
    color: Colors.textPrimary,
    fontVariant: ['tabular-nums'],
  },
  priceBest: {
    color: Colors.savingsGreen,
  },
  available: {
    fontSize: FontSize.caption,
    color: Colors.textSecondary,
  },
  unavailable: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
  },
  goSite: {
    backgroundColor: Colors.savingsGreen,
    borderRadius: Spacing.sm,
    paddingHorizontal: Spacing.md,
    paddingVertical: 10,
    alignItems: 'center',
    alignSelf: 'flex-start',
    minHeight: 44,
    justifyContent: 'center',
  },
  goSitePressed: {
    opacity: 0.8,
  },
  goSiteText: {
    color: '#FFFFFF',
    fontSize: FontSize.body,
    fontWeight: '700',
  },
  bestSummary: {
    marginTop: Spacing.sm,
    fontSize: FontSize.body,
    fontWeight: '600',
    color: Colors.savingsGreen,
  },
  historyButton: {
    marginTop: Spacing.sm,
    backgroundColor: Colors.primary,
    borderRadius: Spacing.md,
    paddingVertical: 12,
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  historyButtonPressed: {
    opacity: 0.8,
  },
  historyButtonText: {
    color: '#FFFFFF',
    fontSize: 15,
    fontWeight: '700',
  },
});
