import { useQuery } from '@tanstack/react-query';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Alert, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Colors, FontSize, Spacing } from '@/constants/design';
import { apiGet, getApiBaseUrl, setApiBaseUrl } from '@/lib/api';
import { getInsights } from '@/lib/products';

function fmt(value: number): string {
  return `₹${value.toLocaleString('en-IN')}`;
}

type HealthState = 'loading' | 'ok' | 'error';

export default function ProfileScreen() {
  const [health, setHealth] = useState<HealthState>('loading');
  const [healthError, setHealthError] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState<string>('');
  const [editing, setEditing] = useState(false);
  const [inputUrl, setInputUrl] = useState('');

  const { data, isFetching, isError } = useQuery({
    queryKey: ['insights'],
    queryFn: getInsights,
  });

  const checkHealth = useCallback(async () => {
    setHealth('loading');
    setHealthError(null);
    try {
      const body = await apiGet<{ status: string }>('/health');
      setHealth(body.status === 'ok' ? 'ok' : 'error');
    } catch (e) {
      setHealth('error');
      setHealthError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    checkHealth();
    getApiBaseUrl().then(setApiUrl);
  }, [checkHealth]);

  const handleSaveUrl = async () => {
    const trimmed = inputUrl.trim();
    if (!trimmed) {
      Alert.alert('Error', 'Please enter a valid URL');
      return;
    }
    try {
      await setApiBaseUrl(trimmed);
      setApiUrl(trimmed);
      setEditing(false);
      checkHealth();
    } catch (e) {
      Alert.alert('Error', 'Failed to save URL');
    }
  };

  const handleClearUrl = async () => {
    await setApiBaseUrl(null);
    const base = await getApiBaseUrl();
    setApiUrl(base);
    checkHealth();
  };

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
        <Text style={styles.title}>Savings insights</Text>
        <Text style={styles.subtitle}>Average savings when buying on GeM vs the next-cheapest marketplace.</Text>

        {isFetching && !data ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={Colors.primary} />
          </View>
        ) : null}

        {isError || !data ? (
          <Text style={styles.errorText}>Could not load insights.</Text>
        ) : (
          <>
            <View style={styles.overallCard}>
              <Text style={styles.overallLabel}>Across {data.overall.products_with_gem} products</Text>
              <Text style={styles.overallValue}>{fmt(data.overall.avg_savings)}</Text>
              <Text style={styles.overallCaption}>average savings per product</Text>
              <Text style={styles.overallCaption}>
                {fmt(data.overall.total_savings)} total if everything bought on GeM
              </Text>
            </View>

            {data.categories.map((c) => (
              <View key={c.category} style={styles.row}>
                <View style={styles.rowHeader}>
                  <Text style={styles.rowLabel}>{c.category}</Text>
                  <Text style={styles.rowValue}>{fmt(c.avg_savings)}</Text>
                </View>
                <View style={styles.barTrack}>
                  <View
                    style={[
                      styles.barFill,
                      { width: `${Math.min(100, (c.avg_savings / Math.max(data.overall.avg_savings, 1)) * 100)}%` },
                    ]}
                  />
                </View>
                <Text style={styles.rowCaption}>
                  avg over {c.products_with_gem} products with a GeM listing
                </Text>
              </View>
            ))}
          </>
        )}

        <View style={styles.healthCard}>
          <View style={styles.healthRow}>
            <View
              style={[
                styles.healthDot,
                { backgroundColor: health === 'ok' ? Colors.savingsGreen : health === 'error' ? Colors.error : Colors.textMuted },
              ]}
            />
            <Text style={styles.healthText}>
              {health === 'loading' && 'Checking backend…'}
              {health === 'ok' && 'Backend reachable'}
              {health === 'error' && 'Backend unreachable'}
            </Text>
            {health === 'error' ? (
              <Pressable style={styles.healthRetry} onPress={checkHealth}>
                <Text style={styles.healthRetryText}>Retry</Text>
              </Pressable>
            ) : null}
          </View>
          <Text style={styles.healthUrl}>{apiUrl}</Text>
          {health === 'error' && healthError ? (
            <Text style={styles.healthError}>{healthError}</Text>
          ) : null}
        </View>

        <View style={styles.settingsCard}>
          <Text style={styles.settingsTitle}>API Settings</Text>
          <View style={styles.settingsRow}>
            <Text style={styles.settingsLabel}>Backend URL</Text>
            {editing ? (
              <View style={styles.inputWrapper}>
                <TextInput
                  style={styles.textInput}
                  value={inputUrl}
                  onChangeText={setInputUrl}
                  placeholder="http://192.168.x.x:8000"
                  autoCapitalize="none"
                  autoComplete="off"
                  onSubmitEditing={handleSaveUrl}
                />
              </View>
            ) : (
              <View style={styles.urlDisplay}>
                <Text style={styles.urlText} numberOfLines={1}>{apiUrl}</Text>
              </View>
            )}
          </View>
          <View style={styles.buttonRow}>
            {editing ? (
              <>
                <Pressable style={[styles.button, styles.buttonPrimary]} onPress={handleSaveUrl}>
                  <Text style={styles.buttonText}>Save</Text>
                </Pressable>
                <Pressable style={[styles.button, styles.buttonSecondary]} onPress={() => { setInputUrl(apiUrl); setEditing(false); }}>
                  <Text style={styles.buttonText}>Cancel</Text>
                </Pressable>
              </>
            ) : (
              <>
                <Pressable style={[styles.button, styles.buttonPrimary]} onPress={() => { setInputUrl(apiUrl); setEditing(true); }}>
                  <Text style={styles.buttonText}>Edit</Text>
                </Pressable>
                <Pressable style={[styles.button, styles.buttonSecondary]} onPress={handleClearUrl}>
                  <Text style={styles.buttonText}>Reset to default</Text>
                </Pressable>
              </>
            )}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
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
    gap: Spacing.md,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  subtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  center: {
    paddingVertical: Spacing.xl,
    alignItems: 'center',
  },
  errorText: {
    fontSize: 14,
    color: Colors.error,
  },
  overallCard: {
    backgroundColor: Colors.savingsGreenBg,
    borderColor: Colors.savingsGreen,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  overallLabel: {
    fontSize: 13,
    color: Colors.savingsBadgeText,
  },
  overallValue: {
    fontSize: 32,
    fontWeight: '800',
    color: Colors.savingsBadgeText,
  },
  overallCaption: {
    fontSize: 12,
    color: Colors.savingsBadgeText,
  },
  row: {
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  rowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  rowLabel: {
    fontSize: 15,
    fontWeight: '600',
    color: Colors.textPrimary,
    textTransform: 'capitalize',
  },
  rowValue: {
    fontSize: 15,
    fontWeight: '700',
    color: Colors.savingsGreen,
  },
  barTrack: {
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.border,
    overflow: 'hidden',
  },
  barFill: {
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.savingsGreen,
  },
  rowCaption: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
  },
  healthCard: {
    marginTop: Spacing.sm,
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.xs,
  },
  healthRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
  },
  healthDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  healthText: {
    flex: 1,
    fontSize: FontSize.body,
    fontWeight: '600',
    color: Colors.textPrimary,
  },
  healthUrl: {
    fontSize: FontSize.caption,
    color: Colors.textMuted,
  },
  healthError: {
    fontSize: FontSize.caption,
    color: Colors.error,
  },
  healthRetry: {
    backgroundColor: Colors.primary,
    borderRadius: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minHeight: 44,
    justifyContent: 'center',
  },
  healthRetryText: {
    color: '#FFFFFF',
    fontSize: FontSize.caption,
    fontWeight: '600',
  },
  settingsCard: {
    marginTop: Spacing.sm,
    backgroundColor: Colors.surface,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.md,
    padding: Spacing.md,
    gap: Spacing.sm,
  },
  settingsTitle: {
    fontSize: FontSize.body,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  settingsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: Spacing.md,
  },
  settingsLabel: {
    fontSize: FontSize.body,
    color: Colors.textSecondary,
  },
  inputWrapper: {
    flex: 1,
    backgroundColor: Colors.background,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.sm,
    minHeight: 44,
  },
  textInput: {
    flex: 1,
    padding: Spacing.sm,
    fontSize: FontSize.body,
    color: Colors.textPrimary,
  },
  urlDisplay: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    minHeight: 44,
    backgroundColor: Colors.background,
    borderColor: Colors.border,
    borderWidth: 1,
    borderRadius: Spacing.sm,
    paddingHorizontal: Spacing.sm,
  },
  urlText: {
    fontSize: FontSize.body,
    color: Colors.textPrimary,
    flexShrink: 1,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginTop: Spacing.xs,
  },
  button: {
    flex: 1,
    borderRadius: Spacing.sm,
    paddingVertical: Spacing.sm,
    paddingHorizontal: Spacing.md,
    minHeight: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonPrimary: {
    backgroundColor: Colors.primary,
  },
  buttonSecondary: {
    backgroundColor: Colors.background,
    borderColor: Colors.border,
    borderWidth: 1,
  },
  buttonText: {
    fontSize: FontSize.body,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});