import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import { useWindowDimensions } from 'react-native';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

import { Colors, FontSize, MarketplaceColors, Spacing } from '@/constants/design';
import { getPriceHistory, type PriceSeries } from '@/lib/products';

function formatShortDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getDate()}/${d.getMonth() + 1}`;
}

function compactPrice(value: number): string {
  if (value >= 100000) return `${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `${(value / 1000).toFixed(0)}k`;
  return `${value}`;
}

export default function PriceHistoryScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const productId = Number(id);
  const { width } = useWindowDimensions();
  const chartWidth = Math.max(width - Spacing.md * 2 - Spacing.lg * 2, 200);

  const { data, isFetching, isError } = useQuery({
    queryKey: ['price-history', productId],
    queryFn: () => getPriceHistory(productId),
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
        <Text style={styles.errorText}>Could not load price history.</Text>
      </View>
    );
  }

  const withHistory = data.series.filter((s) => s.points.length >= 2);

  if (withHistory.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Not enough snapshots yet.</Text>
      </View>
    );
  }

  const allDates = [...new Set(withHistory.flatMap((s) => s.points.map((p) => p.recorded_at)))].sort();
  const labels = allDates.map(formatShortDate);

  const datasets = withHistory.map((series) => {
    const byDate = new Map(series.points.map((p) => [p.recorded_at, p.price]));
    const data: number[] = [];
    let lastKnown: number | null = series.points[0]?.price ?? null;
    for (const date of allDates) {
      const price = byDate.get(date);
      if (price !== undefined) {
        lastKnown = price;
      }
      data.push(lastKnown ?? 0);
    }
    return {
      data,
      color: (opacity = 1) => MarketplaceColors[series.marketplace_slug] ?? Colors.primary,
    };
  });

  const allPrices = withHistory.flatMap((s) => s.points.map((p) => p.price));
  const allTimeLow = Math.min(...allPrices);
  const lowSeries = withHistory.find((s) => s.points.some((p) => p.price === allTimeLow));

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.name}>{data.name}</Text>
      <Text style={styles.category}>{data.category}</Text>

      <View style={styles.card}>
        <LineChart
          data={{ labels, datasets }}
          width={chartWidth}
          height={220}
          bezier
          withDots={allDates.length <= 12}
          withInnerLines
          fromZero={false}
          segments={4}
          formatYLabel={(value) => compactPrice(Number(value))}
          chartConfig={{
            backgroundGradientFrom: Colors.surface,
            backgroundGradientTo: Colors.surface,
            decimalPlaces: 0,
            color: () => Colors.primary,
            labelColor: () => Colors.textMuted,
            propsForBackgroundLines: { stroke: Colors.border },
            propsForDots: { r: '3' },
          }}
          style={styles.chart}
        />

        <View style={styles.legend}>
          {withHistory.map((series) => {
            const last = series.points[series.points.length - 1].price;
            const color = MarketplaceColors[series.marketplace_slug] ?? Colors.primary;
            return (
              <View key={series.listing_id} style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: color }]} />
                <Text style={styles.legendName}>{series.marketplace_name}</Text>
                <Text style={styles.legendPrice}>₹{last.toLocaleString('en-IN')}</Text>
              </View>
            );
          })}
        </View>

        {lowSeries ? (
          <Text style={styles.lowCaption}>
            All-time low: ₹{allTimeLow.toLocaleString('en-IN')} at {lowSeries.marketplace_name}
          </Text>
        ) : null}
      </View>
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
    gap: Spacing.md,
  },
  center: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorText: {
    fontSize: FontSize.body,
    color: Colors.error,
  },
  name: {
    fontSize: FontSize.heading,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  category: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.md,
  },
  chart: {
    borderRadius: Spacing.sm,
  },
  legend: {
    gap: Spacing.sm,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  legendName: {
    flex: 1,
    fontSize: FontSize.body,
    color: Colors.textSecondary,
  },
  legendPrice: {
    fontSize: FontSize.body,
    fontWeight: '700',
    color: Colors.textPrimary,
    fontVariant: ['tabular-nums'],
  },
  lowCaption: {
    fontSize: FontSize.caption,
    fontWeight: '600',
    color: Colors.savingsBadgeText,
  },
});